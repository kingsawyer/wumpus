import random

from wumpushost import WumpusHost


class Player(object):
    def __init__(self, a_seed, map_file):
        self.host = WumpusHost(a_seed, map_file, show_graphics=True, delay=0)

    def play(self):
        return self.host.play(self.status_callback)

    def status_callback(self, near_pit, near_bats, near_wumpus, room, exits, entrances):
        if near_pit:
            print('I feel a draft')
        if near_bats:
            print('I hear bats!')
        if near_wumpus:
            print('I smell a wumpus!')
        print('You are in room {}. Tunnels lead to {}.'.format(
            room + 1,
            [x+1 for x in exits]
        ))
        visible = [x + 1 for x in entrances if x not in exits]
        if visible:
            print("You can also see (but cannot get to) {}".format(visible))
        decision = input('Move or Shoot? (m or s) ')
        if decision in ['m', 'M']:
            self.perform_move()
        elif decision in ['s', 'S']:
            self.perform_shoot()
        else:
            print("That's not an option in this game.")

    def perform_move(self):
        """Perform a move action."""
        new_room = int(input('Where to? ')) - 1
        result, bats_picked_up = self.host.move(new_room)
        if bats_picked_up:
            print('ZAP -- Super Bat snatch! Elsewhereville for you!')
        if result == WumpusHost.MET_WUMPUS:
            print('TSK TSK TSK - Wumpus got you!')
        elif result == WumpusHost.FELL_IN_PIT:
            print('YYYIIIIEEEE . . . Fell in a pit.')
        elif result == WumpusHost.EXHAUSTED:
            print('OOF! You collapse from exhaustion.')
        elif result == WumpusHost.NOT_AN_EXIT:
            print("BONK! That's not a possible move.")

    def perform_shoot(self):
        """Perform a shoot action"""
        rooms = input('You can shoot up to five rooms, separate rooms with a comma ')
        room_list = [int(x) -1 for x in rooms.split(',')]
        result = self.host.shoot(room_list)
        if result == WumpusHost.TOO_CROOKED:
            print("Arrows aren't that crooked - try another room")
        elif result == WumpusHost.WUMPUS_MISSED:
            print("SWISH! The wumpus didn't like that. He may have moved to a quieter room")
        elif result == WumpusHost.WUMPUS_KILLED:
            print("AHA! You got the wumpus!")
        elif result == WumpusHost.KILLED_BY_GROGGY_WUMPUS:
            print("CLANG! Missed and a groggy wumpus just ate you!")
        elif result == WumpusHost.OUT_OF_ARROWS:
            print("WHIZZ! Oh no! Out of arrows. At night the ice weasels come for you...")
        elif result == WumpusHost.SHOT_SELF:
            print("LOOK OUT! Thunk! You shot yourself!")


if __name__ == '__main__':
    player = Player(random.randint(0, 1000), 'mobius.txt')
    print("""
        WELCOME TO 'HUNT THE WUMPUS'

        THE WUMPUS LIVES IN A CAVE OF 20 ROOMS: EACH ROOM HAS 3 TUNNELS LEADING TO OTHER
        ROOMS. THE STANDARD MAP IS A DODECAHEDRON (IF YOU DON'T KNOW WHAT A
        DODECAHEDRON IS, ASK SOMEONE)

        ***
        HAZARDS:

        BOTTOMLESS PITS - TWO ROOMS HAVE BOTTOMLESS PITS IN THEM
        IF YOU GO THERE: YOU FALL INTO THE PIT (& LOSE!)

        SUPER BATS  - TWO OTHER ROOMS HAVE SUPER BATS. IF YOU GO THERE, A BAT GRABS YOU
        AND TAKES YOU TO SOME OTHER ROOM AT RANDOM. (WHICH MIGHT BE TROUBLESOME)

        WUMPUS:

        THE WUMPUS IS NOT BOTHERED BY THE HAZARDS (HE HAS SUCKER FEET AND IS TOO BIG FOR
        A BAT TO LIFT). USUALLY HE IS ASLEEP. TWO THINGS WAKE HIM UP: YOUR ENTERING HIS
        ROOM OR YOUR SHOOTING AN ARROW.

            IF THE WUMPUS WAKES, HE EATS YOU IF YOU ARE THERE, OTHERWISE, HE MOVES (P=0.75)
        ONE ROOM OR STAYS STILL (P=0.25). AFTER THAT, IF HE IS WHERE YOU ARE, HE EATS
        YOU UP (& YOU LOSE!)

        YOU:

        EACH TURN YOU MAY MOVE OR SHOOT A CROOKED ARROW
        MOVING: YOU CAN GO ONE ROOM (THRU ONE TUNNEL)
        ARROWS: YOU HAVE 5 ARROWS. YOU LOSE WHEN YOU RUN OUT.

            EACH ARROW CAN GO FROM 1 TO 5 ROOMS: YOU AIM BY TELLING THE COMPUTER THE ROOMS
        YOU WANT THE ARROW TO GO TO. IF THE ARROW CAN'T GO THAT WAY (IE NO TUNNEL) IT
        MOVES AT RANDOM TO THE NEXT ROOM.

            IF THE ARROW HITS THE WUMPUS: YOU WIN.

            IF THE ARROW HITS YOU: YOU LOSE.

            WARNINGS:

        WHEN YOU ARE ONE ROOM AWAY FROM WUMPUS OR HAZARD, THE COMPUTER SAYS:

        WUMPUS - 'I SMELL A WUMPUS'

        BAT - 'I HEAR BATS'

        PIT - 'I FEEL A DRAFT'

    ***
    HUNT THE WUMPUS
    """)
    score = player.play()
    if score:
        print("HEE HEE HEE - The wumpus'll getcha next time!!\nYou got a score of {}".format(score))
    else:
        print("HA HA HA - You lose!")
