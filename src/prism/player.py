import sdl2
import sdl2.ext
from typing import Tuple
import typing

if typing.TYPE_CHECKING:
    from prism.areamap import Item

class Player:
    sprite: sdl2.ext.SoftwareSprite
    x: int
    y: int
    moving: bool
    bonking: bool
    movement_remaining: int
    direction: Tuple[int, int]
    bag: list["Item"]
    def __init__(self, sprite):
        self.movement_remaining = 0
        self.x=1
        self.y=1
        self.moving = False
        self.bonking = False
        self.direction = (0,0)
        self.sprite = sprite
        self.bag = []

    def pick_up_item(self, item: "Item"):
        self.bag.append(item)

    def set_direction(self, direction: Tuple[int, int]):
        self.direction = direction