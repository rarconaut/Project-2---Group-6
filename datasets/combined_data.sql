DROP TABLE combined_data;

CREATE TABLE combined_data (
 	ticker VARCHAR(255),
 	exchange VARCHAR(255),
	sector VARCHAR(255),
	industry VARCHAR(255),
	state_val VARCHAR(255),
	city VARCHAR(255),
	lat DECIMAL,
	lon DECIMAL,
	rpt_year VARCHAR(255),
	revenue_scaled BIGINT,
	income_tax_scaled BIGINT,
	net_income_scaled BIGINT,
	market_cap BIGINT,
	median_hh_income BIGINT
);

SELECT * FROM combined_data;