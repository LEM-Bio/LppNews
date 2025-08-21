import paramiko
from paramiko import BadHostKeyException, AuthenticationException, SSHException

class LogInfo:
    def __init__(self, user, password, host):
        self.user = user
        self.password = password
        self.host = host
        self.logged = False

    def checkValidation(self):
        client = paramiko.client.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect(self.host, username=self.user, password=self.password)
            client.close()
            return True
        except (BadHostKeyException, AuthenticationException, SSHException) as e:
            print(e)
            client.close()
            self.logged = False
            return False