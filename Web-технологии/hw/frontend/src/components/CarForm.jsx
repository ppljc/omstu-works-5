import { useState } from 'react';

const STATUS_LABELS = {
  OnTheRoad: 'На ходу',
  InRepair: 'В ремонте',
  Sold: 'Продана',
};

const DRIVETRAIN_LABELS = {
  Front: 'Передний',
  Rear: 'Задний',
  Awd: 'Полный',
};

const FUEL_LABELS = {
  Petrol: 'Бензин',
  Diesel: 'Дизель',
  Hybrid: 'Гибрид',
  Electric: 'Электро',
};

export { STATUS_LABELS, DRIVETRAIN_LABELS, FUEL_LABELS };

const EMPTY = {
  make: '',
  model: '',
  year: new Date().getFullYear(),
  vin: '',
  mileage: 0,
  status: 'OnTheRoad',
  drivetrain: 'Front',
  fuelType: 'Petrol',
  engineVolume: '',
  powerHp: '',
};

export default function CarForm({ initial, onSubmit, onCancel, error }) {
  const [form, setForm] = useState(
    initial
      ? {
          ...EMPTY,
          ...initial,
          engineVolume: initial.engineVolume ?? '',
          powerHp: initial.powerHp ?? '',
        }
      : EMPTY
  );

  const set = (field) => (e) =>
    setForm({ ...form, [field]: e.target.value });

  const isElectric = form.fuelType === 'Electric';

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit({
      ...form,
      year: Number(form.year),
      mileage: Number(form.mileage),
      vin: form.vin.toUpperCase(),
      // У электромобиля объёма двигателя нет — принудительно null
      engineVolume: isElectric || form.engineVolume === '' ? null : Number(form.engineVolume),
      powerHp: form.powerHp === '' ? null : Number(form.powerHp),
    });
  };

  return (
    <form className="card form" onSubmit={handleSubmit}>
      <h3>{initial ? 'Редактирование автомобиля' : 'Новый автомобиль'}</h3>

      {error && <div className="error">{error}</div>}

      <div className="grid">
        <label>
          Марка *
          <input value={form.make} onChange={set('make')} required maxLength={50} />
        </label>
        <label>
          Модель *
          <input value={form.model} onChange={set('model')} required maxLength={50} />
        </label>
        <label>
          Год выпуска *
          <input
            type="number"
            value={form.year}
            onChange={set('year')}
            required
            min={1900}
            max={new Date().getFullYear()}
          />
        </label>
        <label>
          VIN (17 символов) *
          <input
            value={form.vin}
            onChange={set('vin')}
            required
            minLength={17}
            maxLength={17}
            pattern="[A-HJ-NPR-Za-hj-npr-z0-9]{17}"
            title="17 символов; буквы I, O, Q не допускаются"
            className="mono"
          />
        </label>
        <label>
          Пробег, км *
          <input
            type="number"
            value={form.mileage}
            onChange={set('mileage')}
            required
            min={0}
          />
        </label>
        <label>
          Статус
          <select value={form.status} onChange={set('status')}>
            {Object.entries(STATUS_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </label>
        <label>
          Привод
          <select value={form.drivetrain} onChange={set('drivetrain')}>
            {Object.entries(DRIVETRAIN_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </label>
        <label>
          Тип топлива
          <select value={form.fuelType} onChange={set('fuelType')}>
            {Object.entries(FUEL_LABELS).map(([value, label]) => (
              <option key={value} value={value}>{label}</option>
            ))}
          </select>
        </label>
        <label>
          Объём двигателя, л
          <input
            type="number"
            step="0.1"
            min="0.1"
            max="20"
            value={isElectric ? '' : form.engineVolume}
            onChange={set('engineVolume')}
            disabled={isElectric}
            title={isElectric ? 'У электромобиля нет объёма двигателя' : undefined}
          />
        </label>
        <label>
          Мощность, л.с.
          <input
            type="number"
            min="1"
            max="2000"
            value={form.powerHp}
            onChange={set('powerHp')}
          />
        </label>
      </div>

      <div className="actions">
        <button type="submit" className="primary">
          {initial ? 'Сохранить' : 'Добавить'}
        </button>
        <button type="button" onClick={onCancel}>Отмена</button>
      </div>
    </form>
  );
}
