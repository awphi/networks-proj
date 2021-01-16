def split_command(data):
    split = data.split(" ", 1)
    command = split[0]
    args = None
    if len(split) > 1:
        args = split[1]
    return command, args