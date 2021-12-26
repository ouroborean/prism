import enum
import typing
from typing import Optional

from prism.stat import Stat
if typing.TYPE_CHECKING:
    from .pokemon import Pokemon

@enum.unique
class BattleEffectType(enum.IntEnum):
    SUNNY_DAY = 0
    STEALTH_ROCK = 1

class BattleEffect:
    
    effect_type: BattleEffectType
    duration: int

    def __init__(self, type: BattleEffectType, duration: Optional[int]):
        self.effect_type = type
        self.duration = duration


@enum.unique
class StatusEffect(enum.IntEnum):
    PARALYZE = 0
    BURN = 1
    FREEZE = 2
    SLEEP = 3
    POISON = 4
    TOXIC = 5
    CURSE = 6
    CONFUSE = 7
    ATTRACT = 8
    FIRESPIN = 9
    WRAP = 10
    BIND = 11
    LEECHSEED = 12
    WHIRLPOOL = 13
    FOCUS_ENERGY = 14
    REST_SLEEP = 15
    FLINCH = 16

def status_applied(target: "Pokemon", status_effect: StatusEffect) -> str:
    if status_effect == StatusEffect.FREEZE:
        return f"{target.name} was frozen solid!"
    elif status_effect == StatusEffect.BURN:
        return f"{target.name} was burned!"
    elif status_effect == StatusEffect.PARALYZE:
        return f"{target.name} was paralyzed!"
    elif status_effect == StatusEffect.SLEEP:
        return f"{target.name} fell asleep!"
    elif status_effect == StatusEffect.POISON:
        return f"{target.name} was poisoned!"
    elif status_effect == StatusEffect.TOXIC:
        return f"{target.name} was badly poisoned!"
    elif status_effect == StatusEffect.CURSE:
        return f"{target.name} was cursed!"
    elif status_effect == StatusEffect.CONFUSE:
        return f"{target.name} was confused!"
    elif status_effect == StatusEffect.ATTRACT:
        return f"{target.name} fell in love!"
    elif status_effect == StatusEffect.FIRESPIN:
        return f"{target.name} was surrounded by flames!"
    elif status_effect == StatusEffect.WRAP:
        return f"{target.name} was wrapped!"
    elif status_effect == StatusEffect.BIND:
        return f"{target.name} was bound!"
    elif status_effect == StatusEffect.LEECHSEED:
        return f"{target.name} was seeded!"
    elif status_effect == StatusEffect.WHIRLPOOL:
        return f"{target.name} was caught in the vortex!"

def status_desc(status_effect: StatusEffect) -> str:
    pass

def is_greater_status(effect: StatusEffect) -> bool:
        gen = (StatusEffect.BURN, StatusEffect.FREEZE, StatusEffect.PARALYZE, StatusEffect.POISON, StatusEffect.TOXIC, StatusEffect.SLEEP)
        for eff in gen:
            if eff == effect:
                return True
        return False