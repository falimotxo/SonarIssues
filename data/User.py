"""
Clase que representa a un usuario
"""
class User:

    accumulatedDebt = 0

    def __init__(self, login, name, email):
        self.login = login
        self.name = name
        self.email = email

    def as_payload(user):
        return User(user['login'], user['name'], user['email'])
