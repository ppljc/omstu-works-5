using System.Text.Json;
using MySqlConnector;

namespace lab12;

public class Program
{
    private const string ServerConnectionString =
        "Server=localhost;User ID=root;Password=644041AS;";

    private const string DatabaseName = "web";

    private const string ConnectionString =
        "Server=localhost;Database=web;User ID=root;Password=644041AS;";

    public static async Task Main(string[] args)
    {
        try
        {
            Console.WriteLine("Начало работы программы...");

            await CreateDatabase();

            await CreateTables();

            var cars = await ReadCarsFromJson();

            Console.WriteLine(
                $"Из cars.json загружено автомобилей: {cars.Count}");

            var dealers = await ReadDealersFromJson();

            Console.WriteLine(
                $"Из dealers.json загружено дилеров: {dealers.Count}");

            if (dealers.Count == 0)
            {
                Console.WriteLine("Список дилеров пуст.");
                return;
            }

            await InsertDealers(dealers);

            Console.WriteLine("Дилеры добавлены в базу данных.");

            var dealerIds = await GetDealerIds();

            var random = new Random();

            foreach (var car in cars)
            {
                var randomIndex = random.Next(dealerIds.Count);

                car.DealerId = dealerIds[randomIndex];
            }

            await InsertCars(cars);

            Console.WriteLine("Автомобили добавлены в базу данных.");

            await PrintDealersAndCars();

            Console.WriteLine();
            Console.WriteLine("Программа успешно завершена.");
        }
        catch (Exception ex)
        {
            Console.WriteLine();
            Console.WriteLine("Произошла ошибка:");
            Console.WriteLine(ex.Message);
        }
    }

    private static async Task CreateDatabase()
    {
        await using var connection =
            new MySqlConnection(ServerConnectionString);

        await connection.OpenAsync();

        var sql = $@"
            CREATE DATABASE IF NOT EXISTS `{DatabaseName}`
            CHARACTER SET utf8mb4
            COLLATE utf8mb4_unicode_ci;
        ";

        await using var command =
            new MySqlCommand(sql, connection);

        await command.ExecuteNonQueryAsync();

        Console.WriteLine(
            $"База данных '{DatabaseName}' готова.");
    }

    private static async Task CreateTables()
    {
        await using var connection =
            new MySqlConnection(ConnectionString);

        await connection.OpenAsync();

        var dealersTable = @"
            CREATE TABLE IF NOT EXISTS dealers
            (
                id INT AUTO_INCREMENT PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                city VARCHAR(255) NOT NULL,
                address VARCHAR(255) NOT NULL,
                area VARCHAR(255) NOT NULL,
                rating DECIMAL(3,2) NOT NULL
            );
        ";

        await using (var command =
                     new MySqlCommand(dealersTable, connection))
        {
            await command.ExecuteNonQueryAsync();
        }

        var carsTable = @"
            CREATE TABLE IF NOT EXISTS cars
            (
                id INT AUTO_INCREMENT PRIMARY KEY,
                firm VARCHAR(255) NOT NULL,
                model VARCHAR(255) NOT NULL,
                year INT NOT NULL,
                power INT NOT NULL,
                color VARCHAR(255) NOT NULL,
                price DECIMAL(12,2) NOT NULL,

                dealer_id INT NOT NULL,

                CONSTRAINT fk_cars_dealer
                    FOREIGN KEY (dealer_id)
                    REFERENCES dealers(id)
                    ON DELETE RESTRICT
                    ON UPDATE CASCADE
            );
        ";

        await using (var command =
                     new MySqlCommand(carsTable, connection))
        {
            await command.ExecuteNonQueryAsync();
        }

        Console.WriteLine("Таблицы готовы.");
    }

    private static async Task<List<Car>> ReadCarsFromJson()
    {
        var filePath = "cars.json";

        if (!File.Exists(filePath))
            throw new FileNotFoundException(
                $"Файл '{filePath}' не найден.");

        var json =
            await File.ReadAllTextAsync(filePath);

        var options =
            new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            };

        var data =
            JsonSerializer.Deserialize<CarsJson>(
                json,
                options);

        return data?.Cars ?? new List<Car>();
    }

    private class CarsJson
    {
        public List<Car> Cars { get; set; } = new();
    }

    private static async Task<List<Dealer>> ReadDealersFromJson()
    {
        var filePath = "dealers.json";

        if (!File.Exists(filePath))
            throw new FileNotFoundException(
                $"Файл '{filePath}' не найден.");

        var json =
            await File.ReadAllTextAsync(filePath);

        var options =
            new JsonSerializerOptions
            {
                PropertyNameCaseInsensitive = true
            };

        var dealers =
            JsonSerializer.Deserialize<List<Dealer>>(
                json,
                options);

        return dealers ?? new List<Dealer>();
    }

    private static async Task InsertDealers(
        List<Dealer> dealers)
    {
        await using var connection =
            new MySqlConnection(ConnectionString);

        await connection.OpenAsync();

        const string sql = @"
            INSERT INTO dealers
            (
                name,
                city,
                address,
                area,
                rating
            )
            VALUES
            (
                @name,
                @city,
                @address,
                @area,
                @rating
            );
        ";

        foreach (var dealer in dealers)
        {
            await using var command =
                new MySqlCommand(sql, connection);

            command.Parameters.AddWithValue(
                "@name",
                dealer.Name);

            command.Parameters.AddWithValue(
                "@city",
                dealer.City);

            command.Parameters.AddWithValue(
                "@address",
                dealer.Address);

            command.Parameters.AddWithValue(
                "@area",
                dealer.Area);

            command.Parameters.AddWithValue(
                "@rating",
                dealer.Rating);

            await command.ExecuteNonQueryAsync();

            dealer.Id = (int)command.LastInsertedId;
        }
    }

    private static async Task<List<int>> GetDealerIds()
    {
        List<int> ids = new();

        await using var connection =
            new MySqlConnection(ConnectionString);

        await connection.OpenAsync();

        const string sql = @"
            SELECT id
            FROM dealers
            ORDER BY id;
        ";

        await using var command =
            new MySqlCommand(sql, connection);

        await using var reader =
            await command.ExecuteReaderAsync();

        while (await reader.ReadAsync()) ids.Add(reader.GetInt32("id"));

        return ids;
    }

    private static async Task InsertCars(
        List<Car> cars)
    {
        await using var connection =
            new MySqlConnection(ConnectionString);

        await connection.OpenAsync();

        const string sql = @"
            INSERT INTO cars
            (
                firm,
                model,
                year,
                power,
                color,
                price,
                dealer_id
            )
            VALUES
            (
                @firm,
                @model,
                @year,
                @power,
                @color,
                @price,
                @dealer_id
            );
        ";

        foreach (var car in cars)
        {
            await using var command =
                new MySqlCommand(sql, connection);

            command.Parameters.AddWithValue(
                "@firm",
                car.Firm);

            command.Parameters.AddWithValue(
                "@model",
                car.Model);

            command.Parameters.AddWithValue(
                "@year",
                car.Year);

            command.Parameters.AddWithValue(
                "@power",
                car.Power);

            command.Parameters.AddWithValue(
                "@color",
                car.Color);

            command.Parameters.AddWithValue(
                "@price",
                car.Price);

            command.Parameters.AddWithValue(
                "@dealer_id",
                car.DealerId);

            await command.ExecuteNonQueryAsync();

            car.Id = (int)command.LastInsertedId;
        }
    }

    private static async Task PrintDealersAndCars()
    {
        await using var connection =
            new MySqlConnection(ConnectionString);

        await connection.OpenAsync();

        const string sql = @"
            SELECT
                d.id AS dealer_id,
                d.name,
                d.city,
                d.address,
                d.area,
                d.rating,

                c.id AS car_id,
                c.firm,
                c.model,
                c.year,
                c.power,
                c.color,
                c.price

            FROM dealers d

            LEFT JOIN cars c
                ON d.id = c.dealer_id

            ORDER BY d.id, c.id;
        ";

        await using var command =
            new MySqlCommand(sql, connection);

        await using var reader =
            await command.ExecuteReaderAsync();

        Console.WriteLine();
        Console.WriteLine("========================================");
        Console.WriteLine("ДИЛЕРЫ И ИХ АВТОМОБИЛИ");
        Console.WriteLine("========================================");

        var currentDealerId = -1;

        while (await reader.ReadAsync())
        {
            var dealerId =
                reader.GetInt32("dealer_id");

            if (dealerId != currentDealerId)
            {
                currentDealerId = dealerId;

                Console.WriteLine();
                Console.WriteLine(
                    $"Дилер #{dealerId}: " +
                    $"{reader.GetString("name")}");

                Console.WriteLine(
                    $"Город: {reader.GetString("city")}");

                Console.WriteLine(
                    $"Адрес: {reader.GetString("address")}");

                Console.WriteLine(
                    $"Район: {reader.GetString("area")}");

                Console.WriteLine(
                    $"Рейтинг: {reader.GetDecimal("rating")}");

                Console.WriteLine("Автомобили:");
            }

            if (!reader.IsDBNull(
                    reader.GetOrdinal("car_id")))
                Console.WriteLine(
                    $"  - #{reader.GetInt32("car_id")} " +
                    $"{reader.GetString("firm")} " +
                    $"{reader.GetString("model")}, " +
                    $"{reader.GetInt32("year")} г., " +
                    $"{reader.GetInt32("power")} л.с., " +
                    $"{reader.GetString("color")}, " +
                    $"{reader.GetDecimal("price")} $");
        }
    }
}