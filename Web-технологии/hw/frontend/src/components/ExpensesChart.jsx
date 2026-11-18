import { useEffect, useState } from 'react';
import { Bar } from 'react-chartjs-2';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Tooltip,
  Legend,
} from 'chart.js';
import { api } from '../api.js';

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend);

const MONTHS = [
  'Янв', 'Фев', 'Мар', 'Апр', 'Май', 'Июн',
  'Июл', 'Авг', 'Сен', 'Окт', 'Ноя', 'Дек',
];

export default function ExpensesChart({ carId, onError }) {
  const [from, setFrom] = useState('');
  const [to, setTo] = useState('');
  const [data, setData] = useState({ total: 0, monthly: [] });

  useEffect(() => {
    const load = async () => {
      try {
        const params = { carId: carId || undefined, from: from || undefined, to: to || undefined };
        setData(await api.getExpenses(params));
      } catch (err) {
        onError(err.message);
      }
    };
    load();
  }, [carId, from, to]);

  const chartData = {
    labels: data.monthly.map((m) => `${MONTHS[m.month - 1]} ${m.year}`),
    datasets: [
      {
        label: 'Затраты на обслуживание, ₽',
        data: data.monthly.map((m) => m.total),
        backgroundColor: '#4f7cff',
        borderRadius: 6,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: { legend: { display: false } },
    scales: { y: { beginAtZero: true } },
  };

  return (
    <section className="card">
      <div className="section-header">
        <h3>Затраты на обслуживание{carId ? ' (выбранный автомобиль)' : ' (весь гараж)'}</h3>
        <div className="period">
          <input type="date" value={from} onChange={(e) => setFrom(e.target.value)} title="С даты" />
          <span>—</span>
          <input type="date" value={to} onChange={(e) => setTo(e.target.value)} title="По дату" />
        </div>
      </div>

      <p className="total">
        Итого за период: <strong>{Number(data.total).toLocaleString('ru-RU')} ₽</strong>
      </p>

      {data.monthly.length === 0 ? (
        <p className="empty">Нет данных за выбранный период.</p>
      ) : (
        <div className="chart-wrap">
          <Bar data={chartData} options={options} />
        </div>
      )}
    </section>
  );
}
