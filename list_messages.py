import socket

PORT = 60000
HEADER = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!Disconnect"


def connect():
    """Establishes connection to the server."""
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        client.connect(ADDR)
        print(f"Connected to server at {ADDR}")
        return client
    except Exception as e:
        print(f"[ERROR] Unable to connect to server: {e}")
        return None


def start():
    """Starts listening for messages from the server."""
    connection = connect()
    if not connection:
        return

    try:
        while True:
            message = connection.recv(HEADER).decode(FORMAT)
            if message:
                print(message)
            else:
                print("[SERVER] Connection closed by the server.")
                break

            if message == DISCONNECT_MESSAGE:
                print("Disconnected from server.")
                break
    except KeyboardInterrupt:
        print("\n[USER] Disconnected by user.")
    finally:
        connection.close()
        print("Connection closed.")


start()
