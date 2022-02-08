from typing import Callable, List, Literal, Union, overload

from dataclasses import dataclass
from logparse.playerlist import Player, Playerlist, _call_hooks
from logparse.rawparse import (
    ChatMessage as RawChatMessage,
    ParseableLogMessage,
    parse_msg,
)


@dataclass
class ChatMessage:
    content: str
    sender: Player
    chat_id: int  # TODO: make this a enum once i know which chat is which

    def __str__(self):
        return f"{self.sender.name} ({self.chat_id}): {self.content}"


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
        if isinstance(p_msg, ParseableLogMessage):
            self.playerlist.decide_svo(p_msg.svo_log)

        if isinstance(p_msg, RawChatMessage):
            self.recieve_chat(p_msg)

    def recieve_chat(self, msg_: RawChatMessage):
        player = self.playerlist.get_player_by_index(msg_.index)
        if player:
            msg = ChatMessage(msg_.message, player, msg_.chat_id)
        else:
            msg = ChatMessage(
                msg_.message, Player.create("unknown_player", -9999), msg_.chat_id
            )
        _call_hooks(self.message_hooks, msg)
