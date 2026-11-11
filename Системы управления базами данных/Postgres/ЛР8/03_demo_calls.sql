DELETE FROM public.coin_features WHERE coin_id = 9001;
DELETE FROM public.coin_metadata  WHERE coin_id = 9001;
DELETE FROM public.collections    WHERE coin_id = 9001;
DELETE FROM public.coins          WHERE coin_id = 9001;

CALL public.coins_insert(
    p_coin_title         => 'Тестовая монета ЛР8',
    p_coin_country_id    => 1,
    p_coin_alloy_id      => 1,
    p_coin_year          => 2025,
    p_coin_mintage       => 1000,
    p_coin_weight        => 5.500,
    p_coin_catalog_price => 1234.56,
    p_coin_history       => 'Временная запись для демонстрации процедур ЛР8.',
    p_coin_id            => 9001);

SELECT coin_id, coin_title, coin_country_id, coin_year, coin_alloy_id,
       coin_mintage, coin_weight, coin_catalog_price, coin_history
  FROM public.coins
 WHERE coin_id = 9001;

CALL public.coins_update(
    9001,
    'Тестовая монета ЛР8 (изменено)',
    1,
    2,
    2025,
    2000,
    5.500,
    2500.00,
    'Цена пересмотрена процедурой coins_update.');

SELECT coin_id, coin_title, coin_alloy_id, coin_mintage,
       coin_catalog_price, coin_history
  FROM public.coins
 WHERE coin_id = 9001;

CALL public.coins_delete(9001);

SELECT COUNT(*) AS "Монет с id = 9001 после удаления"
  FROM public.coins
 WHERE coin_id = 9001;

SELECT public.fn_coin_history(1) AS "История монеты № 1";

CALL public.coins_insert(
    p_coin_title   => 'Монета для проверки функции',
    p_coin_country_id => 1,
    p_coin_alloy_id   => 10,
    p_coin_year    => 1913,
    p_coin_history => 'История добавлена для проверки функции fn_coin_history.',
    p_coin_id      => 9002);

SELECT public.fn_coin_history(9002) AS "История тестовой монеты";

CALL public.coins_delete(9002);

SELECT public.fn_coin_history(9999) AS "История несуществующей монеты";
