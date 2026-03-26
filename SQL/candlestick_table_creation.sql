CREATE TABLE IF NOT EXISTS candlestick_table (
	id SERIAL PRIMARY KEY,
	ticker VARCHAR(10),
	high NUMERIC(15, 4),
	low NUMERIC(15, 4),
	open_val NUMERIC(15, 4),
	close_val NUMERIC(15, 4),
	date_val DATE UNIQUE
)