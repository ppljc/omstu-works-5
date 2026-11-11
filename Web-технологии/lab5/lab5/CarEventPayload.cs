namespace lab5;

public sealed class CarEventPayload
{
    public string Firm { get; init; } = "";
    public string Model { get; init; } = "";
    public int Year { get; init; }
    public int Power { get; init; }
    public string Color { get; init; } = "";
    public decimal Price { get; init; }

    public static CarEventPayload From(Car car) => new()
    {
        Firm = car.Firm,
        Model = car.Model,
        Year = car.Year,
        Power = car.Power,
        Color = car.Color,
        Price = car.Price
    };
}
