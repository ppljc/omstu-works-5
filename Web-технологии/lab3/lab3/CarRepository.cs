using MySqlConnector;

namespace lab3;

public class CarRepository
{
    private readonly string _connectionString;

    public CarRepository(string connectionString)
    {
        _connectionString = connectionString;
    }
    
    public async Task<IEnumerable<Car>> GetAll()
    {
        var cars = new List<Car>();

        await using var connection = new MySqlConnection(_connectionString);
        await connection.OpenAsync();

        const string sql = "SELECT * FROM cars";

        await using var command = new MySqlCommand(sql, connection);

        await using var reader = await command.ExecuteReaderAsync();

        while (await reader.ReadAsync())
            cars.Add(new Car
            {
                Firm = reader.GetString("firm"),
                Model = reader.GetString("model"),
                Year = reader.GetInt32("year"),
                Power = reader.GetInt32("power"),
                Color = reader.GetString("color"),
                Price = reader.GetDecimal("price"),
                Id = reader.GetInt32("id"),
                DealerId = reader.GetInt32("dealer_id")
            });

        return cars;
    }

    public async Task<Car?> GetById(int id)
    {
        await using var connection = new MySqlConnection(_connectionString);
        await connection.OpenAsync();

        const string sql = @"SELECT * FROM cars WHERE id = @id";

        await using var command = new MySqlCommand(sql, connection);
        command.Parameters.AddWithValue("@id", id);

        await using var reader = await command.ExecuteReaderAsync();

        if (await reader.ReadAsync())
        {
            return new Car
            {
                Firm = reader.GetString("firm"),
                Model = reader.GetString("model"),
                Year = reader.GetInt32("year"),
                Power = reader.GetInt32("power"),
                Color = reader.GetString("color"),
                Price = reader.GetDecimal("price"),
                Id = reader.GetInt32("id"),
                DealerId = reader.GetInt32("dealer_id")
            };
        }

        return null;
    }
}
