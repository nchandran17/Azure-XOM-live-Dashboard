CREATE OR REPLACE VIEW VWAP AS
SELECT ticker, 
COUNT(*) as total_trades,
SUM(price*volume)/SUM(volume) as VWAP,
SUM(price*volume) as total_dollar_volume,
EXTRACT(DAY FROM received_at) as date_val
FROM oil_stock_ticks
GROUP BY ticker, date_val