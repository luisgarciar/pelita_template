# This bot selects a food pellet as a function of its distance from the food pellet,
# with closer food pellets having an exponentially more likely chance of being selected.
# It tries on the way to avoid being eaten by the enemy: if the next move
# to get to the food would put it on a ghost, then it steps back to its
# previous position.
# In addition, the bot avoids moving into a space adjacent to a ghost.
TEAM_NAME = 'Awesome Attacker Bots'

DESPERATE_MESSAGES = [
    'You can lick my lollipop'
]

JOYFUL_MESSAGES = [
    'LECKER!!!',
    'YOLO',
    'Get in my belly',
    'Lets get shitfaced',
    'PAAAARTEEEY',
    'YOLO',
    'Capuccino con doppio',
    'Itsse me, Mario',
    'COMMIT!!',
    'Pizza, Pasta, Pesto',
    'For the empire',
]

from pelita.utils import Graph

from utils import next_step

import numpy as np


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


def move(turn, game, randomness=1e0):
    """
    Attributes
    ----------
        turn: which bot's turn it is
        game: game state information
        randomness: a float. Higher randomness makes the probabilities of target
        pellet more equal.
    returns
    -------
    returns the bot's next move
    """
    bot = game.team[turn]
    # we need to create a dictionary to keep information (state) along rounds
    # the game_state object will be passed untouched at every new round
    try:
        game_state = game.state.attacker_state
    except AttributeError:
        if game.state is None:
            # initialize the state dictionary
            game.state = {}
            # each bot needs its own state dictionary to keep track of the
            # food targets
            game.state[0] = None
            game.state[1] = None
            # initialize a graph representation of the maze
            # this can be shared among our bots
            game.state['graph'] = Graph(bot.position, bot.walls)
        game_state = game.state


    target = game_state[turn]
    target_other = game_state[1-turn]

    bot_enemy_food = bot.enemy[0].food

    # choose a target food pellet if we still don't have one or
    # if the old target has been already eaten
    # AND optimally choose a food pellet as a functin of its distance from the bot
    if (target is None) or (target not in bot_enemy_food):
        bot.say(bot.random.choice(JOYFUL_MESSAGES))
        food_dist = np.zeros(len(bot_enemy_food), dtype=np.float32)
        for i, food in enumerate(bot_enemy_food):
            # shortest path to the target
            food_path = game_state['graph'].a_star(bot.position, food)
            food_dist[i] = len(food_path)
            # if the food is the other bot's target, add extra distance to the food target
            if food == target_other:
                    food_dist[i] *= 2
        food_prob = np.exp(-food_dist/randomness)
        food_prob /= food_prob.sum()
        target_ind = bot.random.choices(range(len(bot_enemy_food)), weights=food_prob)[0]
        target = game_state[turn] = bot_enemy_food[target_ind]

    # get the next position along the shortest path to reach our target
    next_pos = next_step(bot.position, target, game_state['graph'])

    # now, let's check if we are getting too near to our enemy
    # where are the enemy ghosts?

    enemy_pos = [bot.enemy[0].position, bot.enemy[1].position]
    if thats_stupid(bot.homezone, next_pos, enemy_pos):
        # we are in the enemy zone: they can eat us!
        # 1. let's forget about this target (the enemy is sitting on it for
        #    now). We will choose a new target in the next round
        game_state[turn] = None
        # 2. let us step back
        # bot.track[-1] is always the current position, so to backtrack
        # we select bot.track[-2]
        if thats_stupid(bot.homezone, bot.track[-2], enemy_pos):
            # look for not stupid moves
            legal_moves = []
            for i in bot.legal_moves:
                if not thats_stupid(bot.homezone, bot.get_position(i), enemy_pos):
                    legal_moves.append(i)
            if len(legal_moves) == 0:
                next_pos = bot.position
            else:
                # Randomly select one of the available options
                bot.say(bot.random.choice(DESPERATE_MESSAGES))
                next_pos = bot.get_position(bot.random.choice(legal_moves))
        else:
            next_pos = bot.track[-2]

    # return the move needed to get from our position to the next position
    return bot.get_move(next_pos)
