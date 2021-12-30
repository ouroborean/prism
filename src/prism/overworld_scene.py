from pathlib import Path
from typing import Tuple, Callable
import queue
import sdl2
import sdl2.ext
import sdl2.surface
import sdl2.sdlttf
import importlib.resources
import typing

from prism import engine
from prism.player import Player
from prism.areamap import get_image_from_path, map_db
from prism.mapname import MapName
from prism.portal import Portal

if typing.TYPE_CHECKING:
    from prism.scene_manager import SceneManager
    from prism.areamap import AreaMap

def get_path(file_name: str) -> Path:
    with importlib.resources.path('prism.resources', file_name) as path:
        return path


TILE_SIZE = 40
BASE_MOVEMENT_SPEED = 8

BLUE = sdl2.SDL_Color(0, 0, 255)
RED = sdl2.SDL_Color(255, 0, 0)
GREEN = sdl2.SDL_Color(50, 190, 50)
PURPLE = sdl2.SDL_Color(255, 60, 255)
AQUA = sdl2.SDL_Color(30, 190, 210)
BLACK = sdl2.SDL_Color(0, 0, 0)
WHITE = sdl2.SDL_Color(255, 255, 255)

#region moving properties
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
#endregion

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

    player: "Player"
    scene_manager: "SceneManager"
    current_map: "AreaMap"
    stored_direction: DirectionQueue
    movement_released: bool
    held_movement_keys: int
    left_held: bool
    right_held: bool
    up_held: bool
    down_held: bool
    reset_direction: bool
    event_running: bool
    menu_opening: bool
    running_events: list[Callable]

    def __init__(self, scene_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_manager = scene_manager
        self.player = Player(self.sprite_factory.from_surface(self.get_scaled_surface(get_image_from_path("player.png")), free=True))
        self.background_sprite = self.sprite_factory.from_color(
            BLACK, (800, 700))
        self.player.x = 1
        self.player.y = 1
        self.menu_opening = False
        self.movement_held = False
        self.player.bonking = False
        self.player.direction = (0, 0)
        self.stored_direction = DirectionQueue()
        self.player.movement_remaining = 0
        self.player.moving = False
        self.change_map(map_db[MapName.TEST])
        self.held_movement_keys = 0
        self.left_held = False
        self.right_held = False
        self.up_held = False
        self.down_held = False
        self.reset_direction = False
        self.event_running = False
        self.tiles = []
        self.running_events = []
        

    def change_map(self, new_map: "AreaMap"):
        self.current_map = new_map    

    def full_render(self):
        self.region.clear()
        self.region.add_sprite(self.background_sprite, 0, 0)
        self.render_map()
        self.render_actors()
        self.render_player()
        self.render_foreground()



    def check_for_player_movement(self):
        
        if self.player.moving and not self.event_running:
            done = False
            continuing = False
            turning = False
            resetting = False
            for tile in self.current_map:
                if moving_sideways(self.player.direction):
                    if tile.x_movement_remaining > 0:
                        if not self.player.bonking:
                            tile.x_movement_remaining -= BASE_MOVEMENT_SPEED
                    if tile.x_movement_remaining == 0 or self.player.bonking:
                        if tile.player_occupied and self.current_map[(self.player.x, self.player.y)] != tile:
                            tile.player_occupied = False
                        tile.grid_x = tile.dest_x
                        if self.reset_direction:
                            self.reset_direction = False
                            resetting = True
                        if not self.direction_walkable(
                                self.player.direction) or (
                                    self.stored_direction.waiting()
                                    and not self.direction_walkable(
                                        self.stored_direction.peek())):
                            self.player.bonking = True
                        if self.movement_held and self.player.direction != (
                                0, 0) and (
                                    self.direction_walkable(
                                        self.player.direction)
                                    or self.player.bonking) and not resetting:
                            continuing = True
                            done = False
                        elif self.movement_held and self.stored_direction.waiting(
                        ) and (self.direction_walkable(
                                self.stored_direction.peek())
                               or self.player.bonking):
                            turning = True
                            continuing = True
                            done = False
                        else:
                            done = True
                            continuing = False
                        tile.x_movement_remaining = 40
                if moving_vertically(self.player.direction):
                    if tile.y_movement_remaining > 0:
                        if not self.player.bonking:
                            tile.y_movement_remaining -= BASE_MOVEMENT_SPEED
                    if tile.y_movement_remaining == 0 or self.player.bonking:
                        if tile.player_occupied and self.current_map[(self.player.x, self.player.y)] != tile:
                            tile.player_occupied = False
                        tile.grid_y = tile.dest_y
                        if self.reset_direction:
                            self.reset_direction = False
                            resetting = True
                        if not self.direction_walkable(
                                self.player.direction) or (
                                    self.stored_direction.waiting()
                                    and not self.direction_walkable(
                                        self.stored_direction.peek())):
                            self.player.bonking = True
                        if self.movement_held and self.player.direction != (
                                0, 0) and (
                                    self.direction_walkable(
                                        self.player.direction)
                                    or self.player.bonking) and not resetting:
                            continuing = True
                            done = False
                        elif self.movement_held and self.stored_direction.waiting(
                        ) and (self.direction_walkable(
                                self.stored_direction.peek())
                               or self.player.bonking):
                            turning = True
                            continuing = True
                            done = False
                        else:
                            done = True
                            continuing = False
                        tile.y_movement_remaining = 40
            if turning:
                self.player.set_direction(self.stored_direction.get())
            if (done or continuing) and (self.player.x, self.player.y) in self.current_map.events:
                self.player.moving = False
                self.event_running = True
                self.player.bonking = False
                self.current_map.events[(self.player.x, self.player.y)](self.player, self.current_map, self)
            elif done:
                self.player.moving = False
                self.player.bonking = False
            elif continuing:
                
                if self.current_map[(self.player.x, self.player.y)].ramp_direction:
                    if self.player.direction[0] == self.current_map[(self.player.x, self.player.y)].ramp_direction[0]:
                        self.player.set_direction(self.current_map[(self.player.x, self.player.y)].ramp_direction)
                    elif self.player.direction[0] != 0:
                        self.player.set_direction((self.player.direction[0], 0))
                        
                if self.direction_walkable(self.player.direction):
                    self.player.bonking = False
                    if moving_sideways(self.player.direction):
                        if moving_right(self.player.direction):
                            for tile in self.current_map:
                                tile.dest_x = tile.dest_x - 1
                            self.player.x += 1
                        elif moving_left(self.player.direction):
                            for tile in self.current_map:
                                tile.dest_x = tile.dest_x + 1
                            self.player.x -= 1
                    if moving_vertically(self.player.direction):
                        if moving_up(self.player.direction):
                            for tile in self.current_map:
                                tile.dest_y = tile.dest_y + 1
                            self.player.y -= 1
                        elif moving_down(self.player.direction):
                            for tile in self.current_map:
                                tile.dest_y = tile.dest_y - 1
                            self.player.y += 1
                    self.current_map[(self.player.x, self.player.y)].player_occupied = True
            if self.player.direction == (0, 0):
                self.player.moving = False

    def check_for_actor_movement(self):
        for actor in self.current_map.actors:
            done = False
            if actor.movement_script:
                actor.movement_script(self, actor)
            if actor.moving:
                dest_point = (actor.position[0] + actor.direction[0], actor.position[1] + actor.direction[1])
                dest_tile = self.current_map[dest_point]
                if not dest_tile.player_occupied:
                    actor.interactable = False
                    dest_tile.occupied = True
                    if actor.direction[0] != 0:
                        actor.x_movement_remaining -= actor.movement_speed

                        if actor.x_movement_remaining == 0 or actor.bonking:
                            done = True
                            actor.x_movement_remaining = 40
                    if actor.direction[1] != 0:
                        actor.y_movement_remaining -= actor.movement_speed

                        if actor.y_movement_remaining == 0 or actor.bonking:
                            done = True
                            actor.y_movement_remaining = 40
                    if done:
                        self.current_map[actor.position].occupied = False
                        actor.position = (actor.dest_x, actor.dest_y)
                        self.current_map[actor.position].occupied = True
                        self.current_map[actor.position].actor = actor
                        actor.moving = False
                        actor.interactable = True
            

    def event_check(self):
        if (self.player.x, self.player.y) in self.current_map.events:
            self.current_map.events[(self.player.x, self.player.y)](self.player, self.current_map, self)

    def render_map(self):
        for i in range(self.current_map.height):
            for j in range(self.current_map.width):
                self.region.add_sprite(
                    self.sprite_factory.from_surface(
                        self.get_scaled_surface(self.current_map[(i,
                                                                  j)].image), free=True),
                    self.current_map[(i, j)].x + self.current_map.x_offset,
                    self.current_map[(i, j)].y + self.current_map.y_offset)
                if self.current_map[(i, j)].item:
                    self.region.add_sprite(
                    self.sprite_factory.from_surface(self.get_scaled_surface(self.current_map[(i, j)].item.image), free=True),
                    self.current_map[(i, j)].x + self.current_map.x_offset, self.current_map[(i, j)].y + self.current_map.y_offset)
                
    def render_actors(self):
        for actor in self.current_map.actors:
            if actor.dest_x > actor.position[0]:
                sprite_x = self.current_map[(actor.position[0], actor.position[1])].x + self.current_map.x_offset + (40 - actor.x_movement_remaining)
            else:
                sprite_x = self.current_map[(actor.position[0], actor.position[1])].x + self.current_map.x_offset - (40 - actor.x_movement_remaining)
            if actor.dest_y > actor.position[1]:
                sprite_y = self.current_map[(actor.position[0], actor.position[1])].y + self.current_map.y_offset - 5 + (40 - actor.y_movement_remaining)
            else:
                sprite_y = self.current_map[(actor.position[0], actor.position[1])].y + self.current_map.y_offset - 5 - (40 - actor.y_movement_remaining)
            self.region.add_sprite(
                    self.sprite_factory.from_surface(
                        self.get_scaled_surface(actor.image), free=True),
                    sprite_x,
                    sprite_y)

    def render_player(self):
        self.region.add_sprite(self.player.sprite, 240, 240 - 5)

    def render_foreground(self):
        for k, v in self.current_map.foreground_items.items():
            self.region.add_sprite(
                    self.sprite_factory.from_surface(
                        self.get_scaled_surface(v), free=True),
                    self.current_map[k].x + self.current_map.x_offset,
                    self.current_map[k].y + self.current_map.y_offset)

    def begin_movement(self, direction: Tuple[int, int]):
        if not self.player.moving and not self.movement_held and not self.event_running:
            if self.current_map[(self.player.x, self.player.y)].ramp_direction:
                if self.current_map[(self.player.x, self.player.y)].ramp_direction[0] == direction[0]:
                    direction = self.current_map[(self.player.x, self.player.y)].ramp_direction
            self.player.set_direction(direction)
            if self.direction_walkable(self.player.direction):
                for tile in self.current_map:
                    tile.dest_x = tile.grid_x - direction[0]
                    tile.dest_y = tile.grid_y - direction[1]
                self.player.moving = True
                self.player.bonking = False
                self.player.x += direction[0]
                self.player.y += direction[1]
                self.current_map[(self.player.x, self.player.y)].player_occupied = True
                self.full_render()
            else:
                self.player.bonking = True
                self.player.moving = True
                self.full_render()
        if self.player.moving or self.player.bonking:
            self.stored_direction.put(direction)
        self.movement_held = True
        

    def pressed_left(self):
        self.begin_movement((-1, 0))
        if not self.left_held:
            self.left_held = True
            self.held_movement_keys += 1

    def pressed_right(self):
        self.begin_movement((1, 0))
        if not self.right_held:
            self.right_held = True
            self.held_movement_keys += 1

    def pressed_up(self):
        self.begin_movement((0, -1))
        if not self.up_held:
            self.up_held = True
            self.held_movement_keys += 1

    def pressed_down(self):
        self.begin_movement((0, 1))
        if not self.down_held:
            self.down_held = True
            self.held_movement_keys += 1

    def pressed_interact(self):
        target_square = ((self.player.x + self.player.direction[0]),
                              (self.player.y + self.player.direction[1]))
        if self.current_map[target_square].has_item:
            self.current_map[target_square].item.pickup_script(self, self.current_map[target_square].item)
            self.current_map[target_square].item = None
            self.full_render()
        elif self.current_map[target_square].occupied and self.current_map[target_square].actor.interactable:
            self.current_map[target_square].actor.dialogue_script(self)

    def released_down(self):
        self.down_held = False
        self.held_movement_keys -= 1
        if self.held_movement_keys < 0:
            self.held_movement_keys = 0
        if (0, 1) in self.stored_direction:
            self.stored_direction.remove((0, 1))
        if self.player.direction[1] == 1:
            if self.player.moving or self.player.bonking:
                self.reset_direction = True
            else:
                self.player.set_direction((self.player.direction[0], 0))
        if self.held_movement_keys == 0:
            self.movement_held = False

    def released_up(self):
        self.up_held = False
        self.held_movement_keys -= 1
        if self.held_movement_keys < 0:
            self.held_movement_keys = 0
        if (0, -1) in self.stored_direction:
            self.stored_direction.remove((0, -1))
        if self.player.direction[1] == -1:
            if self.player.moving or self.player.bonking:
                self.reset_direction = True
            else:
                self.player.set_direction((self.player.direction[0], 0))
        if self.held_movement_keys == 0:
            self.movement_held = False

    def released_left(self):
        self.left_held = False
        self.held_movement_keys -= 1
        if self.held_movement_keys < 0:
            self.held_movement_keys = 0
        if (-1, 0) in self.stored_direction:
            self.stored_direction.remove((-1, 0))
        if self.player.direction[0] == -1:
            if self.player.moving or self.player.bonking:
                self.reset_direction = True
            else:
                self.player.set_direction((0, self.player.direction[1]))
        if self.held_movement_keys == 0:
            self.movement_held = False

    def released_right(self):
        self.right_held = False
        self.held_movement_keys -= 1
        if self.held_movement_keys < 0:
            self.held_movement_keys = 0
        if (1, 0) in self.stored_direction:
            self.stored_direction.remove((1, 0))
        if self.player.direction[0] == 1:
            if self.player.moving or self.player.bonking:
                self.reset_direction = True
            else:
                self.player.set_direction((0, self.player.direction[1]))
        if self.held_movement_keys == 0:
            self.movement_held = False

    def direction_walkable(self, direction: Tuple[int, int]) -> bool:
        destination_square = ((self.player.x + direction[0]),
                              (self.player.y + direction[1]))
        return self.current_map[destination_square].walkable and not self.current_map[destination_square].has_item and not self.current_map[destination_square].occupied

    def pressed_inventory(self):
        for item in self.player.bag:
            print(item.name)
        
    def reset_keys_held(self):
        self.left_held = False
        self.right_held = False
        self.up_held = False
        self.down_held = False
        self.held_movement_keys = 0
        self.movement_held = False

    def pressed_menu(self):
        if not self.player.moving:    
            self.reset_keys_held()
            self.scene_manager.pull_up_menu(self.player)
        

def make_overworld_scene(scene_manager) -> OverworldScene:
    scene = OverworldScene(scene_manager, sdl2.ext.SOFTWARE)
    scene.key_press_events[sdl2.SDLK_LEFT] = scene.pressed_left
    scene.key_press_events[sdl2.SDLK_RIGHT] = scene.pressed_right
    scene.key_press_events[sdl2.SDLK_UP] = scene.pressed_up
    scene.key_press_events[sdl2.SDLK_DOWN] = scene.pressed_down
    scene.key_press_events[sdl2.SDLK_e] = scene.pressed_interact
    scene.key_press_events[sdl2.SDLK_q] = scene.pressed_inventory
    scene.key_release_events[sdl2.SDLK_LEFT] = scene.released_left
    scene.key_release_events[sdl2.SDLK_RIGHT] = scene.released_right
    scene.key_release_events[sdl2.SDLK_UP] = scene.released_up
    scene.key_release_events[sdl2.SDLK_DOWN] = scene.released_down
    scene.key_press_events[sdl2.SDLK_ESCAPE] = scene.pressed_menu
    scene.full_render()
    return scene