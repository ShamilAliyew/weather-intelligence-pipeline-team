import argparse
import logging
from config import CITIES, START_DATE, END_DATE, DAILY_VARIABLES

import pandas as pd
from datetime import datetime, timedelta

from ingestion import fetch_all_cities, fetch_forecast

import os, sys


from database import (
    get_connection,
    create_schemas,
    create_raw_tables,
    load_raw_historical_data,
    load_raw_forecast_data
)

from cleaning import clean_raw_to_staging
from features import (
    create_base_features_historical,
    create_forecast_features
)


# ─────────────────────────────
# FULL PIPELINE
# ─────────────────────────────
def run_full_pipeline(conn, logger):

    start_time = datetime.now()
    logger.info("PIPELINE STARTED (FULL MODE)")

    # 1. DB setup
    create_schemas(conn)
    create_raw_tables(conn)

    conn.execute("DELETE FROM raw.weather_daily_historical")
    conn.execute("DELETE FROM raw.weather_daily_forecast")
    # 2. INGESTION
    historical_data = fetch_all_cities(
        cities_config=CITIES,
        start_date=START_DATE,
        end_date=END_DATE,
        variables=DAILY_VARIABLES
    )

    forecast_data = {
        city["name"]: fetch_forecast(
            city_name=city["name"],
            latitude=city["latitude"],
            longitude=city["longitude"],
            variables=DAILY_VARIABLES
        )
        for city in CITIES
    }

    logger.info("Data fetched")

    # 3. SAVE FILES
    for city, df in historical_data.items():
        df.to_csv(f"data/raw/{city}_historical.csv", index=False)

    for city, df in forecast_data.items():
        df.to_csv(f"data/raw/{city}_forecast.csv", index=False)

    # 4. LOAD RAW
    load_raw_historical_data(conn, "data/raw")
    load_raw_forecast_data(conn, "data/raw")

    logger.info("Raw loaded into DuckDB")

    # 5. STAGING
    clean_raw_to_staging(conn)
    logger.info("Staging completed")

    # 6. FEATURES
    create_base_features_historical(conn)
    create_forecast_features(conn)

    logger.info("Feature engineering completed")

    # 7. SUMMARY
    summary = {
        "historical_rows": conn.execute("SELECT COUNT(*) FROM raw.weather_daily_historical").fetchone()[0],
        "forecast_rows": conn.execute("SELECT COUNT(*) FROM raw.weather_daily_forecast").fetchone()[0],
        "staging_hist_rows": conn.execute("SELECT COUNT(*) FROM staging.weather_daily_historical").fetchone()[0],
        "staging_forecast_rows": conn.execute("SELECT COUNT(*) FROM staging.weather_daily_forecast").fetchone()[0],
        "analytics_hist_rows": conn.execute("SELECT COUNT(*) FROM analytics.weather_features_historical").fetchone()[0],
        "analytics_forecast_rows": conn.execute("SELECT COUNT(*) FROM analytics.weather_features_forecast").fetchone()[0],
        "duration": str(datetime.now() - start_time)
    }

    logger.info(f"SUMMARY: {summary}")

    return summary




# ─────────────────────────────
# HELPERS
# ─────────────────────────────
def get_last_dates_by_city(conn, table_name):
    query = f"""
        SELECT city, MAX(date) as last_date
        FROM {table_name}
        GROUP BY city
    """
    result = conn.execute(query).fetchall()
    return {row[0]: row[1] for row in result}


def window_start(date, days=30):
    return (pd.to_datetime(date) - pd.Timedelta(days=days)).date()


# ─────────────────────────────
# INCREMENTAL PIPELINE
# ─────────────────────────────
def run_incremental_pipeline(conn, logger):

    logger.info("INCREMENTAL PIPELINE STARTED")

    # 1. last dates
    last_dates = get_last_dates_by_city(conn, "raw.weather_daily_historical")

    if not last_dates:
        raise ValueError("No historical data found in raw table")

    rows_added_total = 0
    affected_cities = []
    skipped_cities = []

    # ─────────────────────────────
    # 2. FETCH + INSERT (DEDUP SAFE)
    # ─────────────────────────────
    for city in CITIES:

        name = city["name"]
        city_last = last_dates.get(name)

        if city_last is None:
            skipped_cities.append(name)
            continue

        start_date = (pd.to_datetime(city_last) + timedelta(days=1)).date()
        end_date = datetime.today().date()

        if start_date >= end_date:
            skipped_cities.append(name)
            continue

        df = fetch_all_cities(
            cities_config=[city],
            start_date=str(start_date),
            end_date=str(end_date),
            variables=DAILY_VARIABLES
        )[name]

        if df.empty:
            continue

        # CRITICAL: remove duplicates BEFORE insert
        conn.register("tmp_city", df)

        conn.execute("""
            INSERT INTO raw.weather_daily_historical
            SELECT *
            FROM tmp_city t
            WHERE NOT EXISTS (
                SELECT 1
                FROM raw.weather_daily_historical r
                WHERE r.city = t.city
                AND r.date = t.date
            )
        """)

        rows_added_total += len(df)
        affected_cities.append(name)

        logger.info(f"{name}: +{len(df)} rows")

    # ─────────────────────────────
    # 3. FORECAST (FULL REFRESH OK)
    # ─────────────────────────────
    forecast_dfs = []

    for city in CITIES:
        df = fetch_forecast(
            city_name=city["name"],
            latitude=city["latitude"],
            longitude=city["longitude"],
            variables=DAILY_VARIABLES
        )
        forecast_dfs.append(df)

    forecast_df = pd.concat(forecast_dfs, ignore_index=True)

    conn.execute("DELETE FROM raw.weather_daily_forecast")
    conn.register("tmp_forecast", forecast_df)

    conn.execute("""
        INSERT INTO raw.weather_daily_forecast
        SELECT * FROM tmp_forecast
    """)

    # ─────────────────────────────
    # 4. STAGING (WINDOWED REBUILD)
    # ─────────────────────────────
    logger.info("Updating staging (windowed)")

    for city in affected_cities:

        last_date = last_dates[city]
        start_window = window_start(last_date, 30)

        conn.execute(f"""
            DELETE FROM staging.weather_daily_historical
            WHERE city = '{city}'
            AND date >= '{start_window}'
        """)

    # safer (simple version → full rebuild)
    clean_raw_to_staging(conn)

    # ─────────────────────────────
    # 5. FEATURES (WINDOW SAFE)
    # ─────────────────────────────
    logger.info("Updating features")

    create_base_features_historical(conn)
    create_forecast_features(conn)

    # ─────────────────────────────
    # 6. SUMMARY
    # ─────────────────────────────
    summary = {
        "mode": "incremental",
        "rows_added_raw": rows_added_total,
        "affected_cities": affected_cities,
        "skipped_cities": skipped_cities,
        "raw_hist_total": conn.execute(
            "SELECT COUNT(*) FROM raw.weather_daily_historical"
        ).fetchone()[0],
        "raw_forecast_total": conn.execute(
            "SELECT COUNT(*) FROM raw.weather_daily_forecast"
        ).fetchone()[0],
        "staging_hist": conn.execute(
            "SELECT COUNT(*) FROM staging.weather_daily_historical"
        ).fetchone()[0],
        "analytics_hist": conn.execute(
            "SELECT COUNT(*) FROM analytics.weather_features_historical"
        ).fetchone()[0],
        "analytics_forecast": conn.execute(
            "SELECT COUNT(*) FROM analytics.weather_features_forecast"
        ).fetchone()[0],
        "timestamp": str(datetime.now())
    }

    logger.info(f"INCREMENTAL SUMMARY: {summary}")

    return summary


from logging_utils import setup_logger

if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="Weather Pipeline")

    parser.add_argument(
        "--mode",
        type=str,
        required=True,
        choices=["full", "incremental"],
        help="Pipeline mode: full or incremental"
    )

    args = parser.parse_args()

    sys.path.append(os.path.abspath("../src")) 
    db_path = "../data/database/weather_daily.duckdb"
    os.makedirs(os.path.dirname(db_path), exist_ok=True)


    # DB connection
    conn = get_connection(db_path)

    # Logger (əgər varsa)
    logger = setup_logger()

    try:
        if args.mode == "full":
            result = run_full_pipeline(conn, logger)

        elif args.mode == "incremental":
            result = run_incremental_pipeline(conn, logger)

        print("\n Pipeline completed successfully")
        print(result)
        conn.close()
    except Exception as e:
        logger.error(f"Pipeline failed: {str(e)}", exc_info=True)
        print(" Pipeline failed:", e)