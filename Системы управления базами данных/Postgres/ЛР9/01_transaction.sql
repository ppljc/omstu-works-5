BEGIN;

INSERT INTO public.countries (country_title) VALUES ('Сомали');
INSERT INTO public.countries (country_title) VALUES ('Египет');

SAVEPOINT sp_before_denmark;

INSERT INTO public.countries (country_title) VALUES ('Дания');
INSERT INTO public.countries (country_title) VALUES ('Финляндия');

ROLLBACK TO SAVEPOINT sp_before_denmark;

COMMIT;
