import psycopg2
from psycopg2.extensions import connection

def get_connection() -> connection:
    return psycopg2.connect("dbname=horse user=postgres password=Ohnoke2014")
    

def insert_data(csv_file,table_name='race_data'):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"copy {table_name} from %s delimiter ',' csv header",(csv_file,))
        conn.commit()


def get_all_data(table_name='race_data'):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"select * from {table_name};")
            return cur.fetchall()
        
def get_race_data_distinct(table_name='race_data'):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"select distinct * from {table_name} order by date;")
            return cur.fetchall()


def get_final_race_date(table_name='race_data'):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"select max(date) from {table_name};")
            return cur.fetchall()
        

def get_initial_race_date(table_name='race_data'):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"select min(date) from {table_name};")
            return cur.fetchall()
        

def insert_race_refund(csv_file,table_name='race_refund'):
    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(f"copy {table_name} from %s delimiter ',' csv header",(csv_file,))
        conn.commit()