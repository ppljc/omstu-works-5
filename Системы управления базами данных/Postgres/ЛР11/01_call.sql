INSERT INTO public.collections (
    collector_id, 
    coin_id, 
    collection_quantity, 
    collection_purchase_price, 
    collection_condition_id
)
VALUES (1, 1, 3, NULL, 1);

SELECT collector_id, coin_id, collection_quantity, collection_purchase_price, collection_acquisition_date
FROM public.collections
WHERE collector_id = 1 AND coin_id = 1;