import constants
import utils

class Robot:
    def __init__(self):
        self.previous_loc = None
        self.name         = None
        self.id           = None
        self.obstacle     = False
        self.direction    = None
        self.previousX    = None
        self.previousY    = None
        self.move         = False
        self.y_obstacle   = False

    def choose_direction(self, x, y):
        if 0 > y:
            return constants.UP
        if 0 < y:
            return constants.DOWN
        if 0 > x:
            return constants.RIGHT
        if 0 < x:
            return constants.LEFT

    def pickup(self, conn):
        conn.send(constants.SERVER_PICK_UP)
        final = utils.get_message(conn, 4)[0]
        if constants.CLIENT_RECHARGING in final:
            utils.recharging(conn)
        conn.send(constants.SERVER_LOGOUT)

    def starting_obstacles(self, conn, x, y):
        conn.send(constants.SERVER_TURN_LEFT)
        utils.get_message(conn, 3)
        conn.send(constants.SERVER_MOVE)
        utils.get_message(conn, 3)
        conn.send(constants.SERVER_TURN_RIGHT)
        utils.get_message(conn, 3)
        conn.send(constants.SERVER_MOVE)
        utils.get_message(conn, 3)
        conn.send(constants.SERVER_MOVE)
        utils.get_message(conn, 3)
        conn.send(constants.SERVER_TURN_RIGHT)
        utils.get_message(conn, 3)
        conn.send(constants.SERVER_MOVE)
        coordinates = utils.get_message(conn, 3)[0]
        self.previousX, self.previousY = utils.get_coordinates(coordinates, conn)
        self.direction = utils.get_dir(self.previousX, self.previousY, x, y)
        conn.send(constants.SERVER_TURN_LEFT)
        utils.get_message(conn, 3)

    def y_obstacles(self, conn, x, y, i):
        if i == 0:
            if (x > 0 and self.direction == constants.UP) or (x < 0 and self.direction == constants.DOWN):
                conn.send(constants.SERVER_TURN_LEFT)
            elif (x > 0 and self.direction == constants.DOWN) or (x < 0 and self.direction == constants.UP):
                conn.send(constants.SERVER_TURN_RIGHT)
        elif i == 1:
            conn.send(constants.SERVER_MOVE)
        elif i == 2:
            if (x > 0 and self.direction == constants.UP) or (x < 0 and self.direction == constants.DOWN):
                conn.send(constants.SERVER_TURN_RIGHT)
            elif (x > 0 and self.direction == constants.DOWN) or (x < 0 and self.direction == constants.UP):
                conn.send(constants.SERVER_TURN_LEFT)
            self.y_obstacle = False
            self.previousX = x
            self.previousY = y

    def obstacles(self, conn, x, y, i):
        moves = [
            constants.SERVER_TURN_RIGHT, constants.SERVER_MOVE, constants.SERVER_TURN_LEFT,
            constants.SERVER_MOVE, constants.SERVER_MOVE, constants.SERVER_TURN_LEFT,
            constants.SERVER_MOVE, constants.SERVER_TURN_RIGHT
        ]
        conn.send(moves[i])
        if i == 7:
            self.obstacle = False
            self.previousX = x
            self.previousY = y

    def moves(self, conn, direction):
        turns = {
            (constants.UP,    constants.LEFT): constants.SERVER_TURN_RIGHT, (constants.UP,    constants.RIGHT): constants.SERVER_TURN_LEFT,
            (constants.RIGHT, constants.UP):   constants.SERVER_TURN_RIGHT, (constants.RIGHT, constants.DOWN):  constants.SERVER_TURN_LEFT,
            (constants.LEFT,  constants.UP):   constants.SERVER_TURN_LEFT,  (constants.LEFT,  constants.DOWN):  constants.SERVER_TURN_RIGHT,
            (constants.DOWN,  constants.LEFT): constants.SERVER_TURN_LEFT,  (constants.DOWN,  constants.RIGHT): constants.SERVER_TURN_RIGHT,
        }
        if direction == self.direction:
            conn.send(constants.SERVER_MOVE)
            self.move = True
        else:
            conn.send(turns[(self.direction, direction)])
            self.direction = direction
            self.move = False

    def get_starting_direction(self, conn, additional_data):
        conn.send(constants.SERVER_MOVE)
        coordinates = utils.get_message(conn, 3, additional_data)[0]
        self.previousX, self.previousY = utils.get_coordinates(coordinates, conn)
        if self.previousX == 0 and self.previousY == 0:
            self.pickup(conn)
            conn.close()
            return

        conn.send(constants.SERVER_MOVE)
        coordinates = utils.get_message(conn, 3)[0]
        x, y = utils.get_coordinates(coordinates, conn)
        if x == 0 and y == 0:
            self.pickup(conn)
            conn.close()
            return

        self.direction = utils.get_dir(x, y, self.previousX, self.previousY)
        if not self.direction:
            self.starting_obstacles(conn, x, y)
        direction = self.choose_direction(x, y)
        self.previousX, self.previousY = x, y
        self.moves(conn, direction)
