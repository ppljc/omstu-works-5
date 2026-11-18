namespace lab6;

public interface IEventPublisher
{
    Task PublishAsync(string eventType, Car car);
}
