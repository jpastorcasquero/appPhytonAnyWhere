# Importamos las librerías necesarias
import os

import pandas as pd  # Tratamiento de datos
import numpy as np  # Tratamiento de datos
import requests  # Importamos datos de una dirección web
from datetime import date, datetime  # Manejo de fechas y horas
import time  # Utilizamos formatos de tiempo
import openmeteo_requests  # Solicitudes a la API de OpenMeteo
import requests_cache  # Almacenamiento en caché de las solicitudes HTTP
from retry_requests import retry  # Reintentar solicitudes HTTP en caso de fallos temporales
import pickle  # Para importar el modelo
from flask import Flask, jsonify  # Para crear la aplicación Flask y devolver respuestas JSON

def obtener_prediccion():
    # Cargar tabla para convertir el tiempo a formato numérico y adaptarlo al modelo
    df_tiempo = pd.read_csv('https://raw.githubusercontent.com/jpastorcasquero/Colab/main/CodigosTiempoOpenMeteo.csv', sep=';')
    # Cargar calendario laboral 2025
    df_calendario = pd.read_csv('https://raw.githubusercontent.com/jpastorcasquero/Colab/main/calendario2025.csv', sep=';')

    # Configurar una sesión de caché para almacenar las solicitudes HTTP
    cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
    # Configurar una sesión con reintentos para manejar fallos temporales
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    # Crear un cliente de OpenMeteo utilizando la sesión con reintentos
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # Parámetros para la solicitud a la API de OpenMeteo
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        "latitude": 41.6552,  # Latitud de la ubicación
        "longitude": -4.7237,  # Longitud de la ubicación
        "hourly": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "weather_code", "wind_speed_10m"],
        "timezone": "Europe/Berlin",  # Zona horaria
        "forecast_days": 16,  # Número de días de pronóstico
        "wind_speed_unit": "ms"  # Unidad de velocidad del viento
    }

    # Realizar la solicitud a la API de OpenMeteo
    responses = openmeteo.weather_api(url, params=params)
    response = responses[0]

    # Procesar los datos horarios
    hourly = response.Hourly()
    hourly_data = {
        "date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        ),
        "temperature_2m": hourly.Variables(0).ValuesAsNumpy(),
        "relative_humidity_2m": hourly.Variables(1).ValuesAsNumpy(),
        "apparent_temperature": hourly.Variables(2).ValuesAsNumpy(),
        "weather_code": hourly.Variables(3).ValuesAsNumpy(),
        "wind_speed_10m": hourly.Variables(4).ValuesAsNumpy()
    }

    # Crear un DataFrame de pandas con los datos horarios
    hourly_dataframe = pd.DataFrame(data=hourly_data)
    hourly_dataframe.rename(columns={
        'date': 'datetime',
        'temperature_2m': 'temp',
        'relative_humidity_2m': 'humidity',
        'apparent_temperature': 'atemp',
        'weather_code': 'weather',
        'wind_speed_10m': 'windspeed'
    }, inplace=True)

    # Convertir la columna datetime a formato datetime y eliminar la zona horaria
    hourly_dataframe['datetime'] = pd.to_datetime(hourly_dataframe['datetime']).dt.tz_localize(None)
    # Reemplazar los valores en la columna weather con los valores correspondientes en df_tiempo
    hourly_dataframe['weather'] = hourly_dataframe['weather'].map(df_tiempo.set_index('codigo')['valor'])
    # Añadir la columna season al DataFrame hourly
    hourly_dataframe['season'] = hourly_dataframe['datetime'].apply(lambda x: get_season(x.date()))
    # Convertir la columna datetime a formato de cadena
    hourly_dataframe['datetime'] = hourly_dataframe['datetime'].astype(str)

    # Convertir la columna 'datetime' a formato de fecha
    hourly_dataframe['datetime'] = pd.to_datetime(hourly_dataframe['datetime'])

    # Convertir la columna 'Fecha' a formato de fecha
    df_calendario['Fecha'] = pd.to_datetime(df_calendario['Fecha'], format='%d/%m/%Y')

    # Función para buscar y añadir los valores de 'holiday' y 'workingday'
    def añadir_columnas(row):
        fecha_buscar = row['datetime'].normalize()  # Normalizar la fecha para eliminar la hora
        resultado = df_calendario.loc[df_calendario['Fecha'] == fecha_buscar]
        if not resultado.empty:
            row['holiday'] = resultado['holiday'].values[0]
            row['workingday'] = resultado['workingday'].values[0]
        else:
            row['holiday'] = None
            row['workingday'] = None
        return row

    # Aplicar la función a cada fila del DataFrame
    hourly_dataframe = hourly_dataframe.apply(añadir_columnas, axis=1)

    df = hourly_dataframe.copy()
    df_original = df.copy()

    # Separar la temporada y el clima en columnas dummy
    df = pd.concat([df, pd.get_dummies(df['season'], prefix='season')], axis=1)
    df = pd.concat([df, pd.get_dummies(df['weather'], prefix='weather')], axis=1)
    df.drop(['season', 'weather'], axis=1, inplace=True)

    # Pasar datetime a columnas independientes
    df["hour"] = pd.DatetimeIndex(df.datetime).hour
    df["day"] = pd.DatetimeIndex(df.datetime).day
    df["month"] = pd.DatetimeIndex(df.datetime).month
    df["year"] = pd.DatetimeIndex(df.datetime).year.map(lambda x: x - 2000)
    df["day_of_week"] = pd.DatetimeIndex(df.datetime).dayofweek
    df.drop('datetime', axis=1, inplace=True)

    # Ajustar el valor de las columnas al tipo de dato correcto
    df['temp'] = df['temp'].astype(float)
    df['atemp'] = df['atemp'].astype(float)
    df['humidity'] = df['humidity'].astype(int)
    df['windspeed'] = df['windspeed'].astype(float)

    # Añadir columnas faltantes con valor False
    cabecera = ['holiday', 'workingday', 'temp', 'atemp', 'humidity', 'windspeed',
                'season_1', 'season_2', 'season_3', 'season_4', 'weather_1',
                'weather_2', 'weather_3', 'weather_4', 'hour', 'day', 'month', 'year', 'day_of_week']
    for col in cabecera:
        if col not in df.columns:
            df[col] = False

    df = df[cabecera]

    # Importar el modelo desde un fichero
    model_path = os.path.expanduser("~/JPC/Classifier/clf.pkl")
    with open(model_path, 'rb') as file:
        modelo = pickle.load(file)

    # Realizar la predicción
    test2 = modelo.predict(df)
    df['Count_Predict'] = test2.astype(int)
    df_original['Count_Predict'] = test2.astype(int)

    file_dir = os.path.expanduser('~/JPC/Predicciones')
    os.makedirs(file_dir, exist_ok=True)
    filename = os.path.join(file_dir, f"{time.strftime('%Y%m%d')}_Prediccion.xlsx")
    df.to_excel(filename, index=False)
    filename = os.path.join(file_dir, f"{time.strftime('%Y%m%d')}_Original.xlsx")
    df_original.to_excel(filename, index=False)

    return jsonify(df_original.to_dict(orient='records')), 200

# Función que recibe una fecha y devuelve la estación
def get_season(fecha):
    Y = datetime.now().year
    estaciones = [
        ('4', date(Y, 1, 1), date(Y, 3, 20)),  # Invierno
        ('1', date(Y, 3, 21), date(Y, 6, 20)),  # Primavera
        ('2', date(Y, 6, 21), date(Y, 9, 22)),  # Verano
        ('3', date(Y, 9, 23), date(Y, 12, 20)),  # Otoño
        ('4', date(Y, 12, 21), date(Y, 12, 31))  # Invierno
    ]
    for estacion, inicio, fin in estaciones:
        if inicio <= fecha <= fin:
            return estacion
