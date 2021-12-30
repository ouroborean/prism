from PIL.Image import init
import sdl2
import sdl2.ext
from typing import Tuple
import typing
from prism.poke_db import initialize_pokemon
from prism.abi_db import initialize_abilities
from prism.pokemon import pokespawn

if typing.TYPE_CHECKING:
    from prism.areamap import Item
    from prism.pokemon import Pokemon

abi_db = initialize_abilities()

class Player:
    sprite: sdl2.ext.SoftwareSprite
    x: int
    y: int
    moving: bool
    bonking: bool
    movement_remaining: int
    direction: Tuple[int, int]
    bag: list["Item"]
    team: list["Pokemon"]

    def __init__(self, sprite):
        self.movement_remaining = 0
        self.x=1
        self.y=1
        self.moving = False
        self.bonking = False
        self.direction = (0,0)
        self.sprite = sprite
        self.bag = []
        self.team = [pokespawn("mudkip", 5, ["fire_punch", "thunder_punch"]), pokespawn("mismagius", 40, ["shadow_ball", "aurora_beam", "energy_ball", "flamethrower"])]

    def pick_up_item(self, item: "Item"):
        self.bag.append(item)

    def set_direction(self, direction: Tuple[int, int]):
        self.direction = direction
