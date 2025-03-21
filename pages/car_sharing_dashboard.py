import streamlit as st
import pandas as pd

st.set_page_config(page_title="Car Sharing Dashboard", layout="wide")

# ===============================
# 🚗 Titre et description
# ===============================
st.title("🚗 Car Sharing Dashboard")
st.markdown("Analysis of trips, revenue, and performance of the shared car fleet")

# ===============================
# 📥 Chargement des données
# ===============================
@st.cache_data
def load_data():
    cars = pd.read_csv("dataset/cars.csv")
    trips = pd.read_csv("dataset/trips.csv")
    cities = pd.read_csv("dataset/cities.csv")
    return cars, trips, cities

cars_df, trips_df, cities_df = load_data()

# ===============================
# 🔗 Fusion des datasets
# ===============================
trips_df_merged = trips_df.merge(cars_df, left_on='car_id', right_on='id', how='left')
trips_df_merged = trips_df_merged.merge(cities_df, on='city_id', how='left')

# ===============================
# 🧹 Nettoyage des colonnes inutiles
# ===============================
trips_df_merged = trips_df_merged.drop(columns=[
    "id_x", "id_y", "car_id", "customer_id", "city_id"
])

# ===============================
# 🗓️ Format des dates
# ===============================
trips_df_merged["pickup_time"] = pd.to_datetime(trips_df_merged["pickup_time"])
trips_df_merged["dropoff_time"] = pd.to_datetime(trips_df_merged["dropoff_time"])
trips_df_merged["pickup_date"] = trips_df_merged["pickup_time"].dt.date

# ===============================
# 🎛️ Sidebar : Filtre par marque
# ===============================
st.sidebar.header("🔍 Filtres")
cars_brand = st.sidebar.multiselect(
    "Select one or more car brands",
    options=trips_df_merged["brand"].unique(),
    default=trips_df_merged["brand"].unique()
)

# Application du filtre
if cars_brand:
    trips_df_filtered = trips_df_merged[trips_df_merged["brand"].isin(cars_brand)]
else:
    trips_df_filtered = trips_df_merged

# ===============================
# 📊 Métriques business
# ===============================
st.subheader("📈 Key Metrics")

total_trips = len(trips_df_filtered)
total_distance = trips_df_filtered["distance"].sum()
top_car = trips_df_filtered.groupby("model")["revenue"].sum().idxmax()

col1, col2, col3 = st.columns(3)
col1.metric("Total Trips", total_trips)
col2.metric("Top Earning Car Model", top_car)
col3.metric("Total Distance (km)", f"{total_distance:,.2f}")

# ===============================
# 🧾 Aperçu des données filtrées
# ===============================
st.subheader("🗂️ Filtered Data ✅")
st.dataframe(trips_df_filtered.head(10)) 

st.subheader("📅 Number of Trips per Day")

trips_per_day = trips_df_filtered.groupby("pickup_date").size()

st.line_chart(trips_per_day)

st.subheader("🚘Revenue per Car Model 💰🚘")

revenue_by_model = trips_df_filtered.groupby("model")["revenue"].sum().sort_values(ascending=False)

st.bar_chart(revenue_by_model)

st.subheader("📈Cumulative Revenue Growth Over Time")

cumulative_revenue = trips_df_filtered.groupby("pickup_date")["revenue"].sum().cumsum()

st.area_chart(cumulative_revenue)
st.subheader("⏱️ Average Trip Duration by City")

# Calculer la durée en minutes
trips_df_filtered["trip_duration_min"] = (trips_df_filtered["dropoff_time"] - trips_df_filtered["pickup_time"]).dt.total_seconds() / 60

avg_duration_by_city = trips_df_filtered.groupby("city_name")["trip_duration_min"].mean().sort_values(ascending=False)

st.bar_chart(avg_duration_by_city)
