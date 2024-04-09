import streamlit as st
import pandas as pd
import numpy as np
from math import sin, cos, sqrt, atan2, radians
import matplotlib.pyplot as plt


# Tab Title
st.set_page_config(page_title="Place2B", page_icon=":house:")

# Title & Intro
st.title("Place2B")
st.write("""
Find the ideal place to live that takes your desired commute into account, meets your tax requirements, and offers the best tax rates. :)
""")

# Laden der geografischen Daten
df_geo_daten = pd.read_csv("geo_daten_schweiz_modi.csv", delimiter=";")

# Laden der Steuerdaten aus der Excel-Datei
excel_data = pd.read_excel("/mnt/data/estv_income_rates_Switzerland.xlsx", skiprows=2)
# Bereinigen und Umbenennen der Spalten
excel_data.rename(columns={
    'Unnamed: 4': 'Einkommenssteuer Kanton',
    'Unnamed: 5': 'Einkommenssteuer Gemeinde',
    'Unnamed: 8': 'Vermögenssteuer Kanton',
    'Unnamed: 9': 'Vermögenssteuer Gemeinde',
    'Unnamed: 3': 'Gemeinde',
    'BfS-Id': 'BFS_ID'
}, inplace=True)
excel_data = excel_data[['Kanton', 'Gemeinde', 'BFS_ID', 'Einkommenssteuer Kanton', 'Einkommenssteuer Gemeinde']]

# Funktion zur Berechnung der Luftdistanz
def luftdistanz(lat1, lon1, lat2, lon2):
    R = 6371.0
    lat1, lon1, lat2, lon2 = map(radians, [lat1, lon1, lat2, lon2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat / 2)**2 + cos(lat1) * cos(lat2) * sin(dlon / 2)**2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))
    distance = R * c
    return distance

# Text Input User -> Arbeitsort & Kilometerdistanz
st.subheader("Arbeitsort bestimmen")
arbeit = st.text_input("In welcher Gemeinde arbeiten Sie?", placeholder="Gemeindename...")

st.subheader("Wie weit entfernt von ihrem Arbeitsort möchten sie wohnen?")
dist_km = st.text_input("Distanz zum Arbeitsort (Angabe in km)", placeholder="Distanz...")

try:
    dist_km = float(dist_km)
except ValueError:
    st.write("Bitte geben Sie eine gültige Zahl für die Distanz ein.")
    dist_km = None

if dist_km is not None:
    try:
        arbeitsort_lat = df_geo_daten[df_geo_daten["Ortschaftsname"].str.lower() == arbeit.lower()]["N"].iloc[0]
        arbeitsort_lon = df_geo_daten[df_geo_daten["Ortschaftsname"].str.lower() == arbeit.lower()]["E"].iloc[0]
        
        df_geo_daten["Distanz"] = df_geo_daten.apply(
            lambda row: luftdistanz(arbeitsort_lat, arbeitsort_lon, row["N"], row["E"]), axis=1)
        
        nahe_orte = df_geo_daten[df_geo_daten["Distanz"] <= dist_km]
        
        if not nahe_orte.empty:
            nahe_orte = nahe_orte.merge(excel_data, left_on='Ortschaftsname', right_on='Gemeinde', how='left')
            nahe_orte['Gesamtsteuersatz'] = nahe_orte['Einkommenssteuer Kanton'] + nahe_orte['Einkommenssteuer Gemeinde']
            nahe_orte.sort_values('Gesamtsteuersatz', inplace=True)
            
            st.write(f"Orte innerhalb von {dist_km} km Entfernung zu {arbeit}, sortiert nach dem günstigsten Gesamtsteuersatz:")
            st.dataframe(nahe_orte[['Ortschaftsname', 'Distanz', 'Gesamtsteuersatz']])
        else:
            st.write("Keine Orte gefunden, die innerhalb der angegebenen Distanz liegen.")
            
    except IndexError:
        st.write("Arbeitsort nicht gefunden. Bitte überprüfen Sie die Eingabe.")


