## Construction Weather Risk Planner-Youth Faith(100%) 


## Team Work Breakdown

| Person | Task Area              |
|--------|------------------------|
| Kamal  | ML section, Data       |
| Shamil | ML section, Data       |
| Gonce  | UI section, Data       |
| Nargiz | Data Engineering       |

---


## Project Progress Tracker

| Date | Description | People | Status | URL |
|------|-------------|--------|--------|-----|
| 2026-04-17 | Project Kick-Off & API Exploration – The overall project scope was defined, relevant APIs were explored, and initial data sources were identified for further development. | Kamal, Shamil | Done | |
| 2026-04-19 | Data Ingestion Pipeline – An automated data ingestion pipeline was built using the Open-Meteo API, and the initial dataset was successfully generated. | Nargiz, Kamal | Done | |
| 2026-04-20 | Database Design & Data Loading – A structured database schema was designed and the collected data was efficiently loaded into the database system. | Shamil, Nargiz | Done | |
| 2026-04-21 | Data Cleaning & Feature Engineering – Missing values were handled, outliers were treated, and new features such as rolling averages, lag features, and seasonal indicators were created. | Nargiz, Kamal | Done | day 2-den yeniden baxmaq |
| 2026-04-21 | Pipeline Automation & Data Quality – The entire data pipeline was automated, and data quality checks such as null validation, duplicates, and gap detection were implemented. | Qonce, Shamil | Done | linki elave olunmalidir |
| 2026-04-23 | Exploratory Data Analysis – Initial data analysis was performed, including trend detection, correlation analysis, and distribution visualizations. | Nargiz, Kamal | Done | meet.google.com/xxx |
| 2026-04-23 | Statistical Analysis & Feature Selection – Statistical tests were applied to identify the most relevant features, preparing the dataset for modeling. | Qonce, Shamil | Done | meet.google.com/xxx |
| 2026-04-24 | Predictive Modeling & Evaluation – Machine learning models (including Random Forest) were trained and evaluated using performance metrics. | Kamal, Nargiz | In progress | |
| 2026-04-30 | Final Presentation (Assessment) – The final project presentation will be prepared, including results, insights, and dashboard demonstrations. | Nargiz, Qonce | Not started | |

---

## Problem Statement

Most weather applications only provide forecasts for the next 7 days. However, construction companies need to plan their operations weeks in advance.

We are not forecasting weather beyond 7 days. We are learning historical weather-risk relationships to predict construction risk probability for the next 30 days using projected weather patterns and seasonal trends.

For example, if today is April 19, the model will predict risks for the period April 26 → May 26, helping companies understand how many days will be unsafe for construction work.

---

##  Why It Matters

Construction projects (buildings, bridges, and residential complexes) are highly affected by weather conditions.

Unexpected weather can cause:

- Work stoppages
- Equipment downtime
- Material damage
- Worker safety risks

This leads to **financial losses and delays**.

By predicting future risk days, this system helps:

- Plan construction schedules in advance
- Reduce costs caused by delays
- Improve worker safety (HSE standards)
- Optimize use of equipment and materials

This turns weather data into a **decision-support system**, not just a forecast.

---

### Targets (Live Dashboard)

- **windspeed_10m_max** — Maximum wind speed; used for crane operation risk detection *(stop operations if > 36 km/h)*
- **temperature_2m_min** — Minimum temperature; used for freezing risk *(avoid concrete pouring if < 0°C)*
- **apparent_temperature_max** — Maximum apparent temperature; used for heat risk *(apply safety measures if > 35°C)*
- **precipitation_sum** — Total precipitation; used for excavation flooding risk *(activate drainage if > 10 mm)*


---

##  Data Sources

We will use Open-Meteo API endpoints:

### Historical Data
- Endpoint: `https://archive-api.open-meteo.com/v1/archive`
- Purpose: Model training and pattern learning
- Parameters:
  - latitude, longitude (city-based)
  - start_date, end_date (multi-year historical data)
  - daily + hourly weather variables

### Forecast Data
- Endpoint: `https://api.open-meteo.com/v1/forecast`
- Purpose: 7-day validation and comparison with historical patterns
- Parameters:
  - latitude, longitude
  - daily + hourly variables
  - current weather (for live dashboard)

---

## 3. Cities / Locations

We selected multiple cities with different climate conditions:

- **Baku** (40.41, 49.87) — coastal, high wind and humidity influence
- **Ganja** (40.68, 46.36) — inland, seasonal temperature variation
- **Shusha** (39.76, 46.75) — mountainous, snowfall and wind risks
- **Nakhchivan** (39.21, 45.41) — dry continental climate, extreme temperatures

---

## 4. Weather Variables

We use a multi-layer feature set (daily + hourly + current) to capture construction risk behavior.

### Daily Variables (Core Features)

- **weathercode** — General weather condition (clear, fog, storm); used to classify overall risk level
- **temperature_2m_max** — Maximum daily temperature; used for overheating and concrete drying risk
- **temperature_2m_min** — Minimum daily temperature; used for freezing risk of materials
- **apparent_temperature_max** — Feels-like max temperature; used for worker heat stress (HSE risk)
- **apparent_temperature_min** — Feels-like min temperature; used for cold exposure risk
- **precipitation_sum** — Total precipitation (mm); used for flooding risk in construction sites
- **precipitation_hours** — Duration of rainfall; used for scheduling work interruptions
- **rain_sum** — Total rainfall (mm); used for rain-specific construction disruption analysis
- **snowfall_sum** — Snow amount (cm); used for structural load and accessibility risks
- **windspeed_10m_max** — Maximum wind speed; used for crane safety and stopping operations
- **windgusts_10m_max** — Wind gusts; used for sudden instability detection
- **winddirection_10m_dominant** — Wind direction; used for crane positioning and site planning

---

### Hourly Variables (Feature Engineering Layer)

- **temperature_2m** — Hourly temperature; used to capture daily thermal patterns
- **apparent_temperature** — Feels-like temperature; used for peak worker stress hours
- **relative_humidity_2m** — Humidity (%); used for drying and coating conditions
- **precipitation** — Hourly precipitation; used for precise stop-work timing
- **windspeed_10m** — Hourly wind speed; used for wind pattern analysis
- **windgusts_10m** — Wind gust spikes; used for short-term risk detection
- **weathercode** — Hourly weather condition; used to refine daily classification
- **surface_pressure** — Surface pressure; used for wind behavior estimation
- **sea_level_pressure** — Sea level pressure; used for storm and wind forecasting patterns

---



## 5. Methodology Outline

### Day 1 — Data Understanding & Feature Engineering
- API integration (historical + forecast)
- Data cleaning and alignment
- Feature engineering from hourly → daily aggregation
- Risk label creation (binary + percentage risk)

### Day 2 — Modeling
- Classification models:
  - Logistic Regression
  - Random Forest
- Regression models:
  - Risk probability estimation
- Feature importance analysis
- Model comparison

### Day 3 — Evaluation & Improvement
- Cross-validation
- Class imbalance handling
- Threshold tuning
- Final model selection

### Day 4 — Deployment Concept
- Simple dashboard design
- City selector
- Risk calendar visualization (30-day window)

---

## 6. Success Criteria

The project will be considered successful if:

- The model can predict **construction risk days beyond the 7-day forecast window**
- Classification model achieves reliable performance (F1-score > baseline)
- Regression model provides meaningful risk probability estimates
- Feature importance aligns with real-world construction logic (wind, rain, temperature)
- Results are consistent across all 4 cities
- System provides actionable insights for planning (not just predictions)

---

## Summary

This project transforms weather forecasting into a **construction decision-support system**, enabling companies to plan long-term operations using both classification (safe/risky) and regression (risk intensity) outputs.