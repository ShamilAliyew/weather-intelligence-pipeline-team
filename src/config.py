
CITIES = [
    {"name": "Baku", "latitude": 40.41, "longitude": 49.87},
    {"name": "Ganja", "latitude": 40.69, "longitude": 46.36},
    {"name": "Shusha", "latitude": 39.75, "longitude": 46.75},
    {"name": "Nakhchivan", "latitude": 39.21, "longitude": 45.41}
]

# -----------------------------
# Date range
# -----------------------------
START_DATE = "2021-04-18"
END_DATE = "2026-04-18"

# -----------------------------
# API endpoints
# -----------------------------
ARCHIVE_URL = "https://archive-api.open-meteo.com/v1/archive"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# -----------------------------
# Weather variables
# -----------------------------
DAILY_VARIABLES = [
    "weathercode",
    "temperature_2m_max",
    "temperature_2m_min",
    "apparent_temperature_max",
    "apparent_temperature_min",
    "precipitation_sum",
    "precipitation_hours",
    "rain_sum",
    "snowfall_sum",
    "windspeed_10m_max",
    "windgusts_10m_max",
    "winddirection_10m_dominant"
]