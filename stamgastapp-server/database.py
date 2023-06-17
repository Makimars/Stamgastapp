import mysql.connector
from mysql.connector import errorcode

connection = None
cursor = None


def get_connection():
    f = open("config", "r")
    lines = f.readlines()
    sql_user = lines[0].strip()
    sql_password = lines[1].strip()
    host = lines[2].strip()
    database_name = lines[3].strip()

    try:
        cnx = mysql.connector.connect(user=sql_user, password=sql_password, host=host, database=database_name)
    except mysql.connector.Error as err:
        if err.errno == errorcode.ER_ACCESS_DENIED_ERROR:
            print("Something is wrong with your user name or password")
        elif err.errno == errorcode.ER_BAD_DB_ERROR:
            print("Database does not exist")
        else:
            print(err)
        raise Exception("database connection failed")
    else:
        return cnx
