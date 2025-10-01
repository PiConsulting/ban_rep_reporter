import json
import logging
from datetime import datetime, timedelta
import azure.functions as func
from pydantic import ValidationError
from app.business.report import ReportManager
logging.basicConfig(level=logging.DEBUG)
app = func.FunctionApp(http_auth_level=func.AuthLevel.FUNCTION)


@app.route(route='health', methods=['GET'])
def health_check(req: func.HttpRequest) -> func.HttpResponse:
    """
    Health check endpoint to verify if the function app is running.
    """
    logging.info("Health check endpoint called.")
    return func.HttpResponse(
        body=json.dumps({'status': 'healthy'}, ensure_ascii=False),
        status_code=200,
        mimetype='application/json'
    )
    

@app.route(route='summary_report', methods=['GET'])
def summary_report(req: func.HttpRequest) -> func.HttpResponse:
    
    report_manager = ReportManager()
    report_data = report_manager.execute_summary_report()
    report_data['summary_by_date'] = report_data['summary_by_date'].to_dict('records')
    report_data['summary_by_region'] = report_data['summary_by_region'].to_dict('records')
    report_data['summaty_by_eco'] = report_data['summaty_by_eco'].to_dict('records')
    return func.HttpResponse(
        body=json.dumps(report_data, ensure_ascii=False),
        status_code=201,
        mimetype='application/json'
    )
    
@app.route(route='news_report', methods=['GET'])
def news_report(req: func.HttpRequest) -> func.HttpResponse:
    
    report_manager = ReportManager()
    report_data = report_manager.execute_news_report(datetime.now()-timedelta(days=5))
    return func.HttpResponse(
        body=json.dumps(report_data, ensure_ascii=False),
        status_code=201,
        mimetype='application/json'
    )