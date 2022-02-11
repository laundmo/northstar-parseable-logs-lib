from dataclasses import dataclass
from typing import Any, Dict, Optional, Union

from dataclass_factory import Factory, NameStyle, Schema
from dataclass_factory.schema_helpers import type_checker


@dataclass
class Vector:
    x: float
    y: float
    z: float
    type: str = "vector"


@dataclass
class BasicPlayer:
    name: str
    player_index: int
    team_id: int
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
    subject: Union[str, BasicPlayer, Vector, Dict[str, Any]]
    verb: str
    object: Union[str, BasicPlayer, Vector, Dict[str, Any], None] = None


factory = Factory(
    schemas={
        BasicPlayer: Schema(
            pre_parse=type_checker("player"),
            name_style=NameStyle.camel_lower,  # convert cameCase to camel_case
        ),
        Vector: Schema(pre_parse=type_checker("vector")),
    }
)


def load(json_log: Dict[str, Any]) -> SVOlog:
    return factory.load(json_log, SVOlog)


if __name__ == "__main__":
    s = """{"subject":{"type":"player","name":"ErliteDev","playerIndex":0,"teamId":26,"uid":"1005829030626","ping":720972,"kills":0,"deaths":0,"alive":false},"verb":"connecting"}"""
    import json

    j = json.loads(s)
    a = load(j)
    print(a)
