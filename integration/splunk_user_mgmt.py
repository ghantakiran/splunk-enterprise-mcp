import os
from splunklib.client import Service

class SplunkUserManager:
    def __init__(self, host=None, port=None, username=None, password=None, app=None):
        self.host = host or os.getenv("SPLUNK_HOST", "localhost")
        self.port = port or int(os.getenv("SPLUNK_PORT", 8089))
        self.username = username or os.getenv("SPLUNK_USER", "admin")
        self.password = password or os.getenv("SPLUNK_PASSWORD", "changeme")
        self.app = app or os.getenv("SPLUNK_APP", "search")
        self.service = Service(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password,
            app=self.app
        )

    def add_user(self, username, password, role):
        user = self.service.users.create(username=username, password=password, roles=[role])
        return {"username": user.name, "role": role}

    def update_user_role(self, username, new_role):
        user = self.service.users[username]
        user.update(roles=[new_role])
        return {"username": username, "role": new_role}

    def remove_user(self, username):
        user = self.service.users[username]
        user.delete()
        return True 