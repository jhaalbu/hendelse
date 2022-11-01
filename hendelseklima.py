from matplotlib import pyplot as plt
import streamlit as st
from pyproj import CRS
from pyproj import Transformer
import klimadata
import plot
import folium
from streamlit_folium import st_folium
import pandas as pd
import datetime
import requests
import matplotlib.dates as mdates

def nve_api(lat, lon, startdato, sluttdato, para):
    """Henter data frå NVE api GridTimeSeries
    Args:
        lat (str): øst-vest koordinat (i UTM33)
        output er verdien i ei liste, men verdi per dag, typ ne
        lon (str): nord-sør koordinat (i UTM33)
        startdato (str): startdato for dataserien som hentes ned
        sluttdato (str): sluttdato for dataserien som hentes ned
        para (str): kva parameter som skal hentes ned f.eks rr for nedbør
        
    Returns:
        verdier (liste) : returnerer i liste med klimaverdier
        
    """
    print(f'inne i nve api funksjon lat{lat} lon {lon}')
    api = 'http://h-web02.nve.no:8080/api/'
    url = api + '/GridTimeSeries/' + str(lat) + '/' + str(lon) + '/' + str(startdato) + '/' + str(sluttdato) + '/' + para + '.json'
    r = requests.get(url)

    verdier = r.json()
    return verdier

def klima_dataframe3h(lat, lon, startdato, sluttdato, parametere):
    print(f'lat{lat} lon {lon}')
    parameterdict = {}
    for parameter in parametere:
        print(f'inne i loop lat{lat} lon {lon}')
        api_svar = nve_api(lat, lon, startdato, sluttdato, parameter)
        print(api_svar)
        parameterdict[parameter] = api_svar['Data']
        altitude = api_svar['Altitude']
     
    df = pd.DataFrame(parameterdict)
    df = df.set_index(pd.date_range(
        datetime.datetime(int(startdato[0:4]), int(startdato[5:7]), int(startdato[8:10])),
        datetime.datetime(int(sluttdato[0:4]), int(sluttdato[5:7]), int(sluttdato[8:10])), freq='3h')
    )
    df[df > 1000] = 0
    return df, altitude

st.header('AV-Skredvær')
parameterliste_3h = ['rr3h', 'tm3h', 'windDirection10m3h', 'windSpeed10m3h']
transformer = Transformer.from_crs(4326, 5973)
m = folium.Map(location=[62.14497, 9.404296], zoom_start=5)
folium.raster_layers.WmsTileLayer(
    url='https://opencache.statkart.no/gatekeeper/gk/gk.open_gmaps?layers=topo4&zoom={z}&x={x}&y={y}',
    name='Norgeskart',
    fmt='image/png',
    layers='topo4',
    attr=u'<a href="http://www.kartverket.no/">Kartverket</a>',
    transparent=True,
    overlay=True,
    control=True,
    
).add_to(m)
m.add_child(folium.ClickForMarker(popup="Waypoint"))
#from folium.plugins import Draw
#Draw().add_to(m)
output = st_folium(m, width = 700, height=500)
utm_lat = 0
utm_lon = 0
st.write('Trykk i kartet, eller skriv inn koordinater for å velge klimapunkt.')
st.write('Finn automatisk nærmaste stadnavn dersom det er eit navn innafor 500m radius.')


try:
    kart_kord_lat = output['last_clicked']['lat']
    kart_kord_lng = output['last_clicked']['lng']
    utm_ost, utm_nord = transformer.transform(kart_kord_lat, kart_kord_lng)
    utm_nord = round(utm_nord,2)
    utm_ost = round(utm_ost,2)

except TypeError:
    utm_nord  = 'Trykk i kart, eller skriv inn koordinat'
    utm_ost = 'Trykk i kart, eller skriv inn koordinat'


lat = st.text_input("NORD(UTM 33)", utm_nord)
lon = st.text_input("ØST  (UTM 33)", utm_ost)

lon = int(float(lon.strip()))
lat = int(float(lat.strip()))


try:
    navn = klimadata.stedsnavn(utm_nord, utm_ost)['navn'][0]['stedsnavn'][0]['skrivemåte']
except (IndexError, KeyError):
    navn = 'Skriv inn navn'
#st.write(navn)
#st.write(navn['navn'][0]['stedsnavn'][0]['skrivemåte'])

#st.write(klimadata.stedsnavn(lng, lat))
lokalitet = st.text_input("Gi navn til lokalitet", navn)

start_3h_dato = st.text_input("Gi startdato, må ha riktig format (mellom 01-01-2010 og dagens dato)", '2021-12-24')
antall_dager = st.text_input("Gi antall dager (fungerer best med intill 7 dager)", '5')

start3h_dato = datetime.datetime(int(start_3h_dato[0:4]), int(start_3h_dato[5:7]), int(start_3h_dato[8:10]))
sluttdato_berekna = start3h_dato + datetime.timedelta(days=int(antall_dager))

sluttdato_str = str(sluttdato_berekna)[0:10]
print(start_3h_dato)
print(sluttdato_str)
print(utm_nord, utm_ost)

knapp = st.button('Vis plott')

if knapp:
    df, altitude = klima_dataframe3h(lon, lat, start_3h_dato, sluttdato_str, parameterliste_3h)
    fig = plt.figure(figsize=(15,8)) 
    ax1 = fig.add_subplot(111)
    ax1.set_title('Værdata - 3timer nedbør og temperatur')
    ax1.bar(df.index,  df['rr3h'], width=0.100)
    ax1.set_xlabel('Tidspunkt')
    ax1.set_ylabel('Nedbør (mm)')
    ax1.xaxis.set_major_locator(mdates.HourLocator(interval=3))   
    ax1.set_xticks(ax1.get_xticks(), ax1.get_xticklabels(), rotation=90, ha='right')
    ax1.xaxis.set_major_formatter(mdates.DateFormatter('%d-%m %H:%M')) 

    ax2 = ax1.twinx()
    ax2.plot(df.index, df['tm3h'], 'r', label='Temperatur ')
    ax2.set_ylabel('Temperatur (\u00B0C)')

    st.pyplot(fig)