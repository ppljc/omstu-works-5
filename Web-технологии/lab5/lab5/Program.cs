using lab5;

const string connectionString = "Server=localhost;Database=web;User ID=root;Password=644041AS;";

var builder = WebApplication.CreateBuilder(args);

// Add services to the container.
// Learn more about configuring OpenAPI at https://aka.ms/aspnet/openapi
builder.Services.AddOpenApi();

builder.Services.AddControllers();

builder.Services.AddScoped<CarRepository>(_ =>
    new CarRepository(connectionString));
builder.Services.AddScoped<DealerRepository>(_ =>
    new DealerRepository(connectionString));

var rabbitMqOptions = builder.Configuration.GetSection("RabbitMq").Get<RabbitMqOptions>()
                      ?? new RabbitMqOptions();
builder.Services.AddSingleton(rabbitMqOptions);
builder.Services.AddSingleton<RabbitMqEventPublisher>();
builder.Services.AddSingleton<IEventPublisher>(sp =>
    sp.GetRequiredService<RabbitMqEventPublisher>());

builder.Services.AddScoped<ICarRepository>(sp =>
    new EventPublishingCarRepository(
        sp.GetRequiredService<CarRepository>(),
        sp.GetRequiredService<IEventPublisher>()));

builder.Services.AddEndpointsApiExplorer();
builder.Services.AddSwaggerGen();

var app = builder.Build();

try
{
    await app.Services.GetRequiredService<RabbitMqEventPublisher>().InitializeAsync();
}
catch (Exception ex)
{
    app.Logger.LogError(ex,
        "RabbitMQ недоступен: события не будут отправляться до восстановления соединения");
}

// Configure the HTTP request pipeline.
if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
    app.UseSwagger();
    app.UseSwaggerUI();
}

app.UseHttpsRedirection();

app.MapControllers();

app.Run();
