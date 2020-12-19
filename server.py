#! /usr/bin/python3.9
from model.register import Register
from model.unregister import Unregister
from model.user_list import UserList, User, AddedRemovedUsers

print(
    UserList(
        AddedRemovedUsers(
            [User("nickname", "127.0.0.1", 0000)],
            [])
    ).to_json())

Register.from_json(""" { "type": "register", "nickname": "nickname", "ip": "127.0.0.1", "port": 0 } """)
