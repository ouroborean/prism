import enum
from typing import Tuple, Dict, Optional
from PIL import Image
from .stat import Stat
from . import ptypes
import importlib.resources

def get_image_from_path(file_name: str) -> Image:
    with importlib.resources.path('prism.resources', file_name) as path:
        return Image.open(path)

@enum.unique
class AbilityType(enum.IntEnum):
    DAMAGE = 0
    TARGET_STATUS = 1
    SELF_STATUS = 2
    SELF_BOOST = 3
    TARGET_BOOST = 4
    MULTI_DAMAGE = 5
    RECOIL_DAMAGE = 6
    BATTLEFIELD = 7
    SELF_BATTLEZONE = 8
    ENEMY_BATTLEZONE = 9
    HEALING = 10


class TargetingType(enum.IntEnum):
    ENEMY = 0
    SELF = 1
    BATTLEFIELD = 2
    ENEMY_BATTLEZONE = 3
    SELF_BATTLEZONE = 4


class Ability:
    name: str
    ptype: ptypes.PokemonType
    atype: Dict[AbilityType, list]
    target: TargetingType
    max_pp: int
    current_pp: int
    tags: list[str]
    priority: int
    accuracy: int
    ability_plate: Image.Image

    def __init__(self, name: str, ptype: ptypes.PokemonType, accuracy: Optional[int], max_pp: int, priority: int,
                 target: TargetingType, atype: Tuple[AbilityType],
                 effects: Tuple, *args: str):
        self.name = name
        self.accuracy = accuracy
        self.ptype = ptype
        self.atype = {}
        self.target = target
        self.max_pp = max_pp
        self.current_pp = max_pp
        self.priority = priority

        self.ability_plate = get_image_from_path(ptype.name.lower() + "_button.png")

        for i, abi_type in enumerate(atype):
            self.atype[abi_type] = []
            self.atype[abi_type].append(effects[i])
        self.tags = []
        self.tags.extend(args)
    
    def expend_pp(self):
        self.current_pp -= 1