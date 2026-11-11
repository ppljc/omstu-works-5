SELECT
    coin_title,
    coin_year,
    total_quantity,
    collector_count
FROM mv_coin_statistics
ORDER BY total_quantity DESC
LIMIT 5;