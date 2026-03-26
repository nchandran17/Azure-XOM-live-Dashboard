CREATE OR REPLACE VIEW Whale_Hunting AS
SELECT*FROM oil_stock_ticks
WHERE volume>= (SELECT AVG(volume) FROM oil_stock_ticks
WHERE received_at >= CURRENT_DATE - INTERVAL '4 days')*10