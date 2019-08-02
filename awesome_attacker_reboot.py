# description here
import numpy as np
TEAM_NAME = 'Awesome Attacker Reboot'

from pelita.utils import Graph
from utils import shortest_path

def thats_stupid(homezone, next_pos, enemy_pos):
    """
    Test if the next move would be a stupid one:
    1. Jump on an enemy (very stupid)
    2. Jump next to an enemy to get eaten (still stupid)
    Both of course only true if in enemies territory.
    """
    if (next_pos in enemy_pos) and (next_pos not in homezone):
        return True
    elif ((next_pos[0], next_pos[1] + 1) in enemy_pos) and (next_pos not in homezone):
        return True
    elif ((next_pos[0] + 1, next_pos[1]) in enemy_pos) and (next_pos not in homezone):
        return True
    elif ((next_pos[0], next_pos[1] - 1) in enemy_pos) and (next_pos not in homezone):
        return True
    elif ((next_pos[0] - 1, next_pos[1]) in enemy_pos) and (next_pos not in homezone):
        return True
    else:
        return False

def move(bot, state, randomness = 1e0):
    enemy = bot.enemy
    # we need to create a dictionary to keep information (state) along rounds
    # the state object will be passed untouched at every new round
    if state is None:
        # initialize the state dictionary
        state = {}
        # each bot needs its own state dictionary to keep track of the
        # food targets
        state[0] = (None, None)
        state[1] = (None, None)
        # initialize a graph representation of the maze
        # this can be shared among our bots
        state['graph'] = Graph(bot.position, bot.walls)

    target, path = state[bot.turn]
    target_other = state[1-bot.turn]
    bot_enemy_food = enemy[0].food
    # choose a target food pellet if we still don't have one or
    # if the old target has been already eaten
    if (target is None) or (target not in enemy[0].food):
        # position of the target food pellet
        # old: select the target pellet randomly.
        # target = bot.random.choice(enemy[0].food)

        # select the food pellet that is closest.
        food_dist = np.zeros(len(bot_enemy_food), dtype=np.float32)
        for i, food in enumerate(bot_enemy_food):
            # shortest path to the target
            food_path = state['graph'].a_star(bot.position, food)
            food_dist[i] = len(food_path)
            # if the food is the other bot's target, add extra distance to the food target
            if food == target_other:
                    food_dist[i] *= 2
        food_prob = np.exp(-food_dist/randomness)
        food_prob /= food_prob.sum()
        target_ind = bot.random.choices(range(len(bot_enemy_food)), weights=food_prob)[0]
        target = state[bot.turn] = bot_enemy_food[target_ind]

        # shortest path from here to the target
        path = shortest_path(bot.position, target, state['graph'])
        state[bot.turn] = (target, path)


    # get the next position along the shortest path to reach our target
    next_pos = path.pop()
    # if we are not in our homezone we should check if it is safe to proceed
    if next_pos not in bot.homezone:
        # get a list of safe positions
        safe_positions = []
        for pos in bot.legal_positions:
            if pos not in (enemy[0].position, enemy[1].position):
                safe_positions.append(pos)

        # we are about to step on top of an enemy
        if next_pos not in safe_positions:
            # 1. Let's forget about this target and this path
            #    We will choose a new target in the next round
            state[bot.turn] = (None, None)
            # Choose one safe position at random (this always includes the
            # current position
            next_pos = bot.random.choice(safe_positions)

    # now, let's check if we are getting too near to our enemy
    # where are the enemy ghosts?

    enemy_pos = [bot.enemy[0].position, bot.enemy[1].position]
    if thats_stupid(bot.homezone, next_pos, enemy_pos):
        # we are in the enemy zone: they can eat us!
        # 1. let's forget about this target (the enemy is sitting on it for
        #    now). We will choose a new target in the next round
        state[bot.turn] = (None, None)
        # 2. let us step back
        # bot.track[-1] is always the current position, so to backtrack
        # we select bot.track[-2]
        if thats_stupid(bot.homezone, bot.track[-2], enemy_pos):
            # look for not stupid moves
            legal_moves = []
            for i in bot.legal_positions:
                if not thats_stupid(bot.homezone, i, enemy_pos):
                    legal_moves.append(i)
            if len(legal_moves) == 0:
                next_pos = bot.position
            else:
                # Randomly select one of the available options
                #bot.say(bot.random.choice(DESPERATE_MESSAGES))
                #next_pos = bot.get_position(bot.random.choice(legal_moves))
                next_pos = bot.random.choice(legal_moves)

        else:
            next_pos = bot.track[-2]

    return next_pos, state
