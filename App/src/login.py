import paramiko
from paramiko import BadHostKeyException, AuthenticationException, SSHException

class LogInfo:
    def __init__(self, user, password):
        self.user = user
        self.password = password

    def checkValidation(self):
        client = paramiko.client.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            client.connect('172.22.161.213', username=self.user, password=self.password)
            client.close()
            return True
        except (BadHostKeyException, AuthenticationException, SSHException) as e:
            print(e)
            client.close()
            return False