using MySqlConnector;

namespace lab4;

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

    public async Task<Car> Create(Car car)
    {
        await using var connection = new MySqlConnection(_connectionString);
        await connection.OpenAsync();

        const string sql = """
                               INSERT INTO cars 
                                   (firm, model, year, power, color, price, dealer_id) 
                               VALUES 
                                   (@firm, @model, @year, @power, @color, @price, @dealer_id)
                           """;

        await using var command = new MySqlCommand(sql, connection);

        command.Parameters.AddWithValue("@firm", car.Firm);
        command.Parameters.AddWithValue("@model", car.Model);
        command.Parameters.AddWithValue("@year", car.Year);
        command.Parameters.AddWithValue("@power", car.Power);
        command.Parameters.AddWithValue("@color", car.Color);
        command.Parameters.AddWithValue("@price", car.Price);
        command.Parameters.AddWithValue("@dealer_id", car.DealerId);

        await command.ExecuteNonQueryAsync();

        car.Id = (int)command.LastInsertedId;

        return car;
    }

    public async Task<bool> Update(Car car)
    {
        await using var connection = new MySqlConnection(_connectionString);
        await connection.OpenAsync();

        const string sql = """
                               UPDATE cars
                               SET firm = @firm, model = @model, year = @year, power = @power, color = @color, price = @price, dealer_id = @dealer_id
                               WHERE id = @id
                           """;

        await using var command = new MySqlCommand(sql, connection);
        
        command.Parameters.AddWithValue("@firm", car.Firm);
        command.Parameters.AddWithValue("@model", car.Model);
        command.Parameters.AddWithValue("@year", car.Year);
        command.Parameters.AddWithValue("@power", car.Power);
        command.Parameters.AddWithValue("@color", car.Color);
        command.Parameters.AddWithValue("@price", car.Price);
        command.Parameters.AddWithValue("@id", car.Id);
        command.Parameters.AddWithValue("@dealer_id", car.DealerId);

        var rowsAffected = await command.ExecuteNonQueryAsync();

        return rowsAffected > 0;
    }

    public async Task<bool> Delete(int id)
    {
        await using var connection = new MySqlConnection(_connectionString);
        await connection.OpenAsync();

        const string sql = @"DELETE FROM cars WHERE id = @id";

        await using var command = new MySqlCommand(sql, connection);
        command.Parameters.AddWithValue("@id", id);

        var rowsAffected = await command.ExecuteNonQueryAsync();

        return rowsAffected > 0;
    }
}