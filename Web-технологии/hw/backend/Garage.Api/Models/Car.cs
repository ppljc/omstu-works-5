using System.ComponentModel.DataAnnotations;

namespace Garage.Api.Models;

public enum CarStatus
{
    OnTheRoad = 0,   // На ходу
    InRepair = 1,    // В ремонте
    Sold = 2         // Продана
}

public enum Drivetrain
{
    Front = 0,   // Передний привод
    Rear = 1,    // Задний привод
    Awd = 2      // Полный привод
}

public enum FuelType
{
    Petrol = 0,   // Бензин
    Diesel = 1,   // Дизель
    Hybrid = 2,   // Гибрид
    Electric = 3  // Электро
}

public class Car
{
    public int Id { get; set; }

    [Required(ErrorMessage = "Марка обязательна")]
    [MaxLength(50)]
    public string Make { get; set; } = string.Empty;

    [Required(ErrorMessage = "Модель обязательна")]
    [MaxLength(50)]
    public string Model { get; set; } = string.Empty;

    [Range(1900, 2100, ErrorMessage = "Год выпуска должен быть в диапазоне 1900–2100")]
    public int Year { get; set; }

    [RegularExpression(@"^[A-HJ-NPR-Z0-9]{17}$", ErrorMessage = "VIN должен состоять из 17 символов (без I, O, Q)")]
    public string Vin { get; set; } = string.Empty;

    [Range(0, 2_000_000, ErrorMessage = "Пробег не может быть отрицательным")]
    public int Mileage { get; set; }

    public CarStatus Status { get; set; } = CarStatus.OnTheRoad;

    public Drivetrain Drivetrain { get; set; } = Drivetrain.Front;

    public FuelType FuelType { get; set; } = FuelType.Petrol;

    // Объём двигателя, л. Для электромобилей не задаётся (null).
    [Range(0.1, 20, ErrorMessage = "Объём двигателя должен быть в диапазоне 0.1–20 л")]
    public float? EngineVolume { get; set; }

    // Мощность, л.с.
    [Range(1, 2000, ErrorMessage = "Мощность должна быть в диапазоне 1–2000 л.с.")]
    public int? PowerHp { get; set; }

    public List<ServiceRecord> ServiceRecords { get; set; } = new();
    public List<CarPhoto> Photos { get; set; } = new();
}
