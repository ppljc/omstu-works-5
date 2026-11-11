namespace lab5;

public sealed class EventPublishingCarRepository : ICarRepository
{
    private const string CreateEvent = "CREATE";
    private const string UpdateEvent = "UPDATE";
    private const string DeleteEvent = "DELETE";

    private readonly ICarRepository _inner;
    private readonly IEventPublisher _publisher;

    public EventPublishingCarRepository(ICarRepository inner, IEventPublisher publisher)
    {
        _inner = inner;
        _publisher = publisher;
    }

    public Task<IEnumerable<Car>> GetAll() => _inner.GetAll();

    public Task<Car?> GetById(int id) => _inner.GetById(id);

    public Task<int> CountByDealerId(int dealerId) => _inner.CountByDealerId(dealerId);

    public async Task<Car> Create(Car car)
    {
        var created = await _inner.Create(car);

        await _publisher.PublishAsync(CreateEvent, created);

        return created;
    }

    public async Task<bool> Update(Car car)
    {
        var updated = await _inner.Update(car);

        if (updated)
        {
            await _publisher.PublishAsync(UpdateEvent, car);
        }

        return updated;
    }

    public async Task<bool> Delete(int id)
    {
        var car = await _inner.GetById(id);

        var deleted = await _inner.Delete(id);

        if (deleted && car is not null)
        {
            await _publisher.PublishAsync(DeleteEvent, car);
        }

        return deleted;
    }
}
