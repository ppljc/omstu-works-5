namespace lab5;

public interface IEventPublisher
{
    Task PublishAsync(string eventType, Car car);
}
