import socket
import threading
import select
import sys

# Global variables
clients = {}
base_port = 12345

def listen_for_broadcast():
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broadcast_socket.bind(("127.0.0.1", 54321))

    while True:
        try:
            data, address = broadcast_socket.recvfrom(1024)
            name = data.decode()
            clients[name] = address[0]
        except:
            pass

def handle_client(name, port):
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    client_socket.bind(("0.0.0.0", port))
    while True:
        try:
            message, _ = client_socket.recvfrom(1024)
            print(message.decode())
        except:
            pass

def get_next_port():
    global base_port
    port = base_port
    base_port += 1
    return port

def start_chat():
    name = input("Enter your name: ")

    broadcast_thread = threading.Thread(target=listen_for_broadcast)
    broadcast_thread.start()

    port = get_next_port()

    listen_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    listen_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    listen_socket.bind(("0.0.0.0", port))

    print(f"Listening for incoming connections on port {port}...")

    inputs = [listen_socket, sys.stdin]

    # Broadcast the name to other instances on the local network
    broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    broadcast_socket.sendto(name.encode(), ("<broadcast>", 54321))

    while True:
        try:
            readable, _, _ = select.select(inputs, [], [])
            for sock in readable:
                if sock == listen_socket:
                    data, address = listen_socket.recvfrom(1024)
                    print(data.decode())
                elif sock == sys.stdin:
                    message = input()
                    if message.lower() == "exit":
                        # Send an exit message to all clients and close the sockets
                        message = f"{name} has left the chat."
                        for client_address in clients.values():
                            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                            client_socket.sendto(message.encode(), (client_address, port))
                            client_socket.close()
                        listen_socket.close()
                        sys.exit()
                    message = f"{name}: {message}"
                    for client_address in clients.values():
                        client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                        client_socket.sendto(message.encode(), (client_address, port))
                        client_socket.close()
        except:
            pass

if __name__ == "__main__":
    start_chat()


#python chat.py