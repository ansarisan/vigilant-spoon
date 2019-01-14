import os
import psycopg2
from flask import current_app

# Database URL'S



def connect_to_url(url):
    """
    Takes in a database url and connect to it and returns
    an instance of the connection
    """

    conn = psycopg2.connect(url)

    return conn


def read_db_file(conn):
    """ reads a file's contents """

    # Create a cursor to execute queries and read from the sql file
    # containing commands to create the needed tables and
    # save the changes & return the connection

    with conn as conn, conn.cursor() as cur:
        with current_app.open_resource('questioner.sql', mode='r') as sql:
            cur.execute(sql.read())
        conn.commit()
        return conn


def destroy():
    """ Drops all tables if exists """
    conn = connect_to_url(os.getenv('DATABASE_TESTING_URL'))

    cur = conn.cursor()

    cur.execute("DROP SCHEMA public CASCADE;")
    cur.execute("CREATE SCHEMA public;")
    cur.execute("GRANT USAGE ON SCHEMA public TO leewel;")

    conn.commit()


def init_db(db_type="main"):
    """ 
    Takes an argument with two possible values 'main' or 'testing'
    & initializes the app's main database if 'main' or testing database if 
    'testing' is passed"""

    # Configuring the database url from the current settings
    # Create a new database session and return a new instance of the
    # connection class

    db_url = current_app.config['DATABASE_URL']

    if db_type == "testing":
        db_url = os.getenv('DATABASE_TESTING_URL')
        destroy()

    conn = connect_to_url(db_url)

    return read_db_file(conn)
