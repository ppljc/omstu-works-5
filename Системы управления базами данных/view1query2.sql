SELECT
    coin_title,
    country_title,
    coin_year,
    coin_catalog_price
FROM v_coin_details
WHERE alloy_title = 'Золото'
ORDER BY coin_year;