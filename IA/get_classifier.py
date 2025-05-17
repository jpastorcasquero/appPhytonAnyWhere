import os
import pickle
import warnings
import numpy as np
import pandas as pd
from tqdm import tqdm
from datetime import datetime
from flask import jsonify
from sklearn.model_selection import train_test_split
from sklearn.utils import all_estimators
from sklearn.metrics import mean_squared_log_error, accuracy_score
from sklearn.linear_model import ElasticNet, LinearRegression
from sklearn.tree import DecisionTreeRegressor
from Logger.logger import Logger

# Configurar warnings
warnings.filterwarnings('ignore')

# Logger
home_dir = os.path.expanduser("~")
log_path = os.path.join(home_dir, 'JPC', 'log.txt')
logger = Logger(log_path)

def obtener_clasificador():
    try:
        logger.log("🚀 Lanzando get_clasiffier")

        # Cargar datos
        train = pd.read_csv('https://raw.githubusercontent.com/jpastorcasquero/Colab/main/train.csv')
        df = train.copy()

        # Limpiar columnas dummy antiguas si existen
        for col in ['season_1', 'season_2', 'season_3', 'season_4', 'weather_1', 'weather_2', 'weather_3', 'weather_4']:
            df.drop(columns=[col], errors='ignore', inplace=True)

        # One-hot encoding
        df = pd.concat([df, pd.get_dummies(df['season'], prefix='season')], axis=1)
        df = pd.concat([df, pd.get_dummies(df['weather'], prefix='weather')], axis=1)
        df.drop(['season', 'weather'], axis=1, inplace=True)

        # Features desde datetime
        df["hour"] = pd.to_datetime(df.datetime).dt.hour
        df["day"] = pd.to_datetime(df.datetime).dt.day
        df["month"] = pd.to_datetime(df.datetime).dt.month
        df["year"] = pd.to_datetime(df.datetime).dt.year.map(lambda y: y - 2000)
        df["day_of_week"] = pd.to_datetime(df.datetime).dt.dayofweek
        df.drop('datetime', axis=1, inplace=True)

        # Eliminar columnas no necesarias
        df.drop(columns=['casual', 'registered'], errors='ignore', inplace=True)

        # Split de datos
        x_train, x_test, y_train, y_test = train_test_split(df.drop('count', axis=1), df['count'], test_size=0.25, random_state=42)

        # Entrenar todos los modelos regresores
        estimators = all_estimators(type_filter='regressor')
        resultados = []

        for name, Regressor in tqdm(estimators, desc="Entrenando modelos"):
            try:
                if name in ['CCA', 'PLSCanonical']:
                    model = Regressor(n_components=1)
                elif name in ['MultiTaskElasticNet', 'MultiTaskElasticNetCV', 'MultiTaskLasso', 'MultiTaskLassoCV']:
                    model = ElasticNet()
                elif name in ['StackingRegressor', 'VotingRegressor']:
                    sub_estimators = [('lr', LinearRegression()), ('dt', DecisionTreeRegressor())]
                    model = Regressor(estimators=sub_estimators)
                else:
                    model = Regressor()

                model.fit(x_train, y_train)
                pred = np.abs(model.predict(x_test))
                rmsle = np.sqrt(mean_squared_log_error(pred, y_test))
                accuracy = accuracy_score(y_test, pred.astype(int)) * 100

                resultados.append({
                    "Modelo": name,
                    "RMSLE": round(rmsle, 5),
                    "Precision": round(accuracy, 2),
                    "Model": model
                })
            except Exception:
                continue

        # Preparar dataframe
        df_result = pd.DataFrame(resultados).sort_values(by="RMSLE").head(10)

        # Guardar mejor modelo
        mejor_modelo = df_result.iloc[0]["Model"]
        mejor_modelo.fit(x_train, y_train)

        model_path = os.path.expanduser("~/JPC/Classifier/clf.pkl")
        os.makedirs(os.path.dirname(model_path), exist_ok=True)
        with open(model_path, 'wb') as f:
            pickle.dump(mejor_modelo, f)

        logger.log(f"✅ Modelo más preciso: {df_result.iloc[0]['Modelo']}")

        # Limpiar columna no serializable
        df_result.drop(columns=["Model"], inplace=True)
        return jsonify(df_result.to_dict(orient="records")), 200

    except Exception as e:
        logger.log(f"❌ Error en get_clasiffier: {e}")
        return jsonify({"error": str(e)}), 500
