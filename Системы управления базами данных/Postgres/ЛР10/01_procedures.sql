CREATE TABLE IF NOT EXISTS public.collections_2024 (
    collector_id                integer NOT NULL,
    coin_id                     integer NOT NULL,
    collection_quantity         integer NOT NULL,
    collection_purchase_price   numeric(15,2),
    collection_condition_id     integer NOT NULL,
    collection_acquisition_date date NOT NULL
);

CREATE OR REPLACE PROCEDURE public.coins_select(
    IN p_coin_id    integer,
    IN p_country_id integer,
    IN p_alloy_id   integer)
LANGUAGE plpgsql
AS $$
DECLARE
    c_coin_id      integer;
    c_coin_title   varchar(200);
    c_country      varchar(100);
    c_alloy        varchar(100);
    c_year         smallint;
    c_price        numeric(15,2);
    cur CURSOR FOR SELECT
        c.coin_id, c.coin_title, co.country_title, a.alloy_title,
        c.coin_year, c.coin_catalog_price
    FROM coins c
    JOIN countries co ON co.country_id = c.coin_country_id
    JOIN alloys a ON a.alloy_id = c.coin_alloy_id
    WHERE (p_coin_id IS NULL OR c.coin_id = p_coin_id) AND
          (p_country_id IS NULL OR c.coin_country_id = p_country_id) AND
          (p_alloy_id IS NULL OR c.coin_alloy_id = p_alloy_id)
    ORDER BY c.coin_id;
BEGIN
    OPEN cur;
    LOOP
        FETCH cur INTO c_coin_id, c_coin_title, c_country, c_alloy, c_year, c_price;
        EXIT WHEN NOT FOUND;
        RAISE NOTICE 'Монета: %, «%», страна: %, сплав: %, год: %, цена: %',
            c_coin_id, c_coin_title, c_country, c_alloy, c_year, c_price;
    END LOOP;
    CLOSE cur;
END;
$$;

CREATE OR REPLACE PROCEDURE public.collections_to_2024()
LANGUAGE plpgsql
AS $$
DECLARE
    c_collector_id integer;
    c_coin_id      integer;
    c_quantity     integer;
    c_price        numeric(15,2);
    c_condition_id integer;
    c_date         date;
    cur CURSOR FOR SELECT collector_id, coin_id, collection_quantity,
                          collection_purchase_price, collection_condition_id,
                          collection_acquisition_date
    FROM collections
    WHERE collection_acquisition_date BETWEEN '2024-01-01' AND '2024-12-31';
BEGIN
    OPEN cur;
    LOOP
        FETCH cur INTO c_collector_id, c_coin_id, c_quantity, c_price, c_condition_id, c_date;
        EXIT WHEN NOT FOUND;
        INSERT INTO collections_2024 VALUES
            (c_collector_id, c_coin_id, c_quantity, c_price, c_condition_id, c_date);
    END LOOP;
    CLOSE cur;
END;
$$;
