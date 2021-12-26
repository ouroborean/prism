import enum
from typing import Dict, Tuple


@enum.unique
class PokemonType(enum.IntEnum):
    """A component containing Pokemon Types"""
    NORMAL = 0
    FIGHTING = 1
    FLYING = 2
    POISON = 3
    GROUND = 4
    ROCK = 5
    BUG = 6
    GHOST = 7
    STEEL = 8
    FIRE = 9
    WATER = 10
    GRASS = 11
    ELECTRIC = 12
    PSYCHIC = 13
    ICE = 14
    DRAGON = 15
    DARK = 16
    FAIRY = 17

weak_against = {
    PokemonType.NORMAL: (PokemonType.FIGHTING,),
    PokemonType.FIGHTING: (PokemonType.PSYCHIC, PokemonType.FAIRY, PokemonType.FLYING),
    PokemonType.FLYING: (PokemonType.ROCK, PokemonType.ELECTRIC, PokemonType.ICE),
    PokemonType.POISON: (PokemonType.GROUND, PokemonType.PSYCHIC),
    PokemonType.GROUND: (PokemonType.WATER, PokemonType.GRASS, PokemonType.ICE),
    PokemonType.ROCK: (PokemonType.FIGHTING, PokemonType.GROUND, PokemonType.STEEL, PokemonType.WATER, PokemonType.GRASS),
    PokemonType.BUG: (PokemonType.FLYING, PokemonType.ROCK, PokemonType.FIRE),
    PokemonType.GHOST: (PokemonType.GHOST, PokemonType.DARK),
    PokemonType.STEEL: (PokemonType.FIGHTING, PokemonType.GROUND, PokemonType.FIRE),
    PokemonType.FIRE: (PokemonType.GROUND, PokemonType.ROCK, PokemonType.WATER),
    PokemonType.WATER: (PokemonType.GRASS, PokemonType.ELECTRIC),
    PokemonType.GRASS: (PokemonType.FLYING, PokemonType.POISON, PokemonType.BUG, PokemonType.FIRE, PokemonType.ICE),
    PokemonType.ELECTRIC: (PokemonType.GROUND,),
    PokemonType.PSYCHIC: (PokemonType.BUG, PokemonType.GHOST, PokemonType.DARK),
    PokemonType.ICE: (PokemonType.STEEL, PokemonType.ROCK, PokemonType.FIRE, PokemonType.FIGHTING),
    PokemonType.DRAGON: (PokemonType.DRAGON, PokemonType.ICE, PokemonType.FAIRY),
    PokemonType.DARK: (PokemonType.FIGHTING, PokemonType.BUG, PokemonType.FAIRY),
    PokemonType.FAIRY: (PokemonType.POISON, PokemonType.STEEL)
}

strong_against = {
    PokemonType.NORMAL: (),
    PokemonType.FIGHTING: (PokemonType.ROCK, PokemonType.BUG, PokemonType.DARK),
    PokemonType.FLYING: (PokemonType.FIGHTING, PokemonType.BUG, PokemonType.GRASS),
    PokemonType.POISON: (PokemonType.GRASS, PokemonType.FIGHTING, PokemonType.POISON, PokemonType.FAIRY),
    PokemonType.GROUND: (PokemonType.POISON, PokemonType.ROCK),
    PokemonType.ROCK: (PokemonType.NORMAL, PokemonType.FLYING, PokemonType.POISON, PokemonType.FIRE),
    PokemonType.BUG: (PokemonType.FIGHTING, PokemonType.GROUND, PokemonType.GRASS),
    PokemonType.GHOST: (PokemonType.POISON, PokemonType.BUG),
    PokemonType.STEEL: (PokemonType.NORMAL, PokemonType.FLYING, PokemonType.ROCK, PokemonType.BUG, PokemonType.STEEL, PokemonType.GRASS, PokemonType.PSYCHIC, PokemonType.ICE, PokemonType.DRAGON, PokemonType.FAIRY),
    PokemonType.FIRE: (PokemonType.FIRE, PokemonType.BUG, PokemonType.STEEL, PokemonType.ICE, PokemonType.FAIRY),
    PokemonType.WATER: (PokemonType.WATER, PokemonType.STEEL, PokemonType.FIRE, PokemonType.ICE),
    PokemonType.GRASS: (PokemonType.GROUND, PokemonType.WATER, PokemonType.GRASS, PokemonType.ELECTRIC),
    PokemonType.PSYCHIC: (PokemonType.FIGHTING, PokemonType.PSYCHIC),
    PokemonType.ICE: (PokemonType.ICE,),
    PokemonType.DRAGON: (PokemonType.FIRE, PokemonType.WATER, PokemonType.GRASS, PokemonType.ELECTRIC),
    PokemonType.DARK: (PokemonType.GHOST, PokemonType.DARK),
    PokemonType.FAIRY: (PokemonType.FIGHTING, PokemonType.BUG, PokemonType.DARK),
    PokemonType.ELECTRIC: (PokemonType.FLYING, PokemonType.STEEL, PokemonType.ELECTRIC)
}

immune_to: Dict[PokemonType, Tuple[PokemonType]] = {
    PokemonType.NORMAL: (PokemonType.GHOST,),
    PokemonType.GHOST: (PokemonType.NORMAL, PokemonType.FIGHTING),
    PokemonType.FLYING: (PokemonType.GROUND,),
    PokemonType.GROUND: (PokemonType.ELECTRIC,),
    PokemonType.STEEL: (PokemonType.POISON,),
    PokemonType.DARK: (PokemonType.PSYCHIC,),
    PokemonType.FAIRY: (PokemonType.DRAGON,)
}