using Garage.Api.Models;
using Microsoft.EntityFrameworkCore;

namespace Garage.Api.Data;

public class GarageDbContext : DbContext
{
    public GarageDbContext(DbContextOptions<GarageDbContext> options) : base(options) { }

    public DbSet<Car> Cars => Set<Car>();
    public DbSet<ServiceRecord> ServiceRecords => Set<ServiceRecord>();
    public DbSet<CarPhoto> CarPhotos => Set<CarPhoto>();

    protected override void OnModelCreating(ModelBuilder modelBuilder)
    {
        modelBuilder.Entity<Car>()
            .Property(c => c.Status)
            .HasConversion<string>();

        modelBuilder.Entity<Car>()
            .HasIndex(c => c.Vin)
            .IsUnique();

        modelBuilder.Entity<ServiceRecord>()
            .HasOne(s => s.Car)
            .WithMany(c => c.ServiceRecords)
            .HasForeignKey(s => s.CarId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<Car>()
            .Property(c => c.Drivetrain)
            .HasConversion<string>();

        modelBuilder.Entity<Car>()
            .Property(c => c.FuelType)
            .HasConversion<string>();

        modelBuilder.Entity<CarPhoto>()
            .HasOne(p => p.Car)
            .WithMany(c => c.Photos)
            .HasForeignKey(p => p.CarId)
            .OnDelete(DeleteBehavior.Cascade);

        modelBuilder.Entity<CarPhoto>()
            .HasIndex(p => p.FileName)
            .IsUnique();
    }
}
