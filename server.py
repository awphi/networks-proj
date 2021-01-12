import sys
import socket
import threading
import time

if(len(sys.argv) < 2):
    print("Invalid syntax! Try: 'python server.py [port]'")
    sys.exit()

port = int(sys.argv[1])

clients = {}

def broadcast(data):
    for i in clients:
        i.send(data)

def receive(sock):
    while True:
        try:
            data = sock.recv(1024)
            if data == b'':
                raise Exception("No data received")
        except:
            break
        
        split = data.decode().split(" ", 1)
        if(len(split) != 2):
            continue

        command = split[0]
        args = split[1]
        if(command == "CHAT" and sock in clients):
            # Only allows users who've set a username to send messages
            if sock in clients:
                broadcast((command + " " + clients[sock] + " " + args).encode())
        elif(command == "JOIN"):
            clients[sock] = args
            print("Accepted username " + args +  " for: ", sock.getpeername())
            broadcast(data)
    
    print("Lost connection to: ", sock.getpeername())
    sock.close()
    
    if sock in clients:
        name = clients[sock]
        del clients[sock]
        broadcast(("LEAVE " + name).encode())

def accept_new(server_socket):
    while True:
        # accept connections from outside
        sock, address = server_socket.accept()
        print("Connected to: ", sock.getpeername())
        threading.Thread(target=receive, args=(sock, ), daemon=True).start()


server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.bind(('', port))
server_socket.listen(5)

print("Starting server on port: " + str(port))

if __name__ == "__main__":
    threading.Thread(target=accept_new, args=(server_socket,), daemon=True).start()
    while True:
        try:
            time.sleep(1)
        except:
            sys.exit()

