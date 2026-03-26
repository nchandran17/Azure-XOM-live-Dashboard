-- Note: this is not the actual table creation file i used, since I forgot to save my 
-- creation script, i just did script create in pgAdmin and modified it to roughly how i created mine


CREATE TABLE IF NOT EXISTS public.oil_stock_ticks
(
    PRIMARY KEY id integer,
    ticker varchar(10),
    price numeric(12,4),
    volume numeric(18,2),
    trade_time bigint,   ---- did not end up using this, originally it was to prevent overflow, but it was easier to use recieved_at and the overflow case doesnt affect the purpose of this project
    received_at timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
)

TABLESPACE pg_default;

ALTER TABLE IF EXISTS public.oil_stock_ticks
    OWNER to pitt_admin;
