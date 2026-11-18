import { STATUS_LABELS } from './CarForm.jsx';

const STATUS_CLASS = {
  OnTheRoad: 'badge ok',
  InRepair: 'badge warn',
  Sold: 'badge muted',
};

export default function CarList({ cars, selectedId, onSelect }) {
  if (cars.length === 0) {
    return <p className="empty">Автомобили не найдены. Добавьте первый!</p>;
  }

  return (
    <ul className="car-list">
      {cars.map((car) => (
        <li
          key={car.id}
          className={car.id === selectedId ? 'car-item selected' : 'car-item'}
          onClick={() => onSelect(car.id)}
        >
          <div className="car-title">
            {car.photos?.length > 0 ? (
              <img className="thumb" src={`/uploads/${car.photos[0].fileName}`} alt="" />
            ) : (
              <span className="thumb placeholder">🚗</span>
            )}
            <strong>{car.make} {car.model}</strong>
            <span className={STATUS_CLASS[car.status] ?? 'badge'}>
              {STATUS_LABELS[car.status] ?? car.status}
            </span>
          </div>
          <div className="car-meta">
            {car.year} г. · {car.mileage.toLocaleString('ru-RU')} км
          </div>
        </li>
      ))}
    </ul>
  );
}
