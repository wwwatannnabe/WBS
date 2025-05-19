import click


def get_full_cmd_str(command, commands, result):
    found = False
    for cmd_name, cmd in commands.items():
        if cmd == command:
            result.append(cmd_name)
            return True, result
        elif isinstance(cmd, click.Group):
            result.append(cmd_name)
            found, _ = get_full_cmd_str(command, cmd.commands, result)
            if not found:
                result.remove(cmd_name)
    return found, result
