import asyncio
import json
from urllib.parse import urlencode

import websockets

from logparse.gameserver import ChatMessage, Server
from logparse.playerlist import Player

gameserver = Server()


@gameserver.add_callback("killed")
def on_killed(killer: Player, victim: Player):
    print(killer, "killed", victim)


@gameserver.add_callback("respawned")
def on_respawned(p: Player):
    print(p, "respawned")


@gameserver.add_callback("message")
def on_message(msg: ChatMessage):
    print(msg)


async def loki_reciever(host, port, logql_query, back_limit=200):

    params = {
        "query": logql_query,
        "limit": back_limit,
    }
    url = f"ws://{host}:{port}/loki/api/v1/tail?{urlencode(params)}"

    async with websockets.connect(url) as websocket:
        async for message in websocket:
            j = json.loads(message)
            for stream in j["streams"]:
                for value in stream["values"]:
                    ts, msg = value
                    gameserver.recieve_log(msg)


asyncio.run(
    loki_reciever(
        "localhost",
        3100,
        """{container_name="northstar-dedicated_sticks_stones_1"}""",
    )
)
