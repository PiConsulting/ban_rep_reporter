import os
import logging
from app.core.config import ROOT_DIR


class SummaryQueries():
    
    def __init__(self):
        self.SUMMARY_BY_DATE = self.get_query('summary_by_date')
        self.SUMMARY_BY_REGION = self.get_query('summary_by_region')
        self.SUMMARY_BY_ECONOMIC_ACT = self.get_query('summary_by_economic_activity')
    
    def get_query(self, query_filename: str):
        try:
            with open(os.path.join(ROOT_DIR, 'app', 'core', 'queries', f'{query_filename}.sql'), 'r', encoding='utf-8') as query_file:
                query = query_file.read()
            return query
        except FileNotFoundError as fe:
            error_msg = f'Archivo no encontrado: {query_filename} {str(fe)}'
            logging.error(error_msg)
            raise FileNotFoundError(error_msg, 'SQE001', 500)
        except Exception as e:
            error_msg = f'Error desconocido al intentar leer el archivo {query_filename} {str(e)}'
            logging.error(error_msg)
            raise Exception(error_msg, 'SQE002', 500)
