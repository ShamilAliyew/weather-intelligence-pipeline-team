import streamlit as st
import pandas as pd
import requests
import datetime
from pathlib import Path
import base64

# ── Page config ───────────────────────────────────────────────────
st.set_page_config(
    page_title="BuildSafeAI",
    page_icon="🏗",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── City registry ─────────────────────────────────────────────────
CITIES = {
    "Baku":       {"lat": 40.41, "lon": 49.87},
    "Ganja":      {"lat": 40.68, "lon": 46.36},
    "Shusha":     {"lat": 39.75, "lon": 46.75},
    "Nakhchivan": {"lat": 39.21, "lon": 45.41},
}
CITY_NAMES = list(CITIES.keys())

# ── Background image ──────────────────────────────────────────────
BG_PATH = Path(__file__).parent / "Font_Page.jpeg"
bg_b64 = ""
if BG_PATH.exists():
    with open(BG_PATH, "rb") as f:
        bg_b64 = base64.b64encode(f.read()).decode()

# ── CSV data ──────────────────────────────────────────────────────
CSV_PATH = Path(__file__).parent.parent / "data" / "predictions" / "risk_forecast.csv"

@st.cache_data
def load_forecast():
    try:
        df = pd.read_csv(CSV_PATH)
        df["date_str"] = df["date"].astype(str).str[:10]
        return df
    except Exception:
        return None

forecast_df = load_forecast()

# ── Weather API ───────────────────────────────────────────────────
@st.cache_data(ttl=300)
def fetch_weather(lat, lon):
    try:
        url = (
            f"https://api.open-meteo.com/v1/forecast"
            f"?latitude={lat}&longitude={lon}"
            "&current=temperature_2m,wind_speed_10m,relative_humidity_2m"
            "&wind_speed_unit=ms&timezone=auto"
        )
        r = requests.get(url, timeout=8)
        r.raise_for_status()
        cur = r.json().get("current", {})
        return {
            "wind":  round(cur.get("wind_speed_10m", 0)),
            "temp":  round(cur.get("temperature_2m", 0)),
            "humid": round(cur.get("relative_humidity_2m", 0)),
        }
    except Exception:
        return {"wind": 12, "temp": 18, "humid": 65}

# ── Helpers ───────────────────────────────────────────────────────
def risk_color(pct):
    if pct < 40:  return "#22c55e"
    if pct < 65:  return "#f97316"
    return "#ef4444"

def risk_emoji(pct):
    if pct > 75:  return "🔴", "High Risk"
    if pct > 45:  return "🟠", "Medium Risk"
    if pct > 30:  return "🟡", "Low Risk"
    return "🟢", "Safe"

def ordinal(n):
    if 11 <= n % 100 <= 13:
        return f"{n}th"
    return f"{n}" + {1:"st",2:"nd",3:"rd"}.get(n % 10, "th")

def generate_recommendations(row):
    if not row:
        return [{"icon": "✅", "bar_color": "#22c55e",
                 "title": "All systems nominal",
                 "desc": "No data available — proceed with standard protocols",
                 "conf": 97}]
    recs = []
    crane  = float(row.get("crane_pct",  0) or 0)
    freeze = float(row.get("freeze_pct", 0) or 0)
    heat   = float(row.get("heat_pct",   0) or 0)
    flood  = float(row.get("flood_pct",  0) or 0)
    if crane >= 50:
        recs.append({"icon": "⚠️", "bar_color": "#f97316",
                     "title": "Reschedule crane operations",
                     "desc": f"Wind load exceeds safe threshold — crane risk at {crane:.0f}%",
                     "conf": min(98, int(crane) + 38)})
    else:
        recs.append({"icon": "✅", "bar_color": "#22c55e",
                     "title": "Reschedule crane operations",
                     "desc": "Wind drops below 8 m/s threshold", "conf": 96})
    if flood >= 30:
        recs.append({"icon": "⚠️", "bar_color": "#f97316",
                     "title": "Delay excavation 48h",
                     "desc": f"Flood risk detected — soil saturation {flood:.0f}%", "conf": 91})
    else:
        recs.append({"icon": "✅", "bar_color": "#22c55e",
                     "title": "Delay excavation 48h",
                     "desc": f"Flood risk low — soil saturation at {flood:.0f}%, excavation safe", "conf": 90})
    if freeze < 35 and heat < 55:
        recs.append({"icon": "🟢", "bar_color": "#22c55e",
                     "title": "Safe coating day",
                     "desc": "Optimal humidity & temperature conditions", "conf": 89})
    else:
        recs.append({"icon": "⚠️", "bar_color": "#f97316",
                     "title": "Safe coating day",
                     "desc": f"Conditions non-ideal — freeze {freeze:.0f}% / heat {heat:.0f}%",
                     "conf": 82})
    if freeze >= 50:
        recs.append({"icon": "❄️", "bar_color": "#ef4444",
                     "title": "Optimal concrete pouring window",
                     "desc": f"Freezing risk at {freeze:.0f}% — delay pouring", "conf": min(99, int(freeze) + 30)})
    else:
        recs.append({"icon": "💧", "bar_color": "#3b82f6",
                     "title": "Optimal concrete pouring window",
                     "desc": f"No freezing risk — ideal curing conditions (freeze index {freeze:.0f}%)", "conf": 94})
    return recs[:4]

# ── Session state ─────────────────────────────────────────────────
if "city" not in st.session_state:
    st.session_state.city = "Baku"
if "sel_day" not in st.session_state:
    st.session_state.sel_day = 1

_qp_city = st.query_params.get("city", None)
_qp_day_param = st.query_params.get("day", None)

if _qp_city and _qp_city in CITIES and _qp_city != st.session_state.city:
    st.session_state.city = _qp_city
    st.session_state.sel_day = 1
    st.query_params.clear()
    st.rerun()
elif _qp_day_param and not _qp_city:
    try:
        _day_val = int(_qp_day_param)
        if _day_val != st.session_state.sel_day:
            st.session_state.sel_day = _day_val
            st.query_params.clear()
            st.rerun()
    except Exception:
        pass

city    = st.session_state.city
cfg     = CITIES[city]
weather = fetch_weather(cfg["lat"], cfg["lon"])
sel_day = st.session_state.sel_day

city_df = pd.DataFrame()
if forecast_df is not None:
    city_df = (forecast_df[forecast_df["city"] == city]
               .sort_values("day_number")
               .reset_index(drop=True))

sel_row = {}
if not city_df.empty:
    matches = city_df[city_df["day_number"] == sel_day]
    if not matches.empty:
        sel_row = matches.iloc[0].to_dict()

# ─────────────────────────────────────────────────────────────────
# CSS
# ─────────────────────────────────────────────────────────────────
st.markdown("""
<style>
            /* Ekrandaki "Deploy" ve profil düyməsini gizlədir */
[data-testid="stAppDeployButton"] {
  display: none !important;
}

/* Yuxarı sağdakı hamburger menyunu və adını gizlədir */
#MainMenu {
  display: none !important;
}

/* Aşağıdakı "Made with Streamlit" yazısını gizlədir */
footer {
  display: none !important;
}

/* Yuxarıdakı boşluq yaradan header zolağını tam silir */
header[data-testid="stHeader"] {
  display: none !important;
}
@import url('https://fonts.googleapis.com/css2?family=Sora:wght@300;400;500;600;700;800&family=DM+Sans:wght@300;400;500;600&display=swap');

*, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
html, body,
[data-testid="stAppViewContainer"],
[data-testid="stApp"] {
  background: #f1f5f9 !important;
  font-family: 'DM Sans', sans-serif !important;
  color: #0f172a !important;
}
[data-testid="stHeader"], [data-testid="stToolbar"],
footer, #MainMenu { display: none !important; }
.block-container { padding: 0 !important; max-width: 100% !important; }
[data-testid="column"] { padding: 0 !important; }

/* ── SIDEBAR ── */
section[data-testid="stSidebar"] {
  display: none !important;
}
section[data-testid="stSidebar"] > div:first-child {
  padding: 0 !important;
  background: #0f172a !important;
}
[data-testid="stSidebarContent"] {
  padding: 0 !important;
  background: #0f172a !important;
}
[data-testid="stSidebarUserContent"] {
  padding: 0 !important;
}
[data-testid="stSidebarUserContent"] > div { gap: 0 !important; }

/* hide the radio widget top-label */
[data-testid="stSidebarUserContent"] [data-testid="stWidgetLabel"] {
  display: none !important;
}
/* each radio row */
[data-testid="stSidebarUserContent"] [role="radiogroup"] {
  gap: 0 !important;
}
[data-testid="stSidebarUserContent"] [role="radiogroup"] label {
  display: flex !important;
  align-items: center !important;
  padding: 0.72rem 1.1rem !important;
  margin: 0 !important;
  border-radius: 0 !important;
  border-bottom: 1px solid rgba(255,255,255,0.06) !important;
  cursor: pointer !important;
  width: 100% !important;
  transition: background 0.13s !important;
}
[data-testid="stSidebarUserContent"] [role="radiogroup"] label:hover {
  background: rgba(255,255,255,0.07) !important;
}
/* hide the radio dot */
[data-testid="stSidebarUserContent"] [role="radiogroup"] label > div:first-child {
  display: none !important;
}
/* label text */
[data-testid="stSidebarUserContent"] [role="radiogroup"] label p {
  color: #94a3b8 !important;
  font-family: 'DM Sans', sans-serif !important;
  font-size: 0.82rem !important;
  font-weight: 600 !important;
  letter-spacing: 0.06em !important;
  margin: 0 !important;
}
/* selected row */
[data-testid="stSidebarUserContent"] [role="radiogroup"] label:has(input:checked) {
  background: rgba(59,130,246,0.15) !important;
  border-left: 3px solid #3b82f6 !important;
}
[data-testid="stSidebarUserContent"] [role="radiogroup"] label:has(input:checked) p {
  color: #fff !important;
}
[data-testid="stSidebarUserContent"] [role="radiogroup"] input {
  display: none !important;
}

/* ── CITY NAV ── */
.city-nav-html {
  position: absolute; top: 1.5rem; left: 50%;
  transform: translateX(-50%); z-index: 30;
  display: flex; gap: 0.5rem; align-items: center;
}
.cnav-pill {
  display: inline-block; font-family: 'DM Sans', sans-serif;
  font-size: 0.85rem; font-weight: 600; color: rgba(255,255,255,0.88);
  background: rgba(255,255,255,0.13); border: 1.5px solid rgba(255,255,255,0.28);
  border-radius: 50px; padding: 0.45rem 1.4rem;
  backdrop-filter: blur(18px); -webkit-backdrop-filter: blur(18px);
  white-space: nowrap; text-decoration: none; cursor: pointer;
  transition: all 0.18s ease; letter-spacing: 0.01em;
}
.cnav-pill:hover {
  background: rgba(255,255,255,0.22); border-color: rgba(255,255,255,0.55);
  color: #fff; transform: translateY(-2px);
  box-shadow: 0 6px 18px rgba(0,0,0,0.3); text-decoration: none;
}
.cnav-active {
  background: linear-gradient(135deg,#3b82f6 0%,#1d4ed8 100%) !important;
  border-color: transparent !important; color: #fff !important;
  font-weight: 700 !important; box-shadow: 0 4px 20px rgba(59,130,246,0.55) !important;
  transform: translateY(-2px);
}

/* ── HERO ── */
.hero-wrap {
  position: relative; width: 100%; height: 580px;
  border-radius: 0 0 28px 28px; overflow: hidden; background: #0f172a;
}
""" + f"""
.hero-bg {{
  position: absolute; inset: 0;
  background-image: url('data:image/jpeg;base64,{bg_b64}');
  background-size: cover; background-position: center 30%;
  filter: brightness(0.72);
}}
""" + """
.hero-overlay {
  position: absolute; inset: 0;
  background: linear-gradient(110deg,rgba(5,15,30,0.78) 0%,rgba(5,15,30,0.42) 50%,rgba(5,15,30,0.06) 100%);
}
.hero-content {
  position: relative; z-index: 10; height: 100%;
  padding: 2.2rem 3rem;
  display: flex; flex-direction: column; justify-content: center;
}
.status-badge {
  display: inline-flex; align-items: center; gap: 0.5rem;
  background: rgba(255,255,255,0.13); backdrop-filter: blur(10px);
  border: 1px solid rgba(255,255,255,0.22); border-radius: 30px;
  padding: 0.38rem 0.9rem; font-size: 0.74rem; font-weight: 500;
  color: #fff; width: fit-content; margin-bottom: 1.9rem; letter-spacing: 0.02em;
}
.status-dot {
  width: 7px; height: 7px; border-radius: 50%;
  background: #22c55e; box-shadow: 0 0 0 2px rgba(34,197,94,0.4);
  animation: pdot 2s infinite;
}
@keyframes pdot {
  0%,100% { box-shadow: 0 0 0 2px rgba(34,197,94,0.4); }
  50%      { box-shadow: 0 0 0 6px rgba(34,197,94,0.08); }
}
.hero-title {
  font-family: 'Sora', sans-serif; font-size: 4.2rem; font-weight: 800;
  color: #fff; line-height: 1.03; letter-spacing: -0.04em; margin-bottom: 1rem;
}
.hero-title .ai { color: #3b82f6; }
.hero-sub {
  font-size: 1.08rem; color: rgba(255,255,255,0.82);
  max-width: 400px; line-height: 1.58; margin-bottom: 2.2rem; font-weight: 400;
}
.hero-wx-panel {
  position: absolute; top: 2.2rem; right: 2.5rem; z-index: 20; width: 340px;
  background: rgba(10,20,40,0.76); backdrop-filter: blur(22px);
  border-radius: 22px; padding: 1.7rem 1.8rem 1.5rem;
  box-shadow: 0 20px 56px rgba(0,0,0,0.42); border: 1px solid rgba(255,255,255,0.13);
}
.hwx-city {
  font-family: 'Sora', sans-serif; font-size: 1.9rem; font-weight: 800;
  color: #fff; letter-spacing: -0.03em; line-height: 1.1; margin-bottom: 0.25rem;
}
.hwx-coords {
  font-size: 0.7rem; color: rgba(255,255,255,0.4); letter-spacing: 0.04em;
  margin-bottom: 1.2rem; padding-bottom: 1.1rem;
  border-bottom: 1px solid rgba(255,255,255,0.08);
}
.hwx-grid { display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 0.6rem; }
.hwx-item {
  background: rgba(255,255,255,0.07); border: 1px solid rgba(255,255,255,0.11);
  border-radius: 13px; padding: 0.85rem 0.4rem 0.75rem; text-align: center;
}
.hwx-label {
  font-size: 0.62rem; font-weight: 700; color: rgba(255,255,255,0.42);
  letter-spacing: 0.1em; text-transform: uppercase; display: block; margin-bottom: 0.35rem;
}
.hwx-val {
  font-family: 'Sora', sans-serif; font-size: 1.38rem; font-weight: 800;
  color: #f1f5f9; display: block; line-height: 1;
}

/* ── MAIN ── */
.main-wrap { padding: 0 2.5rem 3rem 2.5rem; max-width: 1480px; margin: 0 auto; }
.forecast-hero { padding: 2.2rem 0 0.5rem 0; }
.forecast-hero-date {
  font-family: 'Sora', sans-serif; font-size: 2.2rem; font-weight: 800;
  color: #0f172a; letter-spacing: -0.035em; line-height: 1.1;
}
.forecast-hero-sub { font-size: 0.85rem; color: #64748b; margin-top: 0.3rem; }

/* ── GAUGE ── */
.gauge-wrap {
  display: flex; align-items: center; gap: 2rem;
  background: rgba(255,255,255,0.72); backdrop-filter: blur(18px);
  border: 1px solid rgba(255,255,255,0.6); border-radius: 24px;
  padding: 1.8rem 2.2rem;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06); margin-bottom: 1.5rem;
}
.gauge-title {
  font-family: 'Sora', sans-serif; font-size: 1.2rem; font-weight: 700;
  color: #0f172a; margin-bottom: 0.3rem;
}
.gauge-desc { font-size: 0.82rem; color: #64748b; line-height: 1.55; margin-bottom: 1rem; }
.gauge-pill {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.4rem 1rem; border-radius: 30px; font-size: 0.8rem; font-weight: 700;
}

/* ── GLASS CARDS ── */
.glass-grid {
  display: grid; grid-template-columns: 1fr 1fr; gap: 1.2rem; margin-bottom: 1.5rem;
}
.glass-card {
  background: rgba(255,255,255,0.65); backdrop-filter: blur(22px);
  border: 1px solid rgba(255,255,255,0.7); border-radius: 22px;
  padding: 1.6rem 1.7rem;
  box-shadow: 0 4px 24px rgba(0,0,0,0.06); position: relative; overflow: hidden;
}
.gc-top { display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 1rem; }
.gc-icon { width: 50px; height: 50px; border-radius: 15px; display: flex; align-items: center; justify-content: center; font-size: 1.45rem; }
.gc-type { font-size: 0.63rem; font-weight: 700; letter-spacing: 0.16em; text-transform: uppercase; }
.gc-title { font-family:'Sora',sans-serif; font-size:1.05rem; font-weight:700; color:#0f172a; margin-bottom:0.18rem; }
.gc-sub { font-size:0.74rem; color:#94a3b8; margin-bottom:1rem; }
.gc-pct { font-family:'Sora',sans-serif; font-size:2.8rem; font-weight:800; color:#0f172a; line-height:1; margin-bottom:0.8rem; }
.gc-pct sup { font-size:1rem; font-weight:500; color:#64748b; vertical-align:super; }
.gc-bar-track { height:6px; background:rgba(0,0,0,0.06); border-radius:6px; overflow:hidden; }
.gc-bar-fill { height:100%; border-radius:6px; }

/* ── AI ENGINE ── */
.sec-head { margin: 0.8rem 0 1.2rem 0; }
.sec-title { font-family:'Sora',sans-serif; font-size:1.1rem; font-weight:700; color:#0f172a; }
.sec-sub { font-size:0.77rem; color:#64748b; margin-top:0.15rem; }
.ai-wrap {
  background: rgba(255,255,255,0.72); backdrop-filter: blur(22px);
  border: 1px solid rgba(255,255,255,0.7); border-radius: 24px; padding: 1.8rem 2rem;
  box-shadow: 0 4px 24px rgba(0,0,0,0.05);
}
.ai-head { display:flex; align-items:center; justify-content:space-between; margin-bottom:0.3rem; padding-bottom:1.4rem; border-bottom:1px solid rgba(0,0,0,0.05); }
.ai-title-grp { display:flex; align-items:center; gap:0.9rem; }
.ai-icon { width:50px; height:50px; border-radius:15px; background:linear-gradient(135deg,#3b82f6 0%,#1d4ed8 100%); display:flex; align-items:center; justify-content:center; font-size:1.4rem; box-shadow:0 4px 14px rgba(59,130,246,0.32); }
.ai-ttl { font-family:'Sora',sans-serif; font-size:1.2rem; font-weight:700; color:#0f172a; }
.ai-st { font-size:0.74rem; color:#94a3b8; margin-top:0.08rem; }
.ai-active { display:flex; align-items:center; gap:0.45rem; font-size:0.7rem; font-weight:700; color:#16a34a; letter-spacing:0.12em; }
.ai-adot { width:7px; height:7px; border-radius:50%; background:#22c55e; animation:pdot 2s infinite; }
.rec-row { display:flex; align-items:center; gap:1rem; padding:1.05rem 0; border-bottom:1px solid rgba(0,0,0,0.04); }
.rec-row:last-child { border-bottom:none; }
.rec-bar { width:3px; height:62px; border-radius:3px; flex-shrink:0; }
.rec-ico { width:40px; height:40px; border-radius:50%; display:flex; align-items:center; justify-content:center; font-size:1.05rem; flex-shrink:0; border:1.5px solid; }
.rec-body { flex:1; min-width:0; }
.rec-ttl { font-family:'Sora',sans-serif; font-size:0.95rem; font-weight:700; color:#0f172a; margin-bottom:0.18rem; }
.rec-dsc { font-size:0.74rem; color:#64748b; margin-bottom:0.48rem; }
.rec-cf-row { display:flex; align-items:center; gap:0.55rem; }
.rec-cf-track { width:120px; height:3px; background:#f1f5f9; border-radius:3px; overflow:hidden; }
.rec-cf-fill { height:100%; border-radius:3px; }
.rec-cf-txt { font-size:0.69rem; color:#64748b; }
.footer { padding:1rem 2.5rem 2rem; text-align:center; font-size:0.7rem; color:#cbd5e1; letter-spacing:0.04em; }

/* ── HORIZONTAL DATE PICKER ── */
.date-picker-wrap {
  padding: 1.4rem 2.5rem 0 2.5rem;
  max-width: 1480px;
  margin: 0 auto;
}
.date-picker-label {
  font-size: 0.68rem; font-weight: 700; color: #94a3b8;
  letter-spacing: 0.12em; text-transform: uppercase;
  margin-bottom: 0.5rem;
}

/* st.radio horizontal → pill görünüşü */
[data-testid="stRadio"] > label { display: none !important; }
[data-testid="stRadio"] [role="radiogroup"] {
  display: flex !important;
  flex-direction: row !important;
  flex-wrap: nowrap !important;
  gap: 0.5rem !important;
  overflow-x: auto !important;
  padding: 0.3rem 0.4rem 0.6rem 0 !important;
  scrollbar-width: thin !important;
}
[data-testid="stRadio"] [role="radiogroup"] label {
  flex-shrink: 0 !important;
  display: inline-flex !important;
  flex-direction: column !important;
  align-items: center !important;
  justify-content: center !important;
  min-width: 60px !important;
  padding: 0.5rem 0.85rem !important;
  border-radius: 14px !important;
  border: 1.5px solid rgba(0,0,0,0.08) !important;
  background: rgba(255,255,255,0.7) !important;
  backdrop-filter: blur(12px) !important;
  cursor: pointer !important;
  transition: all 0.15s ease !important;
  margin: 0 !important;
}
[data-testid="stRadio"] [role="radiogroup"] label:hover {
  background: rgba(59,130,246,0.08) !important;
  border-color: rgba(59,130,246,0.3) !important;
  transform: translateY(-2px) !important;
  box-shadow: 0 4px 14px rgba(59,130,246,0.12) !important;
}
[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) {
  background: linear-gradient(135deg,#3b82f6 0%,#1d4ed8 100%) !important;
  border-color: transparent !important;
  box-shadow: 0 4px 18px rgba(59,130,246,0.4) !important;
  transform: translateY(-2px) !important;
}
[data-testid="stRadio"] [role="radiogroup"] label > div:first-child { display: none !important; }
[data-testid="stRadio"] [role="radiogroup"] label p {
  font-family: 'Sora', sans-serif !important;
  font-size: 0.82rem !important;
  font-weight: 700 !important;
  color: #0f172a !important;
  margin: 0 !important;
  text-align: center !important;
  line-height: 1.3 !important;
}
[data-testid="stRadio"] [role="radiogroup"] label:has(input:checked) p { color: #fff !important; }
[data-testid="stRadio"] [role="radiogroup"] input { display: none !important; }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown(
        f'<div style="padding:1.2rem 1.1rem 0.9rem;border-bottom:1px solid rgba(255,255,255,0.08);margin-bottom:0;">'
        f'<div style="font-family:Sora,sans-serif;font-size:1.05rem;font-weight:800;color:#fff;">🏗 BuildSafe<span style="color:#3b82f6;">AI</span></div>'
        f'<div style="font-size:0.62rem;color:rgba(255,255,255,0.3);margin-top:0.2rem;letter-spacing:0.08em;text-transform:uppercase;">16-Day Forecast · {city}</div>'
        f'</div>',
        unsafe_allow_html=True,
    )

    if not city_df.empty:
        radio_labels, radio_days = [], []
        for _, drow in city_df.iterrows():
            day_n    = int(drow["day_number"])
            date_str = str(drow.get("date_str", drow.get("date", "")))[:10]
            try:
                d        = datetime.date.fromisoformat(date_str)
                lbl      = d.strftime("%b %d").upper()
            except Exception:
                lbl = f"Day {day_n}"
            radio_labels.append(lbl)
            radio_days.append(day_n)

        cur_idx = radio_days.index(st.session_state.sel_day) if st.session_state.sel_day in radio_days else 0
        chosen  = st.radio("sel", options=radio_labels, index=cur_idx, label_visibility="collapsed")
        chosen_day = radio_days[radio_labels.index(chosen)]
        if chosen_day != st.session_state.sel_day:
            st.session_state.sel_day = chosen_day
            st.rerun()
    else:
        st.markdown('<div style="padding:1rem;color:rgba(255,255,255,0.3);font-size:0.78rem;">No data.</div>', unsafe_allow_html=True)

# ── Re-derive after sidebar ───────────────────────────────────────
sel_day = st.session_state.sel_day
sel_row = {}
if not city_df.empty:
    m = city_df[city_df["day_number"] == sel_day]
    if not m.empty:
        sel_row = m.iloc[0].to_dict()

# ─────────────────────────────────────────────────────────────────
# HERO
# ─────────────────────────────────────────────────────────────────
_nav = '<div class="city-nav-html">'
for _c in CITY_NAMES:
    _cls = "cnav-active" if _c == city else ""
    _nav += f'<a class="cnav-pill {_cls}" href="?city={_c}">{_c}</a>'
_nav += '</div>'

st.markdown(
    '<div class="hero-wrap">'
    '<div class="hero-bg"></div>'
    '<div class="hero-overlay"></div>'
    + _nav +
    '<div class="hero-content">'
    '<div class="status-badge"><span class="status-dot"></span>System online</div>'
    '<div class="hero-title">BuildSafe<span class="ai">AI</span></div>'
    '<div class="hero-sub">AI-powered construction risk intelligence — predict,<br>prevent, and optimize every build day.</div>'
    '</div>'
    f'<div class="hero-wx-panel">'
    f'<div class="hwx-city">📍 {city}</div>'
    f'<div class="hwx-coords">{cfg["lat"]:.2f}°N &nbsp; {cfg["lon"]:.2f}°E</div>'
    f'<div class="hwx-grid">'
    f'<div class="hwx-item"><span class="hwx-label">🌡 Temp</span><span class="hwx-val">{weather["temp"]}°C</span></div>'
    f'<div class="hwx-item"><span class="hwx-label">≋ Wind</span><span class="hwx-val">{weather["wind"]}<small style="font-size:0.58rem;opacity:0.65"> m/s</small></span></div>'
    f'<div class="hwx-item"><span class="hwx-label">☁ Hum</span><span class="hwx-val">{weather["humid"]}<small style="font-size:0.58rem;opacity:0.65">%</small></span></div>'
    f'</div></div>'
    '</div>',
    unsafe_allow_html=True,
)

# ─────────────────────────────────────────────────────────────────
# MAIN DETAIL VIEW
# ─────────────────────────────────────────────────────────────────
crane_pct  = float(sel_row.get("crane_pct",  0) or 0)
freeze_pct = float(sel_row.get("freeze_pct", 0) or 0)
heat_pct   = float(sel_row.get("heat_pct",   0) or 0)
flood_pct  = float(sel_row.get("flood_pct",  0) or 0)
total_pct  = float(sel_row.get("total_risk_pct", 0) or 0)

_sel_ds = str(sel_row.get("date_str", sel_row.get("date", "")))[:10] if sel_row else ""
try:
    _dobj       = datetime.date.fromisoformat(_sel_ds)
    _hero_date  = _dobj.strftime(f"%B {ordinal(_dobj.day)}, %Y")
    _short_date = _dobj.strftime("%b %d, %Y")
except Exception:
    _hero_date  = f"Day {sel_day}"
    _short_date = f"Day {sel_day}"

_t_emoji, _t_lbl = risk_emoji(total_pct)
_t_color          = risk_color(total_pct)
_tpi              = int(total_pct)

# ─────────────────────────────────────────────────────────────────
# HORIZONTAL DATE PICKER  (main content üstündə)
# ─────────────────────────────────────────────────────────────────
# HORIZONTAL DATE PICKER — st.radio styled as pills (no page reload)
# ─────────────────────────────────────────────────────────────────
if not city_df.empty:
    _pill_labels = []
    _pill_days   = []
    _pill_dots   = []
    for _, drow in city_df.iterrows():
        day_n    = int(drow["day_number"])
        date_str = str(drow.get("date_str", drow.get("date", "")))[:10]
        try:
            d     = datetime.date.fromisoformat(date_str)
            month = d.strftime("%b").upper()
            lbl   = f"{month} {d.day}"
        except Exception:
            lbl = f"Day {day_n}"
        tr = float(drow.get("total_risk_pct", 0) or 0)
        _pill_labels.append(lbl)
        _pill_days.append(day_n)
        _pill_dots.append(risk_color(tr))

    # Pill header label
    st.markdown('<div class="date-picker-wrap"><div class="date-picker-label">📅 Select Forecast Date</div></div>', unsafe_allow_html=True)

    cur_idx = _pill_days.index(st.session_state.sel_day) if st.session_state.sel_day in _pill_days else 0
    _chosen_lbl = st.radio(
        "date_sel",
        options=_pill_labels,
        index=cur_idx,
        horizontal=True,
        label_visibility="collapsed",
    )
    _chosen_day = _pill_days[_pill_labels.index(_chosen_lbl)]
    if _chosen_day != st.session_state.sel_day:
        st.session_state.sel_day = _chosen_day
        st.rerun()

# Hero date heading
st.markdown(
    '<div class="main-wrap">'
    '<div class="forecast-hero">'
    f'<div class="forecast-hero-date">Forecast for {_hero_date}</div>'
    f'<div class="forecast-hero-sub">{_t_emoji} &nbsp;<strong style="color:{_t_color}">{_t_lbl} — {_tpi}%</strong> &nbsp;·&nbsp; {city} &nbsp;·&nbsp; Day {sel_day} of 16</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

# Gauge
_r   = 54
_c   = 2 * 3.14159 * _r
_sl  = (_c * min(total_pct, 100)) / 100
_sg  = _c - _sl

st.markdown(
    '<div class="main-wrap" style="padding-bottom:0;">'
    '<div class="gauge-wrap">'
    '<div style="flex-shrink:0;">'
    f'<svg width="140" height="140" viewBox="0 0 140 140" xmlns="http://www.w3.org/2000/svg">'
    f'<circle cx="70" cy="70" r="{_r}" fill="none" stroke="rgba(0,0,0,0.06)" stroke-width="11"/>'
    f'<circle cx="70" cy="70" r="{_r}" fill="none" stroke="{_t_color}" stroke-width="11" stroke-linecap="round" stroke-dasharray="{_sl:.2f} {_sg:.2f}" transform="rotate(-90 70 70)"/>'
    f'<text x="70" y="62" text-anchor="middle" font-family="Sora,sans-serif" font-size="26" font-weight="800" fill="#0f172a">{_tpi}</text>'
    f'<text x="70" y="78" text-anchor="middle" font-family="Sora,sans-serif" font-size="10" font-weight="500" fill="#64748b">%</text>'
    f'<text x="70" y="94" text-anchor="middle" font-family="DM Sans,sans-serif" font-size="7.5" font-weight="700" fill="#94a3b8" letter-spacing="1.5">RISK INDEX</text>'
    '</svg>'
    '</div>'
    '<div class="gauge-info">'
    '<div class="gauge-title">Total Construction Risk Index</div>'
    f'<div class="gauge-desc">Composite AI risk score for <strong>{_short_date}</strong> across crane operations, concrete freezing, heat stress, and excavation flooding.</div>'
    f'<div class="gauge-pill" style="background:{_t_color}18;color:{_t_color};border:1.5px solid {_t_color}40;">{_t_emoji} &nbsp; {_t_lbl} — {_tpi}% Composite Risk</div>'
    '</div>'
    '</div>'
    '</div>',
    unsafe_allow_html=True,
)

# 2x2 Glass cards
risk_data = [
    {"icon": "≋",  "icon_bg": "#fff7ed", "icon_color": "#f97316", "type_lbl": "WIND", "type_color": "#f97316", "title": "Crane Operation",     "sub": "Wind load on tower crane",   "pct": crane_pct},
    {"icon": "❄",  "icon_bg": "#eff6ff", "icon_color": "#3b82f6", "type_lbl": "COLD", "type_color": "#3b82f6", "title": "Concrete Freezing",   "sub": "Curing risk overnight",       "pct": freeze_pct},
    {"icon": "🔆", "icon_bg": "#f0fdf4", "icon_color": "#16a34a", "type_lbl": "HEAT", "type_color": "#16a34a", "title": "Heat Stress (HSE)",   "sub": "Worker exposure index",       "pct": heat_pct},
    {"icon": "💧", "icon_bg": "#fef2f2", "icon_color": "#ef4444", "type_lbl": "RAIN", "type_color": "#ef4444", "title": "Excavation Flooding", "sub": "Soil saturation forecast",    "pct": flood_pct},
]
gh = '<div class="main-wrap" style="padding-top:1.2rem;padding-bottom:0;"><div class="glass-grid">'
for c in risk_data:
    bc   = risk_color(c["pct"])
    bw   = min(100, c["pct"])
    gh  += (
        '<div class="glass-card">'
        f'<div style="position:absolute;top:-40%;right:-20%;width:180px;height:180px;border-radius:50%;background:{c["icon_color"]};opacity:0.05;pointer-events:none;"></div>'
        '<div class="gc-top">'
        f'<div class="gc-icon" style="background:{c["icon_bg"]};color:{c["icon_color"]}">{c["icon"]}</div>'
        f'<div class="gc-type" style="color:{c["type_color"]}">{c["type_lbl"]}</div>'
        '</div>'
        f'<div class="gc-title">{c["title"]}</div>'
        f'<div class="gc-sub">{c["sub"]}</div>'
        f'<div class="gc-pct">{c["pct"]:.0f}<sup>%</sup></div>'
        '<div class="gc-bar-track">'
        f'<div class="gc-bar-fill" style="width:{bw:.1f}%;background:{bc};"></div>'
        '</div>'
        '</div>'
    )
gh += '</div></div>'
st.markdown(gh, unsafe_allow_html=True)

# AI Recommendations
recs = generate_recommendations(sel_row)
ah   = (
    '<div class="main-wrap" style="padding-top:1.4rem;">'
    '<div class="sec-head"><div class="sec-title">AI Recommendation Engine</div>'
    '<div class="sec-sub">Live model · updated 2 min ago</div></div>'
    '<div class="ai-wrap">'
    '<div class="ai-head">'
    '<div class="ai-title-grp">'
    '<div class="ai-icon">✦</div>'
    '<div><div class="ai-ttl">Action Items for This Day</div>'
    '<div class="ai-st">Based on composite risk forecast</div></div>'
    '</div>'
    '<div class="ai-active"><div class="ai-adot"></div>ACTIVE</div>'
    '</div>'
)
for rec in recs:
    cw  = min(100, int(rec["conf"] * 1.18))
    bc  = rec["bar_color"]
    ah += (
        '<div class="rec-row">'
        f'<div class="rec-bar" style="background:{bc}"></div>'
        f'<div class="rec-ico" style="border-color:{bc}28;background:{bc}14;color:{bc}">{rec["icon"]}</div>'
        '<div class="rec-body">'
        f'<div class="rec-ttl">{rec["title"]}</div>'
        f'<div class="rec-dsc">{rec["desc"]}</div>'
        '<div class="rec-cf-row">'
        f'<div class="rec-cf-track"><div class="rec-cf-fill" style="width:{cw}%;background:{bc}"></div></div>'
        f'<span class="rec-cf-txt">Confidence {rec["conf"]}%</span>'
        '</div></div></div>'
    )
ah += '</div></div>'
st.markdown(ah, unsafe_allow_html=True)

# Footer
st.markdown(
    f'<div class="footer">BuildSafeAI · {city} · {cfg["lat"]:.2f}°N {cfg["lon"]:.2f}°E · Data: Open-Meteo + ML Risk Forecast</div>',
    unsafe_allow_html=True,
)
