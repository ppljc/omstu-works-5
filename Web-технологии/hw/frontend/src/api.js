const BASE = '/api';

// Извлекает читаемые сообщения из тела ошибки:
// либо из ASP.NET ProblemDetails ({ errors: { "Поле": ["сообщение"] } }),
// либо из словаря BadRequest(ModelState) ({ "Поле": ["сообщение"] }).
function flattenErrors(body) {
  if (!body || typeof body !== 'object') return '';
  const src = body.errors && typeof body.errors === 'object' ? body.errors : body;
  const parts = [];
  for (const value of Object.values(src)) {
    if (Array.isArray(value)) parts.push(...value);
    else if (typeof value === 'string') parts.push(value);
  }
  return parts.filter((s) => s && s !== '[object Object]').join(' ');
}

async function request(path, options = {}) {
  const isFormData = options.body instanceof FormData;
  const res = await fetch(`${BASE}${path}`, {
    // Для multipart (загрузка фото) Content-Type не задаём — браузер сам проставит boundary
    ...(isFormData ? {} : { headers: { 'Content-Type': 'application/json' } }),
    ...options,
  });
  if (res.status === 204) return null;
  const body = await res.json().catch(() => null);
  if (!res.ok) {
    const message = flattenErrors(body) || `Ошибка ${res.status}`;
    throw new Error(message);
  }
  return body;
}

export const api = {
  getCars: (params = {}) => {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v)
    ).toString();
    return request(`/cars${qs ? `?${qs}` : ''}`);
  },
  getCar: (id) => request(`/cars/${id}`),
  createCar: (car) => request('/cars', { method: 'POST', body: JSON.stringify(car) }),
  updateCar: (car) => request(`/cars/${car.id}`, { method: 'PUT', body: JSON.stringify(car) }),
  deleteCar: (id) => request(`/cars/${id}`, { method: 'DELETE' }),

  getServices: (carId) => request(`/cars/${carId}/services`),
  addService: (carId, record) =>
    request(`/cars/${carId}/services`, { method: 'POST', body: JSON.stringify(record) }),
  deleteService: (id) => request(`/services/${id}`, { method: 'DELETE' }),

  getPhotos: (carId) => request(`/cars/${carId}/photos`),
  uploadPhoto: (carId, file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request(`/cars/${carId}/photos`, { method: 'POST', body: formData });
  },
  deletePhoto: (id) => request(`/photos/${id}`, { method: 'DELETE' }),

  getExpenses: (params = {}) => {
    const qs = new URLSearchParams(
      Object.entries(params).filter(([, v]) => v !== undefined && v !== null && v !== '')
    ).toString();
    return request(`/reports/expenses${qs ? `?${qs}` : ''}`);
  },
};
