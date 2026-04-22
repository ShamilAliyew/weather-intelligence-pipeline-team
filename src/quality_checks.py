import pandas as pd
from datetime import datetime


# =====================================================
# Helper: Standard result format
# =====================================================
def make_result(name, status, details):
    return {
        "check_name": name,
        "status": status,   # PASS / WARNING / FAIL
        "details": details
    }


# =====================================================
# 1. ROW COUNT (RAW STAGE) → CRITICAL
# =====================================================
def check_row_count(conn, table):
    count = conn.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]

    if count == 0:
        return make_result("row_count", "FAIL", f"{table} is empty")

    return make_result("row_count", "PASS", f"{table}: {count} rows")


# =====================================================
# 2. FRESHNESS (RAW STAGE)
# =====================================================
def check_freshness(conn, table):
    latest = conn.execute(f"SELECT MAX(date) FROM {table}").fetchone()[0]

    if latest is None:
        return make_result("freshness", "FAIL", f"{table}: no data")

    latest = pd.to_datetime(latest)
    delta = (datetime.today() - latest).days

    if delta <= 2:
        return make_result("freshness", "PASS", f"{table}: {delta} days old")

    return make_result("freshness", "WARNING", f"{table}: {delta} days old")


# =====================================================
# 3. NULL RATIO (STAGING STAGE)
# =====================================================
def check_null_ratio(conn, table, threshold=0.05):

    df = conn.execute(f"SELECT * FROM {table}").df()

    if len(df) == 0:
        return make_result("null_ratio", "FAIL", f"{table}: empty")

    issues = []

    for col in df.columns:
        ratio = df[col].isnull().mean()

        if ratio > threshold:
            issues.append(f"{col}: {ratio:.2%}")

    if issues:
        return make_result("null_ratio", "WARNING", issues)

    return make_result("null_ratio", "PASS", f"{table}: OK")


# =====================================================
# 4. DATE CONTINUITY (STAGING STAGE)
# =====================================================
def check_date_continuity(conn, table):

    df = conn.execute(f"SELECT city, date FROM {table}").df()

    if df.empty:
        return make_result("date_continuity", "FAIL", f"{table}: empty")

    df["date"] = pd.to_datetime(df["date"])

    issues = []

    for city in df["city"].unique():

        cdf = df[df["city"] == city].sort_values("date")

        full = pd.date_range(
            start=cdf["date"].min(),
            end=cdf["date"].max(),
            freq="D"
        )

        missing = full.difference(cdf["date"])

        if len(missing) > 3:
            issues.append(f"{city}: {len(missing)} missing days")

    if issues:
        return make_result("date_continuity", "WARNING", issues)

    return make_result("date_continuity", "PASS", f"{table}: OK")


# =====================================================
# 5. VALUE RANGE (STAGING STAGE)
# =====================================================
def check_temperature_range(conn, table):

    df = conn.execute(f"""
        SELECT city, date, temperature_2m_max, temperature_2m_min
        FROM {table}
    """).df()

    if df.empty:
        return make_result("temperature_range", "FAIL", f"{table}: empty")

    bad = df[
        (df["temperature_2m_max"] > 60) |
        (df["temperature_2m_max"] < -50) |
        (df["temperature_2m_min"] > 60) |
        (df["temperature_2m_min"] < -50)
    ]

    if not bad.empty:
        return make_result(
            "temperature_range",
            "WARNING",
            {
                "invalid_rows": len(bad),
                "sample": bad.head(5).to_dict("records")
            }
        )

    return make_result("temperature_range", "PASS", f"{table}: OK")


# =====================================================
# 6. FEATURE COMPLETENESS (ANALYTICS STAGE)
# =====================================================
def check_feature_completeness(conn, table, required_cols):

    df = conn.execute(f"SELECT * FROM {table}").df()

    if df.empty:
        return make_result("feature_completeness", "FAIL", f"{table}: empty")

    # missing columns
    missing = [c for c in required_cols if c not in df.columns]

    if missing:
        return make_result(
            "feature_completeness",
            "FAIL",
            f"{table}: missing columns {missing}"
        )

    # null columns
    null_cols = [c for c in required_cols if df[c].isnull().any()]

    if null_cols:
        return make_result(
            "feature_completeness",
            "WARNING",
            f"{table}: nulls in {null_cols}"
        )

    return make_result("feature_completeness", "PASS", f"{table}: OK")


# =====================================================
# MASTER FUNCTION
# =====================================================
def run_all_checks(conn):

    results = []

    # ================= RAW =================
    raw_tables = [
        "raw.weather_daily_historical",
        "raw.weather_daily_forecast"
    ]

    for table in raw_tables:

        rc = check_row_count(conn, table)
        results.append(rc)

        # ❗ CRITICAL FAIL → STOP PIPELINE
        if rc["status"] == "FAIL":
            raise RuntimeError(f"Pipeline aborted: {table} is empty")

        results.append(check_freshness(conn, table))

    # ================= STAGING =================
    staging_tables = [
        "staging.weather_daily_historical",
        "staging.weather_daily_forecast"
    ]

    for table in staging_tables:
        results.append(check_null_ratio(conn, table))
        results.append(check_date_continuity(conn, table))
        results.append(check_temperature_range(conn, table))

    # ================= ANALYTICS =================
    results.append(
        check_feature_completeness(
            conn,
            "analytics.weather_features_historical",
            [
                "temp_mean", "temp_range",
                "precip_7d_avg", "temp_7d_avg",
                "month", "season"
            ]
        )
    )

    results.append(
        check_feature_completeness(
            conn,
            "analytics.weather_features_forecast",
            [
                "temp_mean", "temp_range",
                "month", "season"
            ]
        )
    )

    return results