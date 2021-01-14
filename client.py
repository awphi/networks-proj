import sys
import socket
import threading
import threading
import curses
import time
from curses.textpad import Textbox, rectangle

lines = []

if(len(sys.argv) < 4):
    print("Invalid syntax! Try: 'python client.py [username] [hostname] [port]'")
    sys.exit()

username = sys.argv[1]
hostname = sys.argv[2]
port = int(sys.argv[3])

def main(stdscr):
    y_max, x_max = stdscr.getmaxyx()
    stdscr.leaveok(True)

    def redraw(): 
        for i, line in enumerate(lines[-y_max+3:]):
            stdscr.addstr(1+i, 1, line)
            stdscr.clrtoeol()
        rectangle(stdscr, 0, 0, y_max-2, x_max-2)
        stdscr.refresh()

    def receive():
        while True:
            try:
                data = sock.recv(1024).decode()
                # Necessary, otherwise curses will spurt a bunch of garbage onto the main screen
                time.sleep(0.01)
            except ConnectionAbortedError:
                break
            split = data.split(" ", 1)

            if len(split) != 2:
                continue

            command = split[0]
            args = split[1]
            if(command == "CHAT"):
                split2 = args.split(" ", 1)
                lines.append(split2[0].strip() + " > " + split2[1].strip())
            elif(command == "JOIN"):
                lines.append(args + " has joined the channel!")
            elif(command == "LEAVE"):
                lines.append(args + " has left the channel!")
            redraw()

    threading.Thread(target=receive, daemon=True).start()
    while True:
        redraw()
        message = Textbox(curses.newwin(1, x_max-2, y_max-1, 1)).edit()
        sock.send(("CHAT " + message).encode())



if __name__ == "__main__":
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        sock.connect((hostname, port))
    except ConnectionRefusedError:
        print("Connection refused! Could not connect to", (hostname, port))
        sys.exit()

    sock.send(("JOIN " + username).encode())

    try:
        curses.wrapper(main)
    except (KeyboardInterrupt, SystemExit):
        print("")
    except (BrokenPipeError):
        print("Lost connection to server.")
    finally:
        sock.close()