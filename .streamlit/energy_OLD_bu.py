######################
# Import libraries
######################
import pandas as pd
import streamlit as st
import altair as alt
from PIL import Image
import os
import unidecode
import plotly.figure_factory as ff
import plotly.express as px
from datetime import datetime, timedelta


##########################################
# Page Title and wide setting
##########################################
st.set_page_config (page_title='Analizador para instalacion solar', layout="wide")
image = Image.open ('bombillo.jpg')
st.write ("""
    # Analizador de consumo energético
    Esta aplicación analiza en detalle el consumo energético de tu instalación para ayudarte en tus decisiones a la hora de poner un sistema de energía solar!
    """)
st.image (image, use_column_width=True)

with st.sidebar:
    st.sidebar.markdown ('## Versión 1.0.beta ')
    st.sidebar.markdown ('#### Comentarios a: dvegamar@gmail.com ')
    st.sidebar.markdown ("""___""")

# hide menu and footer from streamlit
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
st.markdown (hide_menu_style, unsafe_allow_html=True)

##########################################
# User inputs (province other parameters)
##########################################
# province selector
st.sidebar.markdown ('### Localización de la instalación ')
province_list = ['Madrid', 'Cuenca', 'Guadalajara', 'Toledo', 'Ciudad Real', 'Albacete', 'Huelva', 'Cádiz', 'Málaga',
                 'Granada', 'Almería', 'Jaén', 'Córdoba', 'Sevilla']
province_list = sorted (province_list)
province = st.sidebar.selectbox ('Provincia', options=province_list)
province = province.lower ().replace (" ", "")  # remove capitals and spaces
province = unidecode.unidecode (province)  # remove accents
irradiation_csv_toread = province + '_total_pv_power_output_wh.csv'

# installation parameters and other useful information
st.sidebar.markdown ('### Parámetros de instalación ')
installed_power = st.sidebar.slider ('Potencia nominal de los paneles en Kw', min_value=0.3, max_value=20.0,
                                     step=0.1, value=5.0)
battery_cap = st.sidebar.slider ('Capacidad de tus baterías en Kwh', min_value=1.0, max_value=20.0, step=0.1, value=5.0)

st.sidebar.markdown ('### Parámetros opcionales ')
increase_demand = st.sidebar.slider (
    '¿Cuánto piensas incrementar tu consumo normal? 1 lo dejas igual, 1.2 aumenta un 20%...',
    min_value=1.0, max_value=2.0, step=0.01, value=1.0)
percent_buy = st.sidebar.slider ('Porcentaje sobre el precio de venta de la compañía al que te compran la energía.',
                                 min_value=5.0,
                                 max_value=100.0, step=1.0, value=20.0) / 100

##########################################
# User inputs (xls files)
##########################################
st.write ('### A) Sube los ficheros ')
st.write ("""
    Necesito que subas los archivos xls que te proporciona tu compañia con los detalles mensuales de consumo. Versión Beta, sólo ficheros de Comercializadora Regulada.
    ***
    """)

# upload files
uploaded_files = st.file_uploader ('Selecciona los ficheros xls', type=["xls", "xlsx"], accept_multiple_files=True)
if len (uploaded_files) != 0:
    filenames = []
    for file in uploaded_files:
        filenames.append (file.name)
        # this 2 next lines of code will store the files in disk in case you need it
        # other way they will be kept in buffer and deleted when refresh or exit the app
        # with open (os.path.join ('datos', file.name), 'wb') as f:
        # f.write (file.getbuffer ())
    st.write ('Has subido un total de ' + str (len (filenames)) + ' archivos: \n')
else:
    st.stop ()


##########################################
# Clean xls and merge files
##########################################

# function to clean the xls files headers from logos, customer info ,etc.
# removing rows with a nan is enough for this xls files
def clean_xls (xls):
    df = pd.read_excel (xls)
    df = df.dropna (axis=0, how='any')
    return df


# development function to get info from a dataframe, as streamlit doesnt show it
def show_df_info (df):
    import io
    buffer = io.StringIO ()
    df.info (buf=buffer)
    s = buffer.getvalue ()
    st.text (s)


# clean and merge al the xls in one dataframe only if the button is clicked
# with merge and outer we merge the individual dataframes
# outer removes repeated rows, as the second row with names and in case the user uploaded repeated files and rows

st.write ('### B) Procesa los ficheros subidos ')
process = st.checkbox ('Procesar')
if process:

    df_clean = clean_xls (uploaded_files [0])
    for i in range (1, len (uploaded_files)):
        last_df = clean_xls (uploaded_files [i])
        df_clean = pd.merge (df_clean, last_df, how='outer')
    names = df_clean.iloc [0, :].values.tolist ()  # get names of columns from the first row
    df_clean.columns = names  # assign names to columns
    df_clean = df_clean.iloc [1:, :]  # remove the first row where the old names are


    # change columns dtypes
    df_clean [['Hora Desde', 'Hora Hasta']] = df_clean [['Hora Desde', 'Hora Hasta']].astype (int)
    df_clean [['Tipo consumo']] = df_clean [['Tipo consumo']].astype (str)
    df_clean [['Consumo (kWh)', 'Precio horario de energía (€/kWh)', 'Importe horario de energía (€)']] = df_clean [
        ['Consumo (kWh)', 'Precio horario de energía (€/kWh)', 'Importe horario de energía (€)']].astype (float)

    # change date str to datetime and then a new column with datetime including the hour to get better graphs.
    df_clean ['Fecha'] = pd.to_datetime (df_clean ['Fecha'], format='%d/%m/%Y')
    df_clean ['Hour_DT'] = pd.to_timedelta (df_clean ['Hora Desde'], 'h')
    df_clean ['Fecha con hora'] = df_clean ['Fecha'] + df_clean ['Hour_DT']
    df_clean.drop(['Hour_DT'],inplace=True,axis=1) # there is a bug in streamlit with timedeltas, so need to drop column
    df_clean ['Mes'] = df_clean ['Fecha'].dt.month


    # screen print and save a file
    # show_df_info (df_clean)  # for developing control
    st.write ('Tabla de consumos agregada, estos son los datos que has subido.')
    st.write (df_clean)
    with pd.ExcelWriter (os.path.join ('datos', 'merged_and_clean.xls')) as writer:
        df_clean.to_excel (writer)

else:
    st.stop ()

##########################################
# Solar power dataframe
##########################################
# let´s show a table with the solar power
df_irr = pd.read_csv (os.path.join ('solar_power', irradiation_csv_toread))
st.write ('### C) Tabla de potencia solar ')
st.write ('Potencia de salida en Wh de panel teórico de 1 Kw a 34º de inclinación para la provincia elegida.')
st.write ('Valores de https://globalsolaratlas.info.')
st.write ('Estos valores no tienen corrección horaria CET')
st.write (df_irr)


##########################################
# ADDING NEW COLUMNS AND VALUES FOR ANALYTICS
##########################################
# if st.button ('Hacer el estudio'):

# first need a function that returns the irradiation value from df_irr when passing hour and month
# values in df_irr are gmt we have 2 hours difference in summer and 1 in winter
def read_irr (hora, mes):
    summer_time = (4, 5, 6, 7, 8, 9, 10)
    if mes in summer_time:
        irr = df_irr.iloc [hora - 2, mes]
    else:
        irr = df_irr.iloc [hora - 1, mes]
    return irr


# then we add a new irr column with this radiation value
df_clean ['irr'] = df_clean.apply (lambda x: read_irr (x ["Hora Desde"], x ["Mes"]), axis=1)

# ADDING NEW COLUMNS TO DF_CLEAN FOR FURTHER CALCULATIONS
df_clean ['Consumo (kWh)'] = df_clean ['Consumo (kWh)'] * increase_demand
df_clean ['power_solar'] = df_clean ['irr'] * installed_power / 1000
df_clean ['power_excess'] = df_clean ['power_solar'] - df_clean ['Consumo (kWh)']
df_clean ['venta €'] = (df_clean ['power_excess'] > 0) * df_clean ['Precio horario de energía (€/kWh)'] * percent_buy * \
                       df_clean ['power_excess']
# (df_clean ['power_excess']>0) es boolean true e igual a 1, si no, cero.
df_clean ['compra €'] = (df_clean ['power_excess'] < 0) * df_clean ['Precio horario de energía (€/kWh)'] * df_clean [
    'power_excess'] * (-1)

power_to_grid = []
power_buffer = []
buf = 0
for value in df_clean ['power_excess']:
    if buf + value >= battery_cap:
        power_to_grid.append (buf + value - battery_cap)
        power_buffer.append (battery_cap)
        buf = battery_cap

    else:
        if buf + value >= 0:
            power_buffer.append (buf + value)
            power_to_grid.append (0)
            buf = buf + value
        else:
            power_buffer.append (0)
            buf = 0
            power_to_grid.append (0)

df_clean ['power_buffer'] = power_buffer
df_clean ['power_to_grid'] = power_to_grid

# GETTING SOME NUMBERS FOR FURTHER ANALYSIS
sum_positives = df_clean.loc [df_clean ['power_excess'] >= 0, 'power_excess'].sum ().round (2)
sum_negatives = df_clean.loc [df_clean ['power_excess'] < 0, 'power_excess'].sum ().round (2)
sum_consumo = df_clean ['Consumo (kWh)'].sum ().round (2)
sum_power_solar = df_clean ['power_solar'].sum ().round (2)
sum_venta_eur = df_clean ['venta €'].sum ().round (2)
sum_compra_eur = df_clean ['compra €'].sum ().round (2)
sum_compra_eur_with_batt = df_clean.loc [df_clean ['power_buffer'] <= 0, 'compra €'].sum ().round (2)
sum_venta_eur_with_batt = (
        df_clean ['Precio horario de energía (€/kWh)'] * percent_buy * df_clean ['power_to_grid']).sum ().round (2)
dif_venta_compra = (sum_venta_eur - sum_compra_eur).round (2)

# show_df_info (df_clean)
st.write ('### D) Tabla con el cálculo de valores ')
st.markdown ("""
Tabla de valores utilizados para los cáculos. 
* **irr:** Potencia de salida en Wh del panel teórico de 1Kw. Corregida según horario de verano o invierno.
* **power_solar:** Es irr multiplicado por la potencia de nuestra instalación.
* **power_excess:** Energía producida por la instalación menos el consumo. Si es negativo estaremos usando batería o red.
* **venta €:** Dinero ganado por la instalación al vender a la red si no hay baterías.
* **compra €:** Dinero pagado a la red por consumo.
* **power_buffer:** Energía almacenada en las baterías.
* **power_to_grid:** Energía en exceso que volcamos a la red si tenemos baterías.

""")
st.write(df_clean)

#########################################################################################################
#########################################################################################################
########################################  Graphs plotting  ##############################################
#########################################################################################################
#########################################################################################################

st.write ('### E) Gráficos ')

chart = alt.Chart (df_clean).mark_line ().encode (
    x='Fecha con hora',
    y='power_solar:Q'
).properties (title="Energía entregada por los paneles en Kwh")
st.altair_chart (chart, use_container_width=True)

chart = alt.Chart (df_clean).mark_line ().encode (
    x='Fecha con hora',
    y='power_excess'
).properties (title="Exceso y déficit de energía según consumo y potencia generada por los paneles en Kwh")
st.altair_chart (chart, use_container_width=True)

chart = alt.Chart (df_clean).mark_line ().encode (
    x='Fecha con hora',
    y='power_buffer'
).properties (title="Energía en baterias en Kwh")
st.altair_chart (chart, use_container_width=True)

fig = px.line(df_clean, x='Fecha con hora' , y='power_solar', title="Energía entregada por los paneles en Kwh")
st.plotly_chart (fig, use_container_width=True)

fig = px.line(df_clean, x='Fecha con hora' , y='power_solar', title="Energía entregada por los paneles en Kwh")
st.plotly_chart (fig, use_container_width=True)

fig = px.line(df_clean, x='Fecha con hora' , y='power_solar', title="Energía entregada por los paneles en Kwh")
st.plotly_chart (fig, use_container_width=True)


#########################################################################################################
#########################################################################################################
########################################## Tables with results ##########################################
#########################################################################################################
#########################################################################################################

st.write ('### Resultados del estudio')

######## ---- for all tables ---- ########

colorscale = [[0, '#137d4f'], [.5, '#b8f0d8'], [1, '#cdddd6']]
colorscale2 = [[0, '#314cb2'], [.5, '#93a8f4'], [1, '#d8def4']]

tables_width = 750
def font_resize (table):
    for i in range (len (table.layout.annotations)):
        table.layout.annotations [i].font.size = 16


######## ---- for parameters table ---- ########

table_param = [['Parámetro de instalación', 'Valor'],
               ['Potencia instalada en placas solares:', str (installed_power) + ' Kw'],
               ['Potencia de baterías:', str (battery_cap) + ' Kwh'],
               ['Multiplicación de la demanda:', str (increase_demand)]]

table_p = ff.create_table (table_param, colorscale=colorscale)
table_p.layout.width = tables_width
font_resize (table_p)
st.plotly_chart (table_p, use_container_width=False)

######## ---- for parameters table ---- ########

table_ener_summary = [['Resumen energético', 'Valor'],
                      ['El consumo de energía en el edificio ha sido:', str (sum_consumo) + ' Kwh'],
                      ['La energía producida por los paneles solares:', str (sum_power_solar) + ' Kwh'],
                      ['Exceso de energía para vender o almacenar:', str (sum_positives) + ' Kwh'],
                      ['Déficit de energía a comprar si no hay baterias:', str (sum_negatives) + ' Kwh']]

table_es = ff.create_table (table_ener_summary, colorscale=colorscale)
table_es.layout.width = tables_width
font_resize (table_es)
st.plotly_chart (table_es, use_container_width=False)


######## ---- installation without batteries and selling excess ---- ########

table_eur_nobat = [['SIN baterías y CON venta del exceso', 'Valor'],
                      ['Por venta de energía ** ',  str (sum_venta_eur) + ' €'],
                      ['Por compra de energía fuera del horario de produccion:', str (sum_compra_eur) + ' €'],
                      ['La diferencia VENTA - COMPRA:', str (dif_venta_compra) + ' €']]

table_enb = ff.create_table (table_eur_nobat, colorscale=colorscale2)
table_enb.layout.width = tables_width
font_resize (table_enb)
st.plotly_chart (table_enb, use_container_width=False)


######## ---- installation with batteries and NOT selling excess ---- ########

table_eur_bat = [['CON baterías y SIN venta del exceso', 'Valor'],
                      ['Por compra cuando las baterias están agotadas:', str (sum_compra_eur_with_batt) + ' €']]

table_eb = ff.create_table (table_eur_bat, colorscale=colorscale2)
table_eb.layout.width = tables_width
font_resize (table_eb)
st.plotly_chart (table_eb, use_container_width=False)


######## ---- installation with batteries and selling excess ---- ########

table_eur_bat_sell = [['CON baterías y CON venta del exceso', 'Valor'],
                      ['Por venta de energía ** ', str (sum_venta_eur_with_batt) + ' €'],
                      ['Por compra de energía al estar sin sol y sin baterías:', str (sum_compra_eur_with_batt) + ' €']]

table_ebs = ff.create_table (table_eur_bat_sell, colorscale=colorscale2)
table_ebs.layout.width = tables_width
font_resize (table_ebs)
st.plotly_chart (table_ebs, use_container_width=False)
st.write(' ** la venta de energía se produce al ' + str (percent_buy * 100) + '% del precio de compra en cada tramo: ')



# este apartado se puede mejorar puesto que el cálculo de la compañía es mensual, por tanto habría que
# agrupar por meses la venta y compra de energía para saber si es positivo o negativo

# https://plotly.com/python/figure-factory-table/
