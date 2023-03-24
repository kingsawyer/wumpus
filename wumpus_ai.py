import random
from wumpushost import ActionResult, WumpusHost


class Player:
    def __init__(self, a_seed, map_file):
        self.host = WumpusHost(a_seed, map_file, show_graphics=False, delay=3)

    def play(self):
        return self.host.play(self.status_callback)

    def status_callback(self, near_pit, near_bats, near_wumpus, room, exits, entrances):
        """Gives the current status. Whether you are near a pit, bats, or wumpus. You can
        move to any of the exits. You could have come in through any of the entrances. Yes,
        Some maps, like waterslide, have steep, one-way passages. You can shoot an arrow through
        either entrances or exits. There will always be 20 rooms, each 3 exits.

        DO NOT CHANGE THE PARAMETER LIST. This is called from the game host.
        """
        if near_pit:
            print('I feel a draft')
        if near_bats:
            print('I hear bats!')
        if near_wumpus:
            print('I smell a wumpus!')
        print('You are in (0-based) room {}. Tunnels lead to {}.'.format(
            room,
            [x for x in exits]
        ))
        visible = [x for x in entrances if x not in exits]
        if visible:
            print("You can also see (but cannot get to) {}".format(visible))

        # HERE IS THE AMAZING RANDOM STRATEGY!
        if near_wumpus:
            room_list = [random.choice(exits + entrances)]  # note this strategy always use a list of length 1
            self.perform_shoot(room_list)
        else:
            self.perform_move(exits)

    def perform_move(self, exits):
        """Perform a move action. Feel free to change the parameters passed to this function."""
        new_room = random.choice(exits)
        print('moving to {}'.format(new_room))
        result, bats_picked_up = self.host.move(new_room)
        if bats_picked_up:
            print('ZAP -- Super Bat snatch! Elsewhereville for you!')
        if result == ActionResult.MET_WUMPUS:
            print('TSK TSK TSK - Wumpus got you!')
        elif result == ActionResult.FELL_IN_PIT:
            print('YYYIIIIEEEE . . . Fell in a pit.')
        elif result == ActionResult.EXHAUSTED:
            print('OOF! You collapse from exhaustion.')
        elif result == ActionResult.NOT_AN_EXIT:
            print("BONK! That's not a possible move.")

    def perform_shoot(self, room_list):
        """Perform a shoot action. Feel free to change the parameters passed to this function"""
        print('shooting along path {}'.format(room_list))
        result = self.host.shoot(room_list)
        if result == ActionResult.TOO_CROOKED:
            print("Arrows aren't that crooked - try another room")
        elif result == ActionResult.WUMPUS_MISSED:
            print("SWISH! The wumpus didn't like that. He may have moved to a quieter room")
        elif result == ActionResult.WUMPUS_KILLED:
            print("AHA! You got the wumpus!")
        elif result == ActionResult.KILLED_BY_GROGGY_WUMPUS:
            print("CLANG! Missed and a groggy wumpus just ate you!")
        elif result == ActionResult.OUT_OF_ARROWS:
            print("WHIZZ! Oh no! Out of arrows. At night the ice weasels come for you...")
        elif result == ActionResult.SHOT_SELF:
            print("LOOK OUT! Thunk! You shot yourself.")


if __name__ == '__main__':
    total = 0
    for seed in range(0, 100):
        player = Player(seed, 'standard.txt')
        print('\nhunting the wumpus! - seed {}'.format(seed))
        score = player.play()
        print("Got a score of {}".format(score))
        total += score
    print('Total Score: {}'.format(total))
