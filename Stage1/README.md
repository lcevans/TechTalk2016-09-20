# Stage 1 -- Dumb Terminal Server

This stage implements the server logic for the "Dumb Terminal" approach.

Run the server with
```
python server.py --port 6666
```

and connect (as a spoofed client) with netcat via
```
nc localhost 6666
```

You will receieve broadcasts of the game state.

To send key presses/events to the server, copy e.g. `messages/shoot.txt` to the clipboard and paste it into netcat.
The game state will update according to your actions!