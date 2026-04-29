import pandas as pd
import time
import openmeteo_requests

from config import ARCHIVE_URL, FORECAST_URL  

client = openmeteo_requests.Client()


# -----------------------------
# Retry helper
# -----------------------------
def retry_request(func, retries=5, delay=2):
    for attempt in range(retries):
        try:
            return func()

        except Exception as e:
            error_msg = str(e).lower()

            # 🔴 RATE LIMIT xüsusi handle
            if "limit exceeded" in error_msg:
                wait_time = 60
                print(f"⚠️ Rate limit hit. Waiting {wait_time}s...")
                time.sleep(wait_time)

            else:
                wait_time = delay * (2 ** attempt)
                print(f"⚠️ Retry {attempt+1}/{retries} in {wait_time}s...")

                time.sleep(wait_time)

            if attempt == retries - 1:
                raise RuntimeError(f"❌ API failed after {retries} retries: {e}")


# -----------------------------
# Historical data
# -----------------------------
def fetch_historical(city_name, latitude, longitude,
                     start_date, end_date, variables):

    start = pd.to_datetime(start_date).date()
    end = pd.to_datetime(end_date).date()
    today = pd.Timestamp.today().date()
    max_allowed = today - pd.Timedelta(days=1)


    # Validation
    if start >= end:
        raise ValueError("start_date must be earlier than end_date")

    if end > max_allowed:
        print(f"⚠️ end_date adjusted from {end} to {max_allowed}")
        end = max_allowed

    def _request():
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": str(start),
            "end_date": str(end),
            "daily": variables,
            "timezone": "auto"
        }

        responses = client.weather_api(ARCHIVE_URL, params=params)

        if not responses:
            raise ValueError("Empty API response")

        response = responses[0]
        daily = response.Daily()

        if daily is None:
            raise ValueError("Malformed response")

        values = daily.Variables(0).ValuesAsNumpy()

        if values is None or len(values) == 0:
            raise ValueError("Empty dataset returned")

        n = len(values)

        dates = pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s"),
            periods=n,
            freq="D"
        )

        data = {"date": dates, "city": city_name}

        for i, var in enumerate(variables):
            data[var] = daily.Variables(i).ValuesAsNumpy()

        return pd.DataFrame(data)

    return retry_request(_request)


# -----------------------------
# Forecast data (16 days)
# -----------------------------
def fetch_forecast(city_name, latitude, longitude, variables):

    def _request():
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "daily": variables,
            "forecast_days": 16,
            "timezone": "auto"
        }

        responses = client.weather_api(FORECAST_URL, params=params)

        if not responses:
            raise ValueError("Empty API response")

        response = responses[0]
        daily = response.Daily()

        if daily is None:
            raise ValueError("Malformed forecast response")

        values = daily.Variables(0).ValuesAsNumpy()

        if values is None or len(values) == 0:
            raise ValueError("Empty forecast data")

        n = len(values)

        dates = pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s"),
            periods=n,
            freq="D"
        )

        data = {"date": dates, "city": city_name}

        for i, var in enumerate(variables):
            data[var] = daily.Variables(i).ValuesAsNumpy()

        return pd.DataFrame(data)

    return retry_request(_request)


# -----------------------------
# All cities ingestion
# -----------------------------
def fetch_all_cities(cities_config, start_date, end_date, variables):

    all_data = {}

    for i, city in enumerate(cities_config):
        name = city["name"]

        print(f"Fetching → {name}")

        df = fetch_historical(
            city_name=name,
            latitude=city["latitude"],
            longitude=city["longitude"],
            start_date=start_date,
            end_date=end_date,
            variables=variables
        )

        all_data[name] = df
        print(f"{name}: {df.shape[0]} rows")

        # :fire: dynamic sleep
        if i < len(cities_config) - 1:
            time.sleep(2)

    return all_data