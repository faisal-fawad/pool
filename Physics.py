import phylib
import sqlite3
import math

################################################################################
# Import constants from phylib as global variables
BALL_RADIUS   = phylib.PHYLIB_BALL_RADIUS
BALL_DIAMETER = phylib.PHYLIB_BALL_DIAMETER
HOLE_RADIUS   = phylib.PHYLIB_HOLE_RADIUS
TABLE_LENGTH  = phylib.PHYLIB_TABLE_LENGTH
TABLE_WIDTH   = phylib.PHYLIB_TABLE_WIDTH
SIM_RATE      = phylib.PHYLIB_SIM_RATE
VEL_EPSILON   = phylib.PHYLIB_VEL_EPSILON
DRAG          = phylib.PHYLIB_DRAG
MAX_TIME      = phylib.PHYLIB_MAX_TIME
MAX_OBJECTS   = phylib.PHYLIB_MAX_OBJECTS
HEADER        = """<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<!DOCTYPE svg PUBLIC "-//W3C//DTD SVG 1.1//EN" "http://www.w3.org/Graphics/SVG/1.1/DTD/svg11.dtd">
<svg width="700" height="1375" viewBox="-25 -25 1400 2750" xmlns="http://www.w3.org/2000/svg" xmlns:xlink="http://www.w3.org/1999/xlink">
  <rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" />\n"""
FULL_HEADER   = HEADER + """<rect width="1350" height="2700" x="0" y="0" fill="#C0D0C0" />
  <rect width="1400" height="25" x="-25" y="-25" fill="darkgreen" />
  <rect width="1400" height="25" x="-25" y="2700" fill="darkgreen" />
  <rect width="25" height="2750" x="-25" y="-25" fill="darkgreen" />
  <rect width="25" height="2750" x="1350" y="-25" fill="darkgreen" />
  <circle cx="0" cy="0" r="114" fill="black" />
  <circle cx="0" cy="1350" r="114" fill="black" />
  <circle cx="0" cy="2700" r="114" fill="black" />
  <circle cx="1350" cy="0" r="114" fill="black" />
  <circle cx="1350" cy="1350" r="114" fill="black" />
  <circle cx="1350" cy="2700" r="114" fill="black" />
"""
FOOTER        = """</svg>\n"""
FRAME_RATE    = 0.01
CUE_NUMBER    = 0
BLACK_NUMBER  = 8
MAX_COUNT     = 2500

################################################################################
# The standard colours of pool balls
# Sourced from: https://billiards.colostate.edu/faq/ball/colors/
BALL_COLOURS = [ 
    "WHITE",
    "YELLOW",
    "BLUE",
    "RED",
    "PURPLE",
    "ORANGE",
    "GREEN",
    "BROWN",
    "BLACK",
    "LIGHTYELLOW",
    "LIGHTBLUE",
    "PINK",             # no LIGHTRED
    "MEDIUMPURPLE",     # no LIGHTPURPLE
    "LIGHTSALMON",      # no LIGHTORANGE
    "LIGHTGREEN",
    "SANDYBROWN",       # no LIGHTBROWN 
]


################################################################################
class Coordinate(phylib.phylib_coord):
    """
    This creates a Coordinate subclass, that adds nothing new, but looks
    more like a nice Python class.
    """
    pass


################################################################################
class StillBall(phylib.phylib_object):
    """
    Python StillBall class.
    """

    def __init__(self, number, pos):
        phylib.phylib_object.__init__(self, phylib.PHYLIB_STILL_BALL, number, pos, None, None, 0.0, 0.0)
        self.__class__ = StillBall


    def svg(self, include_id=False):
        obj = self.obj.still_ball
        return """  <circle %s cx="%d" cy="%d" r="%d" fill="%s" />\n""" % ('id="cue"' if obj.number == 0 and include_id else '',
                                                                            obj.pos.x, obj.pos.y, BALL_RADIUS, BALL_COLOURS[obj.number])
    

    def number(self):
        return self.obj.still_ball.number


################################################################################
class RollingBall(phylib.phylib_object):
    """
    Python RollingBall class.
    """

    def __init__(self, number, pos, vel, acc):
        phylib.phylib_object.__init__(self, phylib.PHYLIB_ROLLING_BALL, number, pos, vel, acc, 0.0, 0.0)
        self.__class__ = RollingBall


    def svg(self, include_id=False):
        obj = self.obj.rolling_ball
        return """  <circle %s cx="%d" cy="%d" r="%d" fill="%s" />\n""" % ('id="cue"' if obj.number == 0 and include_id else '', 
                                                                           obj.pos.x, obj.pos.y, BALL_RADIUS, BALL_COLOURS[obj.number])


    def number(self):
        return self.obj.rolling_ball.number

################################################################################
class Hole(phylib.phylib_object):
    """
    Python Hole class.
    """

    def __init__(self, pos):
        phylib.phylib_object.__init__(self, phylib.PHYLIB_HOLE, None, pos, None, None, 0.0, 0.0)
        self.__class__ = Hole


    def svg(self):
        obj = self.obj.hole
        return """  <circle cx="%d" cy="%d" r="%d" fill="black" />\n""" % (obj.pos.x, obj.pos.y, HOLE_RADIUS)


################################################################################
class HCushion(phylib.phylib_object):
    """
    Python HCushion class.
    """

    def __init__(self, y):
        phylib.phylib_object.__init__(self, phylib.PHYLIB_HCUSHION, None, None, None, None, 0.0, y)
        self.__class__ = HCushion


    def svg(self):
        obj = self.obj.hcushion
        return """  <rect width="1400" height="25" x="-25" y="%d" fill="darkgreen" />\n""" % (obj.y if obj.y != 0 else obj.y - 25)


################################################################################
class VCushion(phylib.phylib_object):
    """
    Python VCushion class.
    """

    def __init__(self, x):
        phylib.phylib_object.__init__(self, phylib.PHYLIB_VCUSHION, None, None, None, None, x, 0.0)
        self.__class__ = VCushion


    def svg(self):
        obj = self.obj.vcushion
        return """  <rect width="25" height="2750" x="%d" y="-25" fill="darkgreen" />\n""" % (obj.x if obj.x != 0 else obj.x - 25)


################################################################################
class Table(phylib.phylib_table):
    """
    Pool table class.
    """

    def __init__(self):
        """
        Table constructor method.
        This method call the phylib_table constructor and sets the current
        object index to -1.
        """
        phylib.phylib_table.__init__(self)
        self.current = -1

    def __iadd__(self, other):
        """
        += operator overloading method.
        This method allows you to write "table+=object" to add another object
        to the table.
        """
        self.add_object(other)
        return self

    def __iter__(self):
        """
        This method adds iterator support for the table.
        This allows you to write "for object in table:" to loop over all
        the objects in the table.
        """
        return self

    def __next__(self):
        """
        This provides the next object from the table in a loop.
        """
        self.current += 1  # increment the index to the next object
        if self.current < MAX_OBJECTS:   # check if there are no more objects
            return self[self.current] # return the latest object

        # if we get there then we have gone through all the objects
        self.current = -1    # reset the index counter
        raise StopIteration  # raise StopIteration to tell for loop to stop

    def __getitem__(self, index):
        """
        This method adds item retreivel support using square brackets [ ] .
        It calls get_object (see phylib.i) to retreive a generic phylib_object
        and then sets the __class__ attribute to make the class match
        the object type.
        """
        result = self.get_object(index) 
        if result==None:
            return None
        if result.type == phylib.PHYLIB_STILL_BALL:
            result.__class__ = StillBall
        if result.type == phylib.PHYLIB_ROLLING_BALL:
            result.__class__ = RollingBall
        if result.type == phylib.PHYLIB_HOLE:
            result.__class__ = Hole
        if result.type == phylib.PHYLIB_HCUSHION:
            result.__class__ = HCushion
        if result.type == phylib.PHYLIB_VCUSHION:
            result.__class__ = VCushion
        return result

    def __str__(self):
        """
        Returns a string representation of the table that matches
        the phylib_print_table function from A1Test1.c.
        """
        result = ""    # create empty string
        result += "time = %6.1f;\n" % self.time    # append time
        for i,obj in enumerate(self): # loop over all objects and number them
            result += "  [%02d] = %s\n" % (i,obj)  # append object description
        return result  # return the string

    def segment(self):
        """
        Calls the segment method from phylib.i (which calls the phylib_segment
        functions in phylib.c.
        Sets the __class__ of the returned phylib_table object to Table
        to make it a Table object.
        """

        result = phylib.phylib_table.segment(self)
        if result:
            result.__class__ = Table
            result.current = -1
        return result
    
    def roll(self, t):
        new = Table()
        for ball in self:
            if isinstance(ball, RollingBall):
                new_ball = RollingBall(ball.obj.rolling_ball.number,
                                       Coordinate(0,0),
                                       Coordinate(0,0),
                                       Coordinate(0,0))
                phylib.phylib_roll(new_ball, ball, t)
                new += new_ball
            if isinstance(ball, StillBall):
                new_ball = StillBall(ball.obj.still_ball.number,
                                     Coordinate(ball.obj.still_ball.pos.x, ball.obj.still_ball.pos.y))
                new += new_ball
        return new

    def get_cue(self):
        cue = None
        for ball in iter(self):
            if isinstance(ball, StillBall):
                if ball.obj.still_ball.number == 0:
                    cue = ball
                    # Cannot return here or self.current is positioned incorrectly
        return cue

    def svg(self, include_id=False):
        contents = ""
        for object in iter(self):
            if object:
                if include_id and (isinstance(object, StillBall) or isinstance(object, RollingBall)):
                    contents += object.svg(include_id=True)
                else:
                    contents += object.svg()
        return HEADER + contents + FOOTER
    
    def balls_svg(self, frame, include_id=False):
        contents = ""
        for object in iter(self):
            if isinstance(object, StillBall) or isinstance(object, RollingBall):
                contents += object.svg(include_id)
        return f'<g id="frame-{frame}">\n{contents}</g>\n'
    
    def balls_left(self):
        balls_left = []
        for object in iter(self):
            if isinstance(object, StillBall) or isinstance(object, RollingBall):
                balls_left.append(object.number())
        return balls_left


class Database():
    def __init__(self, reset=False):
        if reset:
            open("phylib.db", "w").close()
        self.conn = sqlite3.connect("phylib.db")

    def createDB(self):
        self.cur = self.conn.cursor()
        # Ball table
        self.cur.execute("""CREATE TABLE IF NOT EXISTS Ball (
                         BALLID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                         BALLNO INTEGER NOT NULL,
                         XPOS FLOAT NOT NULL,
                         YPOS FLOAT NOT NULL,
                         XVEL FLOAT,
                         YVEL FLOAT
        )""")

        # TTable
        self.cur.execute("""CREATE TABLE IF NOT EXISTS TTable (
                         TABLEID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                         TIME FLOAT NOT NULL
        )""")

        # BallTable
        self.cur.execute("""CREATE TABLE IF NOT EXISTS BallTable (
                         BALLID INTEGER NOT NULL,
                         TABLEID INTEGER NOT NULL,
                         FOREIGN KEY (BALLID) REFERENCES Ball (BALLID),
                         FOREIGN KEY (TABLEID) REFERENCES TTable (TABLEID)
        )""")

        # Shot
        self.cur.execute("""CREATE TABLE IF NOT EXISTS Shot (
                         SHOTID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                         PLAYERID INTEGER NOT NULL,
                         GAMEID INTEGER NOT NULL,
                         FOREIGN KEY (PLAYERID) REFERENCES Player (PLAYERID),
                         FOREIGN KEY (GAMEID) REFERENCES Game (GAMEID)
        )""")

        # TableShot
        self.cur.execute("""CREATE TABLE IF NOT EXISTS TableShot (
                         TABLEID INTEGER NOT NULL,
                         SHOTID INTEGER NOT NULL,
                         FOREIGN KEY (TABLEID) REFERENCES TTable (TABLEID),
                         FOREIGN KEY (SHOTID) REFERENCES Shot (SHOTID)
        )""")

        # Game
        self.cur.execute("""CREATE TABLE IF NOT EXISTS Game (
                         GAMEID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                         GAMENAME VARCHAR(64) NOT NULL
        )""")

        # Player
        self.cur.execute("""CREATE TABLE IF NOT EXISTS Player (
                         PLAYERID INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
                         GAMEID INTEGER NOT NULL,
                         PLAYERNAME VARCHAR(64) NOT NULL,
                         FOREIGN KEY (GAMEID) REFERENCES Game (GAMEID)
        )""")
        self.cur.close()
        self.conn.commit()

    def readTable(self, tableID, commit=True):
        self.cur = self.conn.cursor()
        res = self.cur.execute("""SELECT * FROM TTable WHERE TTable.TABLEID=?""", (tableID + 1,))
        res_table = res.fetchone()
        if res_table is None:
            return None # No table with matching ID found
        
        table = Table()
        table.time = res_table[1]
        for ball in self.cur.execute("""SELECT * FROM Ball INNER JOIN BallTable ON Ball.BALLID=BallTable.BALLID WHERE BallTable.TABLEID=?""", (res_table[0],)):
            # The ball tuple has the following properties: (id, number, posx, posy, velx, vely, id, tableid)
            if ball[4] is None or ball[5] is None:
                pos = Coordinate(ball[2], ball[3])
                sb = StillBall(ball[1], pos)
                table += sb
            else:
                pos = Coordinate(ball[2], ball[3])
                vel = Coordinate(ball[4], ball[5])
                if (phylib.phylib_length(vel) > VEL_EPSILON):
                    acc = Coordinate(float(-vel.x / phylib.phylib_length(vel) * DRAG), float(-vel.y / phylib.phylib_length(vel) * DRAG))
                else:
                    acc = Coordinate(0, 0) # Ball should not be moving
                rb = RollingBall(ball[1], pos, vel, acc)
                table += rb
        
        self.cur.close()
        if commit:
            self.conn.commit()
        return table

    def writeTable(self, table, commit=True):
        self.cur = self.conn.cursor()
        self.cur.execute("""INSERT INTO TTable (TIME) VALUES (?)""", (table.time,))
        tableID = self.cur.lastrowid
        for object in iter(table):
            if object:
                if isinstance(object, StillBall):
                    ball = object.obj.still_ball
                    self.cur.execute("""INSERT INTO Ball (BALLNO, XPOS, YPOS) VALUES (?, ?, ?)""",
                                     (ball.number, ball.pos.x, ball.pos.y,))
                    ballID = self.cur.lastrowid
                    self.cur.execute("""INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?)""",
                                     (ballID, tableID,))
                elif isinstance(object, RollingBall):
                    ball = object.obj.rolling_ball
                    self.cur.execute("""INSERT INTO Ball (BALLNO, XPOS, YPOS, XVEL, YVEL) VALUES (?, ?, ?, ?, ?)""",
                                     (ball.number, ball.pos.x, ball.pos.y, ball.vel.x, ball.vel.y,))
                    ballID = self.cur.lastrowid
                    self.cur.execute("""INSERT INTO BallTable (BALLID, TABLEID) VALUES (?, ?)""",
                                     (ballID, tableID,))
                else:
                    pass # Other classes are handled by definition
        self.cur.close()
        if commit:
            self.conn.commit()
        return tableID - 1
    
    def readGame(self, gameID):
        self.cur = self.conn.cursor()
        players = self.cur.execute("SELECT * FROM Player INNER JOIN Game ON Player.GAMEID=Game.GAMEID WHERE Game.GAMEID=?", (gameID,))
        # The player tuple has the following properties (id, gameid, name, gameid, gamename)
        p1 = next(players)
        p2 = next(players)
        if p2[0] < p1[0]:
            # Flip players based on ID
            ptemp = p1
            p1 = p2
            p2 = ptemp
        self.cur.close()
        self.conn.commit()
        return p1[4], p1[2], p2[2]
    
    def writeGame(self, gameName, player1Name, player2Name):
        self.cur = self.conn.cursor()
        self.cur.execute("""INSERT INTO Game (GAMENAME) VALUES (?)""", (gameName,))
        gameID = self.cur.lastrowid
        self.cur.execute("""INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?)""", (gameID, player1Name,))
        self.cur.execute("""INSERT INTO Player (GAMEID, PLAYERNAME) VALUES (?, ?)""", (gameID, player2Name,))
        self.cur.close()
        self.conn.commit()
        return gameID
    
    def writeShot(self, playerName, gameID):
        self.cur = self.conn.cursor()
        res = self.cur.execute("""SELECT Player.PLAYERID FROM Player WHERE Player.PLAYERNAME=?""", (playerName,))
        res_player = res.fetchone()
        # We can assume that the player name will always exist in the database due to the definition of
        # the Game class -> the constructor adds players (id, name) to the database
        
        self.cur.execute("""INSERT INTO Shot (PLAYERID, GAMEID) VALUES (?, ?)""", (res_player[0], gameID,))
        shotID = self.cur.lastrowid
        self.cur.close()
        self.conn.commit()
        return shotID
    
    def writeTableShot(self, tableID, shotID, commit=True):
        self.cur = self.conn.cursor()
        self.cur.execute("""INSERT INTO TableShot (TABLEID, SHOTID) VALUES (?, ?)""", (tableID, shotID,))
        self.cur.close()
        if commit:
            self.conn.commit()
        return shotID

    def close(self):
        self.conn.commit()
        self.conn.close()


class Game():
    def __init__(self, gameID=None, gameName=None, player1Name=None, player2Name=None):
        self.gameID = gameID
        self.gameName = gameName
        self.player1Name = player1Name
        self.player2Name = player2Name
        self.balls = {f'{player1Name}': [], f"{player2Name}": []}
        self.low = None
        self.db = Database()
        self.db.createDB()
        if self.is_new_game():
            # String values will be provided for all three names
            self.gameID = self.db.writeGame(self.gameName, self.player1Name, self.player2Name)
        else:
            # The gameID will be provided
            self.gameID += 1
            self.gameName, self.player1Name, self.player2Name = self.db.readGame(self.gameID)
        self.db.close()
            
        
    def is_new_game(self):
        if self.gameID is None and all(type == str for type in [type(self.gameName), type(self.player1Name), type(self.player2Name)]):
            return True # This is a valid new game!
        elif type(self.gameID) == int and all(type is None for type in [self.gameName, self.player1Name, self.player2Name]):
            return False # This is a valid ongoing game constructor!
        else:
            raise TypeError # Invalid combination
    
    def other_player(self, name):
        return self.player2Name if name == self.player1Name else self.player1Name

    def shoot(self, gameName, playerName, table: Table, xvel, yvel):
        original_table = phylib.phylib_copy_table(table)
        original_table.__class__ = Table
        original_table.current = -1
        cueBall = table.get_cue()
        temp_cue = StillBall(0, Coordinate(cueBall.obj.still_ball.pos.x, cueBall.obj.still_ball.pos.y))

        # Convert ball to rolling and set ball attributes
        pos = Coordinate(cueBall.obj.still_ball.pos.x, cueBall.obj.still_ball.pos.y)
        vel = Coordinate(xvel, yvel)
        if (phylib.phylib_length(vel) > VEL_EPSILON):
            acc = Coordinate(float(-vel.x / phylib.phylib_length(vel) * DRAG), float(-vel.y / phylib.phylib_length(vel) * DRAG))
        else:
            acc = Coordinate(0, 0) # Ball should not be moving
        cueBall.type = phylib.PHYLIB_ROLLING_BALL
        cueBall.obj.rolling_ball.number = 0
        cueBall.obj.rolling_ball.pos.x = pos.x
        cueBall.obj.rolling_ball.pos.y = pos.y
        cueBall.obj.rolling_ball.vel.x = vel.x
        cueBall.obj.rolling_ball.vel.y = vel.y
        cueBall.obj.rolling_ball.acc.x = acc.x
        cueBall.obj.rolling_ball.acc.y = acc.y

        # Run segment
        count = 0
        tables = []
        balls_sunk = []
        full_start = table.time
        while table:
            count += 1
            start = table.time
            temp_table = table
            table = table.segment()
            if table:
                end = table.time
                elapsed = math.floor((end - start) / FRAME_RATE)
                for i in range(elapsed):
                    time = i * FRAME_RATE
                    new_table = temp_table.roll(time)
                    new_table.time = start + time
                    tables.append(new_table)
                tables.append(table)
                balls_sunk.extend(segment_sunk(temp_table, table))
            if not table:
                full_elapsed = temp_table.time - full_start
                # Only write table at the end of the segment
                if CUE_NUMBER in balls_sunk:
                    temp_table += temp_cue
                    tables.append(temp_table)
                if BLACK_NUMBER in balls_sunk:
                    tables.append(Table()) # Empty table
            if count > MAX_COUNT:
                return None, -1, None, [original_table]
        

        # Simple game logic required for A4
        # Assign high and low balls to players
        balls = [ball for ball in balls_sunk if ball != BLACK_NUMBER and ball != CUE_NUMBER]
        if (len(self.balls[playerName]) == 0 or len(self.balls[self.other_player(playerName)]) == 0) and len(balls) != 0:
            if balls[0] in range(1, 8): # 1-7
                self.balls[playerName] = list(range(1, 8))
                self.balls[self.other_player(playerName)] = list(range(9, 16))
                self.low = playerName
            else: # 9-15
                self.balls[playerName] = list(range(9, 16))
                self.balls[self.other_player(playerName)] = list(range(1, 8))
                self.low = self.other_player(playerName)
        
        # Determine next player
        if BLACK_NUMBER in balls_sunk:
            next_player = None
        elif any(ball in balls_sunk for ball in self.balls[playerName]):
            next_player = playerName # Bonus turn for sinking own ball
        else:
            next_player = self.other_player(playerName)      
      
        # NOTE: the above logic does not handle states which determine victory or defeat, it only returns None
        # as the next player. Handling this is the responsiblity of the server. 
        return next_player, full_elapsed, balls_sunk, tables
        
def segment_sunk(table_before: Table, table_after: Table):
    balls_sunk = []
    for ball_before in iter(table_before):
        if isinstance(ball_before, StillBall) or isinstance(ball_before, RollingBall):
            found = False
            for ball_after in iter(table_after):
                if isinstance(ball_after, StillBall) or isinstance(ball_after, RollingBall):
                    if ball_before.number() == ball_after.number():
                        found = True
                        table_after.current = -1
                        break
            if not found:
                balls_sunk.append(ball_before.number())
    return balls_sunk