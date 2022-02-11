from typing import Callable, List, Literal, Union, overload

from r2logparse.models import ChatMessage, Player, ParseableLog, ChatLog
from r2logparse.playerlist import Playerlist
from r2logparse.utils import call_hooks, parse_msg


class Server:
    def __init__(self, playerlist_timeout: int = 60):
        self.playerlist = Playerlist(playerlist_timeout)
        self.message_hooks: List[Callable[[ChatMessage], None]] = []

    @overload
    def add_callback(
        self, eventname: Literal["killed"]
    ) -> Callable[[Callable[[Player, Player], None]], None]:
        ...

    @overload
    def add_callback(
        self,
        eventname: Union[
            Literal["connected"],
            Literal["respawned"],
            Literal["updated"],
            Literal["deleted"],
        ],
    ) -> Callable[[Callable[[Player], None]], None]:
        ...

    @overload
    def add_callback(
        self, eventname: Literal["message"]
    ) -> Callable[[Callable[[ChatMessage], None]], None]:
        ...

    def add_callback(self, eventname):
        if eventname == "message":
            return self.message_hooks.append

        # playerlist
        if eventname == "killed":
            return self.playerlist.killed_hooks.append
        if eventname == "connected":
            return self.playerlist.connected_hooks.append
        if eventname == "respawned":
            return self.playerlist.respawned_hooks.append
        if eventname == "updated":
            return self.playerlist.updated_hooks.append
        if eventname == "deleted":
            return self.playerlist.deleted_hooks.append

    def recieve_log(self, log: str):
        p_msg = parse_msg(log)
        if isinstance(p_msg, ParseableLog):
            self.playerlist.decide_svo(p_msg.svo_log)

        if isinstance(p_msg, ChatLog):
            self.recieve_chat(p_msg)

    def recieve_chat(self, msg_: ChatLog):
        player = self.playerlist.get_player_by_index(msg_.index)
        if player:
            msg = ChatMessage(msg_.message, player, msg_.chat_id)
        else:
            msg = ChatMessage(
                msg_.message, Player.create("unknown_player", -9999), msg_.chat_id
            )
        call_hooks(self.message_hooks, msg)
