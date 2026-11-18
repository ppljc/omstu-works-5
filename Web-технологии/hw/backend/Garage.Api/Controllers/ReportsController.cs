using Garage.Api.Data;
using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;

namespace Garage.Api.Controllers;

[ApiController]
[Route("api/reports")]
public class ReportsController : ControllerBase
{
    private readonly GarageDbContext _db;

    public ReportsController(GarageDbContext db) => _db = db;

    // GET /api/reports/expenses?carId=5&from=2026-01-01&to=2026-12-31
    // Возвращает общую сумму затрат и разбивку по месяцам.
    [HttpGet("expenses")]
    public async Task<IActionResult> Expenses(
        [FromQuery] int? carId,
        [FromQuery] DateOnly? from,
        [FromQuery] DateOnly? to)
    {
        if (carId.HasValue && !await _db.Cars.AnyAsync(c => c.Id == carId.Value))
            return NotFound(new { error = $"Автомобиль с id={carId} не найден" });

        var query = _db.ServiceRecords.AsNoTracking().AsQueryable();

        if (carId.HasValue)
            query = query.Where(s => s.CarId == carId.Value);
        if (from.HasValue)
            query = query.Where(s => s.Date >= from.Value);
        if (to.HasValue)
            query = query.Where(s => s.Date <= to.Value);

        var total = await query.SumAsync(s => (decimal?)s.Cost) ?? 0m;

        var monthly = await query
            .GroupBy(s => new { s.Date.Year, s.Date.Month })
            .Select(g => new
            {
                g.Key.Year,
                g.Key.Month,
                Total = g.Sum(s => s.Cost)
            })
            .OrderBy(x => x.Year).ThenBy(x => x.Month)
            .ToListAsync();

        return Ok(new { total, monthly });
    }
}
