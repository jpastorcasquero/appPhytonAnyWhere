import os
from datetime import datetime
from flask import Flask, jsonify
from sklearn.model_selection import train_test_split
from sklearn.utils import all_estimators
from sklearn.metrics import mean_squared_log_error, accuracy_score
from sklearn.linear_model import ElasticNet, LinearRegression
from sklearn.tree import DecisionTreeRegressor
import pickle
from tqdm import tqdm
import pandas as pd
import numpy as np
import warnings
from Logger.logger import Logger

# Configuración de advertencias para ignorar mensajes molestos
warnings.filterwarnings('ignore')

# Define la ruta para el archivo de log en "Archivos de Programa/JPC"
program_files = os.getenv('ProgramFiles')
log_path = os.path.join(program_files, 'JPC', 'log.txt')
logger = Logger(log_path)

def obtener_clasificador():
    try:
        # Registrar el inicio de la función get_clasiffier
        logger.log("Se ha lanzado get_clasiffier")
        #logger.log_to_db(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), "Se ha lanzado get_clasiffier")

        # Cargar datos desde un archivo CSV en GitHub
        try:
            train = pd.read_csv('https://raw.githubusercontent.com/jpastorcasquero/Colab/main/train.csv')
            df = train.copy()
        except Exception as e:
            logger.log(f"Error al obtener los datos de GitHub. Compruebe su conexión. {e}")
            #logger.log_to_db(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Error al obtener los datos de GitHub. Compruebe su conexión. {e}")

        # Preprocesamiento de datos
        try:
            df = df.drop(['season_1', 'season_2', 'season_3', 'season_4'], axis=1)
        except KeyError:
            pass

        # Convertir la columna 'season' en variables dummy
        season = pd.get_dummies(df['season'], prefix='season')
        df = pd.concat([df, season], axis=1)

        try:
            df = df.drop(['weather_1', 'weather_2', 'weather_3', 'weather_4'], axis=1)
        except KeyError:
            pass

        # Convertir la columna 'weather' en variables dummy
        weather = pd.get_dummies(df['weather'], prefix='weather')
        df = pd.concat([df, weather], axis=1)

        # Eliminar columnas originales 'season' y 'weather'
        df.drop(['season', 'weather'], inplace=True, axis=1)

        # Extraer características de la columna 'datetime'
        df["hour"] = [t.hour for t in pd.DatetimeIndex(df.datetime)]
        df["day"] = [t.day for t in pd.DatetimeIndex(df.datetime)]
        df["month"] = [t.month for t in pd.DatetimeIndex(df.datetime)]
        df['year'] = [t.year for t in pd.DatetimeIndex(df.datetime)]
        df["day_of_week"] = [t.dayofweek for t in pd.DatetimeIndex(df.datetime)]

        # Mapear el año para que sea relativo al año 2000
        year_mapping = {year: year - 2000 for year in range(2000, 2100)}
        df['year'] = df['year'].map(year_mapping)

        # Eliminar la columna 'datetime'
        df.drop('datetime', axis=1, inplace=True)

        # Eliminar columnas no necesarias si existen
        if 'casual' in df.columns:
            df.drop(['casual'], axis=1, inplace=True)
        if 'registered' in df.columns:
            df.drop(['registered'], axis=1, inplace=True)

        # Dividir los datos en conjuntos de entrenamiento y prueba
        x_train, x_test, y_train, y_test = train_test_split(df.drop('count', axis=1), df['count'], test_size=0.25, random_state=42)

        # Obtener todos los estimadores de tipo regresor
        estimators = all_estimators(type_filter='regressor')
        model_names = []
        rmsle = []
        precision = []
        models = []

        # Barra de progreso para el entrenamiento de modelos
        for name, RegressorClass in tqdm(estimators, desc="Entrenando modelos"):
            try:
                # Configurar modelos específicos con parámetros especiales
                if name in ['CCA', 'PLSCanonical']:
                    clf = RegressorClass(n_components=1)
                elif name in ['MultiTaskElasticNet', 'MultiTaskElasticNetCV', 'MultiTaskLasso', 'MultiTaskLassoCV']:
                    clf = ElasticNet()
                elif name in ['StackingRegressor', 'VotingRegressor']:
                    estimators = [('lr', LinearRegression()), ('dt', DecisionTreeRegressor())]
                    clf = RegressorClass(estimators=estimators)
                else:
                    clf = RegressorClass()

                # Entrenar el modelo y calcular métricas
                clf.fit(x_train, y_train)
                test_pred = clf.predict(x_test)
                test_pred = np.abs(test_pred)
                rmsle_value = np.sqrt(mean_squared_log_error(test_pred, y_test))
                precision_value = accuracy_score(y_test, test_pred.astype(int)) * 100
                model_names.append(name)
                rmsle.append(rmsle_value)
                precision.append(precision_value)
                models.append(clf)
            except ValueError as ve:
                pass  # Ignorar errores de valor
            except TypeError as te:
                pass  # Ignorar errores de tipo
            except Exception as e:
                pass  # Ignorar otros errores

        # Crear DataFrame con los resultados
        d = {'Modelo': model_names, 'RMSLE': rmsle, "Precision": precision, "Model": models}
        rmsle_frame = pd.DataFrame(d)

        # Ordenar DataFrame por RMSLE en orden ascendente
        rmsle_frame_sorted = rmsle_frame.sort_values(by='RMSLE')

        # Seleccionar los 10 primeros modelos
        top_10_rmsle_frame = rmsle_frame_sorted.head(10)

        # Obtener el modelo con el menor RMSLE
        min_value = rmsle_frame['RMSLE'].min()
        modelo_win = rmsle_frame.loc[rmsle_frame['RMSLE'] == min_value, 'Model'].iloc[0]
        name_modelo_win = rmsle_frame.loc[rmsle_frame['RMSLE'] == min_value, 'Modelo'].iloc[0]
        clf = modelo_win
        clf.fit(x_train, y_train)
        logger.log(f"El modelo más preciso es: {name_modelo_win}")
        #logger.log_to_db(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"El modelo más preciso es: {name_modelo_win}")

        # Guardar el modelo entrenado en un archivo
        model_path = os.path.expanduser("~/JPC/Classifier/clf.pkl")
        with open(model_path, 'wb') as file:
            pickle.dump(clf, file)

        # Eliminar la columna de modelos del DataFrame antes de devolverlo
        top_10_rmsle_frame.drop(columns=["Model"], inplace=True)
        return jsonify(top_10_rmsle_frame.to_dict(orient='records')), 200
    except Exception as e:
        logger.log(f"Error al obtener el clasificador: {e}")
        #logger.log_to_db(datetime.now().strftime("%Y-%m-%d %H:%M:%S"), f"Error al obtener el clasificador: {e}")
        return False
