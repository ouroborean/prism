import sdl2
import sdl2.ext
import sdl2.surface
import sdl2.sdlttf
import importlib.resources
import typing
from PIL import Image
import os
from typing import Tuple
from prism import engine, text_formatter
import enum
import random
from prism.stat import Stat

def init_font(size: int):
    with importlib.resources.path('prism.resources',
                                  FONT_FILENAME) as path:
        return sdl2.sdlttf.TTF_OpenFont(str.encode(os.fspath(path)), size)

def get_image_from_path(file_name: str) -> Image:
    with importlib.resources.path('prism.resources', file_name) as path:
        return Image.open(path)

BLUE = sdl2.SDL_Color(70, 70, 255)
RED = sdl2.SDL_Color(255, 0, 0)
GREEN = sdl2.SDL_Color(50, 190, 50)
PURPLE = sdl2.SDL_Color(150, 60, 255)
AQUA = sdl2.SDL_Color(30, 190, 210)
BLACK = sdl2.SDL_Color(0, 0, 0)
WHITE = sdl2.SDL_Color(255, 255, 255)

if typing.TYPE_CHECKING:
    from prism.scene_manager import SceneManager
    from prism.scene_manager import Player

@enum.unique
class BeltState(enum.IntEnum):
    SELECTING_POKEMON = 0
    SELECTING_OPTION = 1

NAMEPLATE_FONT_SIZE = 22
FONT_FILENAME = "Basic-Regular.ttf"

class PokeBeltScene(engine.Scene):

    poke_display_region: engine.Region
    scene_manager: "SceneManager"
    in_battle: bool
    forced: bool
    player: "Player"
    selected_slot: int
    belt_state: BeltState
    nameplate_font: sdl2.sdlttf.TTF_Font
    hp_bar_back: Image.Image
    hp_bar_front: Image.Image

    def __init__(self, scene_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_manager = scene_manager
        self.nameplate_font = init_font(NAMEPLATE_FONT_SIZE)
        self.selected_slot = 0
        forced = False
        in_battle = False
        self.hp_bar_back = get_image_from_path("belt_hp_back.png")
        self.hp_bar_front = get_image_from_path("enemy_health_bar.png")
        self.belt_state = BeltState.SELECTING_POKEMON
        self.poke_display_region = self.region.subregion(0, 55, 380, 600)

    def full_render(self):
        self.region.clear()
        background = self.sprite_factory.from_color(BLACK, (800,700))
        self.region.add_sprite(background, 0, 0)
        self.render_poke_display_region()

    def render_poke_display_region(self):
        placeholder = self.sprite_factory.from_color(AQUA, self.poke_display_region.size())
        self.poke_display_region.add_sprite(placeholder, 0, 0)

        for i in range(6):
            if self.selected_slot == i:
                border = self.sprite_factory.from_color(RED, (356, 98))
                self.poke_display_region.add_sprite(border, 12, 7 + (i * 97))
            pokeslot = self.sprite_factory.from_color(PURPLE, (350, 92))
            self.poke_display_region.add_sprite(pokeslot, 15, 10 + (i * 97))

        for i in range(len(self.player.team)):
            poketile = self.sprite_factory.from_color(BLUE, (350, 92))

            name_text = sdl2.sdlttf.TTF_RenderText_Blended(self.nameplate_font, str.encode(self.player.team[i].name), BLACK)
            sdl2.surface.SDL_BlitSurface(name_text, None, poketile.surface, sdl2.SDL_Rect(75, 3, 0, 0))
            sdl2.SDL_FreeSurface(name_text)

            level_text = sdl2.sdlttf.TTF_RenderText_Blended(self.nameplate_font, str.encode(f"Lv.{self.player.team[i].level}"), BLACK)
            sdl2.surface.SDL_BlitSurface(level_text, None, poketile.surface, sdl2.SDL_Rect(270, 58, 0, 0))
            sdl2.SDL_FreeSurface(level_text)

            belt_hp_bar_back = self.get_scaled_surface(self.hp_bar_back)
            sdl2.surface.SDL_BlitSurface(belt_hp_bar_back, None, poketile.surface, sdl2.SDL_Rect(70, 35, 0, 0))

            belt_hp_bar_front = self.get_scaled_surface(self.hp_bar_front)
            sdl2.surface.SDL_BlitSurface(belt_hp_bar_front, None, poketile.surface, sdl2.SDL_Rect(121, 41, 0, 0))

            hp_text = sdl2.sdlttf.TTF_RenderText_Blended(self.nameplate_font, str.encode(f"{int(self.player.team[i].current_hp)} / {int(self.player.team[i].get_stat(Stat.HP))}"), BLACK)
            sdl2.surface.SDL_BlitSurface(hp_text, None, poketile.surface, sdl2.SDL_Rect(110, 58, 0, 0))
            sdl2.SDL_FreeSurface(hp_text)

            belt_image = self.get_scaled_surface(self.player.team[i].belt_image)
            sdl2.surface.SDL_BlitSurface(belt_image, None, poketile.surface, sdl2.SDL_Rect(0, 15, 0, 0))
            sdl2.SDL_FreeSurface(belt_image)

            self.poke_display_region.add_sprite(poketile, 15, 10 + (i * 97))
            

    def render_belt_options(self):
        pass



    def check_belt(self, player: "Player", in_battle: bool, forced: bool):
        self.in_battle = in_battle
        self.player = player
        self.selected_slot = 0
        self.forced = forced
        self.belt_state = BeltState.SELECTING_POKEMON
        self.full_render()
    


    def pressed_up(self):
        if self.belt_state == BeltState.SELECTING_POKEMON:
            self.selected_slot -= 1
            if self.selected_slot < 0:
                self.selected_slot = len(self.player.team) - 1
        self.full_render()

    def pressed_down(self):
        if self.belt_state == BeltState.SELECTING_POKEMON:
            self.selected_slot += 1
            if self.selected_slot == len(self.player.team):
                self.selected_slot = 0
        self.full_render()

    def pressed_left(self):
        pass

    def pressed_right(self):
        pass

    def pressed_confirm(self):
        if self.belt_state == BeltState.SELECTING_POKEMON:
            if self.in_battle:
                if self.player.team[self.selected_slot] != self.scene_manager.battle.player_pokemon:
                    self.scene_manager.swap_pokemon(self.selected_slot)
                    self.selected_slot = 0
                else:
                    #TODO add failure message
                    pass

            #self.belt_state = BeltState.SELECTING_OPTION
        

    def pressed_cancel(self):
        if self.belt_state == BeltState.SELECTING_POKEMON and not self.forced:
            self.scene_manager.close_scene(self)


def make_pokebelt_scene(scene_manager) -> PokeBeltScene:
    scene = PokeBeltScene(scene_manager, sdl2.ext.SOFTWARE)
    scene.key_press_events[sdl2.SDLK_UP] = scene.pressed_up
    scene.key_press_events[sdl2.SDLK_DOWN] = scene.pressed_down
    scene.key_press_events[sdl2.SDLK_LEFT] = scene.pressed_left
    scene.key_press_events[sdl2.SDLK_RIGHT] = scene.pressed_right
    scene.key_press_events[sdl2.SDLK_e] = scene.pressed_confirm
    scene.key_press_events[sdl2.SDLK_q] = scene.pressed_cancel
    return scene