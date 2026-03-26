CREATE OR REPLACE VIEW candlestick_data AS
	WITH refined_data AS(
		SELECT date_trunc('second', received_at) as normalized_second, ticker,
		AVG(price) as price
		FROM oil_stock_ticks
		WHERE received_at >= CURRENT_DATE
		GROUP BY normalized_second, ticker 
		
	)
	SELECT MAX(price) AS high, MIN(price) as low, (SELECT price FROM refined_data 
	ORDER BY normalized_second ASC LIMIT 1) AS open_val, (SELECT price FROM 
	refined_data ORDER BY normalized_second DESC LIMIT 1) as close_val, CURRENT_DATE,
	ticker
	FROM refined_data
	GROUP BY ticker
	
	
	
	