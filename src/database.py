import duckdb
import os


def get_connection(db_path="weather.duckdb"):
    """
    Creates or connects to a DuckDB database file.
    """
    conn = duckdb.connect(db_path)
    return conn



def create_schemas(conn):
    """
    Creates raw, staging, and analytics schemas.
    """

    conn.execute("CREATE SCHEMA IF NOT EXISTS raw;")
    conn.execute("CREATE SCHEMA IF NOT EXISTS staging;")
    conn.execute("CREATE SCHEMA IF NOT EXISTS analytics;")



def create_raw_tables(conn):
    """
    Creates separate raw tables for historical and forecast data.
    """

    # 🔹 HISTORICAL TABLE
    conn.execute("""
    CREATE TABLE IF NOT EXISTS raw.weather_daily_historical (
        date TIMESTAMP,
        city VARCHAR,
        weathercode DOUBLE,
        temperature_2m_max DOUBLE,
        temperature_2m_min DOUBLE,
        apparent_temperature_max DOUBLE,
        apparent_temperature_min DOUBLE,
        precipitation_sum DOUBLE,
        precipitation_hours DOUBLE,
        rain_sum DOUBLE,
        snowfall_sum DOUBLE,
        windspeed_10m_max DOUBLE,
        windgusts_10m_max DOUBLE,
        winddirection_10m_dominant DOUBLE
    );
    """)

    # 🔹 FORECAST TABLE
    conn.execute("""
    CREATE TABLE IF NOT EXISTS raw.weather_daily_forecast (
        date TIMESTAMP,
        city VARCHAR,
        weathercode DOUBLE,
        temperature_2m_max DOUBLE,
        temperature_2m_min DOUBLE,
        apparent_temperature_max DOUBLE,
        apparent_temperature_min DOUBLE,
        precipitation_sum DOUBLE,
        precipitation_hours DOUBLE,
        rain_sum DOUBLE,
        snowfall_sum DOUBLE,
        windspeed_10m_max DOUBLE,
        windgusts_10m_max DOUBLE,
        winddirection_10m_dominant DOUBLE
    );
    """)



import os

def load_raw_historical_data(conn, data_dir):

    for file in os.listdir(data_dir):

        file_path = os.path.join(data_dir, file)

        # 🔹 skip empty files
        if os.path.getsize(file_path) == 0:
            print(f"Skipping empty file: {file}")
            continue

        # 🔥 ONLY HISTORICAL FILES
        if "_historical" not in file:
            continue

        try:

            if file.endswith(".parquet"):
                print(f"Loading Historical Parquet: {file}")

                conn.execute(f"""
                    INSERT INTO raw.weather_daily_historical
                    SELECT * FROM read_parquet('{file_path}');
                """)

            elif file.endswith(".csv"):
                print(f"Loading Historical CSV: {file}")

                conn.execute(f"""
                    INSERT INTO raw.weather_daily_historical
                    SELECT * FROM read_csv_auto('{file_path}');
                """)

            else:
                print(f"Skipping unsupported file: {file}")

        except Exception as e:
            print(f"Error loading historical file {file}: {e}")


def load_raw_forecast_data(conn, data_dir):

    for file in os.listdir(data_dir):

        file_path = os.path.join(data_dir, file) 

        # 🔹 skip empty files
        if os.path.getsize(file_path) == 0:
            print(f"Skipping empty file: {file}")
            continue

        #  ONLY FORECAST FILES
        if "_forecast" not in file:
            continue

        try:

            if file.endswith(".parquet"):
                print(f"Loading Forecast Parquet: {file}")

                conn.execute(f"""
                    INSERT INTO raw.weather_daily_forecast
                    SELECT * FROM read_parquet('{file_path}');
                """)

            elif file.endswith(".csv"):
                print(f"Loading Forecast CSV: {file}")

                conn.execute(f"""
                    INSERT INTO raw.weather_daily_forecast
                    SELECT * FROM read_csv_auto('{file_path}');
                """)

            else:
                print(f"Skipping unsupported file: {file}")

        except Exception as e:
            print(f"Error loading forecast file {file}: {e}")