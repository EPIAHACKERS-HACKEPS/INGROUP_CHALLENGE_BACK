from dotenv import load_dotenv
import os

load_dotenv()

DEBUG = os.getenv('FLASK_DEBUG', 'False') == '1' or os.getenv('FLASK_DEBUG', 'False') == 1 or os.getenv('FLASK_DEBUG', 'False') == 'True'
SECRET_JWT = "secret"
MYSQL_HOST = os.getenv("MYSQL_HOST")
MYSQL_USER = os.getenv("MYSQL_USER")
MYSQL_PASS = os.getenv("MYSQL_PASS")
MYSQL_PORT = os.getenv("MYSQL_PORT")
MYSQL_DB = os.getenv("MYSQL_DB")
DATABASE_URI = f"mysql://{MYSQL_USER}:{MYSQL_PASS}@{MYSQL_HOST}:{MYSQL_PORT}/{MYSQL_DB}"
API_PREFIX = "api/v1"