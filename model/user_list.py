from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class User:
    nickname: str
    ip: str
    port: int

    def __hash__(self):
        return int.from_bytes(
            self.nickname.encode("utf-8")
            + self.ip.encode("utf-8")
            + (self.port).to_bytes(10, byteorder="big"),
            byteorder='big'
        )


@dataclass_json
@dataclass
class AddedRemovedUsers:
    added: List[User]
    removed: List[User]


@dataclass_json
@dataclass
class UserList:
    users: AddedRemovedUsers
    type: str = "user-list"
