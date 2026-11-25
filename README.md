# Data Bridge

An automated ETL pipeline that collects live weather data for Indian cities,
cleans and validates it, stores it in a database, and visualizes trends on an
interactive dashboard.

## Architecture

API (Open-Meteo) -> Extract -> Transform -> Load (SQLite) -> Streamlit dashboard
                                   ^
                          Scheduler (every 15 min)

## Features

- **Extract:** pulls current temperature, humidity and wind speed per city
- **Transform:** renames columns, fixes data types, removes missing, impossible
  and duplicate readings
- **Load:** saves to SQLite with a UNIQUE constraint so reruns never create duplicates
- **Automation:** scheduler runs the pipeline on a timer and survives failed runs
- **Logging:** every run is recorded in `pipeline.log` with severity levels
- **Dashboard:** latest readings, trend charts and a city filter

## Tech stack

Python, Pandas, Requests, SQLite, Schedule, Streamlit, Plotly

## How to run

    git clone https://github.com/YOUR-USERNAME/data-bridge.git
    cd data-bridge
    python -m venv venv
    venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
    pip install -r requirements.txt

    python bridge.py               # run the pipeline once
    python scheduler.py            # run it automatically on a timer
    streamlit run dashboard.py     # open the dashboard

## Project structure

| File | Purpose |
|------|---------|
| bridge.py | extract, transform, load functions |
| scheduler.py | runs the pipeline on a schedule |
| dashboard.py | Streamlit dashboard |
| log_config.py | shared logging setup |

## What I learned

- Designing an ETL pipeline from scratch
- Handling bad data, duplicates and API failures
- Making pipelines idempotent (safe to run repeatedly)
- Logging and error handling for automated jobs

## Future improvements

- Add more data sources (air quality)
- Move from SQLite to PostgreSQL
- Deploy the pipeline and dashboard online
- Add alerts for extreme temperatures