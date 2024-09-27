import threading
import socket
import logging

# Set up logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PORT = 5050
SERVER = "localhost"
ADDR = (SERVER, PORT)
FORMAT = "utf-8"
DISCONNECT_MESSAGE = "!DISCONNECT"

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(ADDR)

clients = {}
clients_lock = threading.Lock()

def broadcast(message, sender_conn):
    """Broadcast a message to all clients except the sender."""
    with clients_lock:
        for conn in clients.keys():
            if conn != sender_conn:
                try:
                    conn.sendall(message.encode(FORMAT))
                except Exception as e:
                    logging.error(f"Error sending message to client: {e}")

def handle_client(conn, addr):
    logging.info(f"[NEW CONNECTION] {addr} Connected")
    
    # Get username from the client
    username = conn.recv(1024).decode(FORMAT)
    with clients_lock:
        clients[conn] = username  # Store connection and username
        broadcast(f"{username} has joined the chat!", conn)  # Broadcast join message

    try:
        while True:
            msg = conn.recv(1024).decode(FORMAT)
            if not msg:
                break
            logging.info(f"[{username}] {msg}")
            broadcast(f"{username}: {msg}", conn)

    except Exception as e:
        logging.error(f"Error handling client {addr}: {e}")
    finally:
        with clients_lock:
            del clients[conn]
            broadcast(f"{username} has left the chat.", conn)
            logging.info(f"[DISCONNECTED] {addr} Disconnected")
        
        conn.close()

def start():
    logging.info('[SERVER STARTED]!')
    server.listen()
    while True:
        conn, addr = server.accept()
        thread = threading.Thread(target=handle_client, args=(conn, addr))
        thread.start()

if __name__ == "__main__":
    try:
        start()
    except KeyboardInterrupt:
        logging.info("\n[SERVER SHUTTING DOWN]!")
    finally:
        server.close()