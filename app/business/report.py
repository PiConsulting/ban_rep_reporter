from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from io import BytesIO
import smtplib
import ssl
import pandas as pd
from datetime import datetime
from app.services.azure_services.azure_sql_services import SqlService
from app.services.azure_services.azure_storage_services import StorageAccount
from app.core.config import (
    AZURE_STORAGE_CONNECTION_STRING, 
    AZURE_STORAGE_CONTAINER,
    TLS_PORT,
    SMTP_SERVER,
    SMTP_USER,
    SMTP_PASSWORD,
    RECEIVER_EMAILS,
)
from app.core.constants import SummaryQueries
import logging
logging.basicConfig(level=logging.DEBUG)


class ReportManager():
    
    def __init__(self):
        self.db_service = SqlService()
        self.storage_service = StorageAccount(AZURE_STORAGE_CONNECTION_STRING, AZURE_STORAGE_CONTAINER)

    def execute_summary_report(self, execution_datetime: datetime = datetime.now()) -> dict:
        execution_datetime_str = execution_datetime.strftime('%Y-%m-%d %H:%M:%S')
        params = (execution_datetime,)
        sq = SummaryQueries()

        # To-Do: Añadir el parametro a la query cuando se tenga data constante 
        df_by_date = self.get_report(sq.SUMMARY_BY_DATE)
        df_by_region = self.get_report(sq.SUMMARY_BY_REGION)
        df_by_economic_act = self.get_report(sq.SUMMARY_BY_ECONOMIC_ACT)
        
        df_by_date['Fecha de ejecución'] = df_by_date['Fecha de ejecución'].dt.strftime('%d-%m-%Y %h:%M:%s')
        df_by_economic_act['Fecha de ejecución'] = df_by_economic_act['Fecha de ejecución'].dt.strftime('%d-%m-%Y %h:%M:%s')
        
        self.send_report()

        result = {
            'summary_by_date': df_by_date.to_dict(orient='records'),
            'summary_by_region': df_by_region.to_dict(orient='records'),
            'summaty_by_eco': df_by_economic_act.to_dict(orient='records')
        }
        return result


    def execute_news_report(self, execution_datetime: datetime = datetime.now()):
        execution_datetime_str = execution_datetime.strftime('%Y-%m-%d %H:%M:%S')
        params = (execution_datetime,)
        sq = SummaryQueries()
        
        df = self.get_report(sq.NEWS_REPORT, 'reporte_sample')
        df['Fecha de publicación'] = df['Fecha de publicación'].dt.strftime('%d-%m-%Y %H:%M:%S')

        output = BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='Reporte')
        output.seek(0)
        logging.info(type(output))
        self.send_report(
            f'Reporte de Noticias al {datetime.now().isoformat()}',
            'reporte.xlsx', 
            output
        )
        
        return {
            'news_report': df.to_dict(orient='records')
        }


    def get_report(self, query: str, params: tuple = None) -> pd.DataFrame:
        """
        Genera un reporte resumen a partir de una consulta SQL y 
        devuelve los resultados en un DataFrame de pandas y una lista de diccionarios.
        Parámetros:
            query (str): Consulta SQL a ejecutar.
            params (tuple, opcional): Parámetros para la consulta SQL (no utilizado en el método actual).
        Retorna:
            tuple[pd.DataFrame, list]: 
                - Un DataFrame de pandas con los resultados de la consulta.
                - Una lista de diccionarios, donde cada diccionario representa una fila del resultado.
        """
        exec_cursor = None
        if params:
            exec_cursor = self.db_service.execute_query(query)
        else:
            exec_cursor = self.db_service.execute_query(query)
        
        cols = [c[0] for c in exec_cursor.description]
        rows = exec_cursor.fetchall()
        result = [dict(zip(cols, row)) for row in rows]

        df = pd.DataFrame(result, columns=cols)
        if 'execution_datetime' in cols:
            df['execution_datetime'] = df['execution_datetime'].dt.strftime('%d-%m-%Y %H:%M:%S')

        return df
    

    def send_report(self, subject: str, filename: str, attach: BytesIO):

        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SMTP_USER
        message["To"] = RECEIVER_EMAILS

        html = """\
        <html>
        <body>
            <p>Aqui va el resumen, creo...<br>
            ¯\_(ツ)_/¯
            </p>
        </body>
        </html>
        """

        body = MIMEText(html, "html")
        message.attach(body)

        part = MIMEBase("application", "octet-stream")
        part.set_payload(attach.getvalue())
        encoders.encode_base64(part)
        part.add_header(
            "Content-Disposition",
            f"attachment; filename={filename}",
        )
        message.attach(part)
        
        try:
            context = ssl.create_default_context()
            with smtplib.SMTP(SMTP_SERVER, TLS_PORT) as server:
                server.ehlo()
                server.starttls(context=context)
                server.ehlo()
                server.login(SMTP_USER, SMTP_PASSWORD)
                server.sendmail(SMTP_USER, RECEIVER_EMAILS, message.as_string())

            logging.info("Correo enviado correctamente")
        except Exception as e:
            error_msg = f'Error al intentar enviar el correo {str(e)}'
            logging.error(error_msg)
            raise Exception(error_msg)