using Microsoft.AspNetCore.Mvc;
using MySqlConnector;

namespace lab4;

[ApiController]
[Route("api/[controller]")]
public class CarsController : ControllerBase
{
    private readonly CarRepository _repository;

    public CarsController(CarRepository repository)
    {
        _repository = repository;
    }

    [HttpGet]
    public async Task<ActionResult<IEnumerable<Car>>> GetAll()
    {
        var cars = await _repository.GetAll();
        return Ok(cars);
    }

    [HttpGet("{id:int}")]
    public async Task<ActionResult<Car>> GetById(int id)
    {
        var car = await _repository.GetById(id);

        if (car is null)
        {
            return NotFound();
        }

        return Ok(car);
    }

    [HttpPost]
    public async Task<ActionResult<Car>> Create(CreateCarRequest request)
    {
        var car = new Car()
        {
            Firm = request.Firm,
            Model = request.Model,
            Year = request.Year,
            Power = request.Power,
            Color = request.Color,
            Price = request.Price,
            DealerId = request.DealerId
        };

        try
        {
            var newCar = await _repository.Create(car);

            return CreatedAtAction(nameof(GetById), new { id = newCar.Id }, newCar);
        }
        catch (MySqlException ex) when (ex.Number == 1452) // no dealer
        {
            return BadRequest(new
            {
                message = $"DealerID '{request.DealerId}' doesnt exist."
            });
        }
    }

    [HttpPut("{id:int}")]
    public async Task<ActionResult<Car>> Update(int id, UpdateCarRequest request)
    {
        var car = new Car()
        {
            Firm = request.Firm,
            Model = request.Model,
            Year = request.Year,
            Power = request.Power,
            Color = request.Color,
            Price = request.Price,
            Id = id,
            DealerId = request.DealerId
        };

        try
        {
            if (await _repository.Update(car))
            {
                return Ok(car);
            }

            return NotFound();
        }
        catch (MySqlException ex) when (ex.Number == 1452) // no dealer
        {
            return BadRequest(new
            {
                message = $"DealerID '{request.DealerId}' doesnt exist."
            });
        }
    }

    [HttpDelete("{id:int}")]
    public async Task<ActionResult> Delete(int id)
    {
        if (await _repository.Delete(id))
        {
            return NoContent();
        }

        return NotFound();
    }
}