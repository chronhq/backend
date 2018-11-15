import time
import sys
import psycopg2

dbname = sys.argv[1]
host = sys.argv[2]
port = int(sys.argv[3])
user = sys.argv[4]
password = sys.argv[5]

while True:
    try:
        conn = psycopg2.connect(
            host=host, port=port, dbname=dbname, user=user, password=password
        )
        conn.close()
        break
    except BaseException:
        time.sleep(1)
