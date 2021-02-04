import sys
import socket
import threading
import threading
import curses
import time
from curses.textpad import Textbox, rectangle

def split_command(data):
    split = data.split(" ", 1)
    command = split[0]
    args = None
    if len(split) > 1:
        args = split[1]
    return command, args

lines = []
HELP = [
    ">> Help menu: ",
    "  * /help - Display this menu.",
    "  * /leave - Exit the application and chat channel.",
    "  * /list - List all users currently in the chat channel.",
    "  * /whisper [user] [message] - Privately send a given user a message.",
    "  * /username [new name] - Change your username.",
    "  ",
    "   NOTE: There is a bug on OS X Big Sur with curses that breaks backspacing in the text input, try ctrl+H!"
    ""
]

if(len(sys.argv) < 4):
    print("Invalid syntax! Try: 'python client.py [username] [hostname] [port]'")
    sys.exit()

username = sys.argv[1].replace(" ", "")
hostname = sys.argv[2]
port = int(sys.argv[3])

def main(stdscr):
    y_max, x_max = stdscr.getmaxyx()
    stdscr.leaveok(True)

    def help_menu(args=None):
        lines.extend(HELP)
        redraw()

    def request_list(args):
        sock.send("LIST".encode())
    
    def leave(args):
        raise BrokenPipeError

    def send_whisper(args):
        to, msg = split_command(args)
        if msg is None:
            lines.append(">> Invalid syntax, try: '/whisper [user] [message]'")
        else:
            sock.send(("WHISPER " + args).encode())
    
    def change_username(args):
        sock.send(("USERNAME " + args.replace(" ", "")).encode())

    commands = {
        "help": help_menu,
        "leave": leave,
        "list": request_list,
        "whisper": send_whisper,
        "username": change_username
    }

    def chat(args):
        split2 = args.split(" ", 1)
        lines.append(split2[0].strip() + " > " + split2[1].strip())

    def join(args):
        lines.append(">> " + args + " has joined the channel!")
    
    def leave(args):
        lines.append(">> " + args + " has left the channel!")
    
    def list_users(args):
        users = map(lambda x: "  * " + x, args.split(" "))
        lines.append(">> Connected users:")
        lines.extend(users)

    def whisper(args):
        fr, msg = split_command(args)
        
        if msg is None:
            return
        
        lines.append(fr + " -> you: " + msg)
    
    def whisperto(args):
        to, msg = split_command(args)

        if msg is None:
            return

        lines.append("you -> " + to + ": " + msg)
    
    def error(args):
        lines.append(">> [ERROR] " + args)
    
    def usernameto(args):
        f, t = split_command(args)
        lines.append(">> '" + f + "' has changed their username to '" + t + "'")

    protocol = {
        "CHAT": chat,
        "JOIN": join,
        "LEAVE": leave,
        "LIST": list_users,
        "WHISPER": whisper,
        "WHISPERTO": whisperto,
        "USERNAMETO": usernameto,
        "ERROR": error
    }

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
                if data == '':
                    raise ConnectionAbortedError
                # Necessary, otherwise curses will spurt a bunch of garbage onto the main screen
                time.sleep(0.01)
            except ConnectionAbortedError:
                break

            command, args = split_command(data)

            if command in protocol:
                protocol[command](args)

            redraw()
        
        lines.append(">> Connection to the server has been lost...")
        redraw()

    threading.Thread(target=receive, daemon=True).start()
    help_menu()
    while True:
        redraw()
        message = Textbox(curses.newwin(1, x_max-2, y_max-1, 1)).edit()
        
        if message == "":
            continue

        if message[0] != "/":
            sock.send(("CHAT " + message).encode())
        else:
            command, args = split_command(message[1:])
            if command in commands:
                commands[command](args)
            else:
                lines.append(">> Unrecognized command, use /help for a list of valid commands!")

        

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