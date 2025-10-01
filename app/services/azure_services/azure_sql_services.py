import pyodbc
from app.core.config import (
    AZURE_DB_DRIVER,
    AZURE_DB_SERVER,
    AZURE_DB_NAME,
    AZURE_DB_USER,
    AZURE_DB_PASS,
)
import logging


class SqlService():
    
    def __init__(self):
        self.conn = self.get_conn()
        self.cr = self.conn.cursor()
        
    def get_conn(self):
        try:
            conn = pyodbc.connect(
                f"DRIVER={AZURE_DB_DRIVER};"
                f"SERVER={AZURE_DB_SERVER};"
                f"DATABASE={AZURE_DB_NAME};"
                f"UID={AZURE_DB_USER};"
                f"PWD={AZURE_DB_PASS};"
                "Encrypt=yes;TrustServerCertificate=no;Connection Timeout=30;"
            )
        except Exception as e:
            logging.error(f'Error al intentar conectar a la base de datos {str(e)}')
            raise Exception(f'Error al intentar conectar a la base de datos {str(e)}', 'SSE001', 500)
        return conn


    def execute_query(self, query: str, params: tuple = None, require_commit: bool = False) -> pyodbc.Cursor:
        """
        Ejecuta una consulta SQL utilizando la conexión establecida.
        Args:
            query (str): Consulta SQL a ejecutar.
            params (tuple, opcional): Parámetros para la consulta SQL. Por defecto es None.
            require_commit (bool, opcional): Indica si se debe realizar commit después de ejecutar la consulta. Por defecto es False.
        Returns:
            pyodbc.Cursor: Cursor con el resultado de la consulta.
        Raises:
            pyodbc.ProgrammingError: Si ocurre un error de programación al ejecutar la consulta.
            Exception: Si ocurre cualquier otro error desconocido durante la ejecución.
        """
        try:
            if params is not None:
                cur = self.cr.execute(query, params)
            else:
                cur = self.cr.execute(query)
            if require_commit:
                self.conn.commit()
            return cur
        except pyodbc.ProgrammingError as pe:
            pe_error_msg = f'Error al intentar ejecutar la query: {pe}'
            logging.error(pe_error_msg)
            raise pyodbc.ProgrammingError(pe_error_msg, 'SSE001', 500)
        except Exception as e:
            error_msg = f'Error Desconocido al ejecutar la consulta: {str(e)}'
            logging.error(error_msg)
            raise Exception(error_msg, 'SSE002', 500)