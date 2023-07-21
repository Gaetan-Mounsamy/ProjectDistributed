import socket
import threading

# Global variables
clients = []

def handle_connection(connection, address, name):
    print(f"{name} connected from {address}")

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

def accept_connections(server_socket, base_port):
    while True:
        connection, address = server_socket.accept()
        name = connection.recv(1024).decode()
        clients.append(connection)

        # Send the assigned port number to the client
        connection.send(str(base_port).encode())

        client_thread = threading.Thread(target=handle_connection, args=(connection, address, name))
        client_thread.start()

def start_chat():
    name = input("Enter your name: ")

    # Create a socket with a random available port
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind(("0.0.0.0", 0))
    server_socket.listen(5)

    # Get the actual port assigned by the system
    _, actual_port = server_socket.getsockname()

    print(f"Waiting for incoming connections on port {actual_port}...")

    connection_thread = threading.Thread(target=accept_connections, args=(server_socket, actual_port))
    connection_thread.start()

    while True:
        message = input()
        if message.lower() == "exit":
            break

    server_socket.close()

if __name__ == "__main__":
    start_chat()

#python chat.py