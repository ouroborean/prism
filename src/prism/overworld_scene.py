from pathlib import Path
from typing import Union
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


BLUE = sdl2.SDL_Color(0, 0, 255)
RED = sdl2.SDL_Color(255, 0, 0)
GREEN = sdl2.SDL_Color(50, 190, 50)
PURPLE = sdl2.SDL_Color(255, 60, 255)
AQUA = sdl2.SDL_Color(30, 190, 210)
BLACK = sdl2.SDL_Color(0, 0, 0)
WHITE = sdl2.SDL_Color(255, 255, 255)


class OverworldScene(engine.Scene):

    player_sprite: sdl2.ext.SoftwareSprite
    scene_manager: "SceneManager"
    player_x: int
    player_y: int
    current_map: prism.areamap.AreaMap

    def __init__(self, scene_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_manager = scene_manager
        self.player_sprite = self.sprite_factory.from_color(WHITE, (40, 40))
        self.background_sprite = self.sprite_factory.from_color(
            BLACK, (800, 700))
        self.player_x = 1
        self.player_y = 1
        self.current_map = prism.areamap.test_map
        self.region.add_sprite(self.player_sprite, 40, 40)

    def full_render(self):
        self.region.clear()
        self.region.add_sprite(self.background_sprite, 0, 0)
        self.render_map()
        self.render_player()

    def render_map(self):
        for i in range(self.current_map.height):
            for j in range(self.current_map.width):
                self.region.add_sprite(
                    self.sprite_factory.from_surface(
                        self.get_scaled_surface(self.current_map[(i,
                                                                  j)].image)),
                    j * 40, i * 40)

    def render_player(self):
        self.region.add_sprite(self.player_sprite, self.player_x * 40,
                               self.player_y * 40)

    def pressed_left(self):
        self.player_x -= 1
        direction = (-1, 0)
        self.full_render()
    
    def pressed_right(self):
        self.player_x += 1
        direction = (1, 0)
        self.full_render()

    def pressed_up(self):
        self.player_y -= 1
        direction = (0, -1)
        self.full_render()
    
    def pressed_down(self):
        self.player_y += 1
        direction = (0, 1)
        self.full_render()

def make_overworld_scene(scene_manager) -> OverworldScene:
    scene = OverworldScene(scene_manager, sdl2.ext.SOFTWARE)
    scene.key_events[sdl2.SDLK_LEFT] = scene.pressed_left
    scene.key_events[sdl2.SDLK_RIGHT] = scene.pressed_right
    scene.key_events[sdl2.SDLK_UP] = scene.pressed_up
    scene.key_events[sdl2.SDLK_DOWN] = scene.pressed_down
    scene.full_render()
    return scene