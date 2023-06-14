# gen_pickle.py
# 15-06-2023

import hashlib
import pickle

def create_initial_pickle_file():
    users = [
        {
            "login": "admin",
            "active": False,
            "password": hashlib.sha256("qwerty12345".encode()).hexdigest()
        },
        {
            "login": "user1",
            "active": False,
            "password": hashlib.sha256("pass1".encode()).hexdigest()
        },
        {
            "login": "user2",
            "active": False,
            "password": hashlib.sha256("pass2".encode()).hexdigest()
        },
        # Можно добавить сюда столько пользователей, сколько нужно
    ]

    # Password [admin]: f6ee94ecb014f74f887b9dcc52daecf73ab3e3333320cadd98bcb59d895c52f5
    print(f'Password [admin]: {hashlib.sha256("qwerty12345".encode()).hexdigest()}')
    with open('users.pickle', 'wb') as f:
        pickle.dump(users, f)

if __name__ == "__main__":
    create_initial_pickle_file()
