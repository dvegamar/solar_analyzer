import pandas as pd


def clean_xls (xls):
    df = pd.read_excel (xls)
    df = df.dropna (axis=0, how='any')
    return df


def CleanCR (uploaded_files):
    # with merge and outer we merge the individual dataframes
    # outer removes repeated rows, as the second row with names and in case the user uploaded repeated files and rows

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
    df_clean.drop (['Hour_DT'], inplace=True,
                   axis=1)  # there is a bug in streamlit with timedeltas, so need to drop column
    df_clean ['Mes'] = df_clean ['Fecha'].dt.month

    return df_clean
