import os

from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

OPENAI_API_KEY = os.getenv('OPENAI_API_KEY')
MYSQL_USER = os.getenv('MYSQL_USER')
MYSQL_PASSWORD = os.getenv('MYSQL_PASSWORD')
MYSQL_HOST = os.getenv('MYSQL_HOST')
MYSQL_PORT = os.getenv('MYSQL_PORT')
MYSQL_DB_NAME = os.getenv('MYSQL_DB_NAME')
MYSQL_TABLES = []
GPT_MODEL = os.getenv('GPT_MODEL')

DEFINITION_DIR = 'data_definition'

for definition in os.listdir(DEFINITION_DIR):
    table_name = definition.rsplit('.', 1)[0]
    MYSQL_TABLES.append(table_name)

ERROR_MESSAGE = 'We are facing an issue at this moment, please try after sometime.'