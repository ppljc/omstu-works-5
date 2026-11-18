using Garage.Api.Data;
using Garage.Api.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Garage.Api.Controllers;

[ApiController]
[Route("api/cars/{carId:int}/services")]
public class ServiceRecordsController : ControllerBase
{
    private readonly GarageDbContext _db;

    public ServiceRecordsController(GarageDbContext db) => _db = db;

    // GET /api/cars/5/services
    [HttpGet]
    public async Task<IActionResult> GetByCar(int carId)
    {
        if (!await _db.Cars.AnyAsync(c => c.Id == carId))
            return NotFound(new { error = $"Автомобиль с id={carId} не найден" });

        var records = await _db.ServiceRecords.AsNoTracking()
            .Where(s => s.CarId == carId)
            .OrderByDescending(s => s.Date)
            .ToListAsync();

        return Ok(records);
    }

    // POST /api/cars/5/services
    [HttpPost]
    public async Task<IActionResult> Create(int carId, [FromBody] ServiceRecord record)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var car = await _db.Cars.FirstOrDefaultAsync(c => c.Id == carId);
        if (car is null)
            return NotFound(new { error = $"Автомобиль с id={carId} не найден" });

        if (record.Date > DateOnly.FromDateTime(DateTime.Now))
            ModelState.AddModelError("Date", "Дата обслуживания не может быть в будущем");

        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        record.CarId = carId;
        record.Car = null;
        _db.ServiceRecords.Add(record);

        // Пробег автомобиля растёт: фиксируем максимальный
        if (record.Mileage > car.Mileage)
            car.Mileage = record.Mileage;

        await _db.SaveChangesAsync();
        return CreatedAtAction(nameof(GetByCar), new { carId }, record);
    }
}

[ApiController]
[Route("api/services")]
public class ServiceRecordItemsController : ControllerBase
{
    private readonly GarageDbContext _db;

    public ServiceRecordItemsController(GarageDbContext db) => _db = db;

    // DELETE /api/services/12
    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id)
    {
        var record = await _db.ServiceRecords.FirstOrDefaultAsync(s => s.Id == id);
        if (record is null)
            return NotFound(new { error = $"Запись об обслуживании с id={id} не найдена" });

        _db.ServiceRecords.Remove(record);
        await _db.SaveChangesAsync();
        return NoContent();
    }
}
