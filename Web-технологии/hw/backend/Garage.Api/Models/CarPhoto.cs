using System.ComponentModel.DataAnnotations;

namespace Garage.Api.Models;

public class CarPhoto
{
    public int Id { get; set; }

    public int CarId { get; set; }
    public Car? Car { get; set; }

    // Уникальное имя файла на диске (uploads/), например "5-a1b2c3....png"
    [MaxLength(255)]
    public string FileName { get; set; } = string.Empty;

    public DateTime UploadedAt { get; set; } = DateTime.UtcNow;
}
