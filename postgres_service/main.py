import psycopg2

def get_conn():
    # todo change these values
    return psycopg2.connect(database="mydb",
        host="localhost",
        user="myuser",
        password="S3cret",
        port="5432")

def start():
    try:
        conn = get_conn()
        cursor = conn.cursor()

        cursor.execute("create extension pgcrypto")

        cursor.execute("""
            create table users(
               username varchar(255),
               password_hash varchar(255),
               primary key (username)
           )
       """)

        conn.commit()
    except:
        conn.rollback()
    finally:
        conn.close()

start()

