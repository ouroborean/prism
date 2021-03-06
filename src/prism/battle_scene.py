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
from prism.poke_db import initialize_pokemon
from prism.abi_db import initialize_abilities
from prism.stat import Stat
from prism.status import BattleEffect, StatusEffect
from prism.pokemon import pokespawn, Pokemon
import enum
import random
from prism.trainer import Trainer
from prism.player import Player
if typing.TYPE_CHECKING:
    from prism.scene_manager import SceneManager


abi_db = initialize_abilities()
poke_db = initialize_pokemon()

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




@enum.unique
class BattlePhase(enum.IntEnum):
    ACTION_SELECTION = 0
    FIRST_ACTION_DESCRIPTION = 1
    FIRST_ACTION_EXECUTION = 2
    FIRST_ACTION_POST_DESCRIPTION = 3
    INTERIM_CHECK = 4
    SECOND_ACTION_DESCRIPTION = 5
    SECOND_ACTION_EXECUTION = 6
    SECOND_ACTION_POST_DESCRIPTION = 7
    TURN_END_CHECK = 8

@enum.unique
class Action(enum.IntEnum):
    FIGHT = 0
    PKMN = 1
    TRNR = 2
    RUN = 3


BLUE = sdl2.SDL_Color(0, 0, 255)
RED = sdl2.SDL_Color(255, 0, 0)
GREEN = sdl2.SDL_Color(50, 190, 50)
PURPLE = sdl2.SDL_Color(255, 60, 255)
AQUA = sdl2.SDL_Color(30, 190, 210)
BLACK = sdl2.SDL_Color(0, 0, 0)
WHITE = sdl2.SDL_Color(255, 255, 255)

class BattleScene(engine.Scene):

    player: Player
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
    message_queue: list[str]
    acting_list: list["Pokemon"]
    current_phase: BattlePhase
    player_ticking_health: bool
    enemy_ticking_health: bool
    executing_turn: bool
    printing: bool
    characters_printed: int
    lines_printed: int
    lines_to_print: int

    def __init__(self, scene_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.waiting_for_input = True
        self.selecting_action = True
        self.selecting_ability = False
        self.selecting_pokemon = False
        self.checking_trainer = False
        self.player_ticking_health = False
        self.enemy_ticking_health = False
        self.executing_turn = False
        self.printing = False
        self.battle_info_string = ""
        self.message_queue = []
        self.scene_manager = scene_manager
        self.current_phase = BattlePhase.ACTION_SELECTION
        self.selected_action = 0
        self.selected_ability = 0
        self.characters_printed = 0
        self.lines_printed = 0
        self.lines_to_print = 0
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
        
        self.acting_list = []
    
    def begin_battle(self, player: Player, trainer: "Trainer"):
        self.player = player
        self.trainer = trainer

        for pokemon in self.player.team:
            if pokemon.current_hp > 0 and not pokemon.is_egg:
                self.player_pokemon = pokemon
                break
        
        for pokemon in self.trainer.team:
            if pokemon.current_hp > 0 and not pokemon.is_egg:
                self.enemy_pokemon = pokemon
                break
        
        self.selected_action = 0
        self.selected_ability = 0
        self.selected_pokemon = 0
        self.selecting_ability = False
        self.selecting_pokemon = False
        self.checking_trainer = False
        self.full_render()

    def render_player_regions(self):
        self.render_player_pokemon_region()
        self.render_player_pokemon_info_region()

    def message(self, message: str):
        self.message_queue.append(message)
        self.printing = True

    def toggle_state(self, action: Action = None):
        if action == Action.FIGHT:
            #TODO Catch Encore
            self.selecting_ability = True
            self.selecting_pokemon = False
            self.selecting_action = False
            self.checking_trainer = False
        elif action == Action.PKMN:
            self.scene_manager.open_belt(self.player, True)
            self.toggle_state()
        elif action == Action.TRNR:
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
        if not self.player_pokemon.fainted:
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

        health_text = sdl2.sdlttf.TTF_RenderText_Blended(self.name_font, str.encode(f"{int(self.player_pokemon.display_hp)}/{int(self.player_pokemon.get_stat(Stat.HP))}"), BLACK)
        sdl2.surface.SDL_BlitSurface(health_text, None, nameplate.surface, sdl2.SDL_Rect(240, 83, 0, 0))
        sdl2.SDL_FreeSurface(health_text)

        health_check = self.player_pokemon.display_hp / self.player_pokemon.get_stat(Stat.HP)
        if health_check < .01 and health_check > 0:
            health_percent = .01
        elif health_check > .99 and health_check < 1:
            health_percent = .99
        else:
            health_percent = round(self.player_pokemon.display_hp / self.player_pokemon.get_stat(Stat.HP), 2)
        
        health_bar_width = int(health_percent * 200)

        self.player_pokemon_info_region.add_sprite(nameplate, -30, -5)

        if health_bar_width > 0:
            health_bar = self.sprite_factory.from_surface(self.get_scaled_surface(get_image_from_path("player_health_bar.png"), width = health_bar_width, height = 14))
            self.player_pokemon_info_region.add_sprite(health_bar, 155, 63)

    def render_enemy_regions(self):
        self.render_enemy_pokemon_region()
        self.render_enemy_pokemon_info_region()

    def render_enemy_pokemon_region(self):
        self.enemy_pokemon_region.clear()
        if not self.enemy_pokemon.fainted:
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

        health_check = self.enemy_pokemon.display_hp / self.enemy_pokemon.get_stat(Stat.HP)
        if health_check < .01 and health_check > 0:
            health_percent = .01
        elif health_check > .99 and health_check < 1:
            health_percent = .99
        else:
            health_percent = round(self.enemy_pokemon.display_hp / self.enemy_pokemon.get_stat(Stat.HP), 2)
        
        health_bar_width = int(health_percent * 200)

        if health_bar_width > 0:
            health_bar = self.sprite_factory.from_surface(self.get_scaled_surface(get_image_from_path("enemy_health_bar.png"), width = health_bar_width, height = 9))
            self.enemy_pokemon_info_region.add_sprite(health_bar, 155, 101)

    def render_battle_regions(self):

        self.render_battle_info_region()
        if self.current_phase == BattlePhase.ACTION_SELECTION and not self.selecting_ability and not self.enemy_ticking_health and not self.player_ticking_health:
            self.render_battle_options_region()

    def render_battle_info_region(self):
        
        self.battle_info_region.clear()
        outer_box = self.sprite_factory.from_color(AQUA, self.battle_info_region.size())
        inner_box = self.sprite_factory.from_color(WHITE, (outer_box.size[0] - 18, outer_box.size[1] - 18))
        abilities_to_render = []
        info_to_render = ()
        if not self.selecting_ability or self.selecting_pokemon or self.checking_trainer:
            if self.current_phase == BattlePhase.ACTION_SELECTION:
                self.lines_to_print = ["What will",  f"{self.player_pokemon.name} do?"]
                max_width = 460
            elif self.message_queue and not (self.player_ticking_health or self.enemy_ticking_health):
                max_width = 690
                self.lines_to_print = text_formatter.get_lines(self.message_queue[0], max_width, MENU_FONT_SIZE)
            outer_box = self.sprite_factory.from_color(AQUA, self.battle_info_region.size())
            inner_box = self.sprite_factory.from_color(WHITE, (outer_box.size[0] - 18, outer_box.size[1] - 18))

            if self.current_phase == BattlePhase.ACTION_SELECTION:
                for row, line in enumerate(self.lines_to_print):
                    text_surface = sdl2.sdlttf.TTF_RenderText_Blended(self.menu_font, str.encode(line), BLACK)
                    sdl2.surface.SDL_BlitSurface(text_surface, None, inner_box.surface, sdl2.SDL_Rect(15, 15 + (row * 80), 0, 0))
                    sdl2.SDL_FreeSurface(text_surface)
            else:
                for row, line in enumerate(self.lines_to_print):
                    if row < self.lines_printed:
                        text_surface = sdl2.sdlttf.TTF_RenderText_Blended(self.menu_font, str.encode(line), BLACK)
                        sdl2.surface.SDL_BlitSurface(text_surface, None, inner_box.surface, sdl2.SDL_Rect(15, 15 + (row * 80), 0, 0))
                        sdl2.SDL_FreeSurface(text_surface)
                    elif row == self.lines_printed:
                        characters_to_print = len(line)
                        text_surface = sdl2.sdlttf.TTF_RenderText_Blended(self.menu_font, str.encode(line[:self.characters_printed]), BLACK)
                        sdl2.surface.SDL_BlitSurface(text_surface, None, inner_box.surface, sdl2.SDL_Rect(15, 15 + (row * 80), 0, 0))
                        sdl2.SDL_FreeSurface(text_surface)
                        self.characters_printed += 1
                        if self.characters_printed > characters_to_print:
                            self.lines_printed += 1
                            if self.lines_printed >= len(self.lines_to_print):
                                self.lines_printed = 0
                                self.characters_printed = 0
                                self.message_queue = self.message_queue[1:]
                                if not self.message_queue:
                                    self.lines_to_print = []
                                    self.printing = False
                            self.characters_printed = 0

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
        if not self.player_ticking_health and not self.enemy_ticking_health and not self.executing_turn:
            if self.selecting_action:
                self.toggle_state(Action(self.selected_action))
            elif self.selecting_ability:
                #TODO catch ability failstates (Disable, Torment, Taunt, No PP)
                if True:
                    self.selecting_ability = False
                    self.player_pokemon.decision = self.selected_ability
                    self.current_phase = BattlePhase.FIRST_ACTION_DESCRIPTION
                    self.start_turn()
                    

        self.full_render()

    def pressed_cancel(self):
        if self.selecting_ability:
            self.toggle_state()
        
        self.full_render()

    def get_enemy(self, pokemon: "Pokemon") -> "Pokemon":
        if pokemon == self.player_pokemon:
            return self.enemy_pokemon
        else:
            return self.player_pokemon

    def get_decision(self, decision_slot: int):
        self.player_pokemon.decision = decision_slot
        self.current_phase = BattlePhase.FIRST_ACTION_DESCRIPTION
        self.start_turn()
        self.full_render()

    def change_pokemon(self, slot: int, player: bool):
        if player:
            self.player_pokemon = self.player.team[slot - 4]
        else:
            self.enemy_pokemon = self.trainer.team[slot - 4]
        self.full_render()


    def start_turn(self):
        self.get_enemy_decision()
        self.acting_list = self.speed_order(self.player_pokemon, self.enemy_pokemon)
        self.pre_check(self.acting_list[0])
        
        self.executing_turn = True
    
    def execution_loop(self):
        
        if self.current_phase == BattlePhase.FIRST_ACTION_DESCRIPTION:
            if not self.message_queue:
                self.execute_action(self.acting_list[0])
                self.current_phase = BattlePhase.FIRST_ACTION_EXECUTION
        elif self.current_phase == BattlePhase.FIRST_ACTION_EXECUTION:
            if not self.message_queue:
                self.current_phase = BattlePhase.INTERIM_CHECK
                self.interim_check()
        elif self.current_phase == BattlePhase.INTERIM_CHECK:
            if not self.message_queue:
                self.pre_check(self.acting_list[1])
                self.current_phase = BattlePhase.SECOND_ACTION_DESCRIPTION
        elif self.current_phase == BattlePhase.SECOND_ACTION_DESCRIPTION:
            if not self.message_queue:
                self.execute_action(self.acting_list[1])
                self.current_phase = BattlePhase.SECOND_ACTION_EXECUTION
        elif self.current_phase == BattlePhase.SECOND_ACTION_EXECUTION:
            if not self.message_queue:
                self.turn_end_check()
                self.current_phase = BattlePhase.TURN_END_CHECK
        elif self.current_phase == BattlePhase.TURN_END_CHECK:
            if not self.message_queue:
                self.toggle_state()
                self.executing_turn = False
                self.current_phase = BattlePhase.ACTION_SELECTION
                self.full_render()

    
    def pre_check(self, pokemon: "Pokemon"):
        if pokemon.decision < 4:
            self.pre_ability_execution(pokemon)
        elif pokemon.decision == 10:
            self.message(f"{pokemon.name} didn't do anything!")
        else:
            self.pre_pokemon_change(pokemon)

    def interim_check(self):
        if self.acting_list[0].current_hp == 0:
            if self.acting_list[0] == self.player_pokemon:
                owner_msg = ""
                self.player_pokemon.fainted = True
            else:
                owner_msg = "The enemy "
                self.enemy_pokemon.fainted = True
            self.message(f"{owner_msg}{self.player_pokemon.name} fainted!")
            self.current_phase = BattlePhase.SECOND_ACTION_EXECUTION
        if self.acting_list[1].current_hp == 0:
            if self.acting_list[1] == self.player_pokemon:
                owner_msg = ""
                self.player_pokemon.fainted = True
            else:
                owner_msg = "The enemy "
                self.enemy_pokemon.fainted = True
            self.message(f"{owner_msg}{self.player_pokemon.name} fainted!")
            self.current_phase = BattlePhase.SECOND_ACTION_EXECUTION

    def turn_end_check(self):
        
        if StatusEffect.BURN in self.player_pokemon.status_effects:
            self.player_pokemon.burn_tick(self)
            self.player_ticking_health = True
        if StatusEffect.POISON in self.player_pokemon.status_effects:
            self.player_pokemon.poison_tick(self)
            self.player_ticking_health = True
        

        if StatusEffect.BURN in self.enemy_pokemon.status_effects:
            self.enemy_pokemon.burn_tick(self)
            self.enemy_ticking_health = True
        if StatusEffect.POISON in self.enemy_pokemon.status_effects:
            self.enemy_pokemon.poison_tick(self)
            self.enemy_ticking_health = True

        if self.acting_list[0].current_hp == 0 and not self.acting_list[0].fainted:
            if self.acting_list[0] == self.player_pokemon:
                owner_msg = ""
                self.player_pokemon.fainted = True
            else:
                owner_msg = "The enemy "
                self.enemy_pokemon.fainted = True
            self.message(f"{owner_msg}{self.acting_list[0].name} fainted!")
        if self.acting_list[1].current_hp == 0 and not self.acting_list[1].fainted:
            if self.acting_list[1] == self.player_pokemon:
                owner_msg = ""
                self.player_pokemon.fainted = True
            else:
                owner_msg = "The enemy "
                self.enemy_pokemon.fainted = True
            
            self.message(f"{owner_msg}{self.acting_list[1].name} fainted!")


    def pre_pokemon_change(self, pokemon: "Pokemon"):

        if pokemon == self.player_pokemon:
            self.message(f"{pokemon.name} switched out to {self.player.team[pokemon.decision - 4].name}!")
        else:
            self.message(f"The enemy {pokemon.name} switched out to {self.trainer.team[pokemon.decision - 4].name}!")
        
    def pre_ability_execution(self, pokemon: "Pokemon"):
        if self.player_pokemon == pokemon:
            player = True
            owner_msg = ""
        else:
            player = False
            owner_msg = "The enemy "
        if not pokemon.pre_check_for_status_failure(self):
            self.message(f"{owner_msg}{pokemon.name} used {pokemon.abilities[pokemon.decision].name}!")

    def get_enemy_decision(self):

        rand_range = len(self.enemy_pokemon.abilities)
        roll = random.randint(1, rand_range)

        self.enemy_pokemon.decision = roll - 1

    def execute_action(self, pokemon: "Pokemon"):
        if pokemon == self.player_pokemon:
            if pokemon.decision < 4:
                if not pokemon.status_failed():
                    pokemon.execute_ability(self.enemy_pokemon, pokemon.abilities[pokemon.decision], self)
            elif pokemon.decision == 10:
                pass
            else:
                self.change_pokemon(pokemon.decision, True)
        else:
            if pokemon.decision < 4:
                if not pokemon.status_failed():
                    pokemon.execute_ability(self.player_pokemon, pokemon.abilities[pokemon.decision], self)
            elif pokemon.decision == 10:
                pass
            else:
                self.change_pokemon(pokemon.decision, True)

    def speed_order(self, pokemon1: "Pokemon", pokemon2: "Pokemon") -> Tuple["Pokemon", "Pokemon"]:
        if pokemon1.using_ability() and pokemon2.using_ability():
            if pokemon1.abilities[pokemon1.decision].priority == pokemon1.abilities[pokemon1.decision].priority:
                if pokemon1.get_stat(Stat.SPD) > pokemon2.get_stat(Stat.SPD):
                    return [pokemon1, pokemon2]
                elif pokemon1.get_stat(Stat.SPD) < pokemon2.get_stat(Stat.SPD):
                    return [pokemon2, pokemon1]
                else:
                    pool = [pokemon1, pokemon2]
                    roll = random.randint(0,1)
                    output = [None, None]
                    output[0] = pool[roll]
                    output[1] = pool[1 - roll]
                    return output
            else:
                if pokemon1.abilities[pokemon1.decision].priority > pokemon1.abilities[pokemon1.decision].priority:
                    return [pokemon1, pokemon2]
                else:
                    return [pokemon2, pokemon1]
        else:
            if not pokemon2.using_ability() and pokemon1.using_ability():
                return [pokemon2, pokemon1]
            elif not pokemon1.using_ability() and pokemon2.using_ability():
                return [pokemon1, pokemon2]
            else:
                if pokemon1.get_stat(Stat.SPD) >= pokemon2.get_stat(Stat.SPD):
                    return [pokemon1, pokemon2]
                elif pokemon1.get_stat(Stat.SPD) < pokemon2.get_stat(Stat.SPD):
                    return [pokemon2, pokemon1]

def make_battle_scene(scene_manager) -> BattleScene:
    scene = BattleScene(scene_manager, sdl2.ext.SOFTWARE)
    scene.key_press_events[sdl2.SDLK_UP] = scene.pressed_up
    scene.key_press_events[sdl2.SDLK_DOWN] = scene.pressed_down
    scene.key_press_events[sdl2.SDLK_LEFT] = scene.pressed_left
    scene.key_press_events[sdl2.SDLK_RIGHT] = scene.pressed_right
    scene.key_press_events[sdl2.SDLK_e] = scene.pressed_confirm
    scene.key_press_events[sdl2.SDLK_q] = scene.pressed_cancel
    return scene