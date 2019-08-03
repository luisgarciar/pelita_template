from awesome_attacker_reboot import move
from pelita.utils import setup_test_game

def test_eat_food():
    # do we eat food when it's available?
    layout="""
    ########
    #    0.#
    #.1  EE#
    ########
    """
    bot = setup_test_game(layout=layout, is_blue=True)
    next_move, _ = move(bot, None)
    assert next_move == (6, 1)

def test_no_kamikaze():
    # do we avoid enemies when they can kill us?
    layout="""
    ########
    #    E.#
    #.1  0E#
    ########
    """
    bot = setup_test_game(layout=layout, is_blue=True)
    next_move, _ = move(bot, None)
    assert next_move == (4, 2) or next_move == (5, 2)

def test_do_not_step_on_enemy():
    # check that we don't step back on an enemy when we are fleeing
    layout="""
    ########
    #    E.#
    #.1 #0E#
    ########
    """
    bot = setup_test_game(layout=layout, is_blue=True)
    next_move, _ = move(bot, None)
    assert next_move == (5, 2)

def test_closest_food():
    # pick the food pellet that is closest (as opposed to randomly picking a pellet)
    layout = """
    ############
    #       EE #
    #     .    #
    #          #
    #     0    #
    #          #
    #1       . #
    ############
    """

    bot = setup_test_game(layout=layout, is_blue=True)
    next_move, _ = move(bot, None)
    assert next_move == (6,3)

    
def test_shortest_path():
    # is the Graph implementation in pelita giving us the shortest path to the
    # food pellet? And are we really following it?

    # straight line is the right choice
    layout1="""
    ########
    #0    .#
    #.1  EE#
    ########
    """
    path1 = [(6,1), (5,1), (4,1), (3,1), (2,1)]
    # there are more alternatives now, but the shortest is unique, so we can
    # test it
    layout2="""
    ########
    #0####.#
    #      #
    #      #
    #.1  EE#
    ########
    """
    path2 = [(6, 1), (6,2), (5,2), (4,2), (3,2), (2,2), (1,2)]
    for l, p in ((layout1, path1), (layout2, path2)):
        bot = setup_test_game(layout=l, is_blue=True)
        # we can ignore this, we just call move to have the bot generate the graph
        # representation of the maze
        next_move, state = move(bot, None)
        graph = state['graph']
        path = graph.a_star((1,1), (6,1))
        # test that the generated path is the shortest one
        assert path == p
        # given this layout, move our bot to the next position in the shortest
        # path and see if we follow it
        path.reverse() # flip the path so we have it in the right order
        for idx, step in enumerate(path[:-1]):
            # create a layout where we are starting from the current step in
            # the path
            bot = setup_test_game(layout=l, is_blue=True, bots=[step])
            next_pos, state = move(bot, state)
            assert next_pos == path[idx+1]

def test_not_stuck():
     # do we get stuck in a loop?
      l="""
      ################
      #         .   #
      #         E    #
      #              #
      #         #    #
      #          .   #
      #E            .#
      ################
      """
#    initial layout="""
     ################
     #1         .   #
     #         E    #
     #        0     #
     #         #    #
     #          .   #
     #E            .#
     ################
#     """
     neighbors = [(9,3),(9,2),(9,4),(10,3),(8,3)]
     init = (9,3)
     state = None
#
      for i in range(4):
          bot = setup_test_game(layout=l, is_blue=True, bots=[init, (1, 1)])
          init, state = move(bot, state)

     assert len(intersection(neighbors,bot.track[-4:])) <= 2

def intersection(lst1, lst2):
    return list(set(lst1) & set(lst2))
