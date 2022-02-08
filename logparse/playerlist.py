from time import time
from logparse.parseable_log import Player as ParsedPlayer, SVOlog
from typing import Callable, Dict, List, Optional, Protocol


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
        self._last_mention: Optional[ParsedPlayer] = None

    @classmethod
    def create(cls, name, uid):
        if uid in cls.players:
            return cls.players[uid]
        return cls(name, uid)

    @classmethod
    def from_parsed_player(cls, player: ParsedPlayer):
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

    def add_last_mention(self, player: ParsedPlayer):
        self._last_mention = player

    def __str__(self):
        return f"<Player {self.name} ({self.uid})>"


def _call_hooks(hooks, *args, **kwargs):
    for hook in hooks:
        try:
            hook(*args, **kwargs)
        except Exception as e:
            print(e)


class HasUid(Protocol):
    uid: int


class Playerlist:
    def __init__(self, timeout):
        self.timeout_seconds = timeout
        self.players: Dict[int, Player] = {}
        self.players_checked: Dict[int, float] = {}
        self.killed_hooks: List[Callable[[Player, Player], None]] = []
        self.connected_hooks: List[Callable[[Player], None]] = []
        self.respawned_hooks: List[Callable[[Player], None]] = []
        self.updated: List[Player] = []
        self.updated_hooks: List[Callable[[Player], None]] = []
        self.deleted: List[Player] = []
        self.deleted_hooks: List[Callable[[Player], None]] = []

    def update_player(self, player_parsed: ParsedPlayer):
        player = Player.from_parsed_player(player_parsed)
        self.players[player.uid] = player
        self.players_checked[player.uid] = time()
        self.updated.append(player)
        return player

    def hook_updated(self):
        for player in self.updated:
            _call_hooks(self.updated_hooks, player)
        for player in self.deleted:
            _call_hooks(self.deleted_hooks, player)
        self.updated = []
        self.deleted = []

    def delete_player(self, player: HasUid):
        try:
            player = self.players[player.uid]
            del self.players[player.uid]
            del self.players_checked[player.uid]
            del Player.players[player.uid]  # hmm
            self.deleted.append(player)
        except KeyError:
            pass

    def timeout_players(self):
        now = time()
        to_delete = []

        for uid, last_time in self.players_checked.items():
            if now - last_time >= self.timeout_seconds:
                player = self.players[uid]
                to_delete.append(player)

        for player in to_delete:
            self.delete_player(player)

    def get_player_by_index(self, index: int):
        for player in self.players.values():
            if player.index == index:
                return player

    def decide_svo(self, svo: SVOlog):

        # All of the following stuff requires the subject to be a player
        if not isinstance(svo.subject, ParsedPlayer):
            return

        if svo.verb == "disconnected":
            self.delete_player(svo.subject)

        if svo.verb == "connecting":
            return  # TODO: do sth with connecting players

        if svo.verb == "killed" and isinstance(svo.object, ParsedPlayer):
            killer = self.update_player(svo.subject)
            victim = self.update_player(svo.object)
            _call_hooks(self.killed_hooks, killer, victim)

        if svo.verb == "connected":
            connected = self.update_player(svo.subject)
            _call_hooks(self.connected_hooks, connected)

        if svo.verb == "existing":
            self.update_player(svo.subject)

        if svo.verb == "respawned":
            player = self.update_player(svo.subject)
            _call_hooks(self.respawned_hooks, player)

        self.timeout_players()
        self.hook_updated()  # call this to callback all updates after other callbacks
