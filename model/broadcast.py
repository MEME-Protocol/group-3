from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Broadcast:
    message: str
    type: str = "broadcast"
