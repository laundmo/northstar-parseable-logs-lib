from dataclasses import dataclass
from enum import Enum
import json
import re
from datetime import datetime
from dateutil.parser import parse as parse_dt
from logparse.parseable_log import SVOlog, load as load_svo


class MessageTypes(Enum):
    log = "log"


def get_subclasses(cls):
    for subclass in cls.__subclasses__():
        yield from get_subclasses(subclass)
        yield subclass


@dataclass
class BaseMessage:
    pass


def parse_msg(logmsg: str):
    for subclass in get_subclasses(BaseMessage):
        result = subclass.from_logmsg(logmsg)
        if result:
            return result
    # return logmsg


# https://regex101.com/r/QrTvxU/1
chat_re = re.compile(
    r"\[(?P<time>.*?)\] .*? CServerGameDLL::OnReceivedSayTextMessage -"
    r" (?P<msg>.*)\((?P<player_index>\d), (?P<chat_id>\d), (?P<unknown>\d)\)"
)


@dataclass
class ChatMessage(BaseMessage):
    time: datetime
    message: str
    index: int
    chat_id: int
    unknown_id: int

    @classmethod
    def from_logmsg(cls, msg: str):
        if "CServerGameDLL::OnReceivedSayTextMessage" in msg:
            match = chat_re.search(msg)
            if match:
                time = parse_dt(match.group("time").split("[")[-1])
                chat_msg = match.group("msg")
                player_index = (
                    int(match.group("player_index")) - 1
                )  # -1 because squirrel mismatches with the game
                chat_id = int(match.group("chat_id"))
                unknown_id = int(match.group("unknown"))
                return cls(time, chat_msg, player_index, chat_id, unknown_id)


@dataclass
class ParseableLogMessage(BaseMessage):
    time: datetime
    svo_log: SVOlog

    @classmethod
    def from_logmsg(cls, msg: str):
        if "[ParseableLog]" in msg:
            rest, json_msg = msg.split("[ParseableLog]")
            timestr = rest.split("] [")[0]
            p_time = parse_dt(timestr[timestr.rfind("[") + 1 :])  # extract time part
            try:
                parsed_msg = json.loads(json_msg)
            except ValueError as e:
                print(e)
            else:
                return cls(p_time, load_svo(parsed_msg))
