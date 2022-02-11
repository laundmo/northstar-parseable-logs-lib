from dataclasses import dataclass

from datetime import datetime
import json

import re
from dateutil.parser import parse as parse_dt

from r2logparse.models import SVOlog, load_svo


@dataclass
class BaseLog:
    pass


# https://regex101.com/r/QrTvxU/1
chat_re = re.compile(
    r"\[(?P<time>.*?)\] .*? CServerGameDLL::OnReceivedSayTextMessage -"
    r" (?P<msg>.*)\((?P<player_index>\d), (?P<chat_id>\d), (?P<unknown>\d)\)"
)


@dataclass
class ChatLog(BaseLog):
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
class ParseableLog(BaseLog):
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
