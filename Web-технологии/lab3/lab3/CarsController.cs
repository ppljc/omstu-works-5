using Microsoft.AspNetCore.Mvc;

namespace lab3;

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
}
