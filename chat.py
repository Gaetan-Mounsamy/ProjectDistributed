import socket
import threading
import sys

# Global variables
clients = []

def handle_connection(connection, name):
    while True:
        try:
            message = connection.recv(1024).decode()
            if not message:
                print(f"{name} disconnected.")
                break
            print(f"{name}: {message}")

            # Broadcast the message to all other connected clients (excluding the sender)
            for client in clients:
                if client != connection:
                    try:
                        client.send(f"{name}: {message}".encode())
                    except:
                        print("Error occurred while broadcasting the message.")
        except:
            print(f"Error occurred with {name}.")
            break

    connection.close()
    clients.remove(connection)

def accept_connections(server_socket):
    while True:
        connection, _ = server_socket.accept()
        name = connection.recv(1024).decode()
        clients.append(connection)

        client_thread = threading.Thread(target=handle_connection, args=(connection, name))
        client_thread.start()

def start_chat(port):
    name = input("Enter your name: ")

    # Create a socket with a specific port number
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", port))
    server_socket.listen(5)

    print(f"Waiting for incoming connections on port {port}...")

    connection_thread = threading.Thread(target=accept_connections, args=(server_socket,))
    connection_thread.start()

    while True:
        message = input()
        if message.lower() == "exit":
            break
        # Broadcast the message to all connected clients (including the sender)
        for client in clients:
            try:
                client.send(f"{name}: {message}".encode())
            except:
                print("Error occurred while sending the message.")

    server_socket.close()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python chat.py <port_number>")
        sys.exit(1)

    port = int(sys.argv[1])
    start_chat(port)
