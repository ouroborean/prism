from pathlib import Path
from typing import Tuple
import os
import threading
import gc
import tkinter as tk
from tkinter import filedialog
import sdl2
import sdl2.ext
import sdl2.surface
import sdl2.sdlttf
import importlib.resources
import typing
from PIL import Image
from io import StringIO

from prism import engine
import prism.areamap
from prism.tile import tile_image_db
if typing.TYPE_CHECKING:
    from prism.scene_manager import SceneManager


def get_path(file_name: str) -> Path:
    with importlib.resources.path('prism.resources', file_name) as path:
        return path

TILE_SIZE = 40
BASE_MOVEMENT_SPEED = 4


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

class OverworldScene(engine.Scene):

    player_sprite: sdl2.ext.SoftwareSprite
    scene_manager: "SceneManager"
    player_x: int
    player_y: int
    current_map: prism.areamap.AreaMap
    player_direction: Tuple[int, int]
    player_moving: bool
    player_movement_remaining: int
    movement_released: bool

    def __init__(self, scene_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_manager = scene_manager
        self.player_sprite = self.sprite_factory.from_color(WHITE, (40, 40))
        self.background_sprite = self.sprite_factory.from_color(
            BLACK, (800, 700))
        self.player_x = 1
        self.player_y = 1
        self.movement_held = False
        self.player_direction = (0, 0)
        self.player_movement_remaining = 0
        self.player_moving = False
        self.current_map = prism.areamap.test_map
        self.region.add_sprite(self.player_sprite, 240, 240)

    def full_render(self):
        self.region.clear()
        self.region.add_sprite(self.background_sprite, 0, 0)
        self.render_map()
        self.render_player()

    def check_for_player_movement(self):
        if (self.player_direction[0] != 0 or self.player_direction[1] != 0) or self.player_moving:
            for tile in self.current_map:
                done = False
                continuing = False
                if moving_sideways(self.player_direction):
                    if tile.x_movement_remaining > 0:
                        tile.x_movement_remaining -= BASE_MOVEMENT_SPEED
                    if tile.x_movement_remaining == 0:
                        tile.grid_x = tile.dest_x
                        if self.movement_held and self.direction_walkable(self.player_direction):
                            continuing = True
                        else:
                            done = True
                        tile.x_movement_remaining = 40
                elif moving_vertically(self.player_direction):
                    if tile.y_movement_remaining > 0:
                        tile.y_movement_remaining -= BASE_MOVEMENT_SPEED
                    if tile.y_movement_remaining == 0:
                        tile.grid_y = tile.dest_y
                        if self.movement_held and self.direction_walkable(self.player_direction):
                            continuing = True
                        else:
                            done = True
                        tile.y_movement_remaining = 40
            if done:
                self.player_moving = False
            if continuing:
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
                    self.current_map[(i, j)].x + self.current_map.start_offset, self.current_map[(i, j)].y + self.current_map.start_offset)

    def render_player(self):
        self.region.add_sprite(self.player_sprite, 240, 240)

    def pressed_left(self):
        if not self.player_moving and not self.movement_held:
            new_direction = (-1, 0)
            if self.direction_walkable(new_direction):
                self.player_direction = (-1, 0)
                for tile in self.current_map:
                    tile.dest_x = tile.grid_x + 1
                self.player_moving = True
                self.movement_held = True
                self.player_x -= 1
                self.full_render()
        
    
    def pressed_right(self):
        if not self.player_moving and not self.movement_held:
            new_direction = (1, 0)
            if self.direction_walkable(new_direction):
                self.player_direction = (1, 0)
                for tile in self.current_map:
                    tile.dest_x = tile.grid_x - 1
                self.player_moving = True
                self.movement_held = True
                self.player_x += 1
                self.full_render()
        

    def pressed_up(self):
        if not self.player_moving and not self.movement_held:
            new_direction = (0, -1)
            if self.direction_walkable(new_direction):
                self.player_direction = (0, -1)
                for tile in self.current_map:
                    tile.dest_y = tile.grid_y + 1
                self.player_moving = True
                self.movement_held = True
                self.player_y -= 1
                self.full_render()
    
    def pressed_down(self):
        if not self.player_moving and not self.movement_held:
            new_direction = (0, 1)
            if self.direction_walkable(new_direction):
                self.player_direction = (0, 1)
                for tile in self.current_map:
                    tile.dest_y = tile.grid_y - 1
                self.player_moving = True
                self.movement_held = True
                self.player_y += 1
                self.full_render()

    def movement_key_released(self):
        self.movement_held = False

    def direction_walkable(self, direction: Tuple[int, int]) -> bool:
        destination_square = ( (self.player_x + direction[0]), (self.player_y + direction[1]) )
        return self.current_map[destination_square].walkable


def make_overworld_scene(scene_manager) -> OverworldScene:
    scene = OverworldScene(scene_manager, sdl2.ext.SOFTWARE)
    scene.key_press_events[sdl2.SDLK_LEFT] = scene.pressed_left
    scene.key_press_events[sdl2.SDLK_RIGHT] = scene.pressed_right
    scene.key_press_events[sdl2.SDLK_UP] = scene.pressed_up
    scene.key_press_events[sdl2.SDLK_DOWN] = scene.pressed_down
    scene.key_release_events[sdl2.SDLK_LEFT] = scene.movement_key_released
    scene.key_release_events[sdl2.SDLK_RIGHT] = scene.movement_key_released
    scene.key_release_events[sdl2.SDLK_UP] = scene.movement_key_released
    scene.key_release_events[sdl2.SDLK_DOWN] = scene.movement_key_released
    scene.full_render()
    return scene