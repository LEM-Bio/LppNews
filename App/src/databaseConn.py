from sshtunnel import SSHTunnelForwarder
import mariadb
import sys
import pandas as pd

class ConnectDB():
    def __init__(self, user, password):
        server = SSHTunnelForwarder(
            ('172.22.161.213', 22),
            ssh_username=user,
            ssh_password=password,
            remote_bind_address=('127.0.0.1', 3306),
            local_bind_address=('127.0.0.1', 3307),
        )
        self.server = server
        server.start()
        print(f"Tunnel active: {server.is_active}, Local port: {server.local_bind_port}")

        try:
            print("Connecting to MariaDB...")
            conn = mariadb.connect(
                user="lembio",
                password="prot24",
                host="127.0.0.1",
                port=3307,
                database="sitesLab",
                connect_timeout=60
            )
            self.conn = conn
            print("Connected successfully.")
            self.cur = conn.cursor(buffered=False) #obrigado gpt
        except mariadb.Error as e:
            print(f"Connection failed: {e}")
            server.stop()
            sys.exit(1)

    def GetAllData(self):
        self.cur.execute("SELECT * FROM pubsLEMBio")
        rows = []
        for row in self.cur:
            print(row)
            rows.append(row)

        # Captura os nomes das colunas
        columns = [desc[0] for desc in self.cur.description]

        # Cria o DataFrame
        df = pd.DataFrame(rows, columns=columns)

        return df

    def ExcuteQuery(self, query):
        self.cur.execute(query)
        self.conn.commit()

    def CloseConnection(self):
        self.conn.close()
        self.server.stop()