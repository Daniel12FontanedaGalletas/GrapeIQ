# app/jobs/forecast/job.py
#
# Este archivo contiene la lógica para el job de pronóstico (forecast)
# por lotes, utilizando LightGBM y una lógica de fallback.
# Se ha modificado para usar la librería `psycopg2` de forma síncrona.

import os
import pandas as pd
import numpy as np
import logging
from uuid import UUID
import psycopg2
import lightgbm as lgb
from datetime import date, timedelta
from typing import List

# Configuración del logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Configuración de la base de datos
# En un entorno real, estas variables vendrían de un gestor de secretos o variables de entorno.
DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://user:password@localhost:5432/dbname")

def get_sales_data(tenant_id: UUID) -> pd.DataFrame:
    """
    Obtiene los datos históricos de ventas para un cliente (tenant) específico
    y los prepara para el pronóstico usando `psycopg2`.
    """
    conn = None
    try:
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT sku, date, qty FROM sales WHERE tenant_id = %s ORDER BY date",
            (str(tenant_id),)
        )
        records = cursor.fetchall()
        
        if not records:
            return pd.DataFrame()

        df = pd.DataFrame(records, columns=['sku', 'date', 'qty'])
        df['date'] = pd.to_datetime(df['date'])
        df = df.pivot_table(index='date', columns='sku', values='qty').fillna(0).reset_index()
        
        # Aseguramos que el índice sea el `date` para el resample
        df.set_index('date', inplace=True)
        return df
    except Exception as e:
        logging.error(f"Error al obtener datos de ventas: {e}")
        return pd.DataFrame()
    finally:
        if conn:
            conn.close()

def create_features(df: pd.DataFrame) -> pd.DataFrame:
    """
    Ingeniería de características simple para el modelo de pronóstico.
    Crea características como día de la semana, mes y lags.
    """
    df['weekday'] = df.index.weekday
    df['month'] = df.index.month
    df['day_of_month'] = df.index.day
    
    # Lags para la serie temporal
    for lag in [7, 14, 28]:
        # Usamos el total de ventas para simplificar
        df[f'lag_{lag}'] = df.sum(axis=1).shift(lag).fillna(0)
        
    return df

def simple_moving_average(series: pd.Series, window: int) -> float:
    """
    Calcula el pronóstico usando la media móvil simple.
    """
    if len(series) < window:
        return series.mean() if not series.empty else 0
    return series.iloc[-window:].mean()

def run_forecast_job(tenant_id: UUID, forecast_horizon: int = 14):
    """
    Función principal para ejecutar el job de pronóstico.
    """
    logging.info(f"Iniciando el job de pronóstico para el tenant: {tenant_id} con un horizonte de {forecast_horizon} días.")

    try:
        sales_df = get_sales_data(tenant_id)
        if sales_df.empty:
            logging.warning(f"No se encontraron datos de ventas para el tenant: {tenant_id}. Job de pronóstico finalizado.")
            return

        skus_processed = 0
        forecast_results = []
        
        for sku in sales_df.columns:
            logging.info(f"Procesando SKU: {sku}")
            
            series = sales_df[sku]
            
            if len(series) < 50:
                logging.warning(f"Pocos datos históricos para SKU {sku}. Usando media móvil.")
                prediction = simple_moving_average(series, 28)
                for i in range(1, forecast_horizon + 1):
                    forecast_results.append({
                        "tenant_id": str(tenant_id),
                        "sku": sku,
                        "date": date.today() + timedelta(days=i),
                        "predicted_qty": prediction,
                        "model_used": "simple_moving_average"
                    })
            else:
                series_df = series.to_frame(name='total_qty')
                series_df = create_features(series_df)

                features = [col for col in series_df.columns if col != 'total_qty']
                target = 'total_qty'
                
                X_train = series_df.iloc[:-forecast_horizon][features]
                y_train = series_df.iloc[:-forecast_horizon][target]
                
                X_predict = series_df.iloc[-forecast_horizon:][features]

                # Rellenar los lags futuros de forma simplificada
                for i in range(1, forecast_horizon + 1):
                    X_predict.loc[X_predict.index[i-1], 'lag_7'] = series_df['total_qty'].iloc[-1]
                    X_predict.loc[X_predict.index[i-1], 'lag_14'] = series_df['total_qty'].iloc[-1]
                    X_predict.loc[X_predict.index[i-1], 'lag_28'] = series_df['total_qty'].iloc[-1]

                lgb_model = lgb.LGBMRegressor()
                lgb_model.fit(X_train, y_train)
                
                predictions = lgb_model.predict(X_predict)
                
                for i, pred_qty in enumerate(predictions):
                    forecast_results.append({
                        "tenant_id": str(tenant_id),
                        "sku": sku,
                        "date": X_predict.index[i].date(),
                        "predicted_qty": max(0, pred_qty),
                        "model_used": "lightgbm"
                    })
            
            skus_processed += 1

        # Guardar las predicciones en la base de datos
        conn = psycopg2.connect(DATABASE_URL)
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM forecasts WHERE tenant_id = %s", (str(tenant_id),))

        insert_query = """
        INSERT INTO forecasts (tenant_id, sku, date, predicted_qty, model_used)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_query, [
            (r['tenant_id'], r['sku'], r['date'], r['predicted_qty'], r['model_used'])
            for r in forecast_results
        ])
        
        conn.commit()

        logging.info(f"Job de pronóstico completado para el tenant: {tenant_id}. SKUs procesados: {skus_processed}. Total de predicciones guardadas: {len(forecast_results)}")

    except Exception as e:
        logging.error(f"Error en el job de pronóstico para el tenant {tenant_id}: {e}", exc_info=True)
    finally:
        if conn:
            conn.close()