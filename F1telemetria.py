""" TELEMETRÍA FÓRMULA 1 """

##### PARTE 0: PREPARACIÓN

# Importamos todas las librerías necesarias
import streamlit as st
import fastf1 as ff1
import numpy as np
import matplotlib as mpl

from matplotlib import pyplot as plt
from matplotlib.collections import LineCollection

# Seleccionamos la carpeta de cache
ff1.Cache.enable_cache("pon aquí la dirección del cache")



##### PARTE 1: SELECCIONAR VALORES CON STREAMLIT

# Ponemos título y descripción en Streamlit
st.title("Visualizador de telemetría de F1")
st.markdown("Aquí podrás visualizar la telemetría de la vuelta más rápida de cualquier piloto en cualquier circuito, a partir de 2018. Es posible que en alguna sesión falten datos")

# Seleccionamos el año
years = range(2018,2023)
year = st.selectbox("Elige el año", years)

# Seleccionamos el Gran Premio
schedule = ff1.get_event_schedule(year)
wknd = st.selectbox("Elige el Gran Premio", schedule.EventName)

# Seleccionamos la sesión
event = ff1.get_event(year, wknd)
sesiones = ["FP1", "FP2", "FP3", "Clasificación", "Carrera"]
ses_name = st.selectbox("Elige la sesión", sesiones)
dic_sesiones = {"FP1" : 1, "FP2" : 2, "FP3" : 3, "Clasificación" : 4, "Carrera" : 5}
ses = dic_sesiones[ses_name]

# Seleccionamos el piloto
session = ff1.get_session(year, wknd, ses)
weekend = session.event
session.load()
driver = st.selectbox("Elige al piloto", session.results.Abbreviation)

# Seleccionamos la variable a representar
parametros = ["Velocidad", "RPM", "Marchas", "Acelerador", "Freno", "DRS"]
par_name = st.selectbox("Elige la variable a representar", parametros)


##### PARTE 2: REPRESENTAR EN EL MAPA DEL CIRCUITO

### PARTE 2.1: PREPARAMOS LOS DATOS DE TELEMETRÍA

# Elegimos los colores del mapa
colormap = mpl.cm.rainbow

# Elegimos la vuelta más rápida del piloto elegido
lap = session.laps.pick_driver(driver).pick_fastest()

# Sacamos de la telemetría la posición en cada punto X-Y
x = lap.telemetry["X"]
y = lap.telemetry["Y"]

# Sacamos de la telemetría los valores de cada parámetro
velocidad = lap.telemetry["Speed"]
rpm = lap.telemetry["RPM"]
marchas = lap.telemetry["nGear"]
acel = lap.telemetry["Throttle"]
freno = lap.telemetry["Brake"]
drs = lap.telemetry["DRS"]

# Asignamos colores al parámetro seleccionado por el usuario
dic_parametros = {"Velocidad" : velocidad, "RPM" : rpm, "Marchas" : marchas, "Acelerador" : acel, "Freno" : freno, "DRS" : drs}
dic_parametros_en = {"Velocidad" : "Speed", "RPM" : "RPM", "Marchas" : "nGear", "Acelerador" : "Throttle", "Freno" : "Brake", "DRS" : "DRS"}
color = dic_parametros[par_name]

# Hacemos los segmentos del circuito
puntos = np.array([x, y]).T.reshape(-1, 1, 2)
segmentos = np.concatenate([puntos[:-1], puntos[1:]], axis=1)



### PARTE 2.2: PREPARAMOS LOS GRÁFICOS

# Creamos una gráfica y su título
fig, ax = plt.subplots(sharex=True, sharey=True, figsize=(12, 6.75))
fig.suptitle(f"{weekend.name} {year} - {driver}", size=24, y=0.97)

# Ajustamos márgenes y giro del eje
plt.subplots_adjust(left=0.1, right=0.9, top=0.9, bottom=0.12)
ax.axis("off")

# Creamos el trazado base del circuito en negro
ax.plot(lap.telemetry["X"], lap.telemetry["Y"], color="black", linestyle="-", linewidth=5, zorder=0)

# Creamos el trazado con colores según los datos de telemetría
norma = plt.Normalize(color.min(), color.max())
lc = LineCollection(segmentos, cmap=colormap, norm=norma, linestyle="-", linewidth=3)
lc.set_array(color)
line = ax.add_collection(lc)

# Creamos la leyenda de colores
cbaxes = fig.add_axes([0.25, 0.05, 0.5, 0.05])
normlegend = mpl.colors.Normalize(vmin=color.min(), vmax=color.max())
legend = mpl.colorbar.ColorbarBase(cbaxes, norm=normlegend, cmap=colormap, orientation="horizontal")
ax.set_aspect("equal", "datalim")

### PARTE 2.3: REPRESENTAMOS LOS GRÁFICOS
st.pyplot(fig)



##### PARTE 3: REPRESENTAR EN UN GRÁFICO

tel = lap.get_car_data().add_distance()
fig2, ax2 = plt.subplots()
ax2.plot(tel["Distance"], tel[dic_parametros_en[par_name]], color="red", label=driver)
ax2.set_xlabel("Distancia")
ax2.set_ylabel(par_name)
ax2.legend()
plt.suptitle(f"Vuelta rápida \n"
             f"{session.event['EventName']} {session.event.year} {ses_name}")
st.pyplot(fig2)



##### COSAS QUE AÑADIR
#
# -Que el gráfico tenga el color del equipo de cada piloto
# -Poder comparar dos vueltas de dos pilotos distintos