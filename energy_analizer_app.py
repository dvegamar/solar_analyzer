######################
# Import libraries
######################
import pandas as pd
import streamlit as st
from PIL import Image
import os
import unidecode
import plotly.figure_factory as ff
import plotly.express as px
import plotly.graph_objects as go
import clean_comercializadora_regulada


# development function to get info from a dataframe, as streamlit doesnt show it
def show_df_info (df):
    import io
    buffer = io.StringIO ()
    df.info (buf=buffer)
    s = buffer.getvalue ()
    st.text (s)
#########################################################################################################
########################################## Page Title and wide settings #################################
#########################################################################################################

st.set_page_config (page_title='Analizador para instalacion solar', layout="wide")
image = Image.open ('bombillo.jpg')
st.write ("""
    # Analizador de consumo energético
    Esta aplicación analiza en detalle el consumo energético de tu instalación para ayudarte en tus decisiones a la hora de poner un sistema de energía solar!  
    Versión 1.0.beta  
    Comentarios a: dvegamar@gmail.com
    """)
st.image (image, use_column_width=True)

with st.sidebar:
    st.sidebar.markdown ("""___""")

# hide menu and footer from streamlit
hide_menu_style = """
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """
st.markdown (hide_menu_style, unsafe_allow_html=True)

#########################################################################################################
#################################  User inputs on the right sidebar  ####################################
#########################################################################################################
# province selector
st.sidebar.markdown ('### Localización de la instalación ')
province_list = ['Albacete', 'Álava', 'Alicante', 'Almería', 'Asturias', 'Ávila', 'Badajoz', 'Barcelona', 'Burgos',
                 'Cantabria',
                 'Castellón', 'Ceuta', 'Ciudad Real', 'Cuenca', 'Cáceres', 'Cádiz', 'Córdoba', 'Girona',
                 'Gran Canaria', 'Granada', 'Guadalajara', 'Guipuzcoa', 'Huelva', 'Huesca', 'Jaén', 'La Coruña',
                 'La Rioja', 'León',
                 'Lleida', 'Lugo', 'Madrid', 'Mallorca', 'Melilla', 'Murcia', 'Málaga', 'Navarra', 'Orense', 'Palencia',
                 'Pontevedra',
                 'Salamanca', 'Segovia', 'Sevilla', 'Soria', 'Tarragona', 'Tenerife', 'Teruel', 'Toledo', 'Valencia',
                 'Valladolid',
                 'Vizcaya', 'Zamora', 'Zaragoza']

province = st.sidebar.selectbox ('Provincia', options=province_list)
province = unidecode.unidecode (province)  # remove accents
province = province.lower ().replace (" ", "")  # remove capitals and spaces
irradiation_csv_toread = province + '_total_pv_power_output_wh.csv'

# installation parameters and other useful information

st.sidebar.markdown ('### Parámetros de instalación ')
installed_power = st.sidebar.slider ('Potencia nominal de los paneles en Kw', min_value=0.3, max_value=20.0,
                             step=0.1, value=5.0)
battery_cap = st.sidebar.slider ('Capacidad de tus baterías en Kwh',
                             min_value=1.0, max_value=20.0, step=0.1, value=5.0)


st.sidebar.markdown ('### Parámetros opcionales ')
increase_demand = st.sidebar.slider (
                            '¿Cuánto piensas incrementar tu consumo normal? 1 lo dejas igual, 1.2 aumenta un 20%...',
                             min_value=1.0, max_value=2.0, step=0.01, value=1.0)
free_prize = st.sidebar.slider (
                            'Precio medio de la energía que compras en el mercado libre €/kwh',
                             min_value=0.01, max_value=1.0, step=0.01, value=0.20)
percent_buy = st.sidebar.slider ('Porcentaje sobre el precio de venta de la compañía al que te compran la energía.',
                             min_value=5.0,
                             max_value=100.0, step=1.0, value=20.0) / 100



#########################################################################################################
#################################  User selection generic or customized #################################
#########################################################################################################
st.write ('### Elige un caso de estudio ')
st.markdown (""" 
* **Genérico:** Ejemplo de una casa de 3 habitantes y precio de energía regulado.
* **Genérico libre:** Ejemplo de una casa de 3 habitantes y precio de energía libre  -  selecciona el precio en la columna izquierda.
* **Personalizado:** tengo mi histórico en archivos xls o csv con mi consumo horario.
""")
study_type = st.radio('Selecciona una opción',('Genérico',
                                               'Genérico libre',
                                               'Personalizado'))

#########################################################################################################
#################################  User inputs (xls files) ##############################################
#########################################################################################################

if study_type == 'Personalizado':
    st.write ('### A) Sube los ficheros ')
    st.write ("""
        Necesito que subas los archivos xls que te proporciona tu compañia con los detalles mensuales de consumo. Versión Beta, sólo ficheros de Comercializadora Regulada.
        ***
        """)
    uploaded_files = st.file_uploader ('Selecciona los ficheros xls', type=["xls", "xlsx"], accept_multiple_files=True)

    if len (uploaded_files) != 0:
        filenames = []
        for file in uploaded_files:
            filenames.append (file.name)
        st.write ('Has subido un total de ' + str (len (filenames)) + ' archivos: \n')

        df_clean = clean_comercializadora_regulada.CleanCR (uploaded_files)
        # show_df_info (df_clean)  # for developing control
        st.write ('Tabla de consumos agregada, estos son los datos que has subido.')
        df_clean = df_clean.sort_values (by='Fecha con hora')
        st.write (df_clean)
        # with pd.ExcelWriter (os.path.join ('datos', 'merged_and_clean.xls')) as writer:
            # df_clean.to_excel (writer)

    else:
        st.stop ()

else:
    # if the user is not uploading files, then we use an internal example stores in merged_and_clean.xls
    df_clean = pd.read_excel (os.path.join ('datos', 'merged_and_clean.xls'))


##########################################
# Solar power dataframe
##########################################
# let´s show a table with the solar power by province
df_irr = pd.read_csv (os.path.join ('solar_power', irradiation_csv_toread))
st.write ('### Tabla de potencia solar ')
st.write ('Potencia de salida en Wh de panel teórico de 1 Kw a 34º de inclinación para la provincia elegida.')
st.write ('Valores de https://globalsolaratlas.info.')
st.write ('Estos valores no tienen corrección horaria CET, los usando en cáculos sí están corregidos')
st.write (df_irr)


#########################################################################################################
################################  ADDING NEW COLUMNS AND VALUES FOR ANALYTICS   #########################
#########################################################################################################

# first need a function that returns the solar power value from df_irr when passing hour and month
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
if study_type ==  'Genérico libre':
    df_clean ['Precio horario de energía (€/kWh)'] = free_prize

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

df_clean ['compra_bat_€'] = (df_clean ['power_excess'] < 0) * (df_clean ['power_buffer'] <= 0) * df_clean [
    'Precio horario de energía (€/kWh)'] * df_clean [
                                'power_excess'] * (-1)
df_clean ['venta_bat_€'] = (df_clean ['power_to_grid'] > 0) * df_clean [
    'Precio horario de energía (€/kWh)'] * percent_buy * \
                           df_clean ['power_to_grid']

#########################################################################################################
################################  GETTING SOME NUMBERS FOR FURTHER ANALYSIS     #########################
#########################################################################################################
sum_positives = df_clean.loc [df_clean ['power_excess'] >= 0, 'power_excess'].sum ().round (2)
sum_negatives = df_clean.loc [df_clean ['power_excess'] < 0, 'power_excess'].sum ().round (2)
sum_consumo = df_clean ['Consumo (kWh)'].sum ().round (2)
sum_power_solar = df_clean ['power_solar'].sum ().round (2)

# for selling power to the grid without batteries installation. We must group by month as companies reset account monthly.
# these are two series with monthly results for selling and buying
monthly_sell_nobat = df_clean.groupby ('Mes') ['venta €'].sum ()
monthly_buy_nobat = df_clean.groupby ('Mes') ['compra €'].sum ()
list_net_nobat = monthly_buy_nobat - monthly_sell_nobat
list_net_nobat = [0 if x <= 0 else x for x in list_net_nobat]
net_sell_buy_nobat = sum (list_net_nobat)

# for selling power to the grid WITH batteries installation. We must group by month as companies reset account monthly.
# these are two series with monthly results for selling and buying
monthly_sell_bat = df_clean.groupby ('Mes') ['venta_bat_€'].sum ()
monthly_buy_bat = df_clean.groupby ('Mes') ['compra_bat_€'].sum ()
list_net_bat = monthly_buy_bat - monthly_sell_bat
list_net_bat = [0 if x <= 0 else x for x in list_net_bat]
net_sell_buy_bat = sum (list_net_bat)

# show_df_info (df_clean)
st.write ('### Tabla con el cálculo de valores ')
st.markdown ("""
Tabla de valores utilizados para la analítica. 
* **irr:** Potencia de salida en Wh del panel teórico de 1Kw. Corregida según horario de verano o invierno.
* **power_solar:** Es irr multiplicado por la potencia de nuestra instalación.
* **power_excess:** Energía producida por la instalación menos el consumo. Si es negativo estaremos usando batería o red.
* **venta €:** Dinero ganado por la instalación al vender a la red si no hay baterías.
* **compra €:** Dinero pagado a la red por consumo si no hay baterías.
* **power_buffer:** Energía almacenada en las baterías.
* **power_to_grid:** Energía en exceso que volcamos a la red si tenemos baterías.
* **compra_bat_€:** Coste de energía comprada cuando no producimos y las baterías están agotadas.
* **venta_bat_€:** Venta de energía cuando las baterías están llenas y la instalación sigue produciendo.



""")
st.write (df_clean)

#########################################################################################################
########################################  Graphs plotting  ##############################################
#########################################################################################################

st.write ('### Gráficos de energía ')

fig = px.line (df_clean, x='Fecha con hora', y='power_solar', title="Energía entregada por los paneles en Kwh")
st.plotly_chart (fig, use_container_width=True)

fig = px.line (df_clean, x='Fecha con hora', y='power_excess',
               title="Exceso y déficit de energía según consumo y potencia generada por los paneles en Kwh")
st.plotly_chart (fig, use_container_width=True)

fig = px.line (df_clean, x='Fecha con hora', y='power_buffer', title="Energía en baterias en Kwh")
st.plotly_chart (fig, use_container_width=True)

#########################################################################################################
########################################## Tables with general results ##################################
#########################################################################################################

st.write ('### Resumen de valores generales de la intalación')

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
               ['Multiplicación de la demanda:', str (increase_demand)],
               ['Precio de compra por la compañía:', str (percent_buy * 100) + '%  del precio de venta']]

table_p = ff.create_table (table_param, colorscale=colorscale)
table_p.layout.width = tables_width
font_resize (table_p)
st.plotly_chart (table_p, use_container_width=False)

######## ---- for energy resume table ---- ########

table_ener_summary = [['Resumen energético', 'Valor'],
                      ['El consumo de energía en el edificio ha sido:', str (sum_consumo) + ' Kwh'],
                      ['La energía producida por los paneles solares:', str (sum_power_solar) + ' Kwh'],
                      ['Exceso de energía para vender o almacenar:', str (sum_positives) + ' Kwh'],
                      ['Déficit de energía a comprar si no hay baterias:', str (sum_negatives) + ' Kwh']]

table_es = ff.create_table (table_ener_summary, colorscale=colorscale)
table_es.layout.width = tables_width
font_resize (table_es)
st.plotly_chart (table_es, use_container_width=False)

########################################################################################################
########################     Instalation: NO BATTERIES + EXCESS SALE    ################################
########################################################################################################
st.write ('')
st.write ('')
st.write ('### Instalación SIN baterías y CON venta de exceso ')

######### table  #########

table_eur_nobat = [['SIN baterías y CON venta del exceso', 'Valor'],
                   ['Por venta de energía ** ', str (round (sum (monthly_sell_nobat), 2)) + ' €'],
                   ['Por compra de energía fuera del horario de produccion:',
                    str (round (sum (monthly_buy_nobat), 2)) + ' €'],
                   ['La diferencia VENTA - COMPRA:', str (round (net_sell_buy_nobat, 2)) + ' €']]

table_enb = ff.create_table (table_eur_nobat, colorscale=colorscale2)
table_enb.layout.width = tables_width
font_resize (table_enb)
st.plotly_chart (table_enb, use_container_width=False)

######### graph  #########

months = monthly_sell_nobat.index

fig = go.Figure (data=[
    go.Bar (name='Ventas', x=months, y=monthly_sell_nobat, marker_color='#137d4f'),
    go.Bar (name='Compras', x=months, y=monthly_buy_nobat, marker_color='#b8f0d8'),
    go.Bar (name='Diferencia', x=months, y=list_net_nobat, marker_color='red')]
)
fig.update_layout (barmode='group',
                   title='Venta y compra de energía por meses en EUROS, instación SIN baterías.',
                   yaxis=dict (title='Euros'),
                   xaxis=dict (title='Mes del año')
                   )
st.write (fig)

st.write (
    "Los valores en rojo significan que la compensación de la compañía no llega a cubrir tu gasto.  \n Por tanto se debe pagar la banda roja: " + str (
        round (net_sell_buy_nobat, 2)) + ' €')

########################################################################################################
########################     Instalation: WITH BATTERIES AND NO EXCESS SALE    #########################
########################################################################################################
st.write ('')
st.write ('')
st.write ('### Instalación CON baterías y SIN venta de exceso ')

######### table  #########

table_eur_bat = [['CON baterías y SIN venta del exceso', 'Valor'],
                 ['Por compra cuando las baterias están agotadas:', str (round (sum (monthly_buy_bat), 2)) + ' €']]

table_eb = ff.create_table (table_eur_bat, colorscale=colorscale2)
table_eb.layout.width = tables_width
font_resize (table_eb)
st.plotly_chart (table_eb, use_container_width=False)

######### graph  #########

fig = go.Figure (data=[
    go.Bar (name='Compras', x=months, y=monthly_buy_bat, marker_color='#b8f0d8')])

fig.update_layout (title='Compra de energía por meses en EUROS, instación CON baterías y SIN venta de exceso.',
                   yaxis=dict (title='Euros'),
                   xaxis=dict (title='Mes del año')
                   )
st.write (fig)

st.write (
    "Los valores en rojo significan que la compensación de la compañía no llega a cubrir tu gasto.  \n Por tanto se debe pagar la banda roja: " + str (
        round (net_sell_buy_nobat, 2)) + ' €')

########################################################################################################
########################     Instalation: WITH BATTERIES + EXCESS SALE    ##############################
########################################################################################################
st.write ('')
st.write ('')
st.write ('### Instalación CON baterías y CON venta de exceso ')

######### table  #########

table_eur_bat_sell = [['CON baterías y CON venta del exceso', 'Valor'],
                      ['Por venta de energía ** ', str (round (sum (monthly_sell_bat), 2)) + ' €'],
                      ['Por compra de energía al estar sin sol y sin baterías:',
                       str (round (sum (monthly_buy_bat), 2)) + ' €'],
                      ['La diferencia VENTA - COMPRA:', str (round (net_sell_buy_bat, 2)) + ' €']]

table_ebs = ff.create_table (table_eur_bat_sell, colorscale=colorscale2)
table_ebs.layout.width = tables_width
font_resize (table_ebs)
st.plotly_chart (table_ebs, use_container_width=False)

st.write (' ** la venta de energía se produce al ' + str (percent_buy * 100) + '% del precio de compra en cada tramo. ')
st.write ('')

######### graph  #########

fig = go.Figure (data=[
    go.Bar (name='Ventas teóricas', x=months, y=monthly_sell_bat, marker_color='#137d4f'),
    go.Bar (name='Compras', x=months, y=monthly_buy_bat, marker_color='#b8f0d8'),
    go.Bar (name='Diferencia', x=months, y=list_net_bat, marker_color='red')]
)
fig.update_layout (barmode='group',
                   title='Venta y compra de energía por meses en EUROS, instación CON baterías.',
                   yaxis=dict (title='Euros'),
                   xaxis=dict (title='Mes del año')
                   )
st.write (fig)

st.write (
    "La compensación mensual de la compañía hace que si inyectas a red más de lo que has consumido ese mes.  \n la diferencia sea cero y no te abonan nada."
    "  \n Si aparecen valores en rojo, son los que tienes que abonar a la compañía.")


