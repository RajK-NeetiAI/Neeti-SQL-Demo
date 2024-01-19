import re
import json

import pandas as pd
from sqlalchemy import create_engine
import mysql.connector
from sqlalchemy_utils import database_exists, create_database

import config

engine = create_engine(
    f'mysql+mysqlconnector://{config.MYSQL_USER}:{config.MYSQL_PASSWORD}@{config.MYSQL_HOST}:{config.MYSQL_PORT}/{config.MYSQL_DB_NAME}')


def clean_column_names(column_name: str) -> str:
    cleaned_name = column_name.replace(' ', '_')
    cleaned_name = re.sub(r'[^\w_]', '', cleaned_name)
    return cleaned_name


def get_column_names(cnx: mysql.connector.MySQLConnection, table_name: str) -> list[str]:
    """Return a list of column names."""
    cursor = cnx.cursor()
    column_names = []
    cursor.execute(
        f"SELECT * FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='{config.MYSQL_DB_NAME}' AND `TABLE_NAME`='{table_name}';")
    for col in cursor:
        column_names.append([col[3], col[7]])
    cursor.close()
    return column_names


print('Checking DB.')

if not database_exists(engine.url):
    create_database(engine.url)

print(f'DB exists - {database_exists(engine.url)}.')

cnx = mysql.connector.connect(user=config.MYSQL_USER, password=config.MYSQL_PASSWORD,
                              host=config.MYSQL_HOST, port=config.MYSQL_PORT, database=config.MYSQL_DB_NAME)

print('Reading CSV file.')

csv_file_path = 'BRS Production Report-3.csv'
data = pd.read_csv(csv_file_path)

print('Cleaning columns name.')

data.columns = [clean_column_names(col) for col in data.columns]

print('Creating table and pushing the data.')

table_name = 'brs_production_report'
data.to_sql(table_name, engine, if_exists='replace',
            index=False, method='multi', chunksize=100)

print('Creating empty data definitions.')

data_definations = {
    "tables": [
        {
            "name": table_name,
            "description": "This table stores detailed information about different parameters of BRS production.",
            "columns": []
        }
    ]
}

columns = get_column_names(cnx, table_name)

for column in columns:
    data_definations['tables'][0]['columns'].append(
        {
            "name": str(column[0]),
            "type": str(column[1]),
            "description": ""
        }
    )

print('Writing data definitions.')

with open('data_definations.json', 'w') as file:
    file.write(json.dumps(data_definations, indent=2))

print('All is well.')
