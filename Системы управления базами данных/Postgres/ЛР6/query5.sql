SELECT
    col.collector_last_name AS "Фамилия коллекционера",

    COALESCE(
        SUM(c.collection_purchase_price)
            FILTER (WHERE co.coin_title = 'Рубль Николая II'
                     AND a.alloy_title = 'Серебро'),
        0
    ) AS "Стоимость серебряных рублей",

    COALESCE(
        SUM(c.collection_purchase_price)
            FILTER (WHERE co.coin_title = 'Червонец Николая II'
                     AND a.alloy_title = 'Золото'),
        0
    ) AS "Стоимость золотых червонцев",

    COALESCE(
        SUM(c.collection_quantity)
            FILTER (WHERE co.coin_title = 'Рубль Николая II'
                     AND a.alloy_title = 'Серебро'),
        0
    ) AS "Количество серебряных рублей",

    COALESCE(
        SUM(c.collection_quantity)
            FILTER (WHERE co.coin_title = 'Червонец Николая II'
                     AND a.alloy_title = 'Золото'),
        0
    ) AS "Количество золотых червонцев"

FROM collectors col
LEFT JOIN collections c
    ON c.collector_id = col.collector_id
LEFT JOIN coins co
    ON co.coin_id = c.coin_id
LEFT JOIN alloys a
    ON a.alloy_id = co.coin_alloy_id
GROUP BY
    col.collector_id,
    col.collector_last_name
ORDER BY col.collector_last_name;