# this script takes csv files from energiaXXI, creates a df and reformats this
# df so it has the same fields as the xls file imported from comerciliazadora regulada
# which is the one used for the first case and makes sense with the rest of the
# energy_analizer_app.py script


import pandas as pd


def clean_csv (csv):
    df = pd.read_csv (csv, sep=';')
    df = df.iloc [0:, [1, 2, 3]]
    df = df.dropna (axis=0, how='any')
    df ['Hora'] = df ['Hora'].apply (lambda x: x - 1)
    return df


def CleanS21 (uploaded_files):

    df_clean = clean_csv (uploaded_files [0])
    for i in range (1, len (uploaded_files)):
        last_df = clean_csv (uploaded_files [i])
        df_clean = pd.merge (df_clean, last_df, how='outer')

    # rename columns to match main script
    df_clean.rename(columns={'Hora':'Hora Desde', 'AE_kWh':'Consumo (kWh)'}, inplace = True)
    df_clean ['Fecha'] = pd.to_datetime (df_clean ['Fecha'], format='%d/%m/%Y')
    df_clean ['Consumo (kWh)'] = df_clean ['Consumo (kWh)'].str.replace (',', '.').astype (float)

    # load the prices csv to another dataframe and adapt to df_clean fields
    df_pvpc = pd.read_csv ('datos/pvpc_21_22.csv')
    df_pvpc ['Hora'] = df_pvpc [['Hora']].astype (int)
    df_pvpc ['Hora'] = df_pvpc ['Hora'].apply (lambda x: x - 1)
    df_pvpc ['Precio'] = df_pvpc ['Precio'].apply (lambda x: x/1000)
    df_pvpc.rename (columns={'Precio': 'Precio horario de energía (€/kWh)', 'Hora': 'Hora Desde'}, inplace=True)
    df_pvpc ['Fecha'] = pd.to_datetime (df_pvpc ['Fecha'], format='%Y/%m/%d')

    # now merge both dataframes to add the prices column matching date and hour
    df_clean = df_clean.merge(df_pvpc, how='inner', on =['Fecha','Hora Desde' ])

    # add Importe horario de energía (€)
    df_clean ['Importe horario de energía (€)'] = df_clean ['Precio horario de energía (€/kWh)']*df_clean ['Consumo (kWh)']

    # add column with data plus hour to get more precise graphs
    df_clean ['Hour_DT'] = pd.to_timedelta (df_clean ['Hora Desde'], 'h')
    df_clean ['Fecha con hora'] = df_clean ['Fecha'] + df_clean ['Hour_DT']
    df_clean.drop (['Hour_DT'], inplace=True,
                   axis=1)  # there is a bug in streamlit with timedeltas, so need to drop column
    df_clean ['Mes'] = df_clean ['Fecha'].dt.month

    return df_clean
