from pathlib import Path
from typing import Tuple
import queue
import sdl2
import sdl2.ext
import sdl2.surface
import sdl2.sdlttf
import importlib.resources
import typing

from prism import engine
import prism.areamap
if typing.TYPE_CHECKING:
    from prism.scene_manager import SceneManager


def get_path(file_name: str) -> Path:
    with importlib.resources.path('prism.resources', file_name) as path:
        return path


TILE_SIZE = 40
BASE_MOVEMENT_SPEED = 5

BLUE = sdl2.SDL_Color(0, 0, 255)
RED = sdl2.SDL_Color(255, 0, 0)
GREEN = sdl2.SDL_Color(50, 190, 50)
PURPLE = sdl2.SDL_Color(255, 60, 255)
AQUA = sdl2.SDL_Color(30, 190, 210)
BLACK = sdl2.SDL_Color(0, 0, 0)
WHITE = sdl2.SDL_Color(255, 255, 255)


def moving_sideways(direction: Tuple[int, int]) -> bool:
    return direction[0] != 0


def moving_vertically(direction: Tuple[int, int]) -> bool:
    return direction[1] != 0


def moving_left(direction: Tuple[int, int]) -> bool:
    return direction[0] == -1


def moving_right(direction: Tuple[int, int]) -> bool:
    return direction[0] == 1


def moving_up(direction: Tuple[int, int]) -> bool:
    return direction[1] == -1


def moving_down(direction: Tuple[int, int]) -> bool:
    return direction[1] == 1


class DirectionQueue(queue.LifoQueue):
    def __init__(self, _maxsize=0):
        self.queue: list = []
        self.set = set()

    def put(self, item):
        if not item in self.set:
            self.set.add(item)
            self.queue.append(item)

    def waiting(self):
        return len(self.queue) and len(self.set)

    def get(self):
        item = self.queue.pop()
        self.set.remove(item)
        return item

    def peek(self):
        if len(self.queue):
            item = self.queue.pop()
            self.queue.append(item)
            return item

    def __contains__(self, item):
        return item in self.set

    def remove(self, item):
        if item in self.set:
            self.set.remove(item)
            items_to_remain = []
            while True:
                queue_item = self.queue.pop()
                if item[0] == queue_item[0] and item[1] == queue_item[1]:
                    break
                else:
                    items_to_remain.append(queue_item)
            items_to_remain.reverse()
            for q_item in items_to_remain:
                self.queue.append(q_item)


class OverworldScene(engine.Scene):

    player_sprite: sdl2.ext.SoftwareSprite
    scene_manager: "SceneManager"
    player_x: int
    player_y: int
    current_map: prism.areamap.AreaMap
    player_direction: Tuple[int, int]
    stored_direction: DirectionQueue
    player_moving: bool
    player_bonking: bool
    player_movement_remaining: int
    movement_released: bool
    held_movement_keys: int
    left_held: bool
    right_held: bool
    up_held: bool
    down_held: bool
    reset_direction: bool

    def __init__(self, scene_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_manager = scene_manager
        self.player_sprite = self.sprite_factory.from_color(WHITE, (40, 40))
        self.background_sprite = self.sprite_factory.from_color(
            BLACK, (800, 700))
        self.player_x = 1
        self.player_y = 1
        self.movement_held = False
        self.player_bonking = False
        self.player_direction = (0, 0)
        self.stored_direction = DirectionQueue()
        self.player_movement_remaining = 0
        self.player_moving = False
        self.current_map = prism.areamap.test_map
        self.region.add_sprite(self.player_sprite, 240, 240)
        self.held_movement_keys = 0
        self.left_held = False
        self.right_held = False
        self.up_held = False
        self.down_held = False
        self.reset_direction = False

    def full_render(self):
        self.region.clear()
        self.region.add_sprite(self.background_sprite, 0, 0)
        self.render_map()
        self.render_player()

    def check_for_player_movement(self):
        if self.player_moving:
            done = False
            continuing = False
            turning = False
            resetting = False
            for tile in self.current_map:
                if moving_sideways(self.player_direction):
                    if tile.x_movement_remaining > 0:
                        if not self.player_bonking:
                            tile.x_movement_remaining -= BASE_MOVEMENT_SPEED
                    if tile.x_movement_remaining == 0 or self.player_bonking:
                        tile.grid_x = tile.dest_x
                        if self.reset_direction:
                            self.reset_direction = False
                            resetting = True
                        if not self.direction_walkable(
                                self.player_direction) or (
                                    self.stored_direction.waiting()
                                    and not self.direction_walkable(
                                        self.stored_direction.peek())):
                            self.player_bonking = True
                        if self.movement_held and self.player_direction != (
                                0, 0) and (
                                    self.direction_walkable(
                                        self.player_direction)
                                    or self.player_bonking) and not resetting:
                            continuing = True
                            done = False
                        elif self.movement_held and self.stored_direction.waiting(
                        ) and (self.direction_walkable(
                                self.stored_direction.peek())
                               or self.player_bonking):
                            turning = True
                            continuing = True
                            done = False
                        else:
                            done = True
                            continuing = False
                            print("Done left/right")
                        tile.x_movement_remaining = 40
                elif moving_vertically(self.player_direction):
                    if tile.y_movement_remaining > 0:
                        if not self.player_bonking:
                            tile.y_movement_remaining -= BASE_MOVEMENT_SPEED
                    if tile.y_movement_remaining == 0 or self.player_bonking:
                        tile.grid_y = tile.dest_y
                        if self.reset_direction:
                            self.reset_direction = False
                            resetting = True
                        if not self.direction_walkable(
                                self.player_direction) or (
                                    self.stored_direction.waiting()
                                    and not self.direction_walkable(
                                        self.stored_direction.peek())):
                            self.player_bonking = True
                        if self.movement_held and self.player_direction != (
                                0, 0) and (
                                    self.direction_walkable(
                                        self.player_direction)
                                    or self.player_bonking) and not resetting:
                            continuing = True
                            done = False
                        elif self.movement_held and self.stored_direction.waiting(
                        ) and (self.direction_walkable(
                                self.stored_direction.peek())
                               or self.player_bonking):
                            turning = True
                            continuing = True
                            done = False
                        else:
                            done = True
                            continuing = False
                            print("Done up/down")
                        tile.y_movement_remaining = 40
            if done:
                self.player_moving = False
                self.player_bonking = False
            if turning:
                self.player_direction = self.stored_direction.get()
            if continuing:
                if self.direction_walkable(self.player_direction):
                    self.player_bonking = False
                    if moving_sideways(self.player_direction):
                        if moving_right(self.player_direction):
                            for tile in self.current_map:
                                tile.dest_x = tile.dest_x - 1
                            self.player_x += 1
                        elif moving_left(self.player_direction):
                            for tile in self.current_map:
                                tile.dest_x = tile.dest_x + 1
                            self.player_x -= 1
                    elif moving_vertically(self.player_direction):
                        if moving_up(self.player_direction):
                            for tile in self.current_map:
                                tile.dest_y = tile.dest_y + 1
                            self.player_y -= 1
                        elif moving_down(self.player_direction):
                            for tile in self.current_map:
                                tile.dest_y = tile.dest_y - 1
                            self.player_y += 1
            if not self.player_moving:
                self.player_direction = (0, 0)
            self.full_render()

    def render_map(self):
        for i in range(self.current_map.height):
            for j in range(self.current_map.width):
                self.region.add_sprite(
                    self.sprite_factory.from_surface(
                        self.get_scaled_surface(self.current_map[(i,
                                                                  j)].image)),
                    self.current_map[(i, j)].x + self.current_map.start_offset,
                    self.current_map[(i, j)].y + self.current_map.start_offset)

    def render_player(self):
        self.region.add_sprite(self.player_sprite, 240, 240)

    def pressed_left(self):
        new_direction = (-1, 0)
        if not self.player_moving and not self.movement_held:
            self.player_direction = new_direction
            if self.direction_walkable(self.player_direction):
                for tile in self.current_map:
                    tile.dest_x = tile.grid_x + 1
                self.player_moving = True
                self.player_bonking = False
                self.player_x -= 1
                self.full_render()
            else:
                self.player_bonking = True
                self.player_moving = True
                self.full_render()
        if (self.player_moving
                or self.player_bonking) and self.player_direction != (-1, 0):
            self.stored_direction.put((-1, 0))
        self.movement_held = True
        if not self.left_held:
            self.left_held = True
            self.held_movement_keys += 1

    def pressed_right(self):
        if not self.player_moving and not self.movement_held:
            self.player_direction = (1, 0)
            if self.direction_walkable(self.player_direction):
                for tile in self.current_map:
                    tile.dest_x = tile.grid_x - 1
                self.player_moving = True
                self.player_bonking = False
                self.player_x += 1
                self.full_render()
            else:
                self.player_bonking = True
                self.player_moving = True
                self.full_render()
        if (self.player_moving
                or self.player_bonking) and self.player_direction != (1, 0):
            self.stored_direction.put((1, 0))
        self.movement_held = True
        if not self.right_held:
            self.right_held = True
            self.held_movement_keys += 1

    def pressed_up(self):
        if not self.player_moving and not self.movement_held:
            self.player_direction = (0, -1)
            if self.direction_walkable(self.player_direction):
                for tile in self.current_map:
                    tile.dest_y = tile.grid_y + 1
                self.player_moving = True
                self.player_bonking = False
                self.player_y -= 1
                self.full_render()
            else:
                self.player_bonking = True
                self.player_moving = True
                self.full_render()
        if (self.player_moving
                or self.player_bonking) and self.player_direction != (0, -1):
            self.stored_direction.put((0, -1))
        self.movement_held = True
        if not self.up_held:
            self.up_held = True
            self.held_movement_keys += 1

    def pressed_down(self):
        if not self.player_moving and not self.movement_held:
            self.player_direction = (0, 1)
            if self.direction_walkable(self.player_direction):
                for tile in self.current_map:
                    tile.dest_y = tile.grid_y - 1
                self.player_moving = True
                self.player_bonking = False
                self.player_y += 1
                self.full_render()
            else:
                self.player_bonking = True
                self.player_moving = True
                self.full_render()
        if (self.player_moving
                or self.player_bonking) and self.player_direction != (0, 1):
            new_direction = (0, 1)
            self.stored_direction.put((0, 1))
        self.movement_held = True
        if not self.down_held:
            self.down_held = True
            self.held_movement_keys += 1

    def released_down(self):
        self.down_held = False
        self.held_movement_keys -= 1
        if (0, 1) in self.stored_direction:
            self.stored_direction.remove((0, 1))
        if self.player_direction == (0, 1):
            if self.player_moving or self.player_bonking:
                self.reset_direction = True
            else:
                self.player_direction = (0, 0)
        if self.held_movement_keys == 0:
            self.movement_held = False

    def released_up(self):
        self.up_held = False
        self.held_movement_keys -= 1
        if (0, -1) in self.stored_direction:
            self.stored_direction.remove((0, -1))
        if self.player_direction == (0, -1):
            if self.player_moving or self.player_bonking:
                self.reset_direction = True
            else:
                self.player_direction = (0, 0)
        if self.held_movement_keys == 0:
            self.movement_held = False

    def released_left(self):
        self.left_held = False
        self.held_movement_keys -= 1
        if (-1, 0) in self.stored_direction:
            self.stored_direction.remove((-1, 0))
        if self.player_direction == (-1, 0):
            if self.player_moving or self.player_bonking:
                self.reset_direction = True
            else:
                self.player_direction = (0, 0)
        if self.held_movement_keys == 0:
            self.movement_held = False

    def released_right(self):
        self.right_held = False
        self.held_movement_keys -= 1
        if (1, 0) in self.stored_direction:
            self.stored_direction.remove((1, 0))
        if self.player_direction == (1, 0):
            if self.player_moving or self.player_bonking:
                self.reset_direction = True
            else:
                self.player_direction = (0, 0)
        if self.held_movement_keys == 0:
            self.movement_held = False

    def direction_walkable(self, direction: Tuple[int, int]) -> bool:
        destination_square = ((self.player_x + direction[0]),
                              (self.player_y + direction[1]))
        return self.current_map[destination_square].walkable


def make_overworld_scene(scene_manager) -> OverworldScene:
    scene = OverworldScene(scene_manager, sdl2.ext.SOFTWARE)
    scene.key_press_events[sdl2.SDLK_LEFT] = scene.pressed_left
    scene.key_press_events[sdl2.SDLK_RIGHT] = scene.pressed_right
    scene.key_press_events[sdl2.SDLK_UP] = scene.pressed_up
    scene.key_press_events[sdl2.SDLK_DOWN] = scene.pressed_down
    scene.key_release_events[sdl2.SDLK_LEFT] = scene.released_left
    scene.key_release_events[sdl2.SDLK_RIGHT] = scene.released_right
    scene.key_release_events[sdl2.SDLK_UP] = scene.released_up
    scene.key_release_events[sdl2.SDLK_DOWN] = scene.released_down
    scene.full_render()
    return scene