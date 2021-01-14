import sys
import socket
import threading
import time

if(len(sys.argv) < 2):
    print("Invalid syntax! Try: 'python server.py [port]'")
    sys.exit()

port = int(sys.argv[1])
clients = {}
log = open("server.log", "w")

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
            broadcast((command + " " + clients[sock] + " " + args).encode())
            log.write(command + " " + clients[sock] + " " + args + "\n")
        elif(command == "JOIN"):
            clients[sock] = args
            print("Accepted username " + args +  " for: ", sock.getpeername())
            broadcast(data)
            log.write(command + " " + args + "\n")
    
    print("Lost connection to: ", sock.getpeername())
    sock.close()

    if sock in clients:
        name = clients[sock]
        del clients[sock]
        msg = "LEAVE " + name
        broadcast(msg.encode())
        log.write(msg)

if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        server_socket.bind(('', port))
    except OSError as e:
        if e.errno == 48:
            print("Port " + str(port) + " already in use.")
            sys.exit()
        else:
            raise
    server_socket.listen(5)
    
    print("Starting server on port: " + str(port))
    try:
        while True:
            # accept connections from outside
            sock, address = server_socket.accept()
            print("Connected to: ", sock.getpeername())
            threading.Thread(target=receive, args=(sock,), daemon=True).start()
    except (KeyboardInterrupt, SystemExit):
        print("")
    finally:
        server_socket.close()
        log.close()

