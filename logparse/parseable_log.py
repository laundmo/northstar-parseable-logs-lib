from dataclasses import dataclass
from typing import Any, Dict, Optional, Union
from dataclass_factory import Factory, Schema
from dataclass_factory.schema_helpers import type_checker


@dataclass
class Vector:
    x: float
    y: float
    z: float
    type: str = "vector"


@dataclass
class Player:
    name: str
    playerIndex: int
    teamId: int
    uid: int
    ping: int
    kills: int
    deaths: int
    alive: bool
    titan: Optional[bool] = None
    location: Optional[Vector] = None
    type: str = "player"


@dataclass
class SVOlog:
    subject: Union[str, Player, Vector, Dict[str, Any]]
    verb: str
    object: Union[str, Player, Vector, Dict[str, Any], None] = None


factory = Factory(
    schemas={
        Player: Schema(pre_parse=type_checker("player")),
        Vector: Schema(pre_parse=type_checker("vector")),
    }
)


def load(json_log: Dict[str, Any]) -> SVOlog:
    return factory.load(json_log, SVOlog)


if __name__ == "__main__":
    svo = {
        "subject": {"type": "a", "x": 3041.9, "y": 1501.14, "z": 944.309},
        "verb": "killed",
        "object": {
            "type": "player",
            "name": "Its_Hen_Swolo",
            "playerIndex": 3,
            "teamId": 17,
            "uid": "1007246486495",
            "ping": 1376356,
            "kills": 10,
            "deaths": 9,
            "alive": False,
        },
    }
    print(factory.load(svo, SVOlog))
