from dataclasses import dataclass
from typing import List

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class User:
    nickname: str
    ip: str
    port: int


@dataclass_json
@dataclass
class AddedRemovedUsers:
    added: List[User]
    removed: List[User]


@dataclass_json
@dataclass
class UserList:
    users: List[AddedRemovedUsers]
    type: str = "user-list"
