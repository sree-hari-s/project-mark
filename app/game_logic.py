import random


def new_player(name):

    return {
        "name": name,
        "total": 0,
        "points": 0,
        "busted": False,
        "done": False,
        "used_dice": []
    }


def create_state(host_name, rounds):

    return {
        "phase": "lobby",
        "host": host_name,
        "num_rounds": rounds,
        "current_round": 1,
        "captain_index": 0,
        "mark": 0,
        "turn_order": [],
        "turn_index": 0,
        "players": [new_player(host_name)],
        "log": []
    }


def roll_die(player, sides):

    roll = random.randint(1, sides)

    player["total"] += roll
    player["used_dice"].append(sides)

    return roll