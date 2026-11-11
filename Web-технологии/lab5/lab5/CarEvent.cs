using System.Text.Json;

namespace lab5;

public sealed class CarEvent
{
    private static readonly JsonSerializerOptions JsonOptions = new()
    {
        PropertyNamingPolicy = JsonNamingPolicy.CamelCase
    };

    public string EventType { get; init; } = "";
    public CarEventPayload Car { get; init; } = new();

    public static CarEvent Create(string eventType, Car car) => new()
    {
        EventType = eventType,
        Car = CarEventPayload.From(car)
    };

    public string ToJson() => JsonSerializer.Serialize(this, JsonOptions);
}
