import streamlit as st
import pandas as pd

st.set_page_config(page_title="Car Sharing Dashboard", layout="wide")

# ===============================
# 🚗 Titre et description
# ===============================
st.title("🚗 Car Sharing Dashboard")
st.markdown("Analyse des trajets, revenus et performances de la flotte de voitures partagées.")

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
    "Sélectionnez une ou plusieurs marques",
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
st.subheader("📈 Indicateurs clés")

total_trips = len(trips_df_filtered)
total_distance = trips_df_filtered["distance"].sum()
top_car = trips_df_filtered.groupby("model")["revenue"].sum().idxmax()

col1, col2, col3 = st.columns(3)
col1.metric("Total de trajets", total_trips)
col2.metric("Modèle le plus rentable", top_car)
col3.metric("Distance totale (km)", f"{total_distance:,.2f}")

# ===============================
# 🧾 Aperçu des données filtrées
# ===============================
st.subheader("🗂️ Données filtrées")
st.dataframe(trips_df_filtered.head())
