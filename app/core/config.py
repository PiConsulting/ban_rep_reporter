import os
from dotenv import load_dotenv

ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
ENV_FILE = os.path.join(ROOT_DIR, ".env")

load_dotenv(dotenv_path=ENV_FILE)

# Azure Storage settings
AZURE_STORAGE_NAME = os.getenv('AZURE_STORAGE_NAME', '')
AZURE_STORAGE_CONNECTION_STRING = os.getenv('AZURE_STORAGE_CONNECTION_STRING', '')
AZURE_STORAGE_CONTAINER = os.getenv('AZURE_STORAGE_CONTAINER', '')
AZURE_STORAGE_DOWNLOAD_PATH = os.getenv('AZURE_STORAGE_DOWNLOAD_PATH', '')

# Azure DB settings
AZURE_DB_CONN_STRING = os.getenv('AZURE_DB_CONN_STRING', '')
AZURE_DB_DRIVER = os.getenv('AZURE_DB_DRIVER', '')
AZURE_DB_SERVER = os.getenv('AZURE_DB_SERVER', '')
AZURE_DB_NAME = os.getenv('AZURE_DB_NAME', '')
AZURE_DB_USER = os.getenv('AZURE_DB_USER', '')
AZURE_DB_PASS = os.getenv('AZURE_DB_PASS', '')