SELECT
    col.collector_last_name AS "Фамилия",
    col.collector_first_name AS "Имя",
    SUM(c.collection_purchase_price) AS "Общая стоимость золотых монет"
FROM collectors col
JOIN collections c
    ON c.collector_id = col.collector_id
JOIN coins co
    ON co.coin_id = c.coin_id
JOIN alloys a
    ON a.alloy_id = co.coin_alloy_id
WHERE col.collector_last_name = 'Петров'
  AND col.collector_first_name = 'Александр'
  AND a.alloy_title = 'Золото'
GROUP BY
    col.collector_id,
    col.collector_last_name,
    col.collector_first_name;