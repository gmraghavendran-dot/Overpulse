import os
import psycopg2
from psycopg2.extras import RealDictCursor


# ============================================================
# DATABASE CONFIGURATION
# ============================================================

DB_CONFIG = {
    "host": os.getenv("POSTGRES_HOST", "localhost"),
    "port": os.getenv("POSTGRES_PORT", "5432"),
    "database": os.getenv("POSTGRES_DB", "data_obs"),
    "user": os.getenv("POSTGRES_USER", "postgres"),
    "password": os.getenv("POSTGRES_PASSWORD", ""),
}


# ============================================================
# CREATE CONNECTION
# ============================================================

def get_connection():

    try:

        connection = psycopg2.connect(
            host=DB_CONFIG["host"],
            port=DB_CONFIG["port"],
            database=DB_CONFIG["database"],
            user=DB_CONFIG["user"],
            password=DB_CONFIG["password"]
        )

        return connection

    except psycopg2.Error as error:

        print("PostgreSQL connection failed:")
        print(error)

        return None


# ============================================================
# TEST CONNECTION
# ============================================================

def test_connection():

    connection = get_connection()

    if connection is None:
        return False

    try:

        cursor = connection.cursor()

        cursor.execute("SELECT 1;")

        result = cursor.fetchone()

        cursor.close()
        connection.close()

        return result[0] == 1

    except psycopg2.Error as error:

        print("Database test failed:")
        print(error)

        return False


# ============================================================
# EXECUTE QUERY
# ============================================================

def execute_query(query, params=None):

    connection = get_connection()

    if connection is None:
        return False

    try:

        cursor = connection.cursor()

        cursor.execute(query, params)

        connection.commit()

        cursor.close()
        connection.close()

        return True

    except psycopg2.Error as error:

        connection.rollback()

        print("Query execution failed:")
        print(error)

        connection.close()

        return False


# ============================================================
# FETCH MULTIPLE ROWS
# ============================================================

def fetch_all(query, params=None):

    connection = get_connection()

    if connection is None:
        return []

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute(query, params)

        rows = cursor.fetchall()

        cursor.close()
        connection.close()

        return rows

    except psycopg2.Error as error:

        print("Fetch failed:")
        print(error)

        connection.close()

        return []


# ============================================================
# FETCH ONE ROW
# ============================================================

def fetch_one(query, params=None):

    connection = get_connection()

    if connection is None:
        return None

    try:

        cursor = connection.cursor(
            cursor_factory=RealDictCursor
        )

        cursor.execute(query, params)

        row = cursor.fetchone()

        cursor.close()
        connection.close()

        return row

    except psycopg2.Error as error:

        print("Fetch failed:")
        print(error)

        connection.close()

        return None