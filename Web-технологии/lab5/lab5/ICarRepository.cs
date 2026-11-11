namespace lab5;

public interface ICarRepository
{
    Task<IEnumerable<Car>> GetAll();

    Task<Car?> GetById(int id);

    Task<Car> Create(Car car);

    Task<bool> Update(Car car);

    Task<bool> Delete(int id);

    Task<int> CountByDealerId(int dealerId);
}
