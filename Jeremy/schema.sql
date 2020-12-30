-- Create a fin_stats table to hold the financial account info for each company
DROP TABLE fin_stats;

CREATE TABLE fin_stats (
 	id SERIAL,
 	ticker VARCHAR(20),
 	exchange VARCHAR(50),
 	rpt_scale VARCHAR(100),
 	rpt_year VARCHAR(25),
 	revenue VARCHAR(50),
 	gross_profit VARCHAR(50),
 	income_tax VARCHAR(50),
 	diluted_shares_outstanding VARCHAR(50)
);

--Alter the fin_stats table as gross_profit and income tax are out of order
ALTER TABLE fin_stats
RENAME income_tax TO net_income;

ALTER TABLE fin_stats
RENAME gross_profit TO income_tax;


-- Alter the fin_stats table to include a primary key
ALTER TABLE fin_stats
ADD CONSTRAINT fin_stats_pk
PRIMARY KEY (ticker, rpt_year);

-- Update the fin_stats table to change "-" values to 0
UPDATE fin_stats
SET revenue = '0'
WHERE revenue = '-';

-- Update the fin_stats table to change "-" values to 0
UPDATE fin_stats
SET gross_profit = '0'
WHERE gross_profit = '-';

-- Update the fin_stats table to change "-" values to 0
UPDATE fin_stats
SET income_tax = '0'
WHERE income_tax = '-';

-- Update the fin_stats table to change "-" values to 0
UPDATE fin_stats
SET diluted_shares_outstanding = '0'
WHERE diluted_shares_outstanding = '-';


-- Alter the fin_stats table to convert revenue string text to integer values
ALTER TABLE fin_stats
ALTER COLUMN revenue TYPE bigint
USING revenue::bigint;

-- Alter the fin_stats table to convert gross profit string text to integer values
ALTER TABLE fin_stats
ALTER COLUMN income_tax TYPE bigint
USING income_tax::bigint;

-- Alter the fin_stats table to convert gross profit string text to integer values
ALTER TABLE fin_stats
ALTER COLUMN net_income TYPE bigint
USING net_income::bigint;

ALTER TABLE fin_stats
ALTER COLUMN diluted_shares_outstanding TYPE decimal
USING diluted_shares_outstanding::decimal;


-- Alter the fin_stats table to include a foreign key in close_price
ALTER TABLE fin_stats
ADD CONSTRAINT fin_stats_fk
FOREIGN KEY (ticker, rpt_year)
REFERENCES fin_stats
ON DELETE CASCADE;

SELECT * FROM fin_stats;

-- Create a close_price table to hold the closing stock price for each company
-- This is needed to calculate the market capitalization for each company
DROP TABLE close_price;

CREATE TABLE close_price (
	id SERIAL,
	ticker VARCHAR(20),
	date_val DATE,
	year_val VARCHAR(25),
	open_val VARCHAR(25),
	high_val VARCHAR(25),
	low_val VARCHAR(25),
	close_val VARCHAR(25),
	volume VARCHAR(50)	
);

-- Alter the close_price table to include a primary key
ALTER TABLE close_price
ADD CONSTRAINT close_price_pk
PRIMARY KEY (ticker, year_val);

--Alter the close price table to change string values to integers
ALTER TABLE close_price
ALTER COLUMN close_val TYPE decimal
USING close_val::decimal;

SELECT * FROM close_price;


--Create a table to house the combined US stock address and industry data
DROP TABLE us_public_companies

CREATE TABLE us_public_companies (
	ticker VARCHAR(20) PRIMARY KEY,
	company VARCHAR(200),
	gics_sector VARCHAR(200),
	gics_sub_industry VARCHAR(200),
	cik VARCHAR(50),
	country VARCHAR(25),
	state_val VARCHAR(25),
	city VARCHAR(25),
	zipcode VARCHAR(25),
	lat decimal,
	lon decimal
);

SELECT * FROM us_public_companies
WHERE ticker = 'AIV';


-- Create a new table which brings the closing price into the fin stats table using a left join so the market cap can be calculated
DROP TABLE scaled_data_by_year;

CREATE TABLE scaled_data_by_year AS
SELECT fs.ticker,
	   fs.exchange,
	   fs.rpt_scale,
	   fs.rpt_year,
	   fs.revenue,
	   		CASE WHEN fs.rpt_scale LIKE '%USD Millions%' THEN fs.revenue * 1000000 
			WHEN fs.rpt_scale LIKE '%USD Thousands%' THEN fs.revenue * 1000
			ELSE fs.revenue
			END as revenue_scaled,
	   fs.income_tax,
	   		CASE WHEN fs.rpt_scale LIKE '%USD Millions%' THEN fs.income_tax * 1000000 
			WHEN fs.rpt_scale LIKE '%USD Thousands%' THEN fs.income_tax * 1000
			ELSE fs.income_tax
			END as income_tax_scaled,
	   fs.net_income,
	   		CASE WHEN fs.rpt_scale LIKE '%USD Millions%' THEN fs.net_income * 1000000 
			WHEN fs.rpt_scale LIKE '%USD Thousands%' THEN fs.net_income * 1000
			ELSE fs.net_income
			END as net_income_scaled,
	   fs.diluted_shares_outstanding,
	   		CASE WHEN fs.rpt_scale LIKE '%USD Millions%' THEN fs.diluted_shares_outstanding * 1000000 
			WHEN fs.rpt_scale LIKE '%USD Thousands%' THEN fs.diluted_shares_outstanding * 1000
			ELSE fs.diluted_shares_outstanding
			END as diluted_shares_outstanding_scaled,
	   cp.close_val,
	   cp.date_val
FROM fin_stats as fs
LEFT JOIN close_price as cp
ON fs.ticker = cp.ticker AND fs.rpt_year = cp.year_val
ORDER BY ticker, rpt_year


-- add a column and calculate the market cap
ALTER TABLE scaled_data_by_year
ADD COLUMN market_cap decimal

UPDATE scaled_data_by_year
SET market_cap = diluted_shares_outstanding * close_val;

--add a column and calculate the scaled market cap
ALTER TABLE scaled_data_by_year
ADD COLUMN market_cap_scaled decimal

UPDATE scaled_data_by_year
SET market_cap_scaled = diluted_shares_outstanding_scaled * close_val;

select * FROM scaled_data_by_year;

--Create a new table which joins the company state and location information to the financial data
CREATE TABLE combined_public_companies AS
SELECT sd.ticker,
	   sd.exchange,
	   pc.gics_sector AS sector,
	   pc.gics_sub_industry AS industry,
	   pc.state_val,
	   pc.city,
	   pc.lat,
	   pc.lon,
	   sd.rpt_year,
	   sd.revenue,
	   sd.revenue_scaled,
	   sd.income_tax,
	   sd.income_tax_scaled,
	   sd.net_income,
	   sd.net_income_scaled,
	   sd.diluted_shares_outstanding,
	   sd.diluted_shares_outstanding_scaled,
	   sd.close_val,
	   sd.date_val,
	   sd.market_cap,
	   sd.market_cap_scaled
FROM scaled_data_by_year AS sd
LEFT JOIN us_public_companies as pc
ON sd.ticker = pc.ticker
ORDER BY ticker, rpt_year

SELECT * FROM combined_public_companies;

--Create a join to bring median household income into combined public companies table
DROP VIEW combined_data_detail;

CREATE VIEW combined_data_detail AS
SELECT pc.ticker,
	   pc.exchange,
	   pc.sector,
	   pc.industry,
	   pc.state_val,
	   pc.city,
	   pc.lat,
	   pc.lon,
	   pc.rpt_year,
	   pc.revenue_scaled,
	   pc.income_tax_scaled,
	   pc.net_income_scaled,
	   ROUND(pc.market_cap_scaled,0) AS market_cap,
	   hhi.median_hh_income
FROM combined_public_companies as pc
LEFT JOIN median_hh_income_postal_code as hhi
ON pc.state_val = hhi.postal_abbreviation AND pc.rpt_year = hhi.year_val
ORDER BY ticker, rpt_year

SELECT * FROM combined_data_detail;
	   

--Create a view that groups financial information by state and year
DROP VIEW financials_by_state_year;

CREATE VIEW financials_by_state_year AS
SELECT pc.state_val,	
	   pc.rpt_year,
	SUM(pc.revenue_scaled) AS revenue,
	SUM(pc.income_tax_scaled) AS income_tax,
	ROUND(SUM(pc.market_cap_scaled),0) AS market_cap,
	ROUND(AVG(hi.median_hh_income),0) AS median_hh_income
FROM combined_public_companies AS pc
LEFT JOIN median_hh_income_postal_code as hi
ON pc.state_val = hi.postal_abbreviation AND pc.rpt_year = hi.year_val
WHERE pc.rpt_year != ' ' AND pc.state_val is not null
GROUP BY pc.state_val, pc.rpt_year
ORDER BY pc.state_val, pc.rpt_year;

SELECT * FROM financials_by_state_year;


--Create a view that groups financial information by state
DROP VIEW financials_by_state;

CREATE VIEW financials_by_state AS
SELECT pc.state_val,
	SUM(pc.revenue_scaled) AS revenue,
	SUM(pc.income_tax_scaled) AS income_tax,
	SUM(pc.market_cap_scaled) AS market_cap,
	ROUND(AVG(hi.median_hh_income),0) AS avg_median_hh_income
FROM combined_public_companies AS  pc
LEFT JOIN median_hh_income_postal_code as hi
ON pc.state_val = hi.postal_abbreviation
WHERE pc.state_val is not null
GROUP BY pc.state_val
ORDER BY state_val;

SELECT * FROM financials_by_state;



--Create a table to hold median household income by state
DROP TABLE median_inc_state;

CREATE TABLE median_inc_state (
	us_state VARCHAR(100),
	year_val VARCHAR(10),
	median_hh_income bigint
);

SELECT * FROM median_inc_state;


-- Update D.C. to District of Columbia
UPDATE median_inc_state
SET us_state = 'District of Columbia'
WHERE us_state = 'D.C.'

SELECT us_state, ROUND(AVG(median_hh_income),0) FROM median_inc_state
GROUP BY us_state
HAVING us_state = 'California'

	
	
-- Create a table to hold state abbreviations
DROP TABLE state_abbreviations;

CREATE TABLE state_abbreviations (
	state_val VARCHAR(50) PRIMARY KEY,
	state_abbreviation VARCHAR(50),
	postal_abbreviation VARCHAR(10)
)

SELECT * FROM state_abbreviations;

--join the postal abbreviation code to the median income by state table
DROP TABLE median_hh_income_postal_code;

CREATE TABLE median_hh_income_postal_code AS
SELECT sb.state_val, 
	   mi.year_val, 
	   mi.median_hh_income,
	   sb.postal_abbreviation
FROM median_inc_state as mi
LEFT JOIN state_abbreviations as sb
ON mi.us_state = sb.state_val;


SELECT * FROM median_hh_income_postal_code;
