SELECT
    col.collector_last_name AS "Фамилия",
    col.collector_first_name AS "Имя",
    col.collector_patronymic AS "Отчество",
    co.coin_title AS "Название монеты",
    country.country_title AS "Страна",
    co.coin_year AS "Год выпуска",
    a.alloy_title AS "Сплав",
    co.coin_weight AS "Вес, г",
    c.collection_quantity AS "Количество",
    c.collection_purchase_price AS "Цена приобретения",
    cond.condition_title AS "Состояние",
    c.collection_acquisition_date AS "Дата приобретения"
FROM collectors col
JOIN collections c
    ON c.collector_id = col.collector_id
JOIN coins co
    ON co.coin_id = c.coin_id
JOIN countries country
    ON country.country_id = co.coin_country_id
JOIN alloys a
    ON a.alloy_id = co.coin_alloy_id
JOIN conditions cond
    ON cond.condition_id = c.collection_condition_id
WHERE col.collector_last_name = 'Сидоров'
ORDER BY co.coin_year, co.coin_title;