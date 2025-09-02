from io import BytesIO
import pandas as pd
from datetime import datetime
from app.services.azure_services.azure_sql_services import SqlService
from app.services.azure_services.azure_storage_services import StorageAccount
from app.core.config import (
    AZURE_STORAGE_CONNECTION_STRING, 
    AZURE_STORAGE_CONTAINER,
    AZURE_STORAGE_DOWNLOAD_PATH
)
from app.core.constants import SummaryQueries
import logging
logging.basicConfig(level=logging.DEBUG)


class ReportManager():
    
    def __init__(self):
        self.db_service = SqlService()

    def execute_summary_report(self, execution_datetime: datetime = datetime.now()):
        execution_datetime_str = execution_datetime.strftime('%Y-%m-%d %H:%M:%S')
        params = (execution_datetime,)
        sq = SummaryQueries()

        # To-Do: Añadir el parametro a la query cuando se tenga data constante 
        df_by_date, data_by_date = self.get_summary_report(sq.SUMMARY_BY_DATE, 'por_fecha')
        df_by_region, data_by_region = self.get_summary_report(sq.SUMMARY_BY_REGION, 'por_region')
        df_by_economic_act, data_by_economic_act = self.get_summary_report(sq.SUMMARY_BY_ECONOMIC_ACT, 'por_actividad_economica')
        
        self.send_report()

        result = {
            'summary_by_date': '',
            'summary_by_region': '',
            'summaty_by_eco': ''
        }
        return result
    
    def get_summary_report(self, query: str, report_name: str, params: tuple = None) -> tuple[pd.DataFrame,list]:
        """
        Genera un reporte resumen a partir de una consulta SQL y 
        devuelve los resultados en un DataFrame de pandas y una lista de diccionarios.
        Parámetros:
            query (str): Consulta SQL a ejecutar.
            report_name (str): Nombre del reporte (no utilizado en el método, pero puede ser útil para futuras extensiones).
            params (tuple, opcional): Parámetros para la consulta SQL (no utilizado en el método actual).
        Retorna:
            tuple[pd.DataFrame, list]: 
                - Un DataFrame de pandas con los resultados de la consulta.
                - Una lista de diccionarios, donde cada diccionario representa una fila del resultado.
        """
        exec_cursor = self.db_service.execute_query(query)
        
        cols = [c[0] for c in exec_cursor.description]
        rows = exec_cursor.fetchall()
        result = [dict(zip(cols, row)) for row in rows]

        df = pd.DataFrame(result, columns=cols)
        if 'execution_datetime' in cols:
            df['execution_datetime'] = df['execution_datetime'].dt.strftime('%d-%m-%Y %H:%M:%S')

        return df, result