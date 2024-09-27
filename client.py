import socket
import threading
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

def connect():
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(ADDR)
    return client

def send(client, username):
    while True:
        msg = input(f"{username}: ")
        if msg.strip().lower() == 'q':
            break
        full_message = f"{username}: {msg}"
        client.send(full_message.encode(FORMAT))
    
    client.send(DISCONNECT_MESSAGE.encode(FORMAT))
    client.close()

def receive(client):
    while True:
        try:
            msg = client.recv(1024).decode(FORMAT)
            if msg:
                print(msg)
            else:
                break
        except Exception as e:
            logging.error(f"Error receiving message: {e}")
            break
    client.close()

def start():
    connection = connect()
    username = input("Enter your username: ")  # Prompt user for username
    connection.send(username.encode(FORMAT))  # Send username to server
    
    # Start a thread to receive messages
    receive_thread = threading.Thread(target=receive, args=(connection,))
    receive_thread.start()

    # Start sending messages
    send(connection, username)

if __name__ == "__main__":
    start()