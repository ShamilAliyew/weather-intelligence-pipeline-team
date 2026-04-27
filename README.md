![logo_ironhack_blue 7](https://user-images.githubusercontent.com/23629340/40541063-a07a0a8a-601a-11e8-91b5-2f13e4e6b441.png)

# Youth Faith Team

# Project 1: Weather Intelligence Pipeline — Can We Trust This Data?

## Overview

Over the next two weeks you will build a complete, end-to-end **weather intelligence pipeline**. You will ingest historical and real-time weather data from the Open-Meteo API, store it in a local DuckDB analytical database, perform rigorous statistical analysis, and build a predictive model — all while critically evaluating whether the data can be trusted.

**Why weather?** Weather data is publicly available, refreshed daily, has genuine quality challenges (sensor gaps, interpolation artefacts, seasonal non-stationarity), and is the backbone of decisions in energy, agriculture, logistics, and insurance. It is the perfect playground for asking *"Can we trust this data?"*

## Project Requirements

| Week | Focus | Skills Applied |
|------|-------|----------------|
| **Week 1** (Days 1–5) | Data Engineering | Unit 2 — data sources, databases, ETL, pipelines |
| **Week 2** (Days 6–8 + Presentation) | Statistical Analysis & Prediction | Unit 3 — descriptive stats, hypothesis testing, correlation, modeling |

**You must:**

1. Choose **3 or more cities** (at least one should be Baku or another city relevant to you).
2. Ingest **at least 5 years** of daily historical weather data per city.
3. Ingest **real-time forecast data** (7-day forecast) for the same cities.
4. Store all data in a local **DuckDB** database with a well-designed schema.
5. Conduct **exploratory data analysis** with descriptive statistics and visualisations.
6. Formulate and execute **at least one formal hypothesis test** (more are encouraged if time permits).
7. Build **at least one statistical prediction model** (e.g., predict next-day temperature, rain probability, or seasonal anomaly) with confidence intervals.
8. Present findings on presentation day with a live pipeline demo.

## Timeline

Each day has a brief in the [`daily-briefs/`](daily-briefs/) folder with detailed tasks, deliverables, and resources. Submit a Pull Request at the end of each day showing your incremental progress.

| Day | Date | Brief | Focus |
|-----|------|-------|-------|
| 1 | 20 Apr | [Project Kick-Off & API Exploration](daily-briefs/day-01-project-kickoff.md) | Repo setup, API exploration, city/variable selection, project plan |
| 2 | 21 Apr | [Data Ingestion Pipeline](daily-briefs/day-02-data-ingestion.md) | Ingestion module, config, full historical fetch, data audit |
| 3 | 22 Apr | [Database Design & Data Loading](daily-briefs/day-03-database-design.md) | DuckDB schema, loading functions, validation queries |
| 4 | 23 Apr | [Data Cleaning & Feature Engineering](daily-briefs/day-04-data-cleaning.md) | Quality assessment, cleaning pipeline, feature engineering, quality report |
| 5 | 24 Apr | [Pipeline Automation & Data Quality](daily-briefs/day-05-pipeline-automation.md) | Orchestrator, incremental loading, quality gates, logging |
| 6 | 27 Apr | [Exploratory Data Analysis](daily-briefs/day-06-eda.md) | Descriptive stats, distributions, time series, cross-city comparison |
| 7 | 28 Apr | [Statistical Analysis & Feature Selection](daily-briefs/day-07-statistical-analysis.md) | Hypothesis testing, correlation, feature selection |
| 8 | 29 Apr | [Predictive Modeling & Evaluation](daily-briefs/day-08-predictive-modeling.md) | 2+ models, train/test, confidence intervals, residual diagnostics |
| — | 30 Apr | [Final Presentation](daily-briefs/day-09-final-presentation.md) | 10 min presentation, live demo, project submission |

## Getting Started

### 1. Fork & Clone

```bash
# Fork this repo on GitHub, then:
git clone https://github.com/<your-username>/m5-project-weather-pipeline.git
cd m5-project-weather-pipeline
```

### 2. Install Dependencies

```bash
pip install -r requirements.txt
```

### 3. Verify the API

No API key needed. Test with:

```bash
curl "https://archive-api.open-meteo.com/v1/archive?latitude=40.41&longitude=49.87&start_date=2024-01-01&end_date=2024-01-07&daily=temperature_2m_max"
```

### 4. Start Day 1

Open [`daily-briefs/day-01-project-kickoff.md`](daily-briefs/day-01-project-kickoff.md) and follow the tasks.

## Repository Structure

```
m5-project-weather-pipeline/
├── README.md               # This file — project overview
├── requirements.txt        # Python dependencies
├── .gitignore
├── daily-briefs/           # Day-by-day task briefs (read-only reference)
│   ├── day-01-project-kickoff.md
│   ├── ...
│   └── day-09-final-presentation.md
├── src/                    # Your pipeline code
│   ├── __init__.py
│   ├── ingestion.py        # Day 2
│   ├── config.py           # Day 2
│   ├── database.py         # Day 3
│   ├── cleaning.py         # Day 4
│   ├── features.py         # Day 4
│   ├── quality_checks.py   # Day 5
│   └── pipeline.py         # Day 5
├── notebooks/              # Daily Jupyter notebooks
│   ├── day_01_exploration.ipynb
│   ├── day_02_ingestion.ipynb
│   ├── ...
│   └── day_08_modeling.ipynb
├── data/
│   └── raw/                # Raw API data (gitignored)
├── reports/
│   ├── figures/            # Saved visualisations
│   └── data_quality_report.md
└── logs/                   # Pipeline logs (gitignored)
```

## Open-Meteo API Reference

[Open-Meteo](https://open-meteo.com/) is a free, open-source weather API. **No API key required.**

**Historical weather endpoint:**

```
https://archive-api.open-meteo.com/v1/archive?latitude=40.41&longitude=49.87&start_date=2020-01-01&end_date=2024-12-31&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max
```

**Forecast endpoint:**

```
https://api.open-meteo.com/v1/forecast?latitude=40.41&longitude=49.87&daily=temperature_2m_max,temperature_2m_min,precipitation_sum,windspeed_10m_max
```

Key daily variables: `temperature_2m_max`, `temperature_2m_min`, `temperature_2m_mean`, `precipitation_sum`, `rain_sum`, `snowfall_sum`, `windspeed_10m_max`, `relative_humidity_2m_mean`, `apparent_temperature_max`, `weathercode`.

## Evaluation Criteria

| Criterion | Weight | Description |
|-----------|--------|-------------|
| Pipeline completeness | 20% | End-to-end from API to database, automated, with quality checks |
| Data quality analysis | 15% | Thorough assessment, documented issues, justified decisions |
| Statistical rigour | 20% | Proper hypothesis testing, assumption checking, effect sizes |
| Prediction model | 20% | Appropriate model selection, evaluation, confidence intervals |
| Presentation quality | 15% | Clear narrative, good visuals, effective demo |
| Code quality | 10% | Clean, modular, documented, reproducible |

## Resources

- [Open-Meteo API Documentation](https://open-meteo.com/en/docs)
- [Open-Meteo Historical Weather API](https://open-meteo.com/en/docs/historical-weather-api)
- [DuckDB Python Documentation](https://duckdb.org/docs/api/python/overview)
- [scipy.stats documentation](https://docs.scipy.org/doc/scipy/reference/stats.html)
- [statsmodels documentation](https://www.statsmodels.org/stable/index.html)
- [Seaborn gallery](https://seaborn.pydata.org/examples/index.html)



---

## 1. Problem Statement

Most weather applications only provide forecasts for the next 7 days. However, construction companies need to plan their operations weeks in advance.

Our goal is to build a model that predicts **construction risk conditions for the next 30 days beyond the standard 7-day forecast window**.

For example, if today is April 19, the model will predict risks for the period **April 26 → May 26**, helping companies understand how many days will be unsafe for construction work.

---

## 2. Why It Matters

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

## 3. Data Sources

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

## 4. Cities / Locations

We selected multiple cities with different climate conditions:

- **Baku** (40.41, 49.87) — coastal, high wind and humidity influence  
- **Ganja** (40.68, 46.36) — inland, seasonal temperature variation  
- **Shusha** (39.76, 46.75) — mountainous, snowfall and wind risks  
- **Nakhchivan** (39.21, 45.41) — dry continental climate, extreme temperatures  

---

## 5. Weather Variables

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

### Current Variables (Live Dashboard)

- **temperature_2m** — Current temperature; used for real-time site monitoring  
- **windspeed_10m** — Current wind speed; used for crane safety alerts  
- **windgusts_10m** — Current wind gusts; used for sudden risk detection  
- **weathercode** — Current weather condition; used for live risk visualization  

---

## 6. Methodology Outline

### Week 1 — Data Understanding & Feature Engineering
- API integration (historical + forecast)
- Data cleaning and alignment
- Feature engineering from hourly → daily aggregation
- Risk label creation (binary + percentage risk)

### Week 2 — Modeling
- Classification models:
  - Logistic Regression
  - Random Forest
- Regression models:
  - Risk probability estimation
- Feature importance analysis
- Model comparison

### Week 3 — Evaluation & Improvement
- Cross-validation
- Class imbalance handling
- Threshold tuning
- Final model selection

### Week 4 — Deployment Concept
- Simple dashboard design
- City selector
- Risk calendar visualization (30-day window)

---

## 7. Success Criteria

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


## Project Progress Tracker

Team Name: Youth Faith
Team members: Shamil Aliyev, Kamal Musayev, Nargiz Aliyeva, Qonche Ismayilova

Roles:  
Shamil Aliyev → Machine Learning Engineer & Data Engineer  
Kamal Musayev → Machine Learning Engineer & Data Engineer  
Nargiz Aliyeva → Data Scientist & ML Engineer  
Qonche Ismayilova → Frontend Engineer & UI/UX Designer  

| Days | Done | People | Date | Status | URL |
|------|------|--------|------|--------|-----|
| Day 1. Project Kick-Off & API Exploration | ✅ | Kamal, Shamil | 2026-04-17 | 🟢 Done | |
| Day 2. Data Ingestion Pipeline | ✅ | Nargiz, Kamal | 2026-04-19 | 🟢 Done | |
| Day 3. Database Design & Data Loading | ✅ | Shamil, Nargiz | 2026-04-20 | 🟢 Done | |
| Day 4. Data Cleaning & Feature Engineering | ✅ | Nargiz, Kamal | 2026-04-21 | 🟢 Done | day 2-den yeniden baxmaq |
| Day 5. Pipeline Automation & Data Quality | ✅ | Qonce, Shamil | 2026-04-21 | 🟢 Done | linki elave olunmalidir |
| Day 6. Exploratory Data Analysis | ✅ | Nargiz, Kamal | 2026-04-23 | 🟢 Done | meet.google.com/xxx |
| Day 7. Statistical Analysis & Feature Selection | ✅ | Qonce, Shamil | 2026-04-23 | 🟢 Done | meet.google.com/xxx |
| Day 8. Predictive Modeling & Evaluation | ✅ | Kamal, Nargiz | 2026-04-24 | 🔵 In progress | |
| Day 9. Final Presentation (Assessment) | ⬜ | Nargiz, Qonce | 2026-04-30 | ⚪ Not started | |