import socket
from server import Server

def main():
    m_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    m_socket.bind((socket.gethostbyname(socket.gethostname()), 5050))
    m_socket.listen()
    server = Server()
    server.get_com(m_socket)

if __name__ == "__main__":
    main()
