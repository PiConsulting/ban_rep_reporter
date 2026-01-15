from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
from io import BytesIO
import smtplib
import ssl
import pandas as pd
from datetime import datetime, timedelta
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

    def execute_summary_report(self, execution_datetime: datetime = datetime.now()) -> dict[pd.DataFrame]:
        execution_datetime_str = execution_datetime.strftime('%Y-%m-%d %H:%M:%S')
        params = (execution_datetime_str,)
        sq = SummaryQueries()

        # To-Do: Añadir el parametro a la query cuando se tenga data constante 
        # df_by_date = self.get_report(sq.SUMMARY_BY_DATE, params)
        df_by_region = self.get_report(sq.SUMMARY_BY_REGION, params)
        df_by_economic_act = self.get_report(sq.SUMMARY_BY_ECONOMIC_ACT, params)
        
        #if not df_by_date.empty:
            #df_by_date['Fecha de ejecución'] = df_by_date['Fecha de ejecución'].dt.strftime('%d-%m-%Y %h:%M:%s')

        result = {
            #'summary_by_date': df_by_date,
            'summary_by_region': df_by_region,
            'summary_by_eco': df_by_economic_act
        }
        return result


    def execute_news_report(self, execution_datetime: datetime = datetime.now()):
        start_time = datetime.now()

        execution_datetime_str = execution_datetime.strftime('%Y-%m-%d %H:%M:%S')
        logging.warning(
            f'[NEWS_REPORT] START | execution_datetime={execution_datetime_str}'
        )

        try:

            params = (execution_datetime_str,)
            sq = SummaryQueries()

            logging.warning('[NEWS_REPORT] About to execute NEWS_REPORT query')


            df = self.get_report(sq.NEWS_REPORT, params)

            logging.warning(
                f'[NEWS_REPORT] Query finished | rows={len(df)} | empty={df.empty}'
            )


            if not df.empty:
                logging.warning('[NEWS_REPORT] Formatting "Fecha de publicación" column')

                if 'Fecha de publicación' not in df.columns:
                    logging.error(
                        '[NEWS_REPORT] Column "Fecha de publicación" NOT FOUND'
                    )
                else:
                    df['Fecha de publicación'] = (
                        df['Fecha de publicación']
                        .dt.strftime('%d-%m-%Y %H:%M:%S')
                    )


            logging.warning('[NEWS_REPORT] Generating Excel report')

            output = BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                df.to_excel(writer, index=False, sheet_name='Reporte')

            output.seek(0)
            logging.warning(
                f'[NEWS_REPORT] Excel generated | size_bytes={output.getbuffer().nbytes}'
            )

            today_date = datetime.now()
            report_date = today_date.isoformat()

            logging.warning('[NEWS_REPORT] Sending email report')

            self.send_report(
                f'Reporte de Noticias al {today_date.strftime("%d-%m-%Y")}',
                f'reporte_noticias_{report_date}.xlsx',
                output,
                execution_datetime
            )


            elapsed = (datetime.now() - start_time).total_seconds()
            logging.warning(
                f'[NEWS_REPORT] END OK | elapsed_seconds={elapsed}'
            )

            return {'success': True}

        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            logging.error(
                f'[NEWS_REPORT] ERROR | elapsed_seconds={elapsed} | {str(e)}',
                exc_info=True
            )
            raise



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
        start_time = datetime.now()
        logging.warning('[GET_REPORT] START')

        try:

            if params:
                logging.warning(
                    f'[GET_REPORT] Executing query WITH params | params={params}'
                )
                exec_cursor = self.db_service.execute_query(query, params)
            else:
                logging.warning('[GET_REPORT] Executing query WITHOUT params')
                exec_cursor = self.db_service.execute_query(query)

            logging.warning('[GET_REPORT] Query executed, fetching metadata')


            if not exec_cursor.description:
                logging.warning('[GET_REPORT] Cursor has no description (no columns)')

            cols = [c[0] for c in exec_cursor.description]
            logging.warning(f'[GET_REPORT] Columns fetched | count={len(cols)}')


            logging.warning('[GET_REPORT] Fetching rows from cursor')
            rows = exec_cursor.fetchall()
            logging.warning(f'[GET_REPORT] Rows fetched | count={len(rows)}')


            logging.warning('[GET_REPORT] Mapping rows to dict')
            result = [dict(zip(cols, row)) for row in rows]


            logging.warning('[GET_REPORT] Creating pandas DataFrame')
            df = pd.DataFrame(result, columns=cols)
            logging.warning(
                f'[GET_REPORT] DataFrame created | shape={df.shape}'
            )

            if 'execution_datetime' in cols:
                logging.warning('[GET_REPORT] Formatting execution_datetime column')
                df['execution_datetime'] = (
                    df['execution_datetime']
                    .dt.strftime('%d-%m-%Y %H:%M:%S')
                )

            elapsed = (datetime.now() - start_time).total_seconds()
            logging.warning(
                f'[GET_REPORT] END OK | elapsed_seconds={elapsed}'
            )

            return df

        except Exception as e:
            elapsed = (datetime.now() - start_time).total_seconds()
            logging.error(
                f'[GET_REPORT] ERROR | elapsed_seconds={elapsed} | {str(e)}',
                exc_info=True
            )
            raise

        

    def send_report(self, subject: str, filename: str, attach: BytesIO, execution_datetime: datetime):

        receiver_emails_list = RECEIVER_EMAILS.split(',')
        
        message = MIMEMultipart("alternative")
        message["Subject"] = subject
        message["From"] = SMTP_USER
        message["To"] = RECEIVER_EMAILS
        
        summary_reports = self.execute_summary_report(execution_datetime)
        
        start_dt = execution_datetime
        end_dt = execution_datetime + timedelta(days=5)

        html = f"""\
        <html>
            <body>
                <h2>
                    Reporte Resumen de Ejecución <br/>
                    {start_dt.strftime('%d-%m-%Y %H:%M:%S')} 
                    al 
                    {end_dt.strftime('%d-%m-%Y %H:%M:%S')}
                </h2>         
                <h3>Resumen por Actividad Económica</h3>
                {summary_reports['summary_by_eco'].to_html(index=False)}
                <br/>
                <h3>Resumen por Cobertura Geográfica</h3>
                {summary_reports['summary_by_region'].to_html(index=False)}
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
                # Pasa la lista directamente a sendmail
                server.sendmail(SMTP_USER, receiver_emails_list, message.as_string())

            logging.info("Correo enviado correctamente")
        except Exception as e:
            error_msg = f'Error al intentar enviar el correo {str(e)}'
            logging.error(error_msg)
            raise Exception(error_msg)