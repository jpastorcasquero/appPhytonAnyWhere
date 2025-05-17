import os
import time
import pickle
import pandas as pd
import numpy as np
from datetime import date, datetime
from flask import jsonify
import openmeteo_requests
import requests_cache
from retry_requests import retry
from Logger.logger import Logger

# Logger
log_path = os.path.expanduser('~/JPC/log.txt')
logger = Logger(log_path)

def obtener_prediccion():
    try:
        # Cargar códigos meteorológicos y calendario laboral
        df_tiempo = pd.read_csv('https://raw.githubusercontent.com/jpastorcasquero/Colab/main/CodigosTiempoOpenMeteo.csv', sep=';')
        df_calendario = pd.read_csv('https://raw.githubusercontent.com/jpastorcasquero/Colab/main/calendario2025.csv', sep=';')

        # Configurar cliente OpenMeteo con caché y reintentos
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        openmeteo = openmeteo_requests.Client(session=retry_session)

        # Parámetros de la API
        url = "https://api.open-meteo.com/v1/forecast"
        params = {
            "latitude": 41.6552,
            "longitude": -4.7237,
            "hourly": ["temperature_2m", "relative_humidity_2m", "apparent_temperature", "weather_code", "wind_speed_10m"],
            "timezone": "Europe/Berlin",
            "forecast_days": 16,
            "wind_speed_unit": "ms"
        }

        # Obtener datos horarios
        response = openmeteo.weather_api(url, params=params)[0]
        hourly = response.Hourly()
        df = pd.DataFrame({
            "datetime": pd.date_range(
                start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
                end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
                freq=pd.Timedelta(seconds=hourly.Interval()),
                inclusive="left"
            ).tz_localize(None),
            "temp": hourly.Variables(0).ValuesAsNumpy(),
            "humidity": hourly.Variables(1).ValuesAsNumpy(),
            "atemp": hourly.Variables(2).ValuesAsNumpy(),
            "weather": hourly.Variables(3).ValuesAsNumpy(),
            "windspeed": hourly.Variables(4).ValuesAsNumpy()
        })

        # Mapear clima y temporada
        df['weather'] = df['weather'].map(df_tiempo.set_index('codigo')['valor'])
        df['season'] = df['datetime'].apply(lambda x: get_season(x.date()))
        df_calendario['Fecha'] = pd.to_datetime(df_calendario['Fecha'], format='%d/%m/%Y')

        def add_calendar_cols(row):
            match = df_calendario[df_calendario['Fecha'] == row['datetime'].normalize()]
            if not match.empty:
                row['holiday'] = match['holiday'].values[0]
                row['workingday'] = match['workingday'].values[0]
            else:
                row['holiday'] = None
                row['workingday'] = None
            return row

        df = df.apply(add_calendar_cols, axis=1)
        df_original = df.copy()

        # One-hot encoding
        df = pd.concat([df, pd.get_dummies(df['season'], prefix='season')], axis=1)
        df = pd.concat([df, pd.get_dummies(df['weather'], prefix='weather')], axis=1)
        df.drop(['season', 'weather'], axis=1, inplace=True)

        # Extraer componentes de fecha
        df["hour"] = df["datetime"].dt.hour
        df["day"] = df["datetime"].dt.day
        df["month"] = df["datetime"].dt.month
        df["year"] = df["datetime"].dt.year.map(lambda y: y - 2000)
        df["day_of_week"] = df["datetime"].dt.dayofweek
        df.drop("datetime", axis=1, inplace=True)

        # Asegurar columnas esperadas por el modelo
        expected_columns = ['holiday', 'workingday', 'temp', 'atemp', 'humidity', 'windspeed',
                            'season_1', 'season_2', 'season_3', 'season_4',
                            'weather_1', 'weather_2', 'weather_3', 'weather_4',
                            'hour', 'day', 'month', 'year', 'day_of_week']
        for col in expected_columns:
            if col not in df.columns:
                df[col] = 0  # Valor por defecto si falta

        df = df[expected_columns]

        # Cargar modelo
        model_path = os.path.expanduser('~/JPC/Classifier/clf.pkl')
        with open(model_path, 'rb') as file:
            model = pickle.load(file)

        # Predecir
        predictions = model.predict(df)
        df['Count_Predict'] = predictions.astype(int)
        df_original['Count_Predict'] = predictions.astype(int)

        # Guardar resultados
        output_dir = os.path.expanduser('~/JPC/Predicciones')
        os.makedirs(output_dir, exist_ok=True)
        df.to_excel(os.path.join(output_dir, f"{time.strftime('%Y%m%d')}_Prediccion.xlsx"), index=False)
        df_original.to_excel(os.path.join(output_dir, f"{time.strftime('%Y%m%d')}_Original.xlsx"), index=False)

        logger.log("✅ Predicción generada y guardada correctamente.")
        return jsonify(df_original.to_dict(orient='records')), 200

    except Exception as e:
        logger.log(f"❌ Error al obtener la predicción: {e}")
        return jsonify({"error": str(e)}), 500


def get_season(fecha):
    Y = fecha.year
    estaciones = [
        ('4', date(Y, 1, 1), date(Y, 3, 20)),
        ('1', date(Y, 3, 21), date(Y, 6, 20)),
        ('2', date(Y, 6, 21), date(Y, 9, 22)),
        ('3', date(Y, 9, 23), date(Y, 12, 20)),
        ('4', date(Y, 12, 21), date(Y, 12, 31))
    ]
    for estacion, inicio, fin in estaciones:
        if inicio <= fecha <= fin:
            return estacion
