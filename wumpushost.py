import random

class Room(object):
    def __init__(self, outs):
        self.ins = []
        self.outs = outs
        self.bats = False
        self.pit = False
        self.near_bats = False
        self.near_pit = False
        self.near_wumpus = False

class WMap(object):
    def __init__(self, mapfile):
        self.rooms = []
        with open(mapfile, 'r') as file:
            self.wumpus_smell_distance = int(file.readline())
            assert self.wumpus_smell_distance >= 1
            count = int(file.readline())
            assert count >= 6
            for _count in range(count):
                room_line = [int(x) - 1 for x in file.readline().split()]
                assert _count == room_line[0]
                self.rooms.append(Room(room_line[1:]))
        self._update_ins()

    def _update_ins(self):
        for index, room in enumerate(self.rooms):
            for out in room.outs:
                self.rooms[out].ins.append(index)

    def set_proximity(self):
        wumpus_room = self.rooms[self.wumpus]
        for room in self.rooms:
            for neighbor in room.outs + room.ins:
                if room.bats:
                    self.rooms[neighbor].near_bats = True
                if room.pit:
                    self.rooms[neighbor].near_pit = True
                if room == wumpus_room:
                    self.rooms[neighbor].near_wumpus = True
        # Spread smell to adjoining rooms when smell distance > 1
        for _c in range(1, self.wumpus_smell_distance):
            add_smell = set()
            for room in self.rooms:
                if room.near_wumpus:
                    for neighbor in room.outs + room.ins:
                        add_smell.add(neighbor)
            for room in add_smell:
                self.rooms[room].near_wumpus = True

    def move_wumpus(self, hunter):
        """Return True if game is over"""
        for room in self.rooms:
            room.near_wumpus = False
        self.wumpus = random.choice(self.rooms[self.wumpus].outs + [self.wumpus])
        if self.wumpus == hunter:
            return True
        self.set_proximity()
        return False

    def init(self, seed):
        random.seed(seed)
        [hunter, bat1, bat2, pit1, pit2, self.wumpus] = random.sample(range(20), 6)
        self.rooms[bat1].bats = True
        self.rooms[bat2].bats = True
        self.rooms[pit1].pit = True
        self.rooms[pit2].pit = True
        self.set_proximity()
        return hunter

    def send_to_room(self, new_room):
        """Return new_room, move result and if bats were involved"""
        if new_room == self.wumpus:
            return new_room, WumpusHost.MET_WUMPUS, False
        room = self.rooms[new_room]
        if room.pit:
            return new_room, WumpusHost.FELL_IN_PIT, False
        if room.bats:
            new_room, result, more_bats = self.send_to_room(random.randint(0, 19))
            return new_room, result, True
        return new_room, WumpusHost.MOVE_SUCCESSFUL, False

    def perform_shoot(self, room_list):
        """Return result of shot. list starts from hunter"""
        hunter = room_list[0]
        for i in range(len(room_list) - 2):
            if room_list[i] == room_list[i + 2]:
                return WumpusHost.TOO_CROOKED
        arrow_location = hunter
        result = WumpusHost.WUMPUS_MISSED
        for room in room_list[1:6]:
            passages = self.rooms[arrow_location].outs + self.rooms[arrow_location].ins
            if room in passages:
                arrow_location = room
            else:
                arrow_location = random.choice(passages)
            if arrow_location == self.wumpus:
                return WumpusHost.WUMPUS_KILLED
            elif arrow_location == hunter:
                return WumpusHost.SHOT_SELF
        if self.move_wumpus(hunter):
            return WumpusHost.KILLED_BY_GROGGY_WUMPUS
        return result

class WumpusHost(object):
    MOVE_SUCCESSFUL = 0
    MET_WUMPUS = 1
    FELL_IN_PIT = 2
    WUMPUS_KILLED = 3
    WUMPUS_MISSED = 4
    KILLED_BY_GROGGY_WUMPUS = 5
    TOO_CROOKED = 6
    OUT_OF_ARROWS = 7
    SHOT_SELF = 8
    EXHAUSTED = 9
    NOT_AN_EXIT = 10

    def __init__(self, seed, mapname):
        self._map = WMap(mapname)
        self._seed = seed
        self._arrows = 5
        self._playing = False
        self._moves = 0
        self._score = 0

    def play(self, status_callback):
        self._playing = True
        self._hunter = self._map.init(self._seed)
        while self._playing:
            room = self._map.rooms[self._hunter]
            status_callback(room.near_pit, room.near_bats, room.near_wumpus, self._hunter, list(room.outs), list(room.ins))
        return self._score

    def move(self, new_room):
        if not self._playing:
            raise Exception("game over. Move on")

        if new_room in self._map.rooms[self._hunter].outs:
            self._hunter, result, bats_involved = self._map.send_to_room(new_room)
            self._playing = result not in [self.MET_WUMPUS, self.FELL_IN_PIT]
            if self._playing:
                self._moves += 1
                if self._moves >= 100:
                    self._playing = False
                    result = self.EXHAUSTED
            return result, bats_involved
        return WumpusHost.NOT_AN_EXIT, False

    def shoot(self, room_list):
        if not self._playing:
            raise Exception("Shoot, the game is over.")

        result = self._map.perform_shoot([self._hunter] + room_list)
        self._playing = result not in [self.WUMPUS_KILLED, self.KILLED_BY_GROGGY_WUMPUS, self.SHOT_SELF]
        if result == self.WUMPUS_KILLED:
            self._score = 100 - self._moves
        elif result != self.TOO_CROOKED and self._playing:
            self._arrows -= 1
            if self._arrows == 0:
                self._playing = False
                result = self.OUT_OF_ARROWS
        return result
