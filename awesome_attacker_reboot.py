# description here
import numpy as np
TEAM_NAME = 'Awesome Attacker Reboot'

from pelita.utils import Graph

from utils import shortest_path


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

    return next_pos, state
