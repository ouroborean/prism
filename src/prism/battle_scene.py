import sdl2
import sdl2.ext
import sdl2.surface
import sdl2.sdlttf
import importlib.resources
import typing
from PIL import Image
import os
from prism import engine
from prism.areamap import get_image_from_path, map_db
from prism.poke_db import initialize_pokemon
from prism.stat import Stat

if typing.TYPE_CHECKING:
    from prism.scene_manager import SceneManager
    from prism.pokemon import Pokemon

def get_image_from_path(file_name: str) -> Image:
    with importlib.resources.path('prism.resources', file_name) as path:
        return Image.open(path)

FONT_FILENAME = "Basic-Regular.ttf"
NAME_FONT_SIZE = 32
HEALTH_FONT_SIZE = 24


def init_font(size: int):
    with importlib.resources.path('prism.resources',
                                  FONT_FILENAME) as path:
        return sdl2.sdlttf.TTF_OpenFont(str.encode(os.fspath(path)), size)

poke_db = initialize_pokemon()

BLUE = sdl2.SDL_Color(0, 0, 255)
RED = sdl2.SDL_Color(255, 0, 0)
GREEN = sdl2.SDL_Color(50, 190, 50)
PURPLE = sdl2.SDL_Color(255, 60, 255)
AQUA = sdl2.SDL_Color(30, 190, 210)
BLACK = sdl2.SDL_Color(0, 0, 0)
WHITE = sdl2.SDL_Color(255, 255, 255)

class BattleScene(engine.Scene):

    scene_manager: "SceneManager"
    enemy_pokemon_region: engine.Region
    player_pokemon_region: engine.Region
    player_pokemon_info_region: engine.Region
    enemy_pokemon_info_region: engine.Region
    battle_info_region: engine.Region
    battle_options_region: engine.Region
    player_pokemon: "Pokemon"
    enemy_pokemon: "Pokemon"
    player_nameplate: Image.Image
    enemy_nameplate: Image.Image
    name_font: sdl2.sdlttf.TTF_Font
    hp_font: sdl2.sdlttf.TTF_Font

    def __init__(self, scene_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.scene_manager = scene_manager
        self.enemy_pokemon_region = self.region.subregion(400, 0, 400, 350)
        self.enemy_pokemon_info_region = self.region.subregion(0, 0, 400, 200)
        self.player_pokemon_region = self.region.subregion(0, 200, 400, 300)
        self.player_pokemon_info_region = self.region.subregion(400, 350, 400, 350)
        self.battle_info_region = self.region.subregion(0, 500, 800, 200)
        self.battle_options_region = self.region.subregion(500, 500, 300, 200)
        self.player_nameplate = get_image_from_path("player_nameplate.png")
        self.enemy_nameplate = get_image_from_path("enemy_nameplate.png")
        self.name_font = init_font(NAME_FONT_SIZE)
        self.hp_font = init_font(HEALTH_FONT_SIZE)
        self.player_pokemon = poke_db["mudkip"]
        self.player_pokemon.set_level(6)
        self.enemy_pokemon = poke_db["mismagius"]
        self.enemy_pokemon.set_level(45)
    
    def render_player_regions(self):
        self.render_player_pokemon_region()
        self.render_player_pokemon_info_region()

    def render_player_pokemon_region(self):
        self.player_pokemon_region.clear()
        pokemon_sprite = self.sprite_factory.from_surface(self.get_scaled_surface(self.player_pokemon.back_image, width=300, height=300))
        height_adjust = self.player_pokemon_region.size()[1] - pokemon_sprite.size[1]
        self.player_pokemon_region.add_sprite(pokemon_sprite, 50, height_adjust)


    def render_player_pokemon_info_region(self):
        self.player_pokemon_info_region.clear()
        nameplate = self.sprite_factory.from_surface(self.get_scaled_surface(self.player_nameplate))
        
        name_text = sdl2.sdlttf.TTF_RenderText_Blended(self.name_font, str.encode(self.player_pokemon.name), BLACK)
        sdl2.surface.SDL_BlitSurface(name_text, None, nameplate.surface, sdl2.SDL_Rect(60, 13, 0, 0))
        sdl2.SDL_FreeSurface(name_text)

        level_text = sdl2.sdlttf.TTF_RenderText_Blended(self.name_font, str.encode(f"Lv{self.player_pokemon.level}"), BLACK)
        sdl2.surface.SDL_BlitSurface(level_text, None, nameplate.surface, sdl2.SDL_Rect(295, 13, 0, 0))
        sdl2.SDL_FreeSurface(level_text)

        health_text = sdl2.sdlttf.TTF_RenderText_Blended(self.name_font, str.encode(f"{int(self.player_pokemon.current_hp)}/{int(self.player_pokemon.get_stat(Stat.HP))}"), BLACK)
        sdl2.surface.SDL_BlitSurface(health_text, None, nameplate.surface, sdl2.SDL_Rect(240, 83, 0, 0))
        sdl2.SDL_FreeSurface(health_text)

        self.player_pokemon_info_region.add_sprite(nameplate, -30, -5)

    def render_enemy_regions(self):
        self.render_enemy_pokemon_region()
        self.render_enemy_pokemon_info_region()

    def render_enemy_pokemon_region(self):
        self.enemy_pokemon_region.clear()
        pokemon_sprite = self.sprite_factory.from_surface(self.get_scaled_surface(self.enemy_pokemon.front_image, width = 300, height = 300))
        self.enemy_pokemon_region.add_sprite(pokemon_sprite, 15, 0)

    def render_enemy_pokemon_info_region(self):
        self.enemy_pokemon_info_region.clear()
        nameplate = self.sprite_factory.from_surface(self.get_scaled_surface(self.enemy_nameplate))

        name_text = sdl2.sdlttf.TTF_RenderText_Blended(self.name_font, str.encode(self.enemy_pokemon.name), BLACK)
        sdl2.surface.SDL_BlitSurface(name_text, None, nameplate.surface, sdl2.SDL_Rect(20, 4, 0, 0))
        sdl2.SDL_FreeSurface(name_text)

        level_text = sdl2.sdlttf.TTF_RenderText_Blended(self.name_font, str.encode(f"Lv{self.enemy_pokemon.level}"), BLACK)
        sdl2.surface.SDL_BlitSurface(level_text, None, nameplate.surface, sdl2.SDL_Rect(205, 4, 0, 0))
        sdl2.SDL_FreeSurface(level_text)

        self.enemy_pokemon_info_region.add_sprite(nameplate, 30, 50)

    def render_battle_regions(self):
        self.render_battle_info_region()
        self.render_battle_options_region()

    def render_battle_info_region(self):
        self.battle_info_region.clear()
        outer_box = self.sprite_factory.from_color(AQUA, self.battle_info_region.size())
        inner_box = self.sprite_factory.from_color(WHITE, (outer_box.size[0] - 18, outer_box.size[1] - 18))
        self.battle_info_region.add_sprite(outer_box, 0, 0)
        self.battle_info_region.add_sprite(inner_box, 9, 9)


    def render_battle_options_region(self):
        self.battle_options_region.clear()
        outer_box = self.sprite_factory.from_color(BLACK, self.battle_options_region.size())
        inner_box = self.sprite_factory.from_color(WHITE, (outer_box.size[0] - 18, outer_box.size[1] - 18))
        self.battle_options_region.add_sprite(outer_box, 0, 0)
        self.battle_options_region.add_sprite(inner_box, 9, 9)

    def full_render(self):
        self.region.clear()
        background = self.sprite_factory.from_surface(self.get_scaled_surface(get_image_from_path("battle_background.png")))
        self.region.add_sprite(background, 0, 0)
        self.render_enemy_regions()
        self.render_player_regions()
        self.render_battle_regions()

def make_battle_scene(scene_manager) -> BattleScene:
    scene = BattleScene(scene_manager, sdl2.ext.SOFTWARE)
    scene.full_render()
    return scene