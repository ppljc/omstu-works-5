CREATE OR REPLACE FUNCTION public.fn_coin_history(p_coin_id integer)
RETURNS text
LANGUAGE plpgsql
AS $$
DECLARE
    v_history text;
BEGIN
    SELECT coin_history
      INTO v_history
      FROM public.coins
     WHERE coin_id = p_coin_id;

    RETURN v_history;
END;
$$;

SELECT public.fn_coin_history(1) AS "История монеты № 1";

SELECT public.fn_coin_history(9999) AS "История несуществующей монеты";
