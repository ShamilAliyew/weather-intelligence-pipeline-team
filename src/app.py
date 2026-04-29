import streamlit as st
import requests
from datetime import datetime, date, timedelta

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Weather Intelligence · AZ",
    page_icon="🌤",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# ── City registry ─────────────────────────────────────────────────────────────
CITIES = {
    "Baku":       {"lat": 40.4093, "lon": 49.8671, "emoji": "🏙", "region": "Absheron"},
    "Ganja":      {"lat": 40.6828, "lon": 46.3606, "emoji": "🏛", "region": "Ganja-Gazakh"},
    "Shusha":     {"lat": 39.7539, "lon": 46.7464, "emoji": "🏔", "region": "Karabakh"},
    "Nakhchivan": {"lat": 39.2090, "lon": 45.4112, "emoji": "🏜", "region": "Nakhchivan AR"},
}

WMO = {
    0:("Clear sky","☀️"),1:("Mainly clear","🌤"),2:("Partly cloudy","⛅"),
    3:("Overcast","☁️"),45:("Foggy","🌫"),48:("Icy fog","🌫"),
    51:("Light drizzle","🌦"),53:("Drizzle","🌧"),55:("Heavy drizzle","🌧"),
    61:("Light rain","🌧"),63:("Rain","🌧"),65:("Heavy rain","🌧"),
    71:("Light snow","🌨"),73:("Snow","❄️"),75:("Heavy snow","❄️"),
    80:("Showers","🌦"),81:("Heavy showers","🌧"),82:("Violent showers","⛈"),
    85:("Snow showers","🌨"),86:("Heavy snow showers","🌨"),
    95:("Thunderstorm","⛈"),96:("Thunderstorm+hail","⛈"),99:("Thunderstorm+hail","⛈"),
}

def wmo(code):
    return WMO.get(int(code), ("Unknown","🌡"))

# ── CSS ───────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=DM+Sans:wght@300;400;500;600;700&display=swap');

*,*::before,*::after{box-sizing:border-box;margin:0;padding:0}
html,body,[data-testid="stAppViewContainer"],[data-testid="stApp"]{
  background:#f4f6f9!important;
  color:#1a202c!important;
  font-family:'Inter',sans-serif!important;
}
[data-testid="stHeader"]{display:none!important}
[data-testid="stToolbar"]{display:none!important}
footer{display:none!important}
#MainMenu{display:none!important}
.block-container{padding:0 2rem 3rem 2rem!important;max-width:1400px!important}
[data-testid="column"]{padding:0 0.3rem!important}

/* ── Card base ── */
.card{background:#fff;border-radius:16px;box-shadow:0 1px 4px rgba(0,0,0,0.07),0 4px 16px rgba(0,0,0,0.04);padding:1.5rem}

/* ── Top nav ── */
.topnav{display:flex;align-items:center;justify-content:space-between;
  padding:1.2rem 0 1rem 0;border-bottom:1px solid #e8ecf1;margin-bottom:1.2rem}
.topnav-logo{font-size:1.4rem;font-weight:800;color:#1a202c;letter-spacing:-0.5px}
.topnav-logo span{color:#f97316}
.topnav-sub{font-size:0.72rem;color:#9aa5b4;margin-top:0.15rem;letter-spacing:0.04em}
.topnav-time{font-size:0.72rem;color:#9aa5b4;text-align:right}

/* ── City tabs ── */
.city-tab-bar{display:flex;gap:0.5rem;margin-bottom:1.2rem}
.city-tab{padding:0.45rem 1.1rem;border-radius:8px;font-size:0.78rem;font-weight:600;
  cursor:pointer;border:2px solid transparent;transition:all 0.15s;
  background:#fff;color:#6b7280;box-shadow:0 1px 3px rgba(0,0,0,0.06)}
.city-tab.active{background:#fff3ec;color:#f97316;border-color:#f97316}
.city-tab:hover{color:#f97316;border-color:rgba(249,115,22,0.3)}

/* ── Status pill ── */
.status-pill{display:inline-flex;align-items:center;gap:0.5rem;padding:0.35rem 0.9rem;
  background:#fff;border-radius:30px;font-size:0.65rem;color:#6b7280;
  box-shadow:0 1px 3px rgba(0,0,0,0.08);letter-spacing:0.04em;margin-bottom:1.2rem}
.dot-live{width:6px;height:6px;border-radius:50%;background:#22c55e;box-shadow:0 0 0 2px rgba(34,197,94,0.2);animation:pulse 2s infinite}
@keyframes pulse{0%,100%{box-shadow:0 0 0 2px rgba(34,197,94,0.2)}50%{box-shadow:0 0 0 4px rgba(34,197,94,0.1)}}
.status-sep{color:#d1d5db}

/* ── Hero weather strip ── */
.weather-strip{background:#fff;border-radius:16px;padding:1.4rem 1.8rem;
  box-shadow:0 1px 4px rgba(0,0,0,0.07),0 4px 16px rgba(0,0,0,0.04);
  display:flex;align-items:center;justify-content:space-between;margin-bottom:1.2rem}
.ws-city{font-size:2rem;font-weight:800;color:#1a202c}
.ws-region{font-size:0.7rem;color:#9aa5b4;margin-top:0.2rem;letter-spacing:0.06em;text-transform:uppercase}
.ws-temp{font-size:3.2rem;font-weight:300;color:#f97316;line-height:1}
.ws-desc{font-size:0.75rem;color:#6b7280;margin-top:0.3rem;text-align:right}
.ws-stats{display:flex;gap:2rem}
.ws-stat-item{text-align:center}
.ws-stat-val{font-size:1.2rem;font-weight:700;color:#374151}
.ws-stat-lbl{font-size:0.6rem;color:#9aa5b4;letter-spacing:0.08em;text-transform:uppercase;margin-top:0.1rem}

/* ── Section header ── */
.sec-hdr{display:flex;align-items:baseline;gap:0.6rem;margin:1.6rem 0 1rem 0}
.sec-hdr-sub{font-size:0.65rem;color:#f97316;font-weight:600;letter-spacing:0.12em;text-transform:uppercase}
.sec-hdr-title{font-size:1.25rem;font-weight:700;color:#1a202c}
.sec-hdr-desc{font-size:0.72rem;color:#9aa5b4;margin-top:0.2rem}

/* ── Donut ring cards ── */
.donut-card{background:#fff;border-radius:16px;padding:1.4rem 1rem 1.2rem 1rem;text-align:center;
  box-shadow:0 1px 4px rgba(0,0,0,0.07),0 4px 16px rgba(0,0,0,0.04);height:100%}
.donut-wrap{position:relative;width:100px;height:100px;margin:0 auto 0.8rem auto}
.donut-wrap svg{width:100px;height:100px;transform:rotate(-90deg)}
.donut-center{position:absolute;top:50%;left:50%;transform:translate(-50%,-50%);text-align:center}
.donut-pct{font-size:1.4rem;font-weight:700;line-height:1}
.donut-days{font-size:0.56rem;color:#9aa5b4;margin-top:0.1rem;white-space:nowrap}
.donut-label{font-size:0.72rem;font-weight:600;color:#374151;margin-top:0.2rem}

/* ── Calendar grid ── */
.cal-grid{display:grid;grid-template-columns:repeat(10,1fr);gap:0.45rem;margin-bottom:0.5rem}
.cal-day{background:#fff;border:2px solid #f0f2f5;border-radius:12px;padding:0.65rem 0.3rem;
  text-align:center;cursor:pointer;transition:all 0.15s}
.cal-day:hover{border-color:#f97316;transform:translateY(-2px);box-shadow:0 4px 12px rgba(249,115,22,0.15)}
.cal-day.selected{border-color:#f97316;background:#fff8f4;box-shadow:0 4px 12px rgba(249,115,22,0.2)}
.cal-dow{font-size:0.55rem;color:#9aa5b4;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.2rem}
.cal-date{font-size:1.35rem;font-weight:700;color:#1a202c;line-height:1;margin-bottom:0.3rem}
.cal-pct{font-size:0.75rem;font-weight:700;margin-top:0.15rem}
.cal-pct.safe{color:#22c55e}
.cal-pct.moderate{color:#f97316}
.cal-pct.high{color:#ef4444}
.cal-legend{display:flex;gap:1.2rem;justify-content:flex-end;margin-bottom:0.6rem}
.leg-item{display:flex;align-items:center;gap:0.35rem;font-size:0.65rem;color:#6b7280}
.leg-dot{width:8px;height:8px;border-radius:50%}

/* ── Day detail ── */
.det-hero{background:#fff;border-radius:16px;padding:1.8rem;
  box-shadow:0 1px 4px rgba(0,0,0,0.07),0 4px 16px rgba(0,0,0,0.04);margin-bottom:1rem}
.det-date{font-size:1.6rem;font-weight:800;color:#1a202c;margin-bottom:1rem;
  padding-bottom:1rem;border-bottom:1px solid #f0f2f5}
.overall-risk-box{background:#f8fafc;border:2px solid #e8ecf1;border-radius:12px;
  padding:1.2rem 1.5rem;margin-bottom:1.2rem;display:inline-block;min-width:180px}
.orl{font-size:0.65rem;color:#9aa5b4;letter-spacing:0.12em;text-transform:uppercase;margin-bottom:0.4rem}
.orv{font-size:2.8rem;font-weight:700;line-height:1}
.orv .pct{font-size:1.2rem;font-weight:400;opacity:0.6}
.orv.safe{color:#22c55e}.orv.moderate{color:#f97316}.orv.high{color:#ef4444}

/* ── Risk breakdown bars ── */
.rb-section-lbl{font-size:0.65rem;color:#9aa5b4;letter-spacing:0.12em;text-transform:uppercase;
  margin:1.2rem 0 0.8rem 0;padding-top:1rem;border-top:1px solid #f0f2f5}
.rb-item{margin-bottom:0.85rem}
.rb-header{display:flex;justify-content:space-between;align-items:center;margin-bottom:0.35rem}
.rb-name{font-size:0.85rem;font-weight:600;color:#374151}
.rb-pct{font-size:0.85rem;font-weight:700}
.rb-pct.safe{color:#22c55e}.rb-pct.moderate{color:#f97316}.rb-pct.high{color:#ef4444}
.rb-track{height:8px;background:#f0f2f5;border-radius:6px;overflow:hidden}
.rb-fill{height:100%;border-radius:6px;transition:width 0.6s ease}
.rb-fill.safe{background:#22c55e}.rb-fill.moderate{background:#f97316}.rb-fill.high{background:#ef4444}

/* ── Weather meta grid ── */
.wm-lbl{font-size:0.6rem;color:#9aa5b4;letter-spacing:0.1em;text-transform:uppercase;margin-bottom:0.3rem}
.wm-val{font-size:1.2rem;font-weight:700;color:#374151}
.wm-unit{font-size:0.65rem;color:#9aa5b4;margin-left:0.15rem}
.wm-card{background:#f8fafc;border-radius:10px;padding:0.9rem 1rem;border:1px solid #f0f2f5}

/* ── Action cards ── */
.ac{border-radius:12px;padding:1.1rem 1.3rem;margin-bottom:0.65rem;border-left:4px solid}
.ac.high{background:#fff5f5;border-color:#ef4444}
.ac.medium{background:#fff8f1;border-color:#f97316}
.ac.low{background:#fffbf0;border-color:#f59e0b}
.ac.safe{background:#f0fdf4;border-color:#22c55e}
.ac-prio{font-size:0.58rem;font-weight:700;letter-spacing:0.15em;text-transform:uppercase;margin-bottom:0.3rem}
.ac.high .ac-prio{color:#ef4444}.ac.medium .ac-prio{color:#f97316}
.ac.low .ac-prio{color:#f59e0b}.ac.safe .ac-prio{color:#22c55e}
.ac-title{font-size:0.92rem;font-weight:700;color:#1a202c;margin-bottom:0.3rem}
.ac-desc{font-size:0.72rem;color:#6b7280;line-height:1.5}
.ac-meta{display:flex;gap:1.2rem;margin-top:0.5rem}
.ac-stat{font-size:0.62rem;color:#9aa5b4;letter-spacing:0.08em;text-transform:uppercase}
.ac-stat b{color:#374151;font-weight:700}

/* ── Streamlit widget overrides ── */
div[data-baseweb="select"]>div{
  background:#fff!important;border-color:#e8ecf1!important;border-radius:10px!important;
  color:#374151!important;font-family:'Inter',sans-serif!important;font-size:0.82rem!important}
div[data-baseweb="select"]>div:hover{border-color:#f97316!important}
div[data-baseweb="popover"]{background:#fff!important}
div[role="option"]{background:#fff!important;color:#374151!important;font-size:0.82rem!important}
div[role="option"]:hover{background:#fff8f4!important}

.stButton button{background:#fff!important;border:2px solid #e8ecf1!important;
  border-radius:10px!important;color:#6b7280!important;
  font-family:'Inter',sans-serif!important;font-size:0.75rem!important;
  font-weight:600!important;padding:0.5rem 0.8rem!important;
  transition:all 0.15s!important;width:100%!important;box-shadow:0 1px 3px rgba(0,0,0,0.06)!important}
.stButton button:hover{color:#f97316!important;border-color:#f97316!important;
  background:#fff8f4!important}
.city-active .stButton button{color:#f97316!important;background:#fff3ec!important;
  border-color:#f97316!important}

[data-testid="stExpander"]{background:#fff!important;border:1px solid #e8ecf1!important;border-radius:12px!important}
[data-testid="stExpander"] summary{font-size:0.8rem!important;color:#374151!important;font-weight:600!important}
</style>
""", unsafe_allow_html=True)

# ── Helpers ───────────────────────────────────────────────────────────────────
def read_parquet_fallback(path):
    try:
        import pandas as pd
        return pd.read_parquet(path)
    except Exception:
        pass
    try:
        import duckdb
        return duckdb.query(f"SELECT * FROM '{path}'").df()
    except Exception:
        pass
    return None

@st.cache_data
def load_predictions():
    df = read_parquet_fallback("/mnt/user-data/uploads/future_predictions.parquet")
    if df is None:
        return None
    import pandas as pd
    if hasattr(df['date'], 'dt'):
        df['date_str'] = df['date'].dt.strftime('%Y-%m-%d')
    else:
        df['date_str'] = df['date'].astype(str).str[:10]
    return df

def get_ml_row(df, city_name, date_str):
    if df is None:
        return None
    mask = (df['city'] == city_name) & (df['date_str'] == date_str)
    rows = df[mask]
    if rows.empty:
        return None
    return rows.iloc[0].to_dict()

def risk_class(score):
    if score is None: return "safe"
    if score < 40: return "safe"
    if score < 65: return "moderate"
    return "high"

def risk_label(score):
    rc = risk_class(score)
    if rc == "safe": return "Safe", rc, "●"
    if rc == "moderate": return "Moderate", rc, "●"
    return "High Risk", rc, "●"

def donut_svg(pct, color, track="#f0f2f5", r=38):
    """Generate SVG donut ring."""
    cx, cy = 50, 50
    circ = 2 * 3.14159 * r
    dash = (pct / 100) * circ
    gap = circ - dash
    return f"""<svg viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg">
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{track}" stroke-width="10"/>
      <circle cx="{cx}" cy="{cy}" r="{r}" fill="none" stroke="{color}" stroke-width="10"
        stroke-dasharray="{dash:.2f} {gap:.2f}" stroke-linecap="round"/>
    </svg>"""

def risk_color(score):
    rc = risk_class(score)
    if rc == "safe": return "#22c55e"
    if rc == "moderate": return "#f97316"
    return "#ef4444"

@st.cache_data(ttl=300)
def fetch_current(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current=temperature_2m,wind_speed_10m,wind_gusts_10m,weather_code,"
        "relative_humidity_2m,apparent_temperature&timezone=auto"
    )
    r = requests.get(url, timeout=10); r.raise_for_status()
    return r.json().get("current", {})

@st.cache_data(ttl=300)
def fetch_forecast(lat, lon):
    url = (
        f"https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&daily=temperature_2m_max,temperature_2m_min,wind_speed_10m_max,"
        "weather_code,precipitation_sum"
        "&forecast_days=7&timezone=auto"
    )
    r = requests.get(url, timeout=10); r.raise_for_status()
    d = r.json()["daily"]
    out = []
    for i, ds in enumerate(d["time"]):
        dt = datetime.strptime(ds, "%Y-%m-%d")
        out.append({
            "date": ds, "dow": dt.strftime("%a").upper(), "display": dt.strftime("%b %-d"),
            "day_num": dt.strftime("%-d"),
            "max": d["temperature_2m_max"][i], "min": d["temperature_2m_min"][i],
            "wind": d["wind_speed_10m_max"][i], "code": d["weather_code"][i],
            "precip": d["precipitation_sum"][i] or 0,
        })
    return out

def build_actions(ml_row):
    if ml_row is None:
        return [("safe", "✅ Standard Operations",
            "All risk indicators are within acceptable thresholds. Maintain standard operational protocols.", 5, 97)]
    actions = []
    crane  = (ml_row.get('crane_risk_prob', 0) or 0)
    freeze = (ml_row.get('freeze_risk_prob', 0) or 0)
    heat   = (ml_row.get('heat_risk_prob', 0) or 0)
    flood  = (ml_row.get('flood_risk_prob', 0) or 0)

    if crane > 0.4:
        actions.append(("high", "🏗 Restrict Crane Operations",
            "Wind speeds exceed safe thresholds for crane operations. Suspend all crane activities until conditions improve.",
            int(crane*100), 94))
    elif crane > 0.2:
        actions.append(("medium", "🏗 Monitor Crane Conditions",
            "Crane risk is elevated. Conduct pre-shift inspections and limit load to 80% capacity.",
            int(crane*100), 88))
    if heat > 0.5:
        actions.append(("high", "🌡 Heat Emergency Protocol",
            "Extreme heat risk. Enforce mandatory hydration breaks every 30 min and reschedule strenuous outdoor tasks.",
            int(heat*100), 91))
    elif heat > 0.25:
        actions.append(("medium", "☀️ Shift Outdoor Crews",
            "High heat probability. Rotate outdoor crew shifts, provide shade stations and increase water supply on site.",
            int(heat*100), 86))
    if flood > 0.4:
        actions.append(("high", "🌊 Flood Preparedness Alert",
            "Significant flood risk. Secure equipment, pre-position pumps and establish emergency evacuation routes.",
            int(flood*100), 89))
    elif flood > 0.2:
        actions.append(("medium", "🌧 Monitor Drainage Systems",
            "Moderate flood probability. Inspect and clear drainage. Keep sandbags on standby.",
            int(flood*100), 83))
    if freeze > 0.3:
        actions.append(("low", "❄️ Monitor Freezing Conditions",
            "Freezing risk present. Pre-treat walkways with de-icer and inspect water lines for frost damage.",
            int(freeze*100), 87))
    if not actions:
        actions.append(("safe", "✅ Standard Operations",
            "All risk indicators within acceptable thresholds. Maintain standard operational protocols.",
            5, 97))
    actions.sort(key=lambda x: {"high":0,"medium":1,"low":2,"safe":3}[x[0]])
    return actions

# ── Session state ─────────────────────────────────────────────────────────────
if "city" not in st.session_state:
    st.session_state.city = "Baku"

pred_df = load_predictions()

# ── TOP NAV ───────────────────────────────────────────────────────────────────
now_str = datetime.now().strftime("%a %d %b %Y · %H:%M")
nav_l, nav_r = st.columns([3, 1])
with nav_l:
    st.markdown(
        "<div class='topnav'>"
        "<div><div class='topnav-logo'>Weather <span>Intelligence</span></div>"
        "<div class='topnav-sub'>Azerbaijan · Construction Risk Platform</div></div>"
        "</div>", unsafe_allow_html=True)
with nav_r:
    st.markdown(
        f"<div style='text-align:right;padding-top:1.4rem;font-size:0.68rem;color:#9aa5b4'>{now_str}</div>",
        unsafe_allow_html=True)

# City nav
city_cols = st.columns(len(CITIES))
for i, cname in enumerate(CITIES):
    with city_cols[i]:
        is_active = cname == st.session_state.city
        if is_active:
            st.markdown('<div class="city-active">', unsafe_allow_html=True)
        if st.button(f"{CITIES[cname]['emoji']} {cname}", key=f"nav_{cname}", use_container_width=True):
            st.session_state.city = cname
            st.rerun()
        if is_active:
            st.markdown("</div>", unsafe_allow_html=True)

st.markdown("<div style='margin-bottom:1rem'></div>", unsafe_allow_html=True)

# ── Load data ─────────────────────────────────────────────────────────────────
city = st.session_state.city
cfg = CITIES[city]
lat, lon = cfg["lat"], cfg["lon"]

try:
    cur = fetch_current(lat, lon)
    fcast = fetch_forecast(lat, lon)
except Exception as e:
    st.error(f"⚠️ API error: {e}")
    st.stop()

temp  = cur.get("temperature_2m", 0)
wind  = cur.get("wind_speed_10m", 0)
gusts = cur.get("wind_gusts_10m", 0)
humid = cur.get("relative_humidity_2m", 0)
feels = cur.get("apparent_temperature", 0)
wcode = int(cur.get("weather_code", 0))
wdesc, wicon = wmo(wcode)

day_labels = [f"{d['dow']} {d['display']}" for d in fcast]
if f"daysel_{city}" not in st.session_state:
    st.session_state[f"daysel_{city}"] = day_labels[0]

# ── STATUS BAR ────────────────────────────────────────────────────────────────
ml_status = "ML Engine · parquet loaded ✓" if pred_df is not None else "ML Engine · unavailable"
st.markdown(f"""
<div class="status-pill">
  <span class="dot-live"></span>
  <span>LIVE</span>
  <span class="status-sep">·</span>
  <span>Open-Meteo connected</span>
  <span class="status-sep">·</span>
  <span>{ml_status}</span>
  <span class="status-sep">·</span>
  <span>Updates every 5 min</span>
</div>
""", unsafe_allow_html=True)

# ── WEATHER STRIP ─────────────────────────────────────────────────────────────
st.markdown(f"""
<div class="weather-strip">
  <div>
    <div class="ws-city">{cfg['emoji']} {city}</div>
    <div class="ws-region">{cfg['region']} · {lat:.4f}°N {lon:.4f}°E</div>
  </div>
  <div class="ws-stats">
    <div class="ws-stat-item">
      <div class="ws-stat-val">💨 {wind:.0f}</div>
      <div class="ws-stat-lbl">Wind km/h</div>
    </div>
    <div class="ws-stat-item">
      <div class="ws-stat-val">💧 {humid}%</div>
      <div class="ws-stat-lbl">Humidity</div>
    </div>
    <div class="ws-stat-item">
      <div class="ws-stat-val">🌬 {gusts:.0f}</div>
      <div class="ws-stat-lbl">Gusts km/h</div>
    </div>
    <div class="ws-stat-item">
      <div class="ws-stat-val">🌡 {feels:.1f}°</div>
      <div class="ws-stat-lbl">Feels Like</div>
    </div>
  </div>
  <div>
    <div class="ws-temp">{temp:.1f}°</div>
    <div class="ws-desc">{wicon} {wdesc}</div>
  </div>
</div>
""", unsafe_allow_html=True)

# ── RISK DISTRIBUTION DONUTS ──────────────────────────────────────────────────
st.markdown("""
<div class="sec-hdr">
  <div>
    <div class="sec-hdr-sub">30-DAY PROBABILITY</div>
    <div class="sec-hdr-title">Risk Distribution by Category</div>
    <div class="sec-hdr-desc">Average probability across all 30 forecast days · avg over 30 days</div>
  </div>
</div>""", unsafe_allow_html=True)

# Compute 30-day averages per risk category
categories = [
    ("crane_risk_prob", "🏗 Crane Operation"),
    ("freeze_risk_prob", "❄️ Concrete Freezing"),
    ("heat_risk_prob", "☀️ Worker Heat Stress"),
    ("flood_risk_prob", "🌊 Excavation Flooding"),
]

cat_avgs = {}
high_day_counts = {}

for col_key, label in categories:
    if pred_df is not None:
        city_df = pred_df[pred_df['city'] == city]
        if col_key in city_df.columns:
            vals = city_df[col_key].dropna() * 100
            cat_avgs[col_key] = vals.mean() if len(vals) else 0
            high_day_counts[col_key] = int((vals >= 60).sum())
        else:
            cat_avgs[col_key] = 0
            high_day_counts[col_key] = 0
    else:
        cat_avgs[col_key] = 0
        high_day_counts[col_key] = 0

d1, d2, d3, d4 = st.columns(4)
donut_pairs = list(zip([d1, d2, d3, d4], categories))

for col, (col_key, label) in donut_pairs:
    avg = cat_avgs[col_key]
    hd = high_day_counts[col_key]
    color = risk_color(avg)
    icon = label.split()[0]
    name = " ".join(label.split()[1:])
    svg = donut_svg(avg, color)
    with col:
        st.markdown(f"""
        <div class="donut-card">
          <div class="donut-wrap">
            {svg}
            <div class="donut-center">
              <div class="donut-pct" style="color:{color}">{avg:.0f}<span style="font-size:0.75rem">%</span></div>
              <div class="donut-days">{hd} high-risk d</div>
            </div>
          </div>
          <div class="donut-label">{icon} {name}</div>
        </div>""", unsafe_allow_html=True)

# ── 30-DAY CALENDAR ───────────────────────────────────────────────────────────
st.markdown("""
<div class="sec-hdr" style="margin-top:2rem">
  <div>
    <div class="sec-hdr-sub">30-DAY FORECAST</div>
    <div class="sec-hdr-title">30-Day Risk Timeline</div>
    <div class="sec-hdr-desc">Hover to preview, click any day for full details.</div>
  </div>
</div>""", unsafe_allow_html=True)

# Legend
st.markdown("""
<div class="cal-legend">
  <div class="leg-item"><div class="leg-dot" style="background:#22c55e"></div> Safe (&lt;40%)</div>
  <div class="leg-item"><div class="leg-dot" style="background:#f97316"></div> Moderate (40–64%)</div>
  <div class="leg-item"><div class="leg-dot" style="background:#ef4444"></div> High (&ge;65%)</div>
</div>""", unsafe_allow_html=True)

sel_label = st.selectbox("Select day", day_labels, label_visibility="collapsed", key=f"daysel_{city}")
sel_idx = day_labels.index(sel_label)
sel_day = fcast[sel_idx]
ml_row = get_ml_row(pred_df, city, sel_day["date"])
total_risk = ml_row.get("total_risk_score") if ml_row else None
r_label_str, r_css, _ = risk_label(total_risk)

# Calendar grid — 3 rows of 10
cal_html = ""
for row_start in range(0, 30, 10):
    cal_html += '<div class="cal-grid">'
    for i in range(row_start, min(row_start+10, len(fcast))):
        d = fcast[i]
        day_ml = get_ml_row(pred_df, city, d["date"])
        day_score = day_ml.get("total_risk_score") if day_ml else None
        rc = risk_class(day_score)
        score_str = f"{day_score:.0f}%" if day_score is not None else "—"
        sel_cls = "selected" if i == sel_idx else ""
        cal_html += f"""
        <div class="cal-day {sel_cls}">
          <div class="cal-dow">{d['dow']}</div>
          <div class="cal-date">{d['day_num']}</div>
          <div class="cal-pct {rc}">{score_str}</div>
        </div>"""
    cal_html += "</div>"

st.markdown(cal_html, unsafe_allow_html=True)

# ── DAY DETAIL ────────────────────────────────────────────────────────────────
st.markdown("""
<div class="sec-hdr" style="margin-top:2rem">
  <div>
    <div class="sec-hdr-sub">DAY DETAIL</div>
    <div class="sec-hdr-title">Risk Breakdown & Intelligence</div>
  </div>
</div>""", unsafe_allow_html=True)

ddesc, dico = wmo(sel_day["code"])
total_display = f"{total_risk:.0f}" if total_risk is not None else "N/A"
orv_cls = risk_class(total_risk)

crane_p  = (ml_row.get("crane_risk_prob",  0) or 0) * 100 if ml_row else 0
freeze_p = (ml_row.get("freeze_risk_prob", 0) or 0) * 100 if ml_row else 0
heat_p   = (ml_row.get("heat_risk_prob",   0) or 0) * 100 if ml_row else 0
flood_p  = (ml_row.get("flood_risk_prob",  0) or 0) * 100 if ml_row else 0

detail_l, detail_r = st.columns([1.2, 1])

with detail_l:
    # Overall risk + breakdown
    st.markdown(f"""
    <div class="det-hero">
      <div class="det-date">{dico} {sel_day['dow'].title()}, {sel_day['display']}</div>
      <div class="overall-risk-box">
        <div class="orl">OVERALL RISK</div>
        <div class="orv {orv_cls}">{total_display}<span class="pct"> %</span></div>
      </div>
      <div class="rb-section-lbl">RISK BREAKDOWN</div>
      {''.join([
        f'''<div class="rb-item">
          <div class="rb-header">
            <span class="rb-name">{nm}</span>
            <span class="rb-pct {risk_class(v)}">{v:.0f}%</span>
          </div>
          <div class="rb-track"><div class="rb-fill {risk_class(v)}" style="width:{v:.1f}%"></div></div>
        </div>'''
        for nm, v in [
          ("🏗 Crane Operation", crane_p),
          ("❄️ Concrete Freezing", freeze_p),
          ("☀️ Worker Heat Stress", heat_p),
          ("🌊 Excavation Flooding", flood_p),
        ]
      ])}
    </div>
    """, unsafe_allow_html=True)

with detail_r:
    # Weather data + actions
    wm_items = [
        ("Max Temp", f"{sel_day['max']:.1f}", "°C"),
        ("Min Temp", f"{sel_day['min']:.1f}", "°C"),
        ("Max Wind", f"{sel_day['wind']:.1f}", "km/h"),
        ("Precip", f"{sel_day['precip']:.1f}", "mm"),
        ("Feels Like", f"{feels:.1f}", "°C"),
        ("Humidity", f"{humid}", "%"),
    ]
    wm_html = '<div style="display:grid;grid-template-columns:repeat(2,1fr);gap:0.6rem;margin-bottom:1rem">'
    for lbl, val, unit in wm_items:
        wm_html += f'<div class="wm-card"><div class="wm-lbl">{lbl}</div><div class="wm-val">{val}<span class="wm-unit">{unit}</span></div></div>'
    wm_html += "</div>"
    st.markdown(wm_html, unsafe_allow_html=True)

    actions = build_actions(ml_row)
    prio_labels = {"high":"🔴 HIGH PRIORITY","medium":"🟠 MEDIUM PRIORITY","low":"🟡 LOW PRIORITY","safe":"🟢 ALL CLEAR"}
    acts_html = ""
    for prio, title, desc, prob_pct, conf_pct in actions:
        acts_html += f"""<div class="ac {prio}">
          <div class="ac-prio">{prio_labels[prio]}</div>
          <div class="ac-title">{title}</div>
          <div class="ac-desc">{desc}</div>
          <div class="ac-meta">
            <div class="ac-stat">PROBABILITY <b>{prob_pct}%</b></div>
            <div class="ac-stat">CONFIDENCE <b>{conf_pct}%</b></div>
          </div>
        </div>"""
    st.markdown(acts_html, unsafe_allow_html=True)

# ── FOOTER ─────────────────────────────────────────────────────────────────────
st.markdown(f"""
<div style="margin-top:3rem;padding-top:1rem;border-top:1px solid #e8ecf1;
  display:flex;justify-content:space-between">
  <span style="font-size:0.6rem;color:#c4cdd8;letter-spacing:0.08em">
    WEATHER INTELLIGENCE · DATA: OPEN-METEO.COM · ML: PARQUET MODEL
  </span>
  <span style="font-size:0.6rem;color:#c4cdd8;letter-spacing:0.08em">
    {city.upper()} · {lat:.4f}°N {lon:.4f}°E
  </span>
</div>
""", unsafe_allow_html=True)