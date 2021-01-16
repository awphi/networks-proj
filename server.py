import sys
import socket
import threading
from utils import split_command

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
        
        command, args = split_command(data.decode())

        if command in protocol:
            protocol[command](sock, args)

    
    print("Lost connection to: ", sock.getpeername())
    sock.close()

    if sock in clients:
        name = clients[sock]
        del clients[sock]
        msg = "LEAVE " + name
        broadcast(msg.encode())
        log.write(msg + "\n")

def chat(sock, args):
    # Makes sure the user has a valid username set
    if sock not in clients:
        return
    
    msg = "CHAT " + clients[sock] + " " + args
    broadcast(msg.encode())
    log.write(msg + "\n")

def join(sock, args):
    args = args.replace(" ", "")
    clients[sock] = args
    msg = "JOIN " + args
    broadcast(msg.encode())
    log.write(msg + "\n")

def list_users(sock, args):
    msg = "LIST"
    for i in clients:
        msg += " " + clients[i]
    sock.send(msg.encode())
    log.write(msg + "\n")

def whisper(sock, args):
    to, msg = split_command(args)
    
    if msg is None:
        sock.send(("ERROR Cannot send empty message.").encode())
        return
    
    for i in clients:
        if clients[i] != to:
            continue

        i.send(("WHISPER " + clients[sock] + " " + msg).encode())
        return
    
    sock.send(("ERROR No connected user named: '" + to + "'.").encode())


protocol = {
    "CHAT": chat,
    "JOIN": join,
    "LIST": list_users,
    "WHISPER": whisper
}

if __name__ == "__main__":
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

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

