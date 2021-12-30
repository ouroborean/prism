from pathlib import Path
from typing import Tuple, Callable
import queue
import sdl2
import sdl2.ext
import sdl2.surface
import sdl2.sdlttf
import importlib.resources
import typing
import os
import enum

from prism import engine
from prism.text_formatter import get_menu_word_size
from prism.stat import Stat

if typing.TYPE_CHECKING:
    from prism.scene_manager import SceneManager
    from prism.areamap import AreaMap
    from prism.player import Player

BLUE = sdl2.SDL_Color(0, 0, 255)
RED = sdl2.SDL_Color(255, 0, 0)
GREEN = sdl2.SDL_Color(50, 190, 50)
PURPLE = sdl2.SDL_Color(255, 60, 255)
AQUA = sdl2.SDL_Color(30, 190, 210)
BLACK = sdl2.SDL_Color(0, 0, 0)
WHITE = sdl2.SDL_Color(255, 255, 255)

FONT_FILENAME = "Basic-Regular.ttf"
FONTSIZE = 40


def init_font(size: int):
    with importlib.resources.path('prism.resources',
                                  FONT_FILENAME) as path:
        return sdl2.sdlttf.TTF_OpenFont(str.encode(os.fspath(path)), size)

@enum.unique
class OptionType(enum.IntEnum):
    POKEMON = 0
    BAG = 1
    TRAINER = 2
    MAP = 3
    SETTINGS = 4
    EXIT = 5

class MenuScene(engine.Scene):

    scene_manager: "SceneManager"
    player: "Player"
    menu_region: engine.Region
    menu_item_region: engine.Region
    selected_option: int
    option_branch: dict[int, Callable]

    def __init__(self, scene_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.selected_option = 0
        self.scene_manager = scene_manager
        self.menu_region = self.region.subregion(15, 15, 200, 320)
        self.font = init_font(FONTSIZE)
        self.option_branch = {0: self.select_pokemon, 1: self.select_bag, 2: self.select_trainer, 3: self.select_map, 4: self.select_settings, 5: self.select_exit}
        
    def set_player(self, player: "Player"):
        self.player = player

    def full_render(self):
        self.menu_region.clear()
        
        outer_box = self.sprite_factory.from_color(AQUA, self.menu_region.size())
        inner_box = self.sprite_factory.from_color(WHITE, (self.menu_region.size()[0] - 8, self.menu_region.size()[1] - 8))

        for i in range(6):
            
            if i == self.selected_option:
                selected_box = self.sprite_factory.from_color(RED, size=(get_menu_word_size(OptionType(i).name) + 8, 52))
                selected_box_inner = self.sprite_factory.from_color(WHITE, size=(get_menu_word_size(OptionType(i).name) + 2, 46))
                sdl2.surface.SDL_BlitSurface(selected_box.surface, None, inner_box.surface, sdl2.SDL_Rect(6, 11 + (i * 48), 0, 0))
                sdl2.surface.SDL_BlitSurface(selected_box_inner.surface, None, inner_box.surface, sdl2.SDL_Rect(9, 14 + (i * 48), 0, 0))
            text_surface = sdl2.sdlttf.TTF_RenderText_Blended(self.font, str.encode(OptionType(i).name), BLACK)
            sdl2.surface.SDL_BlitSurface(text_surface, None, inner_box.surface, sdl2.SDL_Rect(10, 10 + (i * 48), 0, 0))
            sdl2.SDL_FreeSurface(text_surface)
        self.menu_region.add_sprite(outer_box, 0, 0)
        self.menu_region.add_sprite(inner_box, 4, 4) 
    
    def close_menu(self):
        self.selected_option = 0
        self.scene_manager.close_scene(self)
    
    def pressed_up(self):
        self.selected_option -= 1
        if self.selected_option < 0:
            self.selected_option = 5
        self.full_render()

    def pressed_down(self):
        self.selected_option += 1
        if self.selected_option == 6:
            self.selected_option = 0
        self.full_render()
    
    def select_pokemon(self):
        self.scene_manager.open_belt(self.player, False)

    def select_map(self):
        pass

    def select_trainer(self):
        pass

    def select_bag(self):
        print(f"Items in bag:")
        for item in self.player.bag:
            print(f"{item.name}")

    def select_settings(self):
        pass

    def select_exit(self):
        self.close_menu()

    def pressed_confirm(self):
        self.option_branch[self.selected_option]()

def make_menu_scene(scene_manager) -> MenuScene:
    scene = MenuScene(scene_manager, sdl2.ext.SOFTWARE)
    scene.key_press_events[sdl2.SDLK_ESCAPE] = scene.close_menu
    scene.key_press_events[sdl2.SDLK_UP] = scene.pressed_up
    scene.key_press_events[sdl2.SDLK_DOWN] = scene.pressed_down
    scene.key_press_events[sdl2.SDLK_e] = scene.pressed_confirm
    return scene