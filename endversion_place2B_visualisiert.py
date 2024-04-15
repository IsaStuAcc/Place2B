import streamlit as st
import pandas as pd
import math
import plotly.graph_objects as go
import plotly.express as px


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
    df['Distanz in km'] = df.apply(lambda row: haversine(target_coords[0], target_coords[1], row['N'], row['E']), axis=1)
    nearby_communities = df[df['Distanz in km'] <= radius_km]
    sorted_communities = nearby_communities.sort_values(by='Steuerfuss').reset_index(drop=True)
    return sorted_communities

# Laden der Daten  (Info an den Rest der Gruppe, dieser Pfad file_path aus Zeile 43 muss aktualisiert werden und die entsprechende Excel Datei dort auch Lokal abgelegt sein)
file_path = 'C:\\Users\\maxim\\geo_daten_schweiz und estv_income_rates_schweiz.csv'  # Pfad aktualisieren
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
        # Balkendiagramm
        fig_bar = px.bar(result_df, x='Steuerfuss', y='Gemeindename', orientation='h', color='Distanz in km',
                         labels={'Steuerfuss':'Steuerfuss [%]', 'Gemeindename':'Gemeinde'},
                         title='Steuerfuss und Distanz der Gemeinden')
        st.plotly_chart(fig_bar, use_container_width=True)

        # Kartenansicht, zentriert auf die Schweiz
        fig = go.Figure(go.Scattergeo(
            lon = result_df['E'],
            lat = result_df['N'],
            text = result_df['Gemeindename'] + '<br>Steuerfuss: ' + result_df['Steuerfuss'].astype(str) + '%<br>Distanz: ' + result_df['Distanz in km'].astype(str) + ' km',
            mode = 'markers',
            marker=dict(
                size=10,
                color='blue',
                line_color='black',
                line_width=0.5,
                sizemode='diameter'
            )
        ))

        fig.update_layout(
            title_text='Geographische Lage der Gemeinden in der Schweiz',
            geo=dict(
                scope='europe',
                showland=True,
                landcolor="rgb(212, 212, 212)",
                subunitcolor="rgb(255, 255, 255)",
                countrycolor="rgb(255, 255, 255)",
                showlakes=True,
                lakecolor="rgb(255, 255, 255)",
                showsubunits=True,
                showcountries=True,
                resolution=50,
                projection=dict(
                    type='mercator',
                    scale=10  # Skalierung für den Zoom auf die Schweiz
                ),
                center=dict(
                    lat=46.8,  # Zentrierung auf die Schweiz
                    lon=8.3
                ),
                countrywidth=0.5,
                subunitwidth=0.5
            )
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.write('Keine Gemeinden gefunden oder ungültige Eingabe.')
