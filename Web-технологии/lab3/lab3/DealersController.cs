using Microsoft.AspNetCore.Mvc;

namespace lab3;

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
}