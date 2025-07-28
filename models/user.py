from flask_login import UserMixin
from models.database import get_db_connection

class User(UserMixin):
    def __init__(self, id, email, password):
        self.id = id
        self.email = email
        self.password = password

    @staticmethod
    def get(user_id):
        conn = get_db_connection()
        user_row = conn.execute('SELECT * FROM users WHERE id = ?', (user_id,)).fetchone()
        conn.close()
        if user_row:
            return User(id=user_row['id'], email=user_row['email'], password=user_row['password'])
        return None

    @staticmethod
    def find_by_email(email):
        conn = get_db_connection()
        user_row = conn.execute('SELECT * FROM users WHERE email = ?', (email,)).fetchone()
        conn.close()
        if user_row:
            return User(id=user_row['id'], email=user_row['email'], password=user_row['password'])
        return None
