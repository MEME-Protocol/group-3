from dataclasses import dataclass

from dataclasses_json import dataclass_json


@dataclass_json
@dataclass
class Unregister:
    nickname: str
    type: str = "unregister"


# Unregister.from_json(json_string)
# Unregister.to_json() -> json_string
