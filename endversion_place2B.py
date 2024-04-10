import streamlit as st
import pandas as pd
import math

# Tab Title
st.set_page_config(page_title="Place2B", page_icon=":house:")

# Title & Intro
st.title("Place2B")
st.write("""
Finden Sie den idealen Wohnort, der Ihrer gewünschten Entfernung und Ihren steuerlichen Anforderungen entspricht.
""")

# Haversine-Formel zur Berechnung der Distanz zwischen zwei Punkten auf der Erdoberfläche
def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0  # Radius der Erde in Kilometern
    dLat = math.radians(lat2 - lat1)
    dLon = math.radians(lon2 - lon1)
    a = math.sin(dLat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dLon / 2) ** 2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    distance = R * c
    return distance

def find_communities_nearby_fixed(name_or_coords, radius_km, df):
    df = df.copy()
    if isinstance(name_or_coords, str):
        target_row = df[df['Gemeindename'].str.lower() == name_or_coords.lower()]
        if target_row.empty:
            return None
        target_coords = (target_row.iloc[0]['N'], target_row.iloc[0]['E'])
    else:
        target_coords = name_or_coords
    df = df.dropna(subset=['N', 'E'])
    df['Distance'] = df.apply(lambda row: haversine(target_coords[0], target_coords[1], row['N'], row['E']), axis=1)
    nearby_communities = df[df['Distance'] <= radius_km]
    sorted_communities = nearby_communities.sort_values(by='Steuerfuss').reset_index(drop=True)
    return sorted_communities[['Gemeindename', 'BFS-Nr', 'Kantonskürzel', 'E', 'N', 'Steuerfuss', 'Distanz in km']]

# Laden der Daten
file_path = 'C:\\Users\\maxim\\geo_daten_schweiz und estv_income_rates_schweiz.csv'  # Aktualisieren Sie diesen Pfad entsprechend und falls der Link nicht funktioniert 2 // einabuen und nicht nur 1 /
data = pd.read_csv(file_path, sep=';')

# Streamlit UI-Elemente
st.title('Suche nach Gemeinden')
st.sidebar.header('Suchkriterien')

# Eingabe für den Namen der Gemeinde
gemeinde_name = st.sidebar.text_input('Gemeindename')

# Eingabe für den Radius
radius_km = st.sidebar.slider('Radius in Kilometer', min_value=1, max_value=100, value=50)

# Suchen-Button
if st.sidebar.button('Suche starten'):
    st.subheader(f'Gemeinden innerhalb von {radius_km}km um {gemeinde_name}:')
    result_df = find_communities_nearby_fixed(gemeinde_name, radius_km, data)
    if result_df is not None and not result_df.empty:
        st.write(result_df)
    else:
        st.write('Keine Gemeinden gefunden oder ungültige Eingabe.')
