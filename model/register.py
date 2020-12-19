from dataclasses import dataclass
from dataclasses_json import dataclass_json

@dataclass_json
@dataclass
class Register:
    nickname: str
    ip: str
    port: int
    type: str = "register"

# Register.from_json(json_string)
# Register.to_json() -> json_string
