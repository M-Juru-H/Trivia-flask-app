from dotenv import load_dotenv
import os
load_dotenv()


db_name = os.environ.get('DB_NAME')
db_user = os.environ.get('DB_USER')
db_server = os.environ.get('DB_SERVER')
db_pass = os.environ.get('DB_PASSWORD')
db_test = os.environ.get('DB_TEST')