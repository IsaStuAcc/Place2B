# Required Libraries
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

# Tab Title
st.set_page_config(page_title="Place2B", page_icon=":house:")

# Title & Intro
st.title("Place2B")
st.write("""
Find the ideal place to live that takes your desired commute into account and meets your tax requirements. :)
""")

####Der gewünschte Ort mit Radius -> Zugriff auf die Datenbank
df_geo_daten = pd.read_csv("geo_daten_schweiz_modi.csv", delimiter=";")
df_geo_daten.head()

# Importieren von mathematischen Funktionen
from math import sin, cos, sqrt, atan2, radians

# Definition der Luftdistanzfunktion
    # Berechnung von Radius wird gebraucht für spätere Berechnungen der Luftdistanz
def luftdistanz(lat1, lon1, lat2, lon2):
    # approximate radius of earth in km
    R = 6371.0

    lat1 = radians(lat1)
    lon1 = radians(lon1)
    lat2 = radians(lat2)
    lon2 = radians(lon2)

    dlon = lon2 - lon1
    dlat = lat2 - lat1

    a = sin(dlat / 2) ** 2 + cos(lat1) * cos(lat2) * sin(dlon / 2) ** 2
    c = 2 * atan2(sqrt(a), sqrt(1 - a))

    distance = R * c

    return distance



# Text Input User -> Arbeitsort & Kilometerdistanz
st.subheader("Arbeitsort bestimmen")
arbeit = st.text_input("In welcher Gemeinde arbeiten Sie?", placeholder="Gemeindename...")

st.subheader("Wie weit entfernt von ihrem Arbeitsort möchten sie wohnen?")
dist_km = st.text_input("Distanz zum Arbeitsort (Angabe in km)", placeholder="Distanz...")

# Umwandlung der Distanz-Eingabe in einen numerischen Wert
try:
    dist_km = float(dist_km)
except ValueError:
    st.write("Bitte geben Sie eine gültige Zahl für die Distanz ein.")
    dist_km = None


# Berechnung und Ausgabe der Gemeinden, die innerhalb des Radius sind
if dist_km is not None:
    try:
        # Finden der geografische Breite (lat) und Länge (lon) des Arbeitsortes, durch filtern des DataFrame
        # und den Wert aus "N" bzw. "E" für den entsprechenden Ortschaftsnamen ausliest.
        # Die Eingabe wird zuerst in Kleinbuchstaben umgewandelt, um Gross- und Kleinschreibung zu ignorieren.
        # df_geo_daten["Ortschaftsname"].str.lower() == arbeit.lower() -> Ergebnis ist True oder False
        # df_geo_daten[...]: Diese Klammerung wird verwendet, um den DataFrame zu filtern. Nur die Zeilen, bei denen der obige Ausdruck True ergibt, werden im resultierenden DataFrame behalten.
        # .iloc[0] vermeidet Dublikate
        arbeitsort_lat = df_geo_daten[df_geo_daten["Ortschaftsname"].str.lower() == arbeit.lower()]["N"].iloc[0]
        arbeitsort_lon = df_geo_daten[df_geo_daten["Ortschaftsname"].str.lower() == arbeit.lower()]["E"].iloc[0]
        
        # Filterung der Orte basierend auf der Distanz
        # Neue Spalte "Distanz" zu geo_daten hinzufügen, die die Luftdistanz zwischen dem Arbeitsort und jeder Ortschaft im DataFrame berechnet. Dies verwendet die Funktion 'luftdistanz'.
        df_geo_daten["Distanz"] = df_geo_daten.apply(
            lambda row: luftdistanz(arbeitsort_lat, arbeitsort_lon, row["N"], row["E"]), axis=1)
        
        # neue Variable "nahe_orte", die die Orte mit einer Distanz kleiner gleich User-Input speichert. 
        nahe_orte = df_geo_daten[df_geo_daten["Distanz"] <= dist_km]
        
        #Wenn der DataFrame 'nahe_orte' nicht leer ist, also Orte gefunden wurden, zeige sie an.
        if not nahe_orte.empty:
            st.write(f"Orte innerhalb von {dist_km} km Entfernung zu {arbeit}:")
            st.dataframe(nahe_orte[["Ortschaftsname", "Distanz"]])
        else:
            st.write("Keine Orte gefunden, die innerhalb der angegebenen Distanz liegen.")
            
    except IndexError:
        st.write("Arbeitsort nicht gefunden. Bitte überprüfen Sie die Eingabe.")