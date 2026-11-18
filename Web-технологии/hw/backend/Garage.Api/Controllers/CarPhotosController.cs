using Garage.Api.Data;
using Garage.Api.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Garage.Api.Controllers;

[ApiController]
[Route("api/cars/{carId:int}/photos")]
public class CarPhotosController : ControllerBase
{
    private static readonly HashSet<string> AllowedExtensions =
        new(StringComparer.OrdinalIgnoreCase) { ".jpg", ".jpeg", ".png", ".webp" };

    private const long MaxFileSize = 5 * 1024 * 1024; // 5 МБ

    private readonly GarageDbContext _db;
    private readonly IWebHostEnvironment _env;

    public CarPhotosController(GarageDbContext db, IWebHostEnvironment env)
    {
        _db = db;
        _env = env;
    }

    private string UploadsPath => Path.Combine(_env.ContentRootPath, "uploads");

    // GET /api/cars/5/photos
    [HttpGet]
    public async Task<IActionResult> GetByCar(int carId)
    {
        if (!await _db.Cars.AnyAsync(c => c.Id == carId))
            return NotFound(new { error = $"Автомобиль с id={carId} не найден" });

        var photos = await _db.CarPhotos.AsNoTracking()
            .Where(p => p.CarId == carId)
            .OrderBy(p => p.UploadedAt)
            .ToListAsync();

        return Ok(photos);
    }

    // POST /api/cars/5/photos  (multipart/form-data, поле "file")
    [HttpPost]
    [Consumes("multipart/form-data")]
    public async Task<IActionResult> Upload(int carId, IFormFile? file)
    {
        if (!await _db.Cars.AnyAsync(c => c.Id == carId))
            return NotFound(new { error = $"Автомобиль с id={carId} не найден" });

        if (file is null || file.Length == 0)
            return BadRequest(new { error = "Файл не передан или пустой" });

        if (file.Length > MaxFileSize)
            return BadRequest(new { error = "Размер файла не должен превышать 5 МБ" });

        var ext = Path.GetExtension(file.FileName);
        if (!AllowedExtensions.Contains(ext))
            return BadRequest(new { error = "Допустимые форматы: jpg, jpeg, png, webp" });

        Directory.CreateDirectory(UploadsPath);

        // Уникальное имя, чтобы избежать коллизий и перезаписи чужих файлов
        var fileName = $"{carId}-{Guid.NewGuid():N}{ext}";
        var fullPath = Path.Combine(UploadsPath, fileName);
        await using (var stream = System.IO.File.Create(fullPath))
        {
            await file.CopyToAsync(stream);
        }

        var photo = new CarPhoto { CarId = carId, FileName = fileName };
        _db.CarPhotos.Add(photo);
        await _db.SaveChangesAsync();

        return CreatedAtAction(nameof(GetByCar), new { carId }, photo);
    }
}

[ApiController]
[Route("api/photos")]
public class PhotoItemsController : ControllerBase
{
    private readonly GarageDbContext _db;
    private readonly IWebHostEnvironment _env;

    public PhotoItemsController(GarageDbContext db, IWebHostEnvironment env)
    {
        _db = db;
        _env = env;
    }

    // DELETE /api/photos/3 — удаляет запись и файл с диска
    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id)
    {
        var photo = await _db.CarPhotos.FirstOrDefaultAsync(p => p.Id == id);
        if (photo is null)
            return NotFound(new { error = $"Фото с id={id} не найдено" });

        _db.CarPhotos.Remove(photo);
        await _db.SaveChangesAsync();

        var fullPath = Path.Combine(_env.ContentRootPath, "uploads", photo.FileName);
        if (System.IO.File.Exists(fullPath))
            System.IO.File.Delete(fullPath);

        return NoContent();
    }
}
