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
from prism.areamap import get_image_from_path, map_db
from prism.poke_db import initialize_pokemon
from prism.abi_db import initialize_abilities
from prism.stat import Stat
from prism.status import BattleEffect
from prism.pokemon import pokespawn, Pokemon
import enum

if typing.TYPE_CHECKING:
    from prism.scene_manager import SceneManager
    from prism.player import Player
    from prism.trainer import Trainer

def get_image_from_path(file_name: str) -> Image:
    with importlib.resources.path('prism.resources', file_name) as path:
        return Image.open(path)

FONT_FILENAME = "Basic-Regular.ttf"
NAME_FONT_SIZE = 32
HEALTH_FONT_SIZE = 24
MENU_FONT_SIZE = 48
ABILITY_FONT_SIZE = 32

def init_font(size: int):
    with importlib.resources.path('prism.resources',
                                  FONT_FILENAME) as path:
        return sdl2.sdlttf.TTF_OpenFont(str.encode(os.fspath(path)), size)


class BattleSlot:
    active_pokemon: "Pokemon"
    effects: list[BattleEffect]
    battle: "Battle"
    team: list["Pokemon"]

    def __init__(self):
        self.effects = []

    def assign_initial_pokemon(self, pokemon: "Pokemon"):
        self.active_pokemon = pokemon
        pokemon.set_battleslot(self)
        self.team.remove(pokemon)
        self.team.append(pokemon)

    def assign_team(self, team: list["Pokemon"]):
        self.team = team

    def add_effect(self, effect: BattleEffect):
        self.effects.append(effect)

    def change_active(self, slot):
        pokeswap = self.team[slot]
        del self.team[slot]
        self.team.append(pokeswap)
        self.active_pokemon = pokeswap
        self.active_pokemon.set_battleslot(self)
        



class Battle:
    battle_slots: Tuple[BattleSlot]
    teams: Tuple[list["Pokemon"]]
    effects: list[BattleEffect]

    def __init__(self):
        self.effects = []
        
    def assign_battle_slots(self, slots: Tuple[BattleSlot]):
        for battle_slot in slots:
            battle_slot.battle = self
        self.battle_slots = slots
    
    def assign_teams(self, teams: Tuple[list["Pokemon"]]):
        self.teams = teams
        for team in teams:
            for pokemon in team:
                pokemon.assign_team(team)


@enum.unique
class Action(enum.IntEnum):
    FIGHT = 0
    PKMN = 1
    TRNR = 2
    RUN = 3

abi_db = initialize_abilities()
poke_db = initialize_pokemon()

BLUE = sdl2.SDL_Color(0, 0, 255)
RED = sdl2.SDL_Color(255, 0, 0)
GREEN = sdl2.SDL_Color(50, 190, 50)
PURPLE = sdl2.SDL_Color(255, 60, 255)
AQUA = sdl2.SDL_Color(30, 190, 210)
BLACK = sdl2.SDL_Color(0, 0, 0)
WHITE = sdl2.SDL_Color(255, 255, 255)

class BattleScene(engine.Scene):

    player: "Player"
    trainer: "Trainer"
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
    waiting_for_input: bool
    battle_info_string: str
    selected_action: int
    selecting_ability: bool
    selecting_pokemon: bool
    checking_trainer: bool
    selecting_action: bool
    selected_ability: int

    def __init__(self, scene_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.waiting_for_input = True
        self.selecting_action = True
        self.selecting_ability = False
        self.selecting_pokemon = False
        self.checking_trainer = False
        self.battle_info_string = ""
        self.scene_manager = scene_manager
        self.selected_action = 0
        self.selected_ability = 0
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
        self.menu_font = init_font(MENU_FONT_SIZE)
        self.ability_font = init_font(ABILITY_FONT_SIZE)
        self.player_pokemon = Pokemon(*poke_db["hitmontop"])
        self.player_pokemon.set_level(30)
        self.player_pokemon.learn_ability(abi_db["fire_punch"])
        self.player_pokemon.learn_ability(abi_db["ice_punch"])
        self.player_pokemon.learn_ability(abi_db["thunder_punch"])
        self.player_pokemon.learn_ability(abi_db["mega_punch"])
        
        self.enemy_pokemon = Pokemon(*poke_db["mismagius"])
        self.enemy_pokemon.set_level(45)
    
    def begin_battle(self, player: "Player", trainer: "Trainer"):
        self.player = player
        self.trainer = trainer

        for pokemon in self.player.team:
            if pokemon.hp > 0 and not pokemon.is_egg:
                self.player_pokemon = pokemon
                break
        
        for pokemon in self.trainer.team:
            if pokemon.hp > 0 and not pokemon.is_egg:
                self.enemy_pokemon = pokemon
                break
        
        self.selected_action = 0
        self.selected_ability = 0
        self.selected_pokemon = 0
        self.selecting_ability = False
        self.selecting_pokemon = False
        self.checking_trainer = False

    def render_player_regions(self):
        self.render_player_pokemon_region()
        self.render_player_pokemon_info_region()

    def toggle_state(self, action: Action = None):
        if action == Action.FIGHT:
            print("SELECTED FIGHT")
            #TODO Catch Encore
            self.selecting_ability = True
            self.selecting_pokemon = False
            self.selecting_action = False
            self.checking_trainer = False
        elif action == Action.PKMN:
            print("SELECTED POKEMON")
            self.selecting_pokemon = True
            self.selecting_ability = False
            self.selecting_action = False
            self.checking_trainer = False
        elif action == Action.TRNR:
            print("SELECTED TRAINER")
            self.checking_trainer = True
            self.selecting_action = False
            self.selecting_ability = False
            self.selecting_pokemon = False
        else:
            self.selecting_action = True
            self.selecting_ability = False
            self.selecting_pokemon = False
            self.checking_trainer = False


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
        sdl2.surface.SDL_BlitSurface(level_text, None, nameplate.surface, sdl2.SDL_Rect(310, 13, 0, 0))
        sdl2.SDL_FreeSurface(level_text)

        health_text = sdl2.sdlttf.TTF_RenderText_Blended(self.name_font, str.encode(f"{int(self.player_pokemon.current_hp)}/{int(self.player_pokemon.get_stat(Stat.HP))}"), BLACK)
        sdl2.surface.SDL_BlitSurface(health_text, None, nameplate.surface, sdl2.SDL_Rect(240, 83, 0, 0))
        sdl2.SDL_FreeSurface(health_text)



        self.player_pokemon_info_region.add_sprite(nameplate, -30, -5)

        health_bar = self.sprite_factory.from_surface(self.get_scaled_surface(get_image_from_path("player_health_bar.png")))
        self.player_pokemon_info_region.add_sprite(health_bar, 155, 63)

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
        sdl2.surface.SDL_BlitSurface(level_text, None, nameplate.surface, sdl2.SDL_Rect(245, 4, 0, 0))
        sdl2.SDL_FreeSurface(level_text)

        self.enemy_pokemon_info_region.add_sprite(nameplate, 30, 50)

        health_bar = self.sprite_factory.from_surface(self.get_scaled_surface(get_image_from_path("enemy_health_bar.png")))
        self.enemy_pokemon_info_region.add_sprite(health_bar, 155, 101)

    def render_battle_regions(self):

        self.render_battle_info_region()
        if self.selecting_action:
            self.render_battle_options_region()

    def render_battle_info_region(self):
        self.battle_info_region.clear()
        outer_box = self.sprite_factory.from_color(AQUA, self.battle_info_region.size())
        inner_box = self.sprite_factory.from_color(WHITE, (outer_box.size[0] - 18, outer_box.size[1] - 18))
        abilities_to_render = []
        info_to_render = ()
        if self.selecting_action:
            if self.waiting_for_input:
                lines = ["What will", f"{self.player_pokemon.name} do?"]
            else:
                lines = text_formatter.get_lines(self.battle_info_string, 460, MENU_FONT_SIZE)
            outer_box = self.sprite_factory.from_color(AQUA, self.battle_info_region.size())
            inner_box = self.sprite_factory.from_color(WHITE, (outer_box.size[0] - 18, outer_box.size[1] - 18))

            for row, line in enumerate(lines):
                battle_info_text = sdl2.sdlttf.TTF_RenderText_Blended(self.menu_font, str.encode(line), BLACK)
                sdl2.surface.SDL_BlitSurface(battle_info_text, None, inner_box.surface, sdl2.SDL_Rect(15, 15 + (row * 90), 0, 0))
                sdl2.SDL_FreeSurface(battle_info_text)
        elif self.selecting_ability:
            for i, ability in enumerate(self.player_pokemon.abilities):
                ability_button = self.sprite_factory.from_surface(self.get_scaled_surface(ability.ability_plate))
                ability_text = sdl2.sdlttf.TTF_RenderText_Blended(self.ability_font, str.encode(ability.name), BLACK)
                word_width = text_formatter.get_ability_word_size(ability.name)
                x_offset = (ability_button.size[0] - word_width) // 2
                sdl2.surface.SDL_BlitSurface(ability_text, None, ability_button.surface, sdl2.SDL_Rect(x_offset, 20, 0, 0))
                if i != self.selected_ability:
                    null_filter = self.get_scaled_surface(get_image_from_path("null_filter.png"))
                    sdl2.surface.SDL_BlitSurface(null_filter, None, ability_button.surface, sdl2.SDL_Rect(0, 0, 0, 0))
                else:
                    ability_type_sprite = self.sprite_factory.from_surface(self.get_scaled_surface(ability.ability_type_sprite))
                    ability_class_sprite = self.sprite_factory.from_surface(self.get_scaled_surface(ability.ability_class_sprite))
                    pp_text = sdl2.sdlttf.TTF_RenderText_Blended(self.ability_font, str.encode(f"{self.player_pokemon.current_pp[i]}/{ability.max_pp}"), BLACK)
                    pp_width = text_formatter.get_ability_word_size(f"{self.player_pokemon.current_pp[i]}/{ability.max_pp}")
                    sdl2.surface.SDL_BlitSurface(pp_text, None, inner_box.surface, sdl2.SDL_Rect(678 + ((100 - pp_width) // 2), 112, 0, 0))
                    sdl2.SDL_FreeSurface(pp_text)
                    info_to_render = (ability_type_sprite, ability_class_sprite)

                sdl2.SDL_FreeSurface(ability_text)
                abilities_to_render.append(ability_button)


        self.battle_info_region.add_sprite(outer_box, 0, 0)
        self.battle_info_region.add_sprite(inner_box, 9, 9)

        if abilities_to_render:
            for i, ability in enumerate(abilities_to_render):
                self.battle_info_region.add_sprite(ability, 14 + ((i % 2) * 336), 12 + ((i // 2) * 90))
            
            self.battle_info_region.add_sprite(info_to_render[0], 688, 15)
            self.battle_info_region.add_sprite(info_to_render[1], 688, 54)

    def render_battle_options_region(self):
        self.battle_options_region.clear()
        outer_box = self.sprite_factory.from_color(BLACK, self.battle_options_region.size())
        inner_box = self.sprite_factory.from_color(WHITE, (outer_box.size[0] - 18, outer_box.size[1] - 18))
        self.battle_options_region.add_sprite(outer_box, 0, 0)
        self.battle_options_region.add_sprite(inner_box, 9, 9)

        for i in range(4):
            outer_action_box = self.sprite_factory.from_color(BLACK, (132, 82))
            if i == self.selected_action:
                color = RED
            else:
                color = WHITE
            inner_action_box = self.sprite_factory.from_color(color, (126, 76))

            action_text = sdl2.sdlttf.TTF_RenderText_Blended(self.menu_font, str.encode(Action(i).name), BLACK)
            sdl2.surface.SDL_BlitSurface(action_text, None, inner_action_box.surface, sdl2.SDL_Rect(5, 5, 0, 0))
            sdl2.SDL_FreeSurface(action_text)

            self.battle_options_region.add_sprite(outer_action_box, 14 + ((i % 2) * 140), 14 + ((i // 2) * 90))
            self.battle_options_region.add_sprite(inner_action_box, 17 + ((i % 2) * 140), 17 + ((i // 2) * 90))


    def full_render(self):
        self.region.clear()
        background = self.sprite_factory.from_surface(self.get_scaled_surface(get_image_from_path("battle_background.png")))
        self.region.add_sprite(background, 0, 0)
        self.render_enemy_regions()
        self.render_player_regions()
        self.render_battle_regions()

    def pressed_up(self):
        if self.selecting_action:
            if self.selected_action > 1:
                self.selected_action -= 2
        if self.selecting_ability:
            if self.selected_ability > 1:
                self.selected_ability -= 2
        
        self.full_render()

    def pressed_right(self):
        if self.selecting_action:
            if self.selected_action % 2 == 0:
                self.selected_action += 1
        if self.selecting_ability:
            if self.selected_ability % 2 == 0:
                self.selected_ability += 1
                if self.selected_ability >= len(self.player_pokemon.abilities):
                    self.selected_ability = len(self.player_pokemon.abilities) - 1
        
        
        self.full_render()

    def pressed_left(self):
        if self.selecting_action:
            if self.selected_action % 2 != 0:
                self.selected_action -= 1
        if self.selecting_ability:
            if self.selected_ability % 2 != 0:
                self.selected_ability -= 1
        
        self.full_render()

    def pressed_down(self):
        if self.selecting_action:
            if self.selected_action < 2:
                self.selected_action += 2
        if self.selecting_ability:
            if self.selected_ability < 2:
                self.selected_ability += 2
                if self.selected_ability >= len(self.player_pokemon.abilities):
                    self.selected_ability = len(self.player_pokemon.abilities) - 1
        
        self.full_render()

    def pressed_confirm(self):
        if self.selecting_action:
            self.toggle_state(Action(self.selected_action))
        elif self.selecting_ability:
            #TODO catch ability failstates (Disable, Torment, Taunt, No PP)
            #TODO determine what to do with the opponent 'mon
            #TODO determine speed order
            #TODO conate both side's execution
            pass
        self.full_render()

    def pressed_cancel(self):
        if self.selecting_ability:
            self.toggle_state()
        
        self.full_render()

def make_battle_scene(scene_manager) -> BattleScene:
    scene = BattleScene(scene_manager, sdl2.ext.SOFTWARE)
    scene.key_press_events[sdl2.SDLK_UP] = scene.pressed_up
    scene.key_press_events[sdl2.SDLK_DOWN] = scene.pressed_down
    scene.key_press_events[sdl2.SDLK_LEFT] = scene.pressed_left
    scene.key_press_events[sdl2.SDLK_RIGHT] = scene.pressed_right
    scene.key_press_events[sdl2.SDLK_e] = scene.pressed_confirm
    scene.key_press_events[sdl2.SDLK_q] = scene.pressed_cancel
    scene.full_render()
    return scene