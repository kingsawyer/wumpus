from enum import Enum
import queue
from math import atan2, sin, cos
import random
from threading import Event as ThreadEvent, Thread
import time
import tkinter
from tkinter import *


class ActionResult(Enum):
    MOVE_SUCCESSFUL = 0,
    MET_WUMPUS = 1,
    FELL_IN_PIT = 2,
    WUMPUS_KILLED = 3,
    WUMPUS_MISSED = 4,
    KILLED_BY_GROGGY_WUMPUS = 5,
    TOO_CROOKED = 6,
    OUT_OF_ARROWS = 7,
    SHOT_SELF = 8,
    EXHAUSTED = 9,
    NOT_AN_EXIT = 10


_SCREEN_DIM = 800
_ROOM_SIZE = 20  # fraction of screen dim
_INDICATOR_SIZE = 40  # fraction of screen dim


class Room:
    def __init__(self, label, outs):
        self.label = label
        self.ins = []
        self.outs = outs
        self.bats = False
        self.pit = False
        self.near_bats = False
        self.near_pit = False
        self.near_wumpus = False

        # for graphics - location on screen, etc
        self.x = 0
        self.y = 0
        self.oval = None
        self.known = False  # stepped here


class WMap:
    def __init__(self, map_file):
        self.rooms = []
        self.wumpus = None
        with open(map_file, 'r') as file:
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
        for _count in range(1, self.wumpus_smell_distance):
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
        if new_room == self.wumpus:
            return new_room, ActionResult.MET_WUMPUS, False
        room = self.rooms[new_room]
        if room.pit:
            return new_room, ActionResult.FELL_IN_PIT, False
        if room.bats:
            new_room, result, more_bats = self.send_to_room(random.randint(0, 19))
            return new_room, result, True
        return new_room, ActionResult.MOVE_SUCCESSFUL, False

    def perform_shoot(self, room_list):
        """Return result of shot. list starts from hunter"""
        hunter = room_list[0]
        for i in range(len(room_list) - 2):
            if room_list[i] == room_list[i + 2]:
                return ActionResult.TOO_CROOKED
        arrow_location = hunter
        result = ActionResult.WUMPUS_MISSED
        for room in room_list[1:6]:
            passages = self.rooms[arrow_location].outs + self.rooms[arrow_location].ins
            if room in passages:
                arrow_location = room
            else:
                arrow_location = random.choice(passages)
            if arrow_location == self.wumpus:
                return ActionResult.WUMPUS_KILLED
            elif arrow_location == hunter:
                return ActionResult.SHOT_SELF
        if self.move_wumpus(hunter):
            return ActionResult.KILLED_BY_GROGGY_WUMPUS
        return result


class MoveAnimation:
    def __init__(self, room_list, start_time, end_time, rooms, indicator, canvas):
        self.room_list = room_list
        self.start_time = start_time
        self.end_time = end_time
        self.rooms = rooms
        self.indicator = indicator
        self.canvas = canvas
        self._total_time = self.end_time - self.start_time

    @staticmethod
    def _center(x1, y1, x2, y2):
        return (x1 + x2) / 2 - (_SCREEN_DIM / _INDICATOR_SIZE), (y1 + y2) / 2 - (_SCREEN_DIM / _INDICATOR_SIZE)

    # Return true to keep going
    def process(self):
        now = time.time()
        if self.start_time <= now < self.end_time:
            fraction = (now - self.start_time) / self._total_time
            start_num = int((len(self.room_list) - 1) * fraction)
            end_num = start_num + 1
            # print(f'from room list {start_num} to {end_num}')
            start = self._center(*self.canvas.coords(self.rooms[self.room_list[start_num]].oval))
            finish = self._center(*self.canvas.coords(self.rooms[self.room_list[end_num]].oval))
            line_fraction = (fraction - start_num / (len(self.room_list) - 1)) * (len(self.room_list) - 1)
            new_locx = start[0] + (finish[0] - start[0]) * line_fraction
            new_locy = start[1] + (finish[1] - start[1]) * line_fraction
            # print(f"move indicator to {new_locx}, {new_locy}")
            self.canvas.moveto(self.indicator, new_locx, new_locy)
            return True
        self.canvas.moveto(self.indicator, _SCREEN_DIM * 2, _SCREEN_DIM * 2)
        return False


class WumpusHost:
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
        self._screen_dim = _SCREEN_DIM
        self._circle_radius = self._screen_dim / _ROOM_SIZE
        self._root = Tk() if show_graphics else None
        self._canvas = None
        self._move_indicator = None
        self._can_show_result = ThreadEvent()
        self._queue = queue.Queue()

    def after_callback(self):
        if not self._root:
            return
        try:
            _message = self._queue.get(block=False)
            # print(f'got a message {_message}')
            if isinstance(_message, MoveAnimation):
                if _message.process():
                    self._queue.put(_message)  # still running
                else:
                    self._can_show_result.set()
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
            room.oval = self._canvas.create_oval(self._screen_dim * room.x - self._circle_radius,
                                                 self._screen_dim * room.y - self._circle_radius,
                                                 self._screen_dim * room.x + self._circle_radius,
                                                 self._screen_dim * room.y + self._circle_radius,
                                                 fill="green")
            for connect in room.ins:
                dest = self._map.rooms[connect]
                ending = None if connect in room.outs else tkinter.FIRST
                if ending is not None or room.label < dest.label:
                    pt1, pt2 = self._circle_connect((self._screen_dim * room.x,
                                                     self._screen_dim * room.y),
                                                    (self._screen_dim * dest.x,
                                                     self._screen_dim * dest.y), self._circle_radius)
                    self._canvas.create_line(*pt1, *pt2, arrow=ending)
        self._move_indicator = self._canvas.create_oval(self._screen_dim * 2 - self._screen_dim / _INDICATOR_SIZE,
                                                        self._screen_dim * 2 - self._screen_dim / _INDICATOR_SIZE,
                                                        self._screen_dim * 2 + self._screen_dim / _INDICATOR_SIZE,
                                                        self._screen_dim * 2 + self._screen_dim / _INDICATOR_SIZE,
                                                        fill='blue')
        self._shot_indicator = self._canvas.create_oval(self._screen_dim * 2 - self._screen_dim / _INDICATOR_SIZE,
                                                        self._screen_dim * 2 - self._screen_dim / _INDICATOR_SIZE,
                                                        self._screen_dim * 2 + self._screen_dim / _INDICATOR_SIZE,
                                                        self._screen_dim * 2 + self._screen_dim / _INDICATOR_SIZE,
                                                        fill='yellow')

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

            self._canvas.itemconfig(room.oval, fill=circle_color)

        self._root.update()
        self._canvas.pack()

    def play(self, status_callback):
        self._playing = True
        self._hunter = self._map.init(self._seed)
        if self._show_graphics:
            self.setup_canvas()
            player_thread = Thread(target=self.player_loop, name='player', args=[status_callback])
            player_thread.start()
            self._root.mainloop()
            self._root = None
            if self._playing:
                print('quitting early via UI')
            self._playing = False
        else:
            self.player_loop(status_callback)
        return self._score

    def player_loop(self, status_callback):
        while self._playing:
            room = self._map.rooms[self._hunter]
            status_callback(room.near_pit, room.near_bats, room.near_wumpus, self._hunter, list(room.outs), list(room.ins))
            time.sleep(self._delay)

    def _animate_move(self, start, middle, final):
        room_list = [start, final] if middle is None else [start, middle, final]
        self._queue.put(
            MoveAnimation(room_list, time.time(), time.time() + self._delay / 3,
                          self._map.rooms, self._move_indicator, self._canvas)
        )

    def _animate_shoot(self, shoot_list):
        self._queue.put(
            MoveAnimation(shoot_list, time.time(), time.time() + (len(shoot_list) - 1) * self._delay / 3,
                          self._map.rooms, self._shot_indicator, self._canvas)
        )

    def move(self, new_room):
        if not self._playing:
            raise Exception("game over. Shall we move on?")

        bats_involved = False
        result = ActionResult.NOT_AN_EXIT
        start_location = self._hunter
        if new_room in self._map.rooms[self._hunter].outs:
            final_landing, result, bats_involved = self._map.send_to_room(new_room)
            if self._show_graphics:
                self._can_show_result.clear()
                self._animate_move(start_location, new_room, final_landing)
                self._can_show_result.wait()
                self._map.rooms[new_room].known = True
                self._map.rooms[final_landing].known = True
            self._hunter = final_landing
            self._playing = result not in [ActionResult.MET_WUMPUS, ActionResult.FELL_IN_PIT]
            if self._playing:
                self._moves += 1
                if self._moves >= 100:
                    self._playing = False
                    result = ActionResult.EXHAUSTED
            if self._show_graphics:
                self._queue.put(result)
        return result, bats_involved

    def shoot(self, room_list):
        if not self._playing:
            raise Exception("Shoot, the game is over.")
        shoot_list = [self._hunter] + room_list
        if self._show_graphics:
            self._can_show_result.clear()
            self._animate_shoot(shoot_list)
            self._can_show_result.wait()

        result = self._map.perform_shoot(shoot_list)
        self._playing = result not in [ActionResult.WUMPUS_KILLED, ActionResult.KILLED_BY_GROGGY_WUMPUS, ActionResult.SHOT_SELF]
        if result == ActionResult.WUMPUS_KILLED:
            self._score = 100 - self._moves
        elif result != ActionResult.TOO_CROOKED and self._playing:
            self._arrows -= 1
            if self._arrows == 0:
                self._playing = False
                result = ActionResult.OUT_OF_ARROWS
        if self._show_graphics:
            self._queue.put(result)
        return result
