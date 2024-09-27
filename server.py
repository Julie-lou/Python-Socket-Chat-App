from colorama import Fore, Style, init
import threading
import socket
import time
import random

PORT = 60000
HEADER = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!Disconnect"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = set()
clients_lock = threading.Lock()
user_colors = {}  # Dictionary to store username-color mapping

# Define a list of colors to choose from
color_options = [
    Fore.RED,
    Fore.GREEN,
    Fore.YELLOW,
    Fore.BLUE,
    Fore.MAGENTA,
    Fore.CYAN,
    Fore.WHITE
]

def get_user_color(username):
    """Assign a color to each user based on their username."""
    if username not in user_colors:
        # Randomly assign a color if the user doesn't have one
        user_colors[username] = random.choice(color_options)
    return user_colors[username]

def broadcast(message, sender=None):
    """Broadcasts a message to all clients except the sender."""
    with clients_lock:
        for client in clients.copy():  # Safely iterate over the set
            if client != sender:
                try:
                    client.send(message)
                except Exception as e:
                    print(f"[ERROR] Unable to send message: {e}")
                    clients.remove(client)

def handle_client(conn, addr):
    """Handles an individual client connection."""
    print(f"[NEW CONNECTION] {addr} connected.")

    try:
        username = conn.recv(HEADER).decode(FORMAT)
        user_color = get_user_color(username)
        print(f"[NEW USER] {username} connected.")
        broadcast(f"{user_color}{username} has joined the chat.{Style.NORMAL}".encode(FORMAT), conn)

        while True:
            msg = conn.recv(HEADER).decode(FORMAT)
            if not msg or msg == DISCONNECT_MESSAGE:
                break

            timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime())
            # Send messages with the user's color
            broadcast(f"{user_color}{username}: {msg}{Style.NORMAL}".encode(FORMAT), conn)
            print(f"\r[{timestamp}] {msg}{Style.NORMAL}")

    finally:
        with clients_lock:
            clients.remove(conn)
        broadcast(f"{Fore.RED}{username} has left the chat.{Style.NORMAL}".encode(FORMAT))
        conn.close()
        print(f"[DISCONNECTED] {username} disconnected.")

def server_broadcast_input():
    """Allows the server to send messages to all clients."""
    while True:
        msg = input("Server: ").strip()
        if msg:
            broadcast(f"{Fore.YELLOW}[SERVER]: {msg}{Style.NORMAL}".encode(FORMAT))

def start():
    """Starts the server and listens for incoming connections."""
    init()
    print(f"[LISTENING] Server is listening on {SERVER}")
    server.listen()

    threading.Thread(target=server_broadcast_input, daemon=True).start()

    while True:
        conn, addr = server.accept()
        with clients_lock:
            clients.add(conn)
        threading.Thread(target=handle_client, args=(conn, addr)).start()
        print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")

print("[STARTING] Server started...")
start()