import socket
import threading
import constants
from robot import Robot
import utils

class Server:
    def __init__(self):
        self.threads = []

    def get_com(self, m_socket):
        print(f"[LISTENING] Server is listening on {socket.gethostbyname(socket.gethostname())}")
        try:
            while True:
                conn, addr = m_socket.accept()
                thread = threading.Thread(target=self.get_thread, args=(conn, addr))
                thread.start()
                self.threads.append(thread)
        finally:
            for t in self.threads:
                t.join()

    def get_thread(self, conn, addr):
        robot = Robot()
        additional_data = ""

        try:
            data, additional_data = utils.get_message(conn, 0, additional_data)
            robot.get_name(robot, conn, data)
            data, additional_data = utils.get_message(conn, 1, additional_data)
            hash_code = utils.get_id(robot, conn, data)
            data, additional_data = utils.get_message(conn, 2, additional_data)
            utils.get_confirmation(robot, conn, data, hash_code)
            robot.get_starting_direction(conn, additional_data)

            while True:
                data, additional_data = utils.get_message(conn, 3, additional_data)
                if constants.CLIENT_RECHARGING in data:
                    utils.recharging(conn)
                if data:
                    x, y = utils.get_coordinates(data, conn)
                    if x == 0 and y == 0:
                        robot.pickup(conn)
                        break
                    if robot.y_obstacle:
                        self.process_y_obstacles(robot, conn, x, y)
                    if robot.obstacle:
                        self.process_obstacles(robot, conn, x, y)
                    direction = robot.choose_direction(x, y)
                    robot.moves(conn, direction)
                    if robot.move:
                        robot.previousX = x
                        robot.previousY = y
        finally:
            conn.close()

    def process_y_obstacles(self, robot, conn, x, y):
        for i in range(3):
            robot.y_obstacles(conn, x, y, i)
            if i == 0 or i == 2:
                coordinates = utils.get_message(conn, 3)[0]
                x, y = utils.get_coordinates(coordinates, conn)
            else:
                utils.get_message(conn, 3)

    def process_obstacles(self, robot, conn, x, y):
        for i in range(8):
            robot.obstacles(conn, x, y, i)
            if i in (0, 2, 5, 7):
                coordinates = utils.get_message(conn, 3)[0]
                x, y = utils.get_coordinates(coordinates, conn)
            else:
                utils.get_message(conn, 3)

    def handle_obstacle(self, robot, conn, x, y):
        if robot.direction in (constants.UP, constants.DOWN):
            robot.y_obstacle = True
            for i in range(3):
                robot.y_obstacles(conn, x, y, i)
                if i == 0 or i == 2:
                    coordinates = utils.get_message(conn, 3)[0]
                    x, y = utils.get_coordinates(coordinates, conn)
                else:
                    utils.get_message(conn, 3)
        else:
            robot.obstacle = True
            for i in range(8):
                robot.obstacles(conn, x, y, i)
                if i in (0, 2, 5, 7):
                    coordinates = utils.get_message(conn, 3)[0]
                    x, y = utils.get_coordinates(coordinates, conn)
                else:
                    utils.get_message(conn, 3)
