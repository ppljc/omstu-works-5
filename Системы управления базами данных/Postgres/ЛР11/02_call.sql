UPDATE public.coins
SET coin_catalog_price = 2100.00
WHERE coin_id = 1;

SELECT coin_id, jsonb_pretty(metadata) AS price_history
FROM public.coin_metadata
WHERE coin_id = 1;