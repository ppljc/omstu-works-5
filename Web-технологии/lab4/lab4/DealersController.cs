using Microsoft.AspNetCore.Mvc;

namespace lab4;

[ApiController]
[Route("api/[controller]")]
public class DealersController : ControllerBase
{
    private readonly DealerRepository _repository;

    public DealersController(DealerRepository repository)
    {
        _repository = repository;
    }
    
    [HttpGet]
    public async Task<ActionResult<IEnumerable<Dealer>>> GetAll()
    {
        var dealers = await _repository.GetAll();
        return Ok(dealers);
    }

    [HttpGet("{id:int}")]
    public async Task<ActionResult<Dealer>> GetById(int id)
    {
        var dealer = await _repository.GetById(id);
        
        if (dealer is null)
        {
            return NotFound();
        }

        return Ok(dealer);
    }
    
    [HttpPost]
    public async Task<ActionResult<Dealer>> Create(CreateDealerRequest request)
    {
        var dealer = new Dealer()
        {
            Name = request.Name,
            City = request.City,
            Address = request.Address,
            Area = request.Area,
            Rating = request.Rating
        };
        
        var newDealer = await _repository.Create(dealer);

        return CreatedAtAction(nameof(GetById), new { id = newDealer.Id }, newDealer);
    }
    
    [HttpPut("{id:int}")]
    public async Task<ActionResult<Car>> Update(int id, UpdateDealerRequest request)
    {
        var dealer = new Dealer()
        {
            Id = id,
            Name = request.Name,
            City = request.City,
            Address = request.Address,
            Area = request.Area,
            Rating = request.Rating
        };

        if (await _repository.Update(dealer))
        {
            return Ok(dealer);
        }

        return NotFound();
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