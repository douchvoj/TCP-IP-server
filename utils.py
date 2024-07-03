import constants

def get_message(conn, stage, additional_data=""):
    data = ""
    while True:
        index = additional_data.find("\a\b")
        if index != -1:
            data = additional_data[:index]
            additional_data = additional_data[index + 2:]
            break
        tmp = conn.recv(1024).decode('utf-8')
        additional_data += tmp

    if stage in [0, 1, 2, 3] and len(data) > 0:
        if stage == 0 and len(data) > constants.CLIENT_USERNAME_LEN:
            conn.send(constants.SERVER_SYNTAX_ERROR)
        elif stage == 1 and len(data) > constants.CLIENT_KEY_ID_LEN:
            conn.send(constants.SERVER_SYNTAX_ERROR)
        elif stage == 2 and len(data) > constants.CLIENT_CONFIRMATION_LEN:
            conn.send(constants.SERVER_SYNTAX_ERROR)
        elif stage == 3 and len(data) > constants.CLIENT_MESSAGE_LEN:
            conn.send(constants.SERVER_SYNTAX_ERROR)
    return data, additional_data

def get_coordinates(data, conn):
    try:
        x, y = map(int, data.split())
    except ValueError:
        conn.send(constants.SERVER_SYNTAX_ERROR)
        raise
    return x, y

def get_dir(x, y, previous_x, previous_y):
    if previous_y - y > 0:
        return constants.UP
    if previous_y - y < 0:
        return constants.DOWN
    if previous_x - x > 0:
        return constants.RIGHT
    if previous_x - x < 0:
        return constants.LEFT
    return None

def recharging(conn):
    recharge = conn.recv(1024).decode('utf-8')
    if constants.CLIENT_FULL_POWER not in recharge:
        conn.send(constants.SERVER_LOGIC_ERROR)
