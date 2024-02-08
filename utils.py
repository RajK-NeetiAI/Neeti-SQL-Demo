import decimal
import json
import datetime
import os

from mysql.connector.pooling import MySQLConnectionPool
from mysql.connector import Error

import config


def connect_to_mysql_pool():
    try:
        connection_pool = MySQLConnectionPool(
            pool_name="neeti-sql",
            pool_size=5,
            pool_reset_session=True,
            host=config.MYSQL_HOST,
            database=config.MYSQL_DB_NAME,
            user=config.MYSQL_USER,
            password=config.MYSQL_PASSWORD
        )

        return connection_pool
    except Error as e:
        print(f"Error creating MySQL connection pool: {e}")

        return None


def close_mysql_pool(pool: MySQLConnectionPool):
    if pool:
        pool.close()
        print("MySQL connection pool closed")


def get_table_names() -> list[str]:
    """Return a list of table names."""
    pool = connect_to_mysql_pool()
    if not pool:
        return []
    cnx = pool.get_connection()
    cursor = cnx.cursor()
    table_names = []
    cursor.execute(
        f"SELECT table_name FROM information_schema.tables WHERE table_schema = '{config.MYSQL_DB_NAME}';")
    for table in cursor:
        if table[0] in config.MYSQL_TABLES:
            table_names.append(table[0])
    cursor.close()

    return table_names


def get_column_names(table_name: str) -> list[str]:
    """Return a list of column names."""
    pool = connect_to_mysql_pool()
    if not pool:
        return []
    cnx = pool.get_connection()
    cursor = cnx.cursor()
    column_names = []
    cursor.execute(
        f"SELECT `COLUMN_NAME` FROM `INFORMATION_SCHEMA`.`COLUMNS` WHERE `TABLE_SCHEMA`='{config.MYSQL_DB_NAME}' AND `TABLE_NAME`='{table_name}';")
    for col in cursor:
        column_names.append(col[0])
    cursor.close()

    return column_names


def get_database_info() -> dict:
    """Return a list of dicts containing the table name and columns for each table in the database."""
    pool = connect_to_mysql_pool()
    if not pool:
        return {}
    cnx = pool.get_connection()
    cursor = cnx.cursor()
    table_dicts = []
    for table_name in get_table_names():
        columns_names = get_column_names(table_name)
        table_dicts.append(
            {"table_name": table_name, "column_names": columns_names})
    cursor.close()

    return table_dicts


def get_database_schema_string():
    pool = connect_to_mysql_pool()
    if not pool:
        return ''
    cnx = pool.get_connection()
    database_schema_dict = get_database_info()
    database_schema_string = "\n".join(
        [
            f"Table: {table['table_name']}\nColumns: {', '.join(table['column_names'])}"
            for table in database_schema_dict
        ]
    )

    return database_schema_string


def get_database_definitions():
    database_definitions = {
        "tables": []
    }
    pool = connect_to_mysql_pool()
    if not pool:
        return database_definitions
    cnx = pool.get_connection()
    for definition in os.listdir(config.DEFINITION_DIR):
        with open(os.path.join(config.DEFINITION_DIR, definition), 'r') as file:
            database_definitions['tables'].append(json.loads(file.read()))

    return database_definitions


def format_number(amount):
    def truncate_float(number, places):
        return int(number * (10 ** places)) / 10 ** places
    if amount < 1e3:
        return amount
    if 1e3 <= amount < 1e5:
        return str(truncate_float((amount / 1e5) * 100, 2)) + " K"
    if 1e5 <= amount < 1e7:
        return str(truncate_float((amount / 1e7) * 100, 2)) + " L"
    if amount > 1e7:
        return str(truncate_float(amount / 1e7, 2)) + " Cr"


def serialize_data(obj) -> str:
    if isinstance(obj, datetime.datetime):
        return obj.isoformat()
    if isinstance(obj, decimal.Decimal):
        return format_number(float(obj))
    raise TypeError(f"Object type not serializable - {type(obj)}")


def ask_database(query: str):
    """Function to query SQLite database with a provided SQL query."""
    pool = connect_to_mysql_pool()
    if not pool:
        return ''
    cnx = pool.get_connection()
    try:
        cursor = cnx.cursor(dictionary=True)
        cursor.execute(query)
        results = ''
        for data in cursor:
            print(data)
            results += json.dumps(data, default=serialize_data)
    except Exception as e:
        print(e.args[0])
        result = ''
        return result

    return results


def execute_function_call(query: str) -> str:
    results = ask_database(query)
    print(results)

    return results
