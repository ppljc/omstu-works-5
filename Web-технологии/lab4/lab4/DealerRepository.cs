namespace lab4;

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
    
    public async Task<Dealer> Create(Dealer dealer)
    {
        await using var connection = new MySqlConnection(_connectionString);
        await connection.OpenAsync();

        const string sql = """
                               INSERT INTO dealers 
                                   (name, city, address, area, rating) 
                               VALUES 
                                   (@name, @city, @address, @area, @rating)
                           """;

        await using var command = new MySqlCommand(sql, connection);

        command.Parameters.AddWithValue("@name", dealer.Name);
        command.Parameters.AddWithValue("@city", dealer.City);
        command.Parameters.AddWithValue("@address", dealer.Address);
        command.Parameters.AddWithValue("@area", dealer.Area);
        command.Parameters.AddWithValue("@rating", dealer.Rating);

        await command.ExecuteNonQueryAsync();

        dealer.Id = (int)command.LastInsertedId;

        return dealer;
    }

    public async Task<bool> Update(Dealer dealer)
    {
        await using var connection = new MySqlConnection(_connectionString);
        await connection.OpenAsync();

        const string sql = """
                               UPDATE dealers
                               SET name = @name, city = @city, address = @address, area = @area, rating = @rating
                               WHERE id = @id
                           """;

        await using var command = new MySqlCommand(sql, connection);
        
        command.Parameters.AddWithValue("@id", dealer.Id);
        command.Parameters.AddWithValue("@name", dealer.Name);
        command.Parameters.AddWithValue("@city", dealer.City);
        command.Parameters.AddWithValue("@address", dealer.Address);
        command.Parameters.AddWithValue("@area", dealer.Area);
        command.Parameters.AddWithValue("@rating", dealer.Rating);

        var rowsAffected = await command.ExecuteNonQueryAsync();

        return rowsAffected > 0;
    }

    public async Task<bool> Delete(int id)
    {
        await using var connection = new MySqlConnection(_connectionString);
        await connection.OpenAsync();

        const string sql = @"DELETE FROM dealers WHERE id = @id";

        await using var command = new MySqlCommand(sql, connection);
        command.Parameters.AddWithValue("@id", id);

        var rowsAffected = await command.ExecuteNonQueryAsync();

        return rowsAffected > 0;
    }
}
