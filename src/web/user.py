# user.py
from flask_login import UserMixin

class User(UserMixin):
    # Mock user data as a dictionary (username: password)
    users = {
        "Sarthak": "password1",
        "Irwindeep": "password1"
    }

    def __init__(self, username):
        self.id = username

    @classmethod
    def authenticate(cls, username, password):
        # Check if username exists and password matches
        if username in cls.users and cls.users[username] == password:
            return cls(username)  # Return a User instance if authentication is successful
        return None

    def get_id(self):
        # Override get_id to return the username (Flask-Login requirement)
        return self.id
