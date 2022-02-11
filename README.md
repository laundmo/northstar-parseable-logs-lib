# Northstar ParseableLogs lib

This is a companion python module to my Northstar mod [ParseableLogs](https://northstar.thunderstore.io/package/laundmo/ParseableLogs/)

## Usage:

Note: The library should be fully typehinted, so i encourage you to use a typechecking linter such as pylance

The basic usage is as follows

```py
from logparse import Server
from logparse.models import Player

server = Server(playerlist_timeout=120)

@server.add_callback("killed")
def on_killed(killer: Player, victim: Player):
    print(killer, "killed", victim)

for log_line in your_log_source():
    server.recieve_log(log_line)
```

This will parse all the logs using recieve_log. You will likely want to somehow stream them live from the Northstar server.

Players will be removed from the playerlist after timeout seconds, this is to ensure that if a disconnect event is missed, the player doesnt remain tracked in the playerlist forever.

Server object attributes:

- playerlist: Playerlist
- recieve_log: function to call with the string log message
- add_callback: decorator to add a callback

Playerlist object attributes:

- players: Dict[int uid, Player]

Player object attributes:

- location: Vector
- teamId: int
- ping: int
- kills: int
- deaths: int
- alive: bool
- titan: bool

available events for add_callback are:

- killed: victim killed by killer, callback args: (Player, Player)
- connected: player connected to the server, callback args: (Player)
- respawned: player respawned, callback args: (Player)
- updated: player object updated (most likely a new position vector), callback args: (Player)
- deleted: player object deleted (due to disconnect or timeout), callback args: (Player)

keep in mind that callbacks will be called after you call recieve_log on the same thread. The entire library is synchronous.

Please check out the loki-example.py for a example of how to use this module with the Grafan Loki log collector.
