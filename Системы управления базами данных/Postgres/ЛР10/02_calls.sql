CALL public.coins_select(NULL, NULL, NULL);

CALL public.coins_select(1, NULL, NULL);

CALL public.coins_select(NULL, 3, NULL);

CALL public.coins_select(NULL, NULL, 9);

TRUNCATE public.collections_2024;

CALL public.collections_to_2024();

SELECT collector_id, coin_id, collection_quantity,
       collection_purchase_price, collection_condition_id,
       collection_acquisition_date
  FROM public.collections_2024
 ORDER BY collection_acquisition_date, collector_id;
