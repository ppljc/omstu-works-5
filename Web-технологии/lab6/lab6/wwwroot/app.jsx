"use strict";

const { useState, useEffect } = React;

const apiBase = "/api/cars";

async function ensureOk(response) {
    if (!response.ok) {
        let details = "";
        try {
            const body = await response.json();
            if (body && body.message) {
                details = ": " + body.message;
            }
        } catch {
        }
        throw new Error("Запрос завершился с кодом " + response.status + details);
    }
}

async function requestJson(url, options) {
    const response = await fetch(url, options);
    await ensureOk(response);
    if (response.status === 204) {
        return null;
    }
    return await response.json();
}

function formatPrice(price) {
    return new Intl.NumberFormat("ru-RU", {
        style: "currency",
        currency: "RUB",
        maximumFractionDigits: 0
    }).format(price);
}

const commonsImageCache = new Map();

async function findCarImage(firm, model, color, year) {
    const key = (firm + " " + model + " " + color + " " + year).toLowerCase();
    if (commonsImageCache.has(key)) {
        return commonsImageCache.get(key);
    }
    const queries = [firm + " " + model + " " + color + " " + year, firm + " " + model + " " + year, firm + " " + model, firm].filter(Boolean);
    let result = null;
    for (const query of queries) {
        const url = "https://commons.wikimedia.org/w/api.php?action=query&format=json&origin=*"
            + "&generator=search&gsrnamespace=6&gsrlimit=8"
            + "&gsrsearch=" + encodeURIComponent(query)
            + "&prop=imageinfo&iiprop=url|size|mime&iiurlwidth=640";
        try {
            const response = await fetch(url);
            if (response.ok) {
                const data = await response.json();
                const pages = Object.values(data.query ? data.query.pages : {});
                const pick = pages
                    .map((p) => p.imageinfo && p.imageinfo[0])
                    .find((ii) => ii && ii.mime === "image/jpeg" && ii.width >= 800);
                if (pick) {
                    result = pick.thumburl.split("?")[0];
                    break;
                }
            }
        } catch {
        }
    }
    commonsImageCache.set(key, result);
    return result;
}

function colorFromId(id) {
    const hue = (Number(id) * 67) % 360;
    return {
        from: "hsl(" + hue + ", 55%, 45%)",
        to: "hsl(" + ((hue + 40) % 360) + ", 55%, 28%)"
    };
}

function escapeXml(text) {
    return String(text)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;");
}

function buildFallbackSvg(car) {
    const colors = colorFromId(car.id);
    const title = (car.firm + " " + car.model).slice(0, 24);
    const svg =
        '<svg xmlns="http://www.w3.org/2000/svg" width="640" height="360" viewBox="0 0 640 360">' +
        '<defs><linearGradient id="g" x1="0" y1="0" x2="1" y2="1">' +
        '<stop offset="0" stop-color="' + colors.from + '"/>' +
        '<stop offset="1" stop-color="' + colors.to + '"/>' +
        '</linearGradient></defs>' +
        '<rect width="640" height="360" fill="url(#g)"/>' +
        '<g fill="rgba(255,255,255,0.9)">' +
        '<path d="M170 225 l25 -45 a20 20 0 0 1 18 -11 h130 a20 20 0 0 1 18 11 l25 45 z"/>' +
        '<rect x="140" y="220" width="280" height="50" rx="18"/>' +
        '<circle cx="210" cy="275" r="26" fill="#1f2933"/>' +
        '<circle cx="210" cy="275" r="11" fill="#cbd2d9"/>' +
        '<circle cx="350" cy="275" r="26" fill="#1f2933"/>' +
        '<circle cx="350" cy="275" r="11" fill="#cbd2d9"/>' +
        '</g>' +
        '<text x="320" y="90" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif"' +
        ' font-size="34" font-weight="600" fill="#ffffff">' + escapeXml(title) + "</text>" +
        '<text x="320" y="125" text-anchor="middle" font-family="Segoe UI, Arial, sans-serif"' +
        ' font-size="18" fill="rgba(255,255,255,0.75)">ID ' + Number(car.id) + ", " + Number(car.year) + " г.</text>" +
        "</svg>";

    return "data:image/svg+xml;charset=utf-8," + encodeURIComponent(svg);
}

function CarImage({ car }) {
    const [src, setSrc] = useState(() => buildFallbackSvg(car));

    useEffect(() => {
        let alive = true;
        findCarImage(car.firm, car.model, car.color, car.year).then((url) => {
            if (alive && url) {
                setSrc(url);
            }
        });
        return () => {
            alive = false;
        };
    }, [car.id, car.firm, car.model]);

    return (
        <img
            className="car-image"
            alt={"Фотография автомобиля " + car.firm + " " + car.model}
            loading="lazy"
            src={src}
            onError={() => setSrc(buildFallbackSvg(car))}
        />
    );
}

function CarCard({ car, onChanged, onDeleted }) {
    const [editing, setEditing] = useState(false);
    const [draft, setDraft] = useState(car);
    const [saving, setSaving] = useState(false);

    const field = (name, label, type) => (
        <label className="field">
            <span>{label}</span>
            <input
                type={type}
                value={draft[name]}
                required
                onChange={(e) => setDraft({ ...draft, [name]: e.target.value })}
            />
        </label>
    );

    async function save(event) {
        event.preventDefault();
        setSaving(true);
        try {
            const updated = await requestJson(apiBase + "/" + car.id, {
                method: "PUT",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    firm: draft.firm,
                    model: draft.model,
                    year: Number(draft.year),
                    power: Number(draft.power),
                    color: draft.color,
                    price: Number(draft.price),
                    dealerId: Number(draft.dealerId)
                })
            });
            setEditing(false);
            onChanged(updated);
        } catch (error) {
            window.alert("Не удалось сохранить изменения. " + error.message);
        } finally {
            setSaving(false);
        }
    }

    async function remove() {
        if (!window.confirm("Удалить автомобиль № " + car.id + "?")) {
            return;
        }
        try {
            await requestJson(apiBase + "/" + car.id, { method: "DELETE" });
            onDeleted(car.id);
        } catch (error) {
            window.alert("Не удалось удалить автомобиль. " + error.message);
        }
    }

    return (
        <article className="card" data-car-id={car.id}>
            {editing ? (
                <form className="edit-form" onSubmit={save}>
                    <h3 className="car-title">Изменить: {car.firm} {car.model}</h3>
                    {field("firm", "Фирма", "text")}
                    {field("model", "Модель", "text")}
                    {field("year", "Год выпуска", "number")}
                    {field("power", "Мощность (л.с.)", "number")}
                    {field("color", "Цвет", "text")}
                    {field("price", "Цена", "number")}
                    {field("dealerId", "ID дилера", "number")}
                    <div className="car-buttons">
                        <button type="submit" disabled={saving}>
                            {saving ? "Сохранение…" : "Сохранить"}
                        </button>
                        <button type="button" className="secondary" onClick={() => setEditing(false)}>
                            Отмена
                        </button>
                    </div>
                </form>
            ) : (
                <React.Fragment>
                    <CarImage car={car} />
                    <div className="car-info">
                        <h3 className="car-title">{car.firm} {car.model}</h3>
                        <p className="car-line">Год выпуска: {car.year}</p>
                        <p className="car-line">Мощность: {car.power} л.с.</p>
                        <p className="car-line">Цвет: {car.color}</p>
                        <p className="car-line">Цена: {formatPrice(car.price)}</p>
                        <p className="car-line">Дилер (ID): {car.dealerId}</p>
                    </div>
                    <div className="car-buttons">
                        <button type="button" onClick={() => { setDraft(car); setEditing(true); }}>
                            Изменить
                        </button>
                        <button type="button" className="danger" onClick={remove}>Удалить</button>
                    </div>
                </React.Fragment>
            )}
        </article>
    );
}

function App() {
    const [cars, setCars] = useState(null);
    const [status, setStatus] = useState({ text: "Загрузка списка…", isError: false });
    const [searchId, setSearchId] = useState("");

    function showError(prefix, error) {
        setStatus({ text: prefix + " " + error.message, isError: true });
    }

    async function loadCars() {
        setStatus({ text: "Загрузка списка…", isError: false });
        try {
            const list = await requestJson(apiBase);
            setCars(list);
            setStatus(list.length === 0
                ? { text: "В базе нет ни одного автомобиля.", isError: false }
                : { text: "", isError: false });
        } catch (error) {
            setCars([]);
            showError("Не удалось загрузить автомобили.", error);
        }
    }

    useEffect(() => {
        loadCars();
    }, []);

    async function searchCar() {
        const id = searchId.trim();
        if (id === "") {
            setStatus({ text: "Введите идентификатор автомобиля.", isError: true });
            return;
        }
        setStatus({ text: "Поиск автомобиля № " + id + "…", isError: false });
        try {
            const car = await requestJson(apiBase + "/" + encodeURIComponent(id));
            setCars([car]);
            setStatus({ text: "", isError: false });
        } catch (error) {
            setCars([]);
            if (error.message.includes("404")) {
                setStatus({ text: "Автомобиль с идентификатором " + id + " не найден.", isError: true });
            } else {
                showError("Поиск не удался.", error);
            }
        }
    }

    function handleChanged(updated) {
        setCars((list) => list.map((c) => (c.id === updated.id ? updated : c)));
        setStatus({ text: "Автомобиль № " + updated.id + " обновлён.", isError: false });
    }

    function handleDeleted(id) {
        setCars((list) => list.filter((c) => c.id !== id));
        setStatus({ text: "Автомобиль № " + id + " удалён.", isError: false });
    }

    return (
        <React.Fragment>
            <header className="page-header">
                <h1>Каталог автомобилей</h1>
            </header>

            <section className="search-panel">
                <label htmlFor="search-id">Поиск автомобиля по идентификатору</label>
                <div className="search-row">
                    <input
                        id="search-id"
                        type="number"
                        min="1"
                        placeholder="Например, 1"
                        value={searchId}
                        onChange={(e) => setSearchId(e.target.value)}
                        onKeyDown={(e) => { if (e.key === "Enter") searchCar(); }}
                    />
                    <button type="button" onClick={searchCar}>Найти</button>
                    <button type="button" className="secondary" onClick={loadCars}>Показать все</button>
                </div>
            </section>

            <div className={"status" + (status.isError ? " error" : "")} role="status" aria-live="polite">
                {status.text}
            </div>

            <main className="cars-grid">
                {(cars || []).map((car) => (
                    <CarCard key={car.id} car={car} onChanged={handleChanged} onDeleted={handleDeleted} />
                ))}
            </main>
        </React.Fragment>
    );
}

ReactDOM.createRoot(document.getElementById("root")).render(<App />);
