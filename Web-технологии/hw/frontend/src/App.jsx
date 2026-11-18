import { useCallback, useEffect, useState } from 'react';
import { api } from './api.js';
import CarList from './components/CarList.jsx';
import CarForm from './components/CarForm.jsx';
import ServiceHistory from './components/ServiceHistory.jsx';
import ExpensesChart from './components/ExpensesChart.jsx';
import CarPhotos from './components/CarPhotos.jsx';
import { STATUS_LABELS, DRIVETRAIN_LABELS, FUEL_LABELS } from './components/CarForm.jsx';

export default function App() {
  const [cars, setCars] = useState([]);
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState('');
  const [selectedId, setSelectedId] = useState(null);
  const [services, setServices] = useState([]);
  const [showForm, setShowForm] = useState(false);
  const [editing, setEditing] = useState(null);
  const [error, setError] = useState('');
  const [notice, setNotice] = useState('');

  const flash = (msg) => {
    setNotice(msg);
    setTimeout(() => setNotice(''), 3000);
  };

  const loadCars = useCallback(async () => {
    try {
      setCars(await api.getCars({ search, status }));
    } catch (err) {
      setError(err.message);
    }
  }, [search, status]);

  const loadServices = useCallback(async () => {
    if (!selectedId) return;
    try {
      setServices(await api.getServices(selectedId));
    } catch (err) {
      setError(err.message);
    }
  }, [selectedId]);

  useEffect(() => { loadCars(); }, [loadCars]);
  useEffect(() => { loadServices(); }, [loadServices]);

  const selectedCar = cars.find((c) => c.id === selectedId) ?? null;

  const handleCreateOrUpdate = async (car) => {
    try {
      setError('');
      if (editing) {
        await api.updateCar({ ...car, id: editing.id });
        flash('Автомобиль обновлён');
      } else {
        const created = await api.createCar(car);
        setSelectedId(created.id);
        flash('Автомобиль добавлен');
      }
      setShowForm(false);
      setEditing(null);
      await loadCars();
    } catch (err) {
      setError(err.message);
    }
  };

  const handleDelete = async (id) => {
    const car = cars.find((c) => c.id === id);
    if (!window.confirm(`Удалить автомобиль ${car?.make} ${car?.model}? Вся история обслуживания будет удалена.`)) return;
    try {
      await api.deleteCar(id);
      if (selectedId === id) setSelectedId(null);
      flash('Автомобиль удалён');
      await loadCars();
    } catch (err) {
      setError(err.message);
    }
  };

  return (
    <div className="app">
      <header>
        <h1>🚗 Гараж</h1>
        <p>Учёт автомобилей и их обслуживания</p>
      </header>

      {notice && <div className="notice">{notice}</div>}
      {error && (
        <div className="error" onClick={() => setError('')}>
          {error} <span className="dismiss">(закрыть)</span>
        </div>
      )}

      <main className="layout">
        <aside className="card sidebar">
          <div className="filters">
            <input
              placeholder="Поиск: марка, модель, VIN…"
              value={search}
              onChange={(e) => setSearch(e.target.value)}
            />
            <select value={status} onChange={(e) => setStatus(e.target.value)}>
              <option value="">Все статусы</option>
              {Object.entries(STATUS_LABELS).map(([value, label]) => (
                <option key={value} value={value}>{label}</option>
              ))}
            </select>
            <button
              className="primary"
              onClick={() => { setEditing(null); setShowForm(!showForm); }}
            >
              {showForm ? 'Скрыть форму' : '+ Добавить автомобиль'}
            </button>
          </div>

          {showForm && (
            <CarForm
              initial={editing}
              error={error}
              onSubmit={handleCreateOrUpdate}
              onCancel={() => { setShowForm(false); setEditing(null); }}
            />
          )}

          <CarList cars={cars} selectedId={selectedId} onSelect={setSelectedId} />
        </aside>

        <section className="content">
          {selectedCar && (
            <div className="card car-detail">
              <div className="section-header">
                <h2>{selectedCar.make} {selectedCar.model}</h2>
                <div>
                  <button onClick={() => { setEditing(selectedCar); setShowForm(true); }}>
                    Редактировать
                  </button>
                  <button className="danger" onClick={() => handleDelete(selectedCar.id)}>
                    Удалить
                  </button>
                </div>
              </div>
              <dl className="props">
                <div><dt>Год выпуска</dt><dd>{selectedCar.year}</dd></div>
                <div><dt>VIN</dt><dd className="mono">{selectedCar.vin}</dd></div>
                <div><dt>Пробег</dt><dd>{selectedCar.mileage.toLocaleString('ru-RU')} км</dd></div>
                <div><dt>Статус</dt><dd>{STATUS_LABELS[selectedCar.status]}</dd></div>
                <div><dt>Привод</dt><dd>{DRIVETRAIN_LABELS[selectedCar.drivetrain]}</dd></div>
                <div><dt>Топливо</dt><dd>{FUEL_LABELS[selectedCar.fuelType]}</dd></div>
                <div>
                  <dt>Объём двигателя</dt>
                  <dd>{selectedCar.engineVolume != null ? `${selectedCar.engineVolume} л` : '—'}</dd>
                </div>
                <div>
                  <dt>Мощность</dt>
                  <dd>{selectedCar.powerHp != null ? `${selectedCar.powerHp} л.с.` : '—'}</dd>
                </div>
              </dl>
            </div>
          )}

          {selectedId && (
            <CarPhotos carId={selectedId} onChanged={loadCars} onError={setError} />
          )}

          {selectedId && (
            <ServiceHistory
              carId={selectedId}
              records={services}
              onChanged={loadServices}
              onError={setError}
            />
          )}

          <ExpensesChart carId={selectedId} onError={setError} />
        </section>
      </main>
    </div>
  );
}
