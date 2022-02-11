from dataclasses import dataclass
from typing import Optional
from r2logparse.models import BasicPlayer


class Player:
    players = {}

    def __init__(self, name, uid):
        if uid in self.players:
            raise ValueError(
                "Player already exists, use Player.from_parsed_player or Player.create"
                " to ensure singlton behaviour"
            )
        self.players[uid] = self
        self.name = name
        self.uid = uid
        self._last_mention: Optional[BasicPlayer] = None

    @classmethod
    def create(cls, name, uid):
        if uid in cls.players:
            return cls.players[uid]
        return cls(name, uid)

    @classmethod
    def from_parsed_player(cls, player: BasicPlayer):
        ins = cls.create(player.name, player.uid)
        ins.add_last_mention(player)
        return ins

    @property
    def index(self):
        if self._last_mention:
            return self._last_mention.playerIndex

    @property
    def location(self):
        if self._last_mention:
            return self._last_mention.location

    @property
    def teamId(self) -> Optional[int]:
        if self._last_mention:
            return self._last_mention.teamId

    @property
    def ping(self) -> Optional[int]:
        if self._last_mention:
            return self._last_mention.ping

    @property
    def kills(self) -> Optional[int]:
        if self._last_mention:
            return self._last_mention.kills

    @property
    def deaths(self) -> Optional[int]:
        if self._last_mention:
            return self._last_mention.deaths

    @property
    def alive(self) -> Optional[bool]:
        if self._last_mention:
            return self._last_mention.alive

    @property
    def titan(self) -> Optional[float]:
        if self._last_mention:
            return self._last_mention.titan

    def add_last_mention(self, player: BasicPlayer):
        self._last_mention = player

    def __str__(self):
        return f"<Player {self.name} ({self.uid})>"


@dataclass
class ChatMessage:
    content: str
    sender: Player
    chat_id: int  # TODO: make this a enum once i know which chat is which

    def __str__(self):
        return f"{self.sender.name} ({self.chat_id}): {self.content}"
