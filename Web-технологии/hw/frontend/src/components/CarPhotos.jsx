import { useEffect, useRef, useState } from 'react';
import { api } from '../api.js';

export default function CarPhotos({ carId, onChanged, onError }) {
  const [photos, setPhotos] = useState([]);
  const [uploading, setUploading] = useState(false);
  const fileInput = useRef(null);

  const load = async () => {
    try {
      setPhotos(await api.getPhotos(carId));
    } catch (err) {
      onError(err.message);
    }
  };

  useEffect(() => { load(); }, [carId]);

  const handleUpload = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = ''; // чтобы можно было выбрать тот же файл повторно
    if (!file) return;
    try {
      setUploading(true);
      await api.uploadPhoto(carId, file);
      await load();
      onChanged(); // обновить миниатюры в списке автомобилей
    } catch (err) {
      onError(err.message);
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm('Удалить фото?')) return;
    try {
      await api.deletePhoto(id);
      await load();
      onChanged();
    } catch (err) {
      onError(err.message);
    }
  };

  return (
    <section className="card">
      <div className="section-header">
        <h3>Фото</h3>
        <div>
          <input
            ref={fileInput}
            type="file"
            accept="image/jpeg,image/png,image/webp"
            onChange={handleUpload}
            style={{ display: 'none' }}
          />
          <button
            className="primary"
            disabled={uploading}
            onClick={() => fileInput.current?.click()}
          >
            {uploading ? 'Загрузка…' : '+ Добавить фото'}
          </button>
        </div>
      </div>

      {photos.length === 0 ? (
        <p className="empty">Фотографий пока нет. Форматы: jpg, png, webp, до 5 МБ.</p>
      ) : (
        <div className="photo-grid">
          {photos.map((p) => (
            <figure key={p.id} className="photo-item">
              <img src={`/uploads/${p.fileName}`} alt={`Фото автомобиля ${p.id}`} />
              <figcaption>
                <button className="danger small" onClick={() => handleDelete(p.id)}>
                  Удалить
                </button>
              </figcaption>
            </figure>
          ))}
        </div>
      )}
    </section>
  );
}
