import { useState } from 'react';
import { api } from '../api.js';

const WORK_TYPES = [
  'Замена масла',
  'Шиномонтаж',
  'Техническое обслуживание (ТО)',
  'Замена тормозных колодок',
  'Диагностика',
  'Ремонт подвески',
  'Другое',
];

export default function ServiceHistory({ carId, records, onChanged, onError }) {
  const [showForm, setShowForm] = useState(false);
  const [form, setForm] = useState({
    workType: WORK_TYPES[0],
    date: new Date().toISOString().slice(0, 10),
    mileage: 0,
    cost: '',
    notes: '',
  });

  const set = (field) => (e) => setForm({ ...form, [field]: e.target.value });

  const handleAdd = async (e) => {
    e.preventDefault();
    try {
      await api.addService(carId, {
        workType: form.workType,
        date: form.date,
        mileage: Number(form.mileage),
        cost: Number(form.cost),
        notes: form.notes || null,
      });
      setShowForm(false);
      setForm({ ...form, cost: '', notes: '' });
      onChanged();
    } catch (err) {
      onError(err.message);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить запись об обслуживании?')) return;
    try {
      await api.deleteService(id);
      onChanged();
    } catch (err) {
      onError(err.message);
    }
  };

  const total = records.reduce((sum, r) => sum + Number(r.cost), 0);

  return (
    <section className="card">
      <div className="section-header">
        <h3>История обслуживания</h3>
        <button className="primary" onClick={() => setShowForm(!showForm)}>
          {showForm ? 'Скрыть форму' : '+ Добавить запись'}
        </button>
      </div>

      {showForm && (
        <form className="form service-form" onSubmit={handleAdd}>
          <div className="grid">
            <label>
              Тип работы
              <select value={form.workType} onChange={set('workType')}>
                {WORK_TYPES.map((t) => <option key={t}>{t}</option>)}
              </select>
            </label>
            <label>
              Дата
              <input type="date" value={form.date} onChange={set('date')} required
                     max={new Date().toISOString().slice(0, 10)} />
            </label>
            <label>
              Пробег, км
              <input type="number" value={form.mileage} onChange={set('mileage')}
                     required min={0} />
            </label>
            <label>
              Стоимость, ₽ (0 — бесплатно)
              <input type="number" step="0.01" min="0" value={form.cost}
                     onChange={set('cost')} required />
            </label>
          </div>
          <label>
            Примечание
            <input value={form.notes} onChange={set('notes')} maxLength={500} />
          </label>
          <div className="actions">
            <button type="submit" className="primary">Добавить</button>
          </div>
        </form>
      )}

      {records.length === 0 ? (
        <p className="empty">Записей об обслуживании пока нет.</p>
      ) : (
        <>
          <table className="table">
            <thead>
              <tr>
                <th>Дата</th>
                <th>Работа</th>
                <th>Пробег</th>
                <th>Стоимость</th>
                <th></th>
              </tr>
            </thead>
            <tbody>
              {records.map((r) => (
                <tr key={r.id}>
                  <td>{r.date}</td>
                  <td>
                    {r.workType}
                    {r.notes && <div className="notes">{r.notes}</div>}
                  </td>
                  <td>{Number(r.mileage).toLocaleString('ru-RU')} км</td>
                  <td>{Number(r.cost).toLocaleString('ru-RU')} ₽</td>
                  <td>
                    <button className="danger small" onClick={() => handleDelete(r.id)}>
                      Удалить
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
          <p className="total">Итого по автомобилю: <strong>{total.toLocaleString('ru-RU')} ₽</strong></p>
        </>
      )}
    </section>
  );
}
