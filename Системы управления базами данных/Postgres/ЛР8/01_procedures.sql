CREATE OR REPLACE PROCEDURE public.coins_insert(
    p_coin_title         varchar(200),
    p_coin_country_id    integer,
    p_coin_alloy_id      integer,
    p_coin_year          integer       DEFAULT NULL,
    p_coin_mintage       bigint        DEFAULT NULL,
    p_coin_weight        numeric(10,3) DEFAULT NULL,
    p_coin_catalog_price numeric(15,2) DEFAULT NULL,
    p_coin_history       text          DEFAULT NULL,
    p_coin_id            integer       DEFAULT NULL)
LANGUAGE sql
AS $$
    INSERT INTO public.coins (coin_id,
                              coin_title,
                              coin_country_id,
                              coin_year,
                              coin_alloy_id,
                              coin_mintage,
                              coin_weight,
                              coin_catalog_price,
                              coin_history)
    OVERRIDING SYSTEM VALUE
    VALUES (COALESCE(p_coin_id, nextval('public.coins_coin_id_seq')),
            p_coin_title,
            p_coin_country_id,
            p_coin_year,
            p_coin_alloy_id,
            p_coin_mintage,
            p_coin_weight,
            p_coin_catalog_price,
            p_coin_history);
$$;

CREATE OR REPLACE PROCEDURE public.coins_update(
    p_coin_id            integer,
    p_coin_title         varchar(200),
    p_coin_country_id    integer,
    p_coin_alloy_id      integer,
    p_coin_year          integer       DEFAULT NULL,
    p_coin_mintage       bigint        DEFAULT NULL,
    p_coin_weight        numeric(10,3) DEFAULT NULL,
    p_coin_catalog_price numeric(15,2) DEFAULT NULL,
    p_coin_history       text          DEFAULT NULL)
LANGUAGE sql
AS $$
    UPDATE public.coins
       SET coin_title         = p_coin_title,
           coin_country_id    = p_coin_country_id,
           coin_year          = p_coin_year,
           coin_alloy_id      = p_coin_alloy_id,
           coin_mintage       = p_coin_mintage,
           coin_weight        = p_coin_weight,
           coin_catalog_price = p_coin_catalog_price,
           coin_history       = p_coin_history
     WHERE coin_id = p_coin_id;
$$;

CREATE OR REPLACE PROCEDURE public.coins_delete(
    p_coin_id integer)
LANGUAGE sql
AS $$
    DELETE FROM public.coins
     WHERE coin_id = p_coin_id;
$$;
