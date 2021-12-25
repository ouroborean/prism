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

from prism.text_formatter import get_lines, get_word_size
from prism import engine
from prism.player import Player


BLUE = sdl2.SDL_Color(0, 0, 255)
RED = sdl2.SDL_Color(255, 0, 0)
GREEN = sdl2.SDL_Color(50, 190, 50)
PURPLE = sdl2.SDL_Color(255, 60, 255)
AQUA = sdl2.SDL_Color(30, 190, 210)
BLACK = sdl2.SDL_Color(0, 0, 0)
WHITE = sdl2.SDL_Color(255, 255, 255)

Y_OFFSET = 32

FONT_FILENAME = "Basic-Regular.ttf"
FONTSIZE = 30


def init_font(size: int):
    with importlib.resources.path('prism.resources',
                                  FONT_FILENAME) as path:
        return sdl2.sdlttf.TTF_OpenFont(str.encode(os.fspath(path)), size)

class DialogueScene(engine.Scene):

    printing_dialogue: bool
    waiting_on_confirm: bool
    message: str
    prompts: list[str]
    outer_box: sdl2.ext.SoftwareSprite
    printed_line: str
    lines_to_print: list[str]
    characters_printed: int
    dialogue_speed: int
    lines_printed: int
    confirm_to_close = bool
    confirm_to_continue = bool
    next_lines = list[str]

    def __init__(self, scene_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_manager = scene_manager
        self.printing_dialogue = False
        self.confirm_to_close = False
        self.confirm_to_continue = False
        self.dialogue_speed = 1
        self.lines_printed = 0
        self.characters_printed = 0
        self.font = init_font(FONTSIZE)
        self.lines_to_print = []
        self.next_lines = []
        self.printed_message = ""
        self.outer_box = self.sprite_factory.from_color(AQUA, (650, 150))
    
    def not_waiting(self):
        return not self.confirm_to_continue and not self.confirm_to_close

    def create_dialogue(self, message: str):
        self.message = message
        self.printing_dialogue = True
        self.lines_to_print = get_lines(message, 580)


    def create_dialogue_with_prompt(self, message: str, prompts: list[str]):
        self.message = message
        self.prompts = prompts
        self.printing_dialogue = True
        self.lines_to_print = get_lines(message, 580)

    def render_prompt(self):
        widest_prompt = 0
        for prompt in self.prompts:
            if get_word_size(prompt) > widest_prompt:
                widest_prompt = get_word_size(prompt)
        
        prompt_height = 30 + (30 * len(self.prompts))
        prompt_width = widest_prompt + 30

        outer_box = self.sprite_factory.from_color(AQUA, size=(prompt_width, prompt_height))
        # inner_box = self.sprite_factory.from_color(WHITE, )
        # # for row, prompt in enumerate(self.prompts):
        # #     text_surface

    def full_render(self):
        self.region.clear()
        self.region.add_sprite(self.outer_box, 75, 540)
        new_inner = self.sprite_factory.from_color(WHITE, (644, 144))
        for row, line in enumerate(self.lines_to_print):
            if row < self.lines_printed:
                text_surface = sdl2.sdlttf.TTF_RenderText_Blended(self.font, str.encode(line), BLACK)
                sdl2.surface.SDL_BlitSurface(text_surface, None, new_inner.surface, sdl2.SDL_Rect(15, 15 + (row * Y_OFFSET), 0, 0))
                sdl2.SDL_FreeSurface(text_surface)
            elif row == self.lines_printed:
                characters_to_print = len(line)
                text_surface = sdl2.sdlttf.TTF_RenderText_Blended(self.font, str.encode(line[:self.characters_printed]), BLACK)
                sdl2.surface.SDL_BlitSurface(text_surface, None, new_inner.surface, sdl2.SDL_Rect(15, 15 + (row * Y_OFFSET), 0, 0))
                sdl2.SDL_FreeSurface(text_surface)
                self.characters_printed += 1
                if self.characters_printed > characters_to_print:
                    self.lines_printed += 1
                    if self.lines_printed >= len(self.lines_to_print):
                        self.confirm_to_close = True
                        self.lines_printed = 0
                        self.characters_printed = 0
                    elif self.lines_printed == 3:
                        next_lines = [line[self.characters_printed:], *[line for line in self.lines_to_print[3:]]]
                        self.next_lines = get_lines("".join(next_lines), 580)
                        self.confirm_to_continue = True
                    self.characters_printed = 0

    
            

        self.region.add_sprite(new_inner, 78, 543)



    def pressed_confirm(self):
        if self.confirm_to_close:
            self.scene_manager.close_scene(self)
            self.lines_printed = 0
            self.characters_printed = 0
            self.confirm_to_close = False
        if self.confirm_to_continue:
            self.confirm_to_continue = False
            self.lines_to_print = self.next_lines
            self.lines_printed = 0
            self.characters_printed = 0

    def pressed_cancel(self):
        self.scene_manager.close_scene(self)

def make_dialogue_scene(scene_manager) -> DialogueScene:
    scene = DialogueScene(scene_manager, sdl2.ext.SOFTWARE)
    scene.key_press_events[sdl2.SDLK_e] = scene.pressed_confirm
    scene.key_press_events[sdl2.SDLK_q] = scene.pressed_cancel
    
    return scene
