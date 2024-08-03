import socket
import threading
import time
import json
import os

clients = {}
clients_last_activity = {}

DATA_FILE = "clients_data.json"

def load_clients_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as file:
            data = json.load(file)
            for username, info in data.items():
                clients[username] = None  # Clients will connect dynamically
                clients_last_activity[username] = info["last_activity"]
    print("Loaded clients data from file")

def save_clients_data():
    data = {
        username: {"last_activity": last_activity}
        for username, last_activity in clients_last_activity.items()
    }
    with open(DATA_FILE, "w") as file:
        json.dump(data, file)
    print("Saved clients data to file")

def handle_client(client_socket, client_address):
    try:
        # Receive and store the username
        username = client_socket.recv(1024).decode('utf-8')
        clients[username] = client_socket
        clients_last_activity[username] = time.time()
        print(f"{username} ({client_address}) connected")

        while True:
            try:
                client_socket.settimeout(60)  # Set a timeout for inactivity
                message = client_socket.recv(1024).decode('utf-8')
                if not message:
                    break
                clients_last_activity[username] = time.time()  # Update last activity time
                print(f"Received from {username}: {message}")
                
                # Parse the recipient and the message
                recipient, msg = message.split(":", 1)
                send_message_to_client(recipient.strip(), f"{username}: {msg.strip()}")
            except socket.timeout:
                print(f"{username} timed out due to inactivity")
                break
            except ConnectionResetError:
                break
    finally:
        print(f"Connection closed by {client_address}")
        clients.pop(username, None)
        clients_last_activity.pop(username, None)
        client_socket.close()
        save_clients_data()

def send_message_to_client(recipient, message):
    if recipient in clients and clients[recipient] is not None:
        try:
            clients[recipient].send(message.encode('utf-8'))
        except Exception as e:
            print(f"Error sending message to {recipient}: {e}")
    else:
        print(f"User {recipient} not found or not connected")

def main():
    load_clients_data()

    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('0.0.0.0', 9999))
    server.listen(5)
    print("Server listening on port 9999")
    
    try:
        while True:
            client_socket, client_address = server.accept()
            client_handler = threading.Thread(target=handle_client, args=(client_socket, client_address))
            client_handler.start()
    except KeyboardInterrupt:
        save_clients_data()
        print("Server shutting down")

if __name__ == "__main__":
    main()
