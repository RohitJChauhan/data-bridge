import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

DB_PATH = "data_bridge.db"

st.set_page_config(page_title="Data Bridge", page_icon="🌦️", layout="wide")
st.title("Data Bridge: Live Weather Dashboard")


@st.cache_data(ttl=60)  # re-read the database at most once a minute
def load_data():
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql("SELECT * FROM weather", conn)
    conn.close()
    df["time"] = pd.to_datetime(df["time"])
    return df.sort_values("time")


df = load_data()

if df.empty:
    st.warning("No data yet. Run bridge.py or scheduler.py first.")
    st.stop()

# Sidebar filter
all_cities = sorted(df["city"].unique())
selected = st.sidebar.multiselect("Cities", all_cities, default=all_cities)
df = df[df["city"].isin(selected)]

if df.empty:
    st.info("Select at least one city in the sidebar.")
    st.stop()

# Latest reading per city
st.subheader("Latest readings")
latest = df.groupby("city").tail(1)
columns = st.columns(len(latest))
for col, (_, row) in zip(columns, latest.iterrows()):
    col.metric(
        label=row["city"],
        value=f"{row['temp_c']:.1f} °C",
        delta=f"{row['humidity_pct']:.0f}% humidity",
        delta_color="off",
    )

# Trend charts
st.subheader("Temperature over time")
st.plotly_chart(
    px.line(df, x="time", y="temp_c", color="city", markers=True,
            labels={"temp_c": "Temperature (°C)", "time": "Time"}),
    use_container_width=True,
)

left, right = st.columns(2)
with left:
    st.subheader("Humidity over time")
    st.plotly_chart(
        px.line(df, x="time", y="humidity_pct", color="city", markers=True,
                labels={"humidity_pct": "Humidity (%)", "time": "Time"}),
        use_container_width=True,
    )
with right:
    st.subheader("Wind speed over time")
    st.plotly_chart(
        px.line(df, x="time", y="wind_kmh", color="city", markers=True,
                labels={"wind_kmh": "Wind (km/h)", "time": "Time"}),
        use_container_width=True,
    )

with st.expander("See raw data"):
    st.dataframe(df.sort_values("time", ascending=False), use_container_width=True)