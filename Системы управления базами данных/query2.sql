SELECT COUNT(DISTINCT col.collector_id) AS "Число коллекционеров"
FROM collectors col
JOIN collections c
    ON c.collector_id = col.collector_id
JOIN coins co
    ON co.coin_id = c.coin_id
JOIN alloys a
    ON a.alloy_id = co.coin_alloy_id
WHERE a.alloy_title = 'Золото';