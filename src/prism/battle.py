from typing import Tuple
from prism.status import BattleEffect
from .pokemon import Pokemon



class BattleSlot:
    active_pokemon: Pokemon
    effects: list[BattleEffect]
    battle: "Battle"
    team: list[Pokemon]

    def __init__(self):
        self.effects = []

    def assign_initial_pokemon(self, pokemon: Pokemon):
        self.active_pokemon = pokemon
        pokemon.set_battleslot(self)
        self.team.remove(pokemon)
        self.team.append(pokemon)

    def assign_team(self, team: list[Pokemon]):
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
    teams: Tuple[list[Pokemon]]
    effects: list[BattleEffect]

    def __init__(self):
        self.effects = []
    def assign_battle_slots(self, slots: Tuple[BattleSlot]):
        for battle_slot in slots:
            battle_slot.battle = self
        self.battle_slots = slots
    
    def assign_teams(self, teams: Tuple[list[Pokemon]]):
        self.teams = teams
        for team in teams:
            for pokemon in team:
                pokemon.assign_team(team)
