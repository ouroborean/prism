import random

from . import ability_ingestor
from .battle import BattleSlot, Battle
from .status import StatusEffect
from . import pokemon
from .ability import Ability, AbilityType, TargetingType
from . import ptypes
from . import decisions
from . import abi_db
from . import poke_db
from .passive import Passive
from .stat import Stat

def make_decision(acting_pokemon: pokemon.Pokemon, acting_enemy: pokemon.Pokemon, ally_team: list[pokemon.Pokemon], enemy_team: list[pokemon.Pokemon]) -> int:
    #placeholder decision loop (Equal weights)

    ability_odds = []
    switch_odds = []

    for _ in range(len(acting_pokemon.abilities)):
        ability_odds.append(1)

    for _ in range(4 - len(ability_odds)):
        ability_odds.append(0)

    for i in range(len(ally_team) - 1):
        if not ally_team[i].fainted:
            switch_odds.append(1)

    for _ in range(5 - len(switch_odds)):
        switch_odds.append(0)

    all_odds = ability_odds + switch_odds
    odds_range = 0
    for n in all_odds:
        odds_range += n
    roll = random.randint(1, odds_range)
    rolling_total = 0
    for i, odds in enumerate(all_odds):
        rolling_total += odds
        if roll <= rolling_total:
            return i

    return 69

def tick_post_turn_effects(battle: Battle):
    for battle_slot in battle.battle_slots:
        if StatusEffect.BURN in battle_slot.active_pokemon.status_effects:
            battle_slot.active_pokemon.burn_tick()
        if StatusEffect.POISON in pokemon.status_effects:
            pokemon.poison_tick()

def speed_order(pokemon1: pokemon.Pokemon, pokemon2: pokemon.Pokemon) -> list[pokemon.Pokemon]:
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

def execute_turn(team1: list[pokemon.Pokemon], team2: list[pokemon.Pokemon], battle: Battle) -> bool:
    #TODO Pokemon 1 decides on an action
    battle.battle_slots[0].active_pokemon.decision = make_decision(battle.battle_slots[0].active_pokemon, battle.battle_slots[1].active_pokemon, team1, team2)

    #TODO Pokemon 2 decides on an action
    battle.battle_slots[1].active_pokemon.decision = make_decision(battle.battle_slots[1].active_pokemon, battle.battle_slots[0].active_pokemon, team2, team1)

    #TODO Put Pokemon in current speed order
    acting_list = speed_order(battle.battle_slots[0].active_pokemon, battle.battle_slots[1].active_pokemon)

    #TODO Have Pokemon act in order
    for pokemon in acting_list:
        if pokemon.decision >= 4:
            print(f"{pokemon.name} switches to {pokemon.battle_slot.team[pokemon.decision - 4].name}!")
            pokemon.battle_slot.change_active(pokemon.decision - 4)
        else:
            if not pokemon.check_for_status_failure():
                pokemon.execute_ability(pokemon.get_enemy((battle.battle_slots[0].active_pokemon, battle.battle_slots[1].active_pokemon)), pokemon.abilities[pokemon.decision])
        if pokemon.get_enemy((battle.battle_slots[0].active_pokemon, battle.battle_slots[1].active_pokemon)).fainted:
            break

    tick_post_turn_effects(battle)
    for battle_slot in battle.battle_slots:
        if battle_slot.active_pokemon.fainted:
            return False
    print()
    return True

def main():

    abilities = abi_db.initialize_abilities()
    pokemon = poke_db.initialize_pokemon()

    slowbro = pokemon["slowbro"]
    garchomp = pokemon["garchomp"]
    fucko = pokemon["fucko"]
    bigmon = pokemon["bigmon"]
    squirpy = pokemon["squirpy"]
    blangdib = pokemon["blangdib"]

    slowbro.set_passive(Passive.REGENERATOR)

    slowbro.learn_ability(abilities["pound"])
    slowbro.learn_ability(abilities["scratch"])
    slowbro.learn_ability(abilities["mega_punch"])
    slowbro.learn_ability(abilities["vise_grip"])
    print()
    garchomp.set_passive(Passive.ROUGH_SKIN)
    garchomp.learn_ability(abilities["fire_punch"])
    garchomp.learn_ability(abilities["ice_punch"])
    garchomp.learn_ability(abilities["thunder_punch"])
    garchomp.learn_ability(abilities["karate_chop"])
    print()
    fucko.learn_ability(abilities["pound"])
    fucko.set_passive(Passive.OBLIVIOUS)
    bigmon.learn_ability(abilities["pound"])
    bigmon.set_passive(Passive.OBLIVIOUS)
    squirpy.learn_ability(abilities["pound"])
    squirpy.set_passive(Passive.OBLIVIOUS)
    blangdib.learn_ability(abilities["pound"])
    blangdib.set_passive(Passive.OBLIVIOUS)

    battle = Battle()
    team1 = [slowbro, fucko, bigmon]
    team2 = [garchomp, squirpy, blangdib]
    battle.assign_teams((team1, team2))

    slot1 = BattleSlot()
    slot1.assign_team(team1)
    slot2 = BattleSlot()
    slot2.assign_team(team2)

    battle.assign_battle_slots((slot1, slot2))

    slot1.assign_initial_pokemon(team1[0])
    slot2.assign_initial_pokemon(team2[0])

    while True:
        if not execute_turn(team1, team2, battle):
            break

    return 0
