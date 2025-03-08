import mysql.connector

def get_db_connection():
    connection = mysql.connector.connect(
        host='localhost',
        user='root',
        password='@njuM2004',
        database='fact_checker'
    )
    return connection
