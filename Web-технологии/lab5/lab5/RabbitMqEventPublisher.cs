using System.Text;
using RabbitMQ.Client;

namespace lab5;

public sealed class RabbitMqEventPublisher : IEventPublisher, IAsyncDisposable
{
    private readonly RabbitMqOptions _options;
    private readonly ILogger<RabbitMqEventPublisher> _logger;
    private readonly SemaphoreSlim _initLock = new(1, 1);
    private readonly SemaphoreSlim _publishLock = new(1, 1);

    private IConnection? _connection;
    private IChannel? _channel;
    private bool _disposed;

    public RabbitMqEventPublisher(RabbitMqOptions options, ILogger<RabbitMqEventPublisher> logger)
    {
        _options = options;
        _logger = logger;
    }

    public async Task InitializeAsync(CancellationToken cancellationToken = default)
    {
        await GetChannelAsync(cancellationToken);
    }

    public async Task PublishAsync(string eventType, Car car)
    {
        var payload = CarEvent.Create(eventType, car);
        var body = Encoding.UTF8.GetBytes(payload.ToJson());

        try
        {
            await PublishAsync(eventType, body, CancellationToken.None);
        }
        catch (Exception ex)
        {
            _logger.LogError(ex,
                "Не удалось отправить событие {EventType} для автомобиля {CarId}",
                eventType, car.Id);
        }
    }

    private async Task PublishAsync(string eventType, byte[] body, CancellationToken cancellationToken)
    {
        var channel = await GetChannelAsync(cancellationToken);

        await _publishLock.WaitAsync(cancellationToken);
        try
        {
            await channel.BasicPublishAsync(
                exchange: _options.ExchangeName,
                routingKey: "",
                mandatory: false,
                basicProperties: new BasicProperties(),
                body: body,
                cancellationToken: cancellationToken);

            _logger.LogInformation(
                "Опубликовано событие {EventType} в {Exchange}, {Bytes} байт",
                eventType, _options.ExchangeName, body.Length);
        }
        finally
        {
            _publishLock.Release();
        }
    }

    private async Task<IChannel> GetChannelAsync(CancellationToken cancellationToken)
    {
        if (_channel is { IsOpen: true })
        {
            return _channel;
        }

        await _initLock.WaitAsync(cancellationToken);
        try
        {
            if (_channel is { IsOpen: true })
            {
                return _channel;
            }

            if (_connection is not { IsOpen: true })
            {
                var factory = new ConnectionFactory
                {
                    HostName = _options.HostName,
                    Port = _options.Port,
                    UserName = _options.UserName,
                    Password = _options.Password
                };

                _connection = await factory.CreateConnectionAsync(cancellationToken);
            }

            var channel = await _connection.CreateChannelAsync(cancellationToken: cancellationToken);

            await channel.ExchangeDeclareAsync(
                exchange: _options.ExchangeName,
                type: ExchangeType.Fanout,
                durable: true,
                autoDelete: false,
                cancellationToken: cancellationToken);

            await channel.QueueDeclareAsync(
                queue: _options.QueueName,
                durable: true,
                exclusive: false,
                autoDelete: false,
                cancellationToken: cancellationToken);

            await channel.QueueBindAsync(
                queue: _options.QueueName,
                exchange: _options.ExchangeName,
                routingKey: "",
                cancellationToken: cancellationToken);

            _channel = channel;

            _logger.LogInformation(
                "Точка обмена {Exchange} связана с очередью {Queue}",
                _options.ExchangeName, _options.QueueName);

            return channel;
        }
        finally
        {
            _initLock.Release();
        }
    }

    public async ValueTask DisposeAsync()
    {
        if (_disposed)
        {
            return;
        }

        _disposed = true;

        if (_channel is not null)
        {
            await _channel.DisposeAsync();
        }

        if (_connection is not null)
        {
            await _connection.DisposeAsync();
        }

        _initLock.Dispose();
        _publishLock.Dispose();
    }
}
