from typing import Dict

from prism import ability

from .pokemon import Pokemon
from .ptypes import PokemonType
from .passive import Passive
from . import abi_db

def create_move_pool(database: Dict, *args: str) -> list:
    abilities = []
    output = []
    abilities.extend(args)
    for ability in abilities:
        output.append(database[ability])

def initialize_pokemon() -> Dict[str, Pokemon]:

    ability_db = abi_db.initialize_abilities()

    poke_db = {}
    poke_db["slowbro"] = Pokemon("Slowbro", (PokemonType.WATER, PokemonType.PSYCHIC), 75,110,100,80,30,95, (Passive.OBLIVIOUS, Passive.OWN_TEMPO, Passive.REGENERATOR))
    poke_db["garchomp"] = Pokemon("Garchomp", (PokemonType.DRAGON, PokemonType.GROUND), 130, 95, 80, 85, 102, 108, (Passive.SAND_VEIL, Passive.ROUGH_SKIN))
    poke_db["mudkip"] = Pokemon("Mudkip", (PokemonType.WATER, ), 70, 50, 50, 50, 40, 50, (Passive.TORRENT, Passive.DAMP))
    poke_db["misdreavus"] = Pokemon("Misdreavus", (PokemonType.GHOST, ), 60, 60, 85, 85, 85, 60, (Passive.LEVITATE,))
    poke_db["mismagius"] = Pokemon("Mismagius", (PokemonType.GHOST,), 60, 60, 105, 105, 105, 60, (Passive.LEVITATE,))
    return poke_db


