namespace lab3;

using MySqlConnector;

public class DealerRepository
{
    private readonly string _connectionString;

    public DealerRepository(string connectionString)
    {
        _connectionString = connectionString;
    }
    
    public async Task<IEnumerable<Dealer>> GetAll()
    {
        var dealers = new List<Dealer>();

        await using var connection = new MySqlConnection(_connectionString);
        await connection.OpenAsync();

        const string sql = "SELECT * FROM dealers";

        await using var command = new MySqlCommand(sql, connection);

        await using var reader = await command.ExecuteReaderAsync();

        while (await reader.ReadAsync())
            dealers.Add(new Dealer
            {
                Id = reader.GetInt32("id"),
                Name = reader.GetString("name"),
                City = reader.GetString("city"),
                Address = reader.GetString("address"),
                Area = reader.GetString("area"),
                Rating = reader.GetDecimal("rating")
            });

        return dealers;
    }
    
    public async Task<Dealer?> GetById(int id)
    {
        await using var connection = new MySqlConnection(_connectionString);
        await connection.OpenAsync();

        const string sql = @"SELECT * FROM dealers WHERE id = @id";

        await using var command = new MySqlCommand(sql, connection);
        command.Parameters.AddWithValue("@id", id);

        await using var reader = await command.ExecuteReaderAsync();

        if (await reader.ReadAsync())
            return new Dealer
            {
                Id = reader.GetInt32("id"),
                Name = reader.GetString("name"),
                City = reader.GetString("city"),
                Address = reader.GetString("address"),
                Area = reader.GetString("area"),
                Rating = reader.GetDecimal("rating")
            };

        return null;
    }
}
