import duckdb



def create_base_features_historical(conn):

    conn.execute("""
    CREATE OR REPLACE TABLE analytics.weather_features_historical AS

    WITH base AS (
        SELECT
            *,
            (temperature_2m_max + temperature_2m_min)/2 AS temp_mean,
            (temperature_2m_max - temperature_2m_min) AS temp_range
        FROM staging.weather_daily_historical
    )

    SELECT
        *,
        
        AVG(precipitation_sum) OVER (
            PARTITION BY city ORDER BY DATE(date)
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS precip_7d_avg,

        AVG(precipitation_sum) OVER (
            PARTITION BY city ORDER BY DATE(date)
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS precip_30d_avg,

        LAG(precipitation_sum, 1) OVER (PARTITION BY city ORDER BY DATE(date)) AS precip_lag_1,
        LAG(precipitation_sum, 2) OVER (PARTITION BY city ORDER BY DATE(date)) AS precip_lag_2,

        AVG(temp_mean) OVER (
            PARTITION BY city ORDER BY DATE(date)
            ROWS BETWEEN 6 PRECEDING AND CURRENT ROW
        ) AS temp_7d_avg,

        AVG(temp_mean) OVER (
            PARTITION BY city ORDER BY DATE(date)
            ROWS BETWEEN 29 PRECEDING AND CURRENT ROW
        ) AS temp_30d_avg,

        LAG(temp_mean, 1) OVER (PARTITION BY city ORDER BY DATE(date)) AS temp_lag_1,
        LAG(temp_mean, 2) OVER (PARTITION BY city ORDER BY DATE(date)) AS temp_lag_2,

        EXTRACT(MONTH FROM date) AS month,
        EXTRACT(QUARTER FROM date) AS quarter,
        EXTRACT(DOY FROM date) AS day_of_year,

        CASE
            WHEN EXTRACT(MONTH FROM date) IN (12,1,2) THEN 'winter'
            WHEN EXTRACT(MONTH FROM date) IN (3,4,5) THEN 'spring'
            WHEN EXTRACT(MONTH FROM date) IN (6,7,8) THEN 'summer'
            ELSE 'autumn'
        END AS season,

        GREATEST(0, 18 - temp_mean) AS HDD,
        GREATEST(0, temp_mean - 18) AS CDD

    FROM base;
    """)




def create_forecast_features(conn):

    conn.execute("""
    CREATE OR REPLACE TABLE analytics.weather_features_forecast AS

    SELECT
        *,
        (temperature_2m_max + temperature_2m_min)/2 AS temp_mean,
        (temperature_2m_max - temperature_2m_min) AS temp_range,

        EXTRACT(MONTH FROM date) AS month,
        EXTRACT(QUARTER FROM date) AS quarter,
        EXTRACT(DOY FROM date) AS day_of_year,

        CASE
            WHEN EXTRACT(MONTH FROM date) IN (12,1,2) THEN 'winter'
            WHEN EXTRACT(MONTH FROM date) IN (3,4,5) THEN 'spring'
            WHEN EXTRACT(MONTH FROM date) IN (6,7,8) THEN 'summer'
            ELSE 'autumn'
        END AS season

    FROM staging.weather_daily_forecast;
    """)