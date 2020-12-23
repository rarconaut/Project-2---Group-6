DROP TABLE fin_accts;

CREATE TABLE fin_accts (
	ticker VARCHAR(20),
	reporting_date VARCHAR(25),
	total_revenue VARCHAR(25),
	gross_profit BIGINT,
	total_years_reporting INT
);

SELECT * FROM fin_accts;


DROP TABLE fin_stats;

CREATE TABLE fin_stats (
	ticker VARCHAR(20),
	reporting_date VARCHAR(25),
	market_cap VARCHAR(25),
	market_cap_num BIGINT,
	total_years_reporting INT
);

SELECT * FROM fin_stats;