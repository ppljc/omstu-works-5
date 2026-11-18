using System.ComponentModel.DataAnnotations;

namespace Garage.Api.Models;

public class ServiceRecord
{
    public int Id { get; set; }

    public int CarId { get; set; }
    public Car? Car { get; set; }

    [Required(ErrorMessage = "Тип работы обязателен")]
    [MaxLength(100)]
    public string WorkType { get; set; } = string.Empty;

    [DataType(DataType.Date)]
    public DateOnly Date { get; set; }

    [Range(0, 2_000_000, ErrorMessage = "Пробег не может быть отрицательным")]
    public int Mileage { get; set; }

    [Range(0, 10_000_000, ErrorMessage = "Стоимость не может быть отрицательной (ноль допускается)")]
    public decimal Cost { get; set; }

    [MaxLength(500)]
    public string? Notes { get; set; }
}
