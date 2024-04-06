import os
import sys
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
import json
import random

# For physics
from Physics import *

# Reset DB every time server starts
Database(reset=True).close()

# Hardcoded values
TABLE_NAME = "table.svg"
EMPTY_NAME = "empty.svg"
FOLDER = "frontend"

# Global variables used to make working with the server a LOT easier
table: Table = None
game: Game = None 
p1 = None # P1 name
p2 = None # P2 name
name = None # Game name
current_player = None # Current player

def nudge():
    return random.uniform(-1, 1)

# Makes a new table with a full set of balls
def make_new_table():
    table = Table()
    # Cue ball
    pos = Coordinate(TABLE_WIDTH/2.0, TABLE_LENGTH - TABLE_WIDTH/2.0)
    cue = StillBall(0, pos)
    table += cue

    # All balls from front to back (left to right each row)
    # Row 1
    pos = Coordinate(TABLE_WIDTH / 2.0 + nudge(), TABLE_WIDTH / 2.0 + nudge())
    sb = StillBall(1, pos)
    table += sb
    # Row 2
    pos = Coordinate(TABLE_WIDTH/2.0 - (BALL_DIAMETER+4.0)/2.0 + nudge(), TABLE_WIDTH/2.0 - math.sqrt(3.0)/2.0*(BALL_DIAMETER+4.0) + nudge())
    sb = StillBall(2, pos)
    table += sb
    pos = Coordinate(TABLE_WIDTH/2.0 + (BALL_DIAMETER+4.0)/2.0 + nudge(), TABLE_WIDTH/2.0 - math.sqrt(3.0)/2.0*(BALL_DIAMETER+4.0) + nudge())
    sb = StillBall(9, pos)
    table += sb
    # Row 3
    pos = Coordinate(TABLE_WIDTH/2.0 - 2.0*(BALL_DIAMETER+4.0)/2.0 + nudge(), TABLE_WIDTH/2.0 - 2.0*math.sqrt(3.0)/2.0*(BALL_DIAMETER+4.0) + nudge())
    sb = StillBall(3, pos)
    table += sb
    pos = Coordinate(TABLE_WIDTH/2.0 + nudge(), TABLE_WIDTH/2.0 - 2.0*math.sqrt(3.0)/2.0*(BALL_DIAMETER+4.0) + nudge())
    sb = StillBall(8, pos)
    table += sb
    pos = Coordinate(TABLE_WIDTH/2.0 + 2.0*(BALL_DIAMETER+4.0)/2.0 + nudge(), TABLE_WIDTH/2.0 - 2.0*math.sqrt(3.0)/2.0*(BALL_DIAMETER+4.0) + nudge())
    sb = StillBall(10, pos)
    table += sb
    # Row 4
    pos = Coordinate(TABLE_WIDTH/2.0 - 3.0*(BALL_DIAMETER+4.0)/2.0 + nudge(), TABLE_WIDTH/2.0 - 3.0*math.sqrt(3.0)/2.0*(BALL_DIAMETER+4.0) + nudge())
    sb = StillBall(4, pos)
    table += sb
    pos = Coordinate(TABLE_WIDTH/2.0 - (BALL_DIAMETER+4.0)/2.0 + nudge(), TABLE_WIDTH/2.0 - 3.0*math.sqrt(3.0)/2.0*(BALL_DIAMETER+4.0) + nudge())
    sb = StillBall(14, pos)
    table += sb
    pos = Coordinate(TABLE_WIDTH/2.0 + (BALL_DIAMETER+4.0)/2.0 + nudge(), TABLE_WIDTH/2.0 - 3.0*math.sqrt(3.0)/2.0*(BALL_DIAMETER+4.0) + nudge())
    sb = StillBall(7, pos)
    table += sb
    pos = Coordinate(TABLE_WIDTH/2.0 + 3.0*(BALL_DIAMETER+4.0)/2.0 + nudge(), TABLE_WIDTH/2.0 - 3.0*math.sqrt(3.0)/2.0*(BALL_DIAMETER+4.0) + nudge())
    sb = StillBall(11, pos)
    table += sb
    # Row 5
    pos = Coordinate(TABLE_WIDTH/2.0 - 4.0*(BALL_DIAMETER+4.0)/2.0 + nudge(), TABLE_WIDTH/2.0 - 4.0*math.sqrt(3.0)/2.0*(BALL_DIAMETER+4.0) + nudge())
    sb = StillBall(12, pos)
    table += sb
    pos = Coordinate(TABLE_WIDTH/2.0 - 2.0*(BALL_DIAMETER+4.0)/2.0 + nudge(), TABLE_WIDTH/2.0 - 4.0*math.sqrt(3.0)/2.0*(BALL_DIAMETER+4.0) + nudge())
    sb = StillBall(6, pos)
    table += sb
    pos = Coordinate(TABLE_WIDTH/2.0 + nudge(), TABLE_WIDTH/2.0 - 4.0*math.sqrt(3.0)/2.0*(BALL_DIAMETER+4.0) + nudge())
    sb = StillBall(15, pos)
    table += sb
    pos = Coordinate(TABLE_WIDTH/2.0 + 2.0*(BALL_DIAMETER+4.0)/2.0 + nudge(), TABLE_WIDTH/2.0 - 4.0*math.sqrt(3.0)/2.0*(BALL_DIAMETER+4.0) + nudge())
    sb = StillBall(13, pos)
    table += sb
    pos = Coordinate(TABLE_WIDTH/2.0 + 4.0*(BALL_DIAMETER+4.0)/2.0 + nudge(), TABLE_WIDTH/2.0 - 4.0*math.sqrt(3.0)/2.0*(BALL_DIAMETER+4.0) + nudge())
    sb = StillBall(5, pos)
    table += sb

    return table

def save_table(table: Table):
    with open(f"{FOLDER}/{TABLE_NAME}", "w") as f:
        f.write(table.svg(include_id=True))
        f.close()

class Handler(BaseHTTPRequestHandler):
    def write_json(self, data):
        content = json.dumps(data)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", len(content))
        self.end_headers()
        self.wfile.write(bytes(content, "utf-8"))

    def do_GET(self):
        parsed = urlparse(self.path)
        path = f"./{FOLDER}{parsed.path}"

        if parsed.path in ["/index.html"]:
            f = open(path)
            content = f.read()
            f.close()

            # Generate headers
            self.send_response(200)
            self.send_header("Content-Type", "text/html")
            self.send_header("Content-Length", len(content))
            self.end_headers()

            # Send to browser
            self.wfile.write(bytes(content, "utf-8"))
        elif ((parsed.path.startswith("/table") and parsed.path.endswith(".svg")) or parsed.path in ["/empty.svg"]) and os.path.exists(path):
            f = open(path)
            content = f.read()
            f.close()

            # Generate headers
            self.send_response(200)
            self.send_header("Content-Type", "image/svg+xml")
            self.send_header("Content-Length", len(content))
            self.end_headers()

            # Send to browser
            self.wfile.write(bytes(content, "utf-8"))
        elif os.path.exists(path) and os.path.isfile(path):
            # This case is so that the server can load any files that exist in the
            # directory. This is implemented so index.html can access its corresponding .css / .js
            f = open(path)
            content = f.read()
            f.close()

            self.send_response(200)
            self.send_header("Content-Length", len(content))
            self.end_headers()
            self.wfile.write(bytes(content, "utf-8"))
        else:
            # Raise error
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: %s not found" % parsed.path, "utf-8"))


    def do_POST(self):
        # Use global variables
        global table
        global game
        global p1, p2, name, current_player
        parsed = urlparse(self.path)

        if parsed.path in ["/api/table/shoot"]:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            data = json.loads(data_string)
            
            prev_player = current_player
            current_player, elapsed, balls_sunk, tables = game.shoot(name, current_player, table, data["x"], data["y"])
            table = tables[-1] # Update with the next table
            if elapsed < 0:
                print("Segment function failed: Aborting...")
                self.write_json({"svg": None})
                current_player = prev_player
                return

            with open(f"{FOLDER}/{TABLE_NAME}", "w") as f:
                f.write(FULL_HEADER)
                for i, table in enumerate(tables):
                    f.write(table.balls_svg(i, True if i == len(tables) - 1 else False))
                f.write(FOOTER)

            
            if current_player:
                self.write_json({"svg": TABLE_NAME, "current": current_player, "low": game.low, "elapsed": elapsed,
                                 "frames": [f"frame-{i}" for i in range(len(tables))], "current": current_player, "ongoing": True,
                                 "balls": [f"ball-{num}" for num in balls_sunk]})
            else:
                # Decide winner
                prev_table = tables[-2] # Get table before emptying table
                if any(ball in game.balls[prev_player] for ball in prev_table.balls_left()):
                    winner = game.other_player(prev_player) # 8 ball sunk early
                else:
                    winner = prev_player
                self.write_json({"svg": TABLE_NAME, "current": current_player, "low": game.low, "elapsed": elapsed,
                                 "frames": [f"frame-{i}" for i in range(len(tables))], "current": winner, "ongoing": False,
                                 "balls": [f"ball-{num}" for num in balls_sunk]})
            
            # Write frames after sending result
            db = Database()
            shotID = db.writeShot(prev_player, game.gameID)
            for table in tables:
                tableID = db.writeTable(table, False)
                db.writeTableShot(tableID + 1, shotID, False)
            db.conn.commit()
            db.close()
        elif parsed.path in ["/api/table/new"]:
            data_string = self.rfile.read(int(self.headers['Content-Length']))
            data = json.loads(data_string)

            p1 = data["p1"]
            p2 = data["p2"]
            name = data["game"]
            game = Game(None, name, p1, p2)
            table = make_new_table()
            save_table(table)
            current_player = random.choice([p1, p2])
            data = {"svg": TABLE_NAME, "current": current_player, "low": None}
            self.write_json(data)
        else:
            # Raise error
            self.send_response(404)
            self.end_headers()
            self.wfile.write(bytes("404: %s not found" % parsed.path, "utf-8"))
        

if __name__ == "__main__":
    # ID: 1221363 -> Use port: 51363
    # Command: python server.py 51363
    if (len(sys.argv) != 2):
        print("This file must be invoked with a single command line argument representing the server port")
        exit(1)
    # Use "0.0.0.0" for docker container and "localhost" locally
    server = HTTPServer(("0.0.0.0", int(sys.argv[1])), Handler)
    print(f"Server listing on port: http://localhost:{int(sys.argv[1])}")
    server.serve_forever()