CREATE OR REPLACE PROCEDURE candlestick_add() 
LANGUAGE plpgsql
AS $$
BEGIN
	INSERT INTO candlestick_table (ticker, high, low, open_val, close_val, date_val)
	SELECT ticker, high, low, open_val, close_val, CURRENT_DATE FROM candlestick_data;
END;
$$;
