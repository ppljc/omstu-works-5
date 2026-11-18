using Garage.Api.Data;
using Garage.Api.Models;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Garage.Api.Controllers;

[ApiController]
[Route("api/cars")]
public class CarsController : ControllerBase
{
    private readonly GarageDbContext _db;

    public CarsController(GarageDbContext db) => _db = db;

    // GET /api/cars?status=OnTheRoad&search=audi
    [HttpGet]
    public async Task<IActionResult> GetAll([FromQuery] string? status, [FromQuery] string? search)
    {
        var query = _db.Cars.AsNoTracking().Include(c => c.Photos).AsQueryable();

        if (!string.IsNullOrWhiteSpace(status) && Enum.TryParse<CarStatus>(status, true, out var parsedStatus))
            query = query.Where(c => c.Status == parsedStatus);

        if (!string.IsNullOrWhiteSpace(search))
        {
            var term = search.Trim().ToUpper();
            query = query.Where(c =>
                c.Make.ToUpper().Contains(term) ||
                c.Model.ToUpper().Contains(term) ||
                c.Vin.ToUpper().Contains(term));
        }

        var cars = await query.OrderBy(c => c.Make).ThenBy(c => c.Model).ToListAsync();
        return Ok(cars);
    }

    // GET /api/cars/5
    [HttpGet("{id:int}")]
    public async Task<IActionResult> GetById(int id)
    {
        var car = await _db.Cars.AsNoTracking().Include(c => c.Photos).FirstOrDefaultAsync(c => c.Id == id);
        return car is null ? NotFound(new { error = $"Автомобиль с id={id} не найден" }) : Ok(car);
    }

    // POST /api/cars
    [HttpPost]
    public async Task<IActionResult> Create([FromBody] Car car)
    {
        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        if (car.Year > DateTime.Now.Year)
            ModelState.AddModelError("Year", "Год выпуска не может быть в будущем");

        if (await _db.Cars.AnyAsync(c => c.Vin == car.Vin))
            ModelState.AddModelError("Vin", "Автомобиль с таким VIN уже существует");

        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        _db.Cars.Add(car);
        await _db.SaveChangesAsync();
        return CreatedAtAction(nameof(GetById), new { id = car.Id }, car);
    }

    // PUT /api/cars/5
    [HttpPut("{id:int}")]
    public async Task<IActionResult> Update(int id, [FromBody] Car car)
    {
        if (id != car.Id)
            return BadRequest(new { error = "Id в адресе и в теле запроса не совпадают" });

        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        if (car.Year > DateTime.Now.Year)
            ModelState.AddModelError("Year", "Год выпуска не может быть в будущем");

        if (await _db.Cars.AnyAsync(c => c.Vin == car.Vin && c.Id != id))
            ModelState.AddModelError("Vin", "Автомобиль с таким VIN уже существует");

        if (!ModelState.IsValid)
            return BadRequest(ModelState);

        var existing = await _db.Cars.FirstOrDefaultAsync(c => c.Id == id);
        if (existing is null)
            return NotFound(new { error = $"Автомобиль с id={id} не найден" });

        existing.Make = car.Make;
        existing.Model = car.Model;
        existing.Year = car.Year;
        existing.Vin = car.Vin;
        existing.Mileage = car.Mileage;
        existing.Status = car.Status;
        existing.Drivetrain = car.Drivetrain;
        existing.FuelType = car.FuelType;
        existing.EngineVolume = car.EngineVolume;
        existing.PowerHp = car.PowerHp;

        await _db.SaveChangesAsync();
        return Ok(existing);
    }

    // DELETE /api/cars/5
    [HttpDelete("{id:int}")]
    public async Task<IActionResult> Delete(int id)
    {
        var car = await _db.Cars.FirstOrDefaultAsync(c => c.Id == id);
        if (car is null)
            return NotFound(new { error = $"Автомобиль с id={id} не найден" });

        _db.Cars.Remove(car);
        await _db.SaveChangesAsync();
        return NoContent();
    }
}
