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
| 2026-04-24 | Predictive Modeling & Evaluation – Machine learning models (including Random Forest) were trained and evaluated using performance metrics. | Kamal, Shamil, Qonche, Nargiz | In progress | |
| 2026-04-30 | Final Presentation (Assessment) – The final project presentation will be prepared, including results, insights, and dashboard demonstrations. | Nargiz, Qonce | Not started | |

---

## Problem Statement

Most weather applications only provide forecasts for the next 7 days. However, construction companies need to plan their operations weeks in advance.

We are not forecasting weather beyond 7 days. We are learning historical weather-risk relationships to predict construction risk probability for the next 16 days using projected weather patterns and seasonal trends.

For example, if today is May 2, the model will predict risks for the period May 2 → May 18, helping companies understand how many days will be unsafe for construction work.

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
- **temperature_2m_min** — Minimum temperature; used for freezing risk *(avoid concrete pouring if < -5°C)*
- **apparent_temperature_max** — Maximum apparent temperature; used for heat risk *(apply safety measures if > 35°C)*
- **precipitation_sum** — Total precipitation; used for excavation flooding risk *(activate drainage if > 10 mm)*

https://www.forconstructionpros.com/concrete/equipment-products/article/22954894/american-[…]-cold-weather-concrete-placement?utm_source=chatgpt.com - freezing

https://ehab.co/knowledge/wind-crane-operations?utm_source=chatgpt.com  -crane risk

Flood Risk: Precipitation > 10 mm/day

Rainfall intensity classifications (NOAA, WMO-based systems) define moderate
rain as approximately 2.5–10 mm/hour. Additionally, NOAA precipitation
analyses commonly use thresholds such as 5 mm, 10 mm, and 25 mm per day
for evaluating rainfall intensity.

Based on these classifications, 10 mm/day is used as a practical threshold
to indicate rainfall levels that may disrupt construction activities.





Heat Risk (>35°C)

Based on OSHA/NIOSH heat stress guidelines for heavy construction work.
WBGT is the standard metric, but since it is unavailable, temperature
>35°C is used as an approximation of high heat risk.

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

## 4. Weather Variables (Feature Engineering Schema)

We define a structured feature set from daily and hourly weather data to support construction risk prediction (crane safety, heat stress, freezing, and flood risk).

---

##  A Daily Features (Primary Risk Signals)

| Source | Feature Name | Unit | Aggregation | Usage in Construction Risk |
|--------|--------------|------|-------------|-----------------------------|
| Open-Meteo | weathercode | categorical | daily mode | General weather state (risk classification) |
| Open-Meteo | temperature_2m_max | °C | daily max | Overheating risk, concrete curing stress |
| Open-Meteo | temperature_2m_min | °C | daily min | Freezing risk for materials |
| Open-Meteo | apparent_temperature_max | °C | daily max | Worker heat stress (HSE risk) |
| Open-Meteo | apparent_temperature_min | °C | daily min | Cold exposure risk |
| Open-Meteo | precipitation_sum | mm | daily sum | Flooding risk in construction sites |
| Open-Meteo | precipitation_hours | hours | daily sum | Work interruption duration |
| Open-Meteo | rain_sum | mm | daily sum | Rain-specific disruption risk |
| Open-Meteo | snowfall_sum | cm | daily sum | Structural load and access disruption |
| Open-Meteo | windspeed_10m_max | km/h | daily max | Crane operation safety risk |
| Open-Meteo | windgusts_10m_max | km/h | daily max | Sudden structural instability risk |
| Open-Meteo | winddirection_10m_dominant | degrees | daily mode | Crane orientation and site planning |

---

##  B Hourly Features (Fine-Grained Risk Detection Layer)

| Source | Feature Name | Unit | Aggregation | Usage in Construction Risk |
|--------|--------------|------|-------------|-----------------------------|
| Open-Meteo | temperature_2m | °C | hourly | Thermal pattern detection |
| Open-Meteo | apparent_temperature | °C | hourly | Peak worker heat stress hours |
| Open-Meteo | relative_humidity_2m | % | hourly avg | Drying / coating conditions |
| Open-Meteo | precipitation | mm | hourly sum | Real-time work stop decisions |
| Open-Meteo | windspeed_10m | km/h | hourly | Wind pattern analysis |
| Open-Meteo | windgusts_10m | km/h | hourly max | Short-term hazard spikes |
| Open-Meteo | weathercode | categorical | hourly mode | Refinement of daily classification |
| Open-Meteo | surface_pressure | hPa | hourly avg | Wind behavior estimation |
| Open-Meteo | sea_level_pressure | hPa | hourly avg | Storm and cyclone pattern detection |

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
- Risk calendar visualization (16-day window)

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
