SELECT DISTINCT
    col.collector_id,
    col.collector_last_name AS "Фамилия",
    col.collector_first_name AS "Имя",
    col.collector_patronymic AS "Отчество",
    col.collector_phone AS "Телефон"
FROM collectors col
WHERE EXISTS (
    SELECT 1
    FROM collections c
    JOIN coins co
        ON co.coin_id = c.coin_id
    JOIN countries country
        ON country.country_id = co.coin_country_id
    JOIN alloys a
        ON a.alloy_id = co.coin_alloy_id
    WHERE c.collector_id = col.collector_id
      AND country.country_title = 'Российская империя'
      AND a.alloy_title = 'Серебро'
      AND co.coin_title IN (
          'Рубль Екатерины II',
          'Рубль Александра I'
      )
)
ORDER BY col.collector_last_name;