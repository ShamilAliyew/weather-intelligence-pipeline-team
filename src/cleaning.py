import pandas as pd
import numpy as np
from database import get_connection


# ─────────────────────────────────────────────
# 1. handle_missing_values
# ─────────────────────────────────────────────

def handle_missing_values(df: pd.DataFrame, strategy: dict) -> pd.DataFrame:
    """
    Imputes or drops missing values based on a strategy dict.

    strategy format:
        {
            "temperature_2m_max":       "ffill",
            "temperature_2m_min":       "ffill",
            "apparent_temperature_max": "ffill",
            "apparent_temperature_min": "ffill",
            "precipitation_sum":        "zero",
            "rain_sum":                 "zero",
            "snowfall_sum":             "zero",
            "precipitation_hours":      "zero",
            "windspeed_10m_max":        "ffill",
            "windgusts_10m_max":        "ffill",
            "winddirection_10m_dominant": "ffill",
            "weathercode":              "ffill",
        }

    Supported strategies per column:
        "ffill"  — forward-fill (good for temperature / wind)
        "bfill"  — backward-fill
        "zero"   — fill with 0 (good for precipitation / snowfall)
        "mean"   — fill with column mean
        "median" — fill with column median
        "drop"   — drop rows where this column is null
    """
    df = df.copy()

    for column, method in strategy.items():
        if column not in df.columns:
            continue

        if method == "ffill":
            df[column] = df[column].ffill()

        elif method == "bfill":
            df[column] = df[column].bfill()

        elif method == "zero":
            df[column] = df[column].fillna(0)

        elif method == "mean":
            df[column] = df[column].fillna(df[column].mean())

        elif method == "median":
            df[column] = df[column].fillna(df[column].median())

        elif method == "drop":
            df = df.dropna(subset=[column])

        else:
            raise ValueError(f"Unknown strategy '{method}' for column '{column}'.")

    return df


# ─────────────────────────────────────────────
# 2. flag_outliers
# ─────────────────────────────────────────────

def flag_outliers(
    df: pd.DataFrame,
    columns: list,
    method: str = "iqr",
    threshold: float = 1.5,
) -> pd.DataFrame:
    """
    Adds a boolean flag column '<col>_outlier' for each column in `columns`.
    Does NOT remove any rows — removal is a modelling decision for later.

    method:
        "iqr"     — flag if value < Q1 - threshold*IQR  or  > Q3 + threshold*IQR
        "zscore"  — flag if |z-score| > threshold  (use threshold=3 for z-score)
    """
    df = df.copy()

    for col in columns:
        if col not in df.columns:
            print(f"  [flag_outliers] Column '{col}' not found — skipping.")
            continue

        flag_col = f"{col}_outlier"

        if method == "iqr":
            q1 = df[col].quantile(0.25)
            q3 = df[col].quantile(0.75)
            iqr = q3 - q1
            lower = q1 - threshold * iqr
            upper = q3 + threshold * iqr
            df[flag_col] = (df[col] < lower) | (df[col] > upper)

        elif method == "zscore":
            mean = df[col].mean()
            std  = df[col].std()
            if std == 0:
                df[flag_col] = False
            else:
                df[flag_col] = ((df[col] - mean) / std).abs() > threshold

        else:
            raise ValueError(f"Unknown method '{method}'. Use 'iqr' or 'zscore'.")

    return df


# ─────────────────────────────────────────────
# 3. validate_date_continuity
# ─────────────────────────────────────────────

def validate_date_continuity(df: pd.DataFrame, city: str) -> dict:
    """
    Checks for gaps in the daily date sequence for a given city.

    Returns a summary dict:
        {
            "city":           str,
            "start_date":     Timestamp,
            "end_date":       Timestamp,
            "expected_days":  int,
            "actual_days":    int,
            "missing_count":  int,
            "missing_dates":  List[Timestamp],
        }
    """
    city_df = df[df["city"] == city].copy()
    city_df["date"] = pd.to_datetime(city_df["date"])
    city_df = city_df.sort_values("date")

    if city_df.empty:
        return {
            "city": city,
            "start_date": None,
            "end_date": None,
            "expected_days": 0,
            "actual_days": 0,
            "missing_count": 0,
            "missing_dates": [],
        }

    start = city_df["date"].min()
    end   = city_df["date"].max()

    full_range     = pd.date_range(start=start, end=end, freq="D")
    actual_dates   = pd.DatetimeIndex(city_df["date"].unique())
    missing_dates  = full_range.difference(actual_dates)

    summary = {
        "city":          city,
        "start_date":    start,
        "end_date":      end,
        "expected_days": len(full_range),
        "actual_days":   len(actual_dates),
        "missing_count": len(missing_dates),
        "missing_dates": missing_dates.tolist(),
    }

    # ── pretty print ──
    print(f"\n{'─'*45}")
    print(f"  City            : {city}")
    print(f"  Date range      : {start.date()} → {end.date()}")
    print(f"  Expected days   : {summary['expected_days']}")
    print(f"  Actual days     : {summary['actual_days']}")
    print(f"  Missing days    : {summary['missing_count']}")
    if summary["missing_count"] > 0:
        print(f"  First 5 missing : {[str(d.date()) for d in missing_dates[:5]]}")
    print(f"{'─'*45}")

    return summary


# ─────────────────────────────────────────────
# Default cleaning strategy (matches config.py)
# ─────────────────────────────────────────────

DEFAULT_STRATEGY = {
    "weathercode":                "ffill",
    "temperature_2m_max":         "ffill",
    "temperature_2m_min":         "ffill",
    "apparent_temperature_max":   "ffill",
    "apparent_temperature_min":   "ffill",
    "precipitation_sum":          "zero",
    "precipitation_hours":        "zero",
    "rain_sum":                   "zero",
    "snowfall_sum":               "zero",
    "windspeed_10m_max":          "ffill",
    "windgusts_10m_max":          "ffill",
    "winddirection_10m_dominant": "ffill",
}

NUMERIC_COLUMNS = [
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
    "winddirection_10m_dominant",
]


# ─────────────────────────────────────────────
# 4. clean_raw_to_staging
# ─────────────────────────────────────────────

def _clean_single_table(conn, raw_table: str) -> pd.DataFrame:
    """
    Internal helper — cleans one raw table and returns the cleaned DataFrame.
    Steps: read → handle_missing_values → flag_outliers → validate_date_continuity
    """
    print(f"\n{'═'*50}")
    print(f"  Processing {raw_table} …")

    df = conn.execute(f"SELECT * FROM {raw_table}").df()
    print(f"  Rows loaded : {len(df):,}")

    # Step 1 : handle missing values
    print("  Handling missing values …")
    before_nulls = df[NUMERIC_COLUMNS].isnull().sum().sum()
    df = handle_missing_values(df, DEFAULT_STRATEGY)
    after_nulls  = df[NUMERIC_COLUMNS].isnull().sum().sum()
    print(f"  Nulls before: {before_nulls:,}  →  after: {after_nulls:,}")

    # Step 2 : flag outliers
    print("  Flagging outliers (IQR, threshold=1.5) …")
    df = flag_outliers(df, columns=NUMERIC_COLUMNS, method="iqr", threshold=1.5)
    flag_cols   = [c for c in df.columns if c.endswith("_outlier")]
    total_flags = df[flag_cols].sum().sum()
    print(f"  Total outlier flags: {total_flags:,}  across {len(flag_cols)} columns")

    # Step 3 : date continuity report per city
    print("  Validating date continuity …")
    for city in df["city"].unique().tolist():
        validate_date_continuity(df, city)

    return df


def clean_raw_to_staging(conn) -> None:
    """
    Full pipeline for BOTH raw tables:
        1. raw.weather_daily_historical  →  staging.weather_daily_historical
        2. raw.weather_daily_forecast    →  staging.weather_daily_forecast

    Each table goes through:
        - handle_missing_values  (DEFAULT_STRATEGY)
        - flag_outliers          (IQR, threshold=1.5)
        - validate_date_continuity (per city)

    Staging tables are dropped and recreated on every run so re-runs are safe.
    """

    tables = [
        ("raw.weather_daily_historical", "staging.weather_daily_historical"),
        ("raw.weather_daily_forecast",   "staging.weather_daily_forecast"),
    ]

    for raw_table, staging_table in tables:
        df = _clean_single_table(conn, raw_table)

        print(f"\n  Writing to {staging_table} …")
        conn.execute(f"DROP TABLE IF EXISTS {staging_table};")
        conn.register("temp_df", df)
        conn.execute(f"""CREATE TABLE {staging_table} AS SELECT * FROM temp_df""")

        row_count = conn.execute(f"SELECT COUNT(*) FROM {staging_table}").fetchone()[0]
        print(f"  Rows written: {row_count:,}")

    print("\n✓ clean_raw_to_staging completed successfully.")
