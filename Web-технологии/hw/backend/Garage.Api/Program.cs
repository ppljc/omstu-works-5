using Garage.Api.Data;
using Microsoft.EntityFrameworkCore;
using Microsoft.Extensions.FileProviders;
using System.Text.Json.Serialization;

var builder = WebApplication.CreateBuilder(args);

builder.Services.AddControllers()
    // Отдаём ошибки валидации сами (BadRequest(ModelState) с сообщениями по полям),
    // а не стандартный ProblemDetails "One or more validation errors occurred".
    .ConfigureApiBehaviorOptions(o => o.SuppressModelStateInvalidFilter = true)
    // Enum'ы (CarStatus) сериализуем/десериализуем строками: "OnTheRoad", а не 0.
    .AddJsonOptions(o => o.JsonSerializerOptions.Converters.Add(new JsonStringEnumConverter()));
builder.Services.AddOpenApi();

builder.Services.AddDbContext<GarageDbContext>(options =>
    options.UseNpgsql(builder.Configuration.GetConnectionString("GarageDb")));

// CORS для фронтенда на Vite (dev-сервер на порту 5173)
builder.Services.AddCors(options =>
{
    options.AddPolicy("Frontend", policy =>
        policy.WithOrigins("http://localhost:5173")
              .AllowAnyHeader()
              .AllowAnyMethod());
});

var app = builder.Build();

if (app.Environment.IsDevelopment())
{
    app.MapOpenApi();
}

app.UseCors("Frontend");

// Раздача загруженных фото: /uploads/<fileName>
var uploadsPath = Path.Combine(app.Environment.ContentRootPath, "uploads");
Directory.CreateDirectory(uploadsPath);
app.UseStaticFiles(new StaticFileOptions
{
    FileProvider = new PhysicalFileProvider(uploadsPath),
    RequestPath = "/uploads"
});

app.UseAuthorization();
app.MapControllers();

app.Run();
