from sshtunnel import SSHTunnelForwarder
import mariadb
import sys
import pandas as pd

server = SSHTunnelForwarder(
    ('172.22.161.213', 22),
    ssh_username='pedroand',
    ssh_password='password',
    remote_bind_address=('127.0.0.1', 3306),
    local_bind_address=('127.0.0.1', 3307)
)

server.start()
print(f"Tunnel active: {server.is_active}, Local port: {server.local_bind_port}")

try:
    print("Connecting to MariaDB...")
    conn = mariadb.connect(
        user="lembio",
        password="password",
        host="127.0.0.1",
        port=3307,
        database="sitesLab"
    )
    print("Connected successfully.")
except mariadb.Error as e:
    print(f"Connection failed: {e}")
    server.stop()
    sys.exit(1)

cur = conn.cursor()
upperlimit = 20

df = pd.read_sql(f"SELECT * FROM pubsLEMBio WHERE id < {100} AND id > {20};", conn)
print(df.values)

conn.close()
server.stop()