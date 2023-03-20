import queue
from math import atan2, sin, cos
import random
import threading
import time
import tkinter
from tkinter import *


class Room(object):
    def __init__(self, label, outs):
        self.label = label
        self.ins = []
        self.outs = outs
        self.bats = False
        self.pit = False
        self.near_bats = False
        self.near_pit = False
        self.near_wumpus = False
        # location on screen
        self.x = 0
        self.y = 0
        self.known = False  # stepped here


class WMap(object):
    def __init__(self, mapfile):
        self.rooms = []
        self.wumpus = None
        with open(mapfile, 'r') as file:
            self.wumpus_smell_distance = int(file.readline())
            assert self.wumpus_smell_distance >= 1
            count = int(file.readline())
            assert count >= 6
            for _count in range(count):
                room_line = [int(x) - 1 for x in file.readline().split()]
                assert _count == room_line[0]
                self.rooms.append(Room(str(_count+1), room_line[1:]))
            for room in self.rooms:
                location_line = (float(x) for x in file.readline().split())
                _, room.x, room.y = location_line
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
        self.rooms[hunter].known = True
        return hunter

    def send_to_room(self, new_room):
        """Return new_room, move result and if bats were involved"""
        self.rooms[new_room].known = True
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

    def __init__(self, seed, map_name, show_graphics, delay=1):
        self._map = WMap(map_name)
        self._seed = seed
        self._arrows = 5
        self._playing = False
        self._moves = 0
        self._score = 0
        self._hunter = None
        self._show_graphics = show_graphics
        self._delay = delay if show_graphics else 0
        self._screen_dim = 800
        self._circle_radius = self._screen_dim / 20.0
        self._root = Tk()
        self._canvas = None
        self._queue = queue.Queue()

    def after_callback(self):
        if not self._root:
            return
        try:
            _message = self._queue.get(block=False)
            # print(f'got a message {_message}')
            self._redraw_canvas()
            self._queue.task_done()
        except queue.Empty:
            # let's try again later
            pass
        self._root.after(100, self.after_callback)

    @staticmethod
    def _circle_connect(center1, center2, radius):
        angle = atan2(center2[1] - center1[1], center2[0] - center1[0])
        start = center1[0] + cos(angle) * radius, center1[1] + sin(angle) * radius
        finish = center2[0] - cos(angle) * radius, center2[1] - sin(angle) * radius
        return start, finish

    def setup_canvas(self):
        self._root.title("Hunt the Wumpus!")
        self._root.geometry(f'{self._screen_dim}x{self._screen_dim}')
        self._root.resizable(False, False)
        self._canvas = Canvas(self._root, width=self._screen_dim, height=self._screen_dim)
        self._root.eval('tk::PlaceWindow . center')

        for room_num, room in enumerate(self._map.rooms):
            label = Label(self._canvas, text=str(room.label))
            label.pack()
            self._canvas.pack(fill="both", expand=True)
            self._root.update()
            w = label.winfo_width()
            h = label.winfo_height()
            label.place(x=self._screen_dim * room.x - w / 2,
                        y=self._screen_dim * room.y - h / 2)
            for connect in room.ins:
                dest = self._map.rooms[connect]
                ending = None if connect in room.outs else tkinter.FIRST
                if ending is not None or room.label < dest.label:
                    pt1, pt2 = self._circle_connect((self._screen_dim * room.x,
                                                     self._screen_dim * room.y),
                                                    (self._screen_dim * dest.x,
                                                     self._screen_dim * dest.y), self._circle_radius)
                    self._canvas.create_line(*pt1, *pt2, arrow=ending)

        self._redraw_canvas()
        self._root.after(100, self.after_callback)

    def _redraw_canvas(self):
        for room_num, room in enumerate(self._map.rooms):
            circle_color = 'green'
            if room.known:
                circle_color = 'ivory'
                if self._hunter == room_num:
                    circle_color = 'blue'
                if self._map.wumpus == room_num:  # we might be both hunter and wumpus so check this second
                    circle_color = 'red'
                if room.pit:
                    circle_color = 'black'
                if room.bats:
                    circle_color = 'brown'
            elif self._map.wumpus == room_num and self._score > 0:
                circle_color = 'yellow'  # victory!

            room.oval = self._canvas.create_oval(self._screen_dim * room.x - self._circle_radius,
                                      self._screen_dim * room.y - self._circle_radius,
                                      self._screen_dim * room.x + self._circle_radius,
                                      self._screen_dim * room.y + self._circle_radius,
                                      fill=circle_color)

            self._root.update()
        self._canvas.pack()

    def play(self, status_callback):
        self._playing = True
        self._hunter = self._map.init(self._seed)
        t = threading.Thread(target=self.player_loop, name='player', args=[status_callback])
        t.start()
        if self._show_graphics:
            self.setup_canvas()
            self._root.mainloop()
            self._root = None
            if self._playing:
                print('quitting early via UI')
            self._playing = False
        else:
            t.join()
        return self._score

    def player_loop(self, status_callback):
        while self._playing:
            room = self._map.rooms[self._hunter]
            status_callback(room.near_pit, room.near_bats, room.near_wumpus, self._hunter, list(room.outs), list(room.ins))
            time.sleep(self._delay)

    def move(self, new_room):
        if not self._playing:
            raise Exception("game over. Shall we move on?")

        bats_involved = False
        result = WumpusHost.NOT_AN_EXIT
        if new_room in self._map.rooms[self._hunter].outs:
            self._hunter, result, bats_involved = self._map.send_to_room(new_room)
            self._playing = result not in [self.MET_WUMPUS, self.FELL_IN_PIT]
            if self._playing:
                self._moves += 1
                if self._moves >= 100:
                    self._playing = False
                    result = self.EXHAUSTED
        if self._show_graphics:
            self._queue.put(result)
        return result, bats_involved

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
        if self._show_graphics:
            self._queue.put(result)
        return result
