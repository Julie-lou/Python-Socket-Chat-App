from colorama import Fore, Style, init
import socket
import threading
import sys
import random

PORT = 60000
HEADER = 2048
SERVER = socket.gethostbyname(socket.gethostname())
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!Disconnect"

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

user_colors = {}  # Dictionary to store username-color mapping

def get_user_color(username):
    """Assign a color to each user based on their username."""
    if username not in user_colors:
        # Randomly assign a color if the user doesn't have one
        user_colors[username] = random.choice(color_options)
    return user_colors[username]

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

def send(client, msg):
    """Sends a message to the server."""
    try:
        client.send(msg.encode(FORMAT))
    except Exception as e:
        print(f"[ERROR] Failed to send message: {e}")

def receive(client):
    """Continuously receives messages from the server."""
    while True:
        try:
            message = client.recv(HEADER).decode(FORMAT)
            if message:
                sys.stdout.write("\033[K\r" + message + "\nYou: ")
                sys.stdout.flush()
            else:
                break
        except Exception:
            break

def handle_input(client, username):
    """Handles user input and sends it to the server."""
    user_color = get_user_color(username)  # Get color for the user
    send(client, username)  # Send username as the first message
    while True:
        msg = input("You: ")
        if msg.lower() == '!exit':
            break
        # Send message with the user's color
        send(client, f" {msg}{Style.NORMAL}")

def start():
    """Main function to initialize and start the client."""
    init()
    
    if input("CONNECT or NOT: ").strip().lower() != "connect":
        print("Exiting program.")
        return

    connection = connect()
    if not connection:
        return

    username = input("What's your name: ")

    # Start thread to receive messages
    threading.Thread(target=receive, args=(connection,), daemon=True).start()

    try:
        handle_input(connection, username)
    except KeyboardInterrupt:
        print(f"\n{username} has been disconnected!")
    finally:
        send(connection, DISCONNECT_MESSAGE)
        connection.close()
        print('Disconnected')

start()