import sdl2.ext
import sdl2
import enum
from PIL import Image
from sdl2 import endian
import importlib.resources
import typing
from prism.portal import Portal
from prism.mapname import MapName
from typing import Optional

GREEN = sdl2.SDL_Color(50, 190, 50)
AQUA = sdl2.SDL_Color(30, 190, 210)

FACTORY = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE, free=False)


def get_image_from_path(file_name: str) -> Image:
    with importlib.resources.path('prism.resources', file_name) as path:
        return Image.open(path)


class Tile:
    image: Image
    walkable: bool
    grid_x: int
    grid_y: int
    x: int
    y: int
    dest_x: int
    dest_y: int
    x_movement_remaining: int
    y_movement_remaining: int
    dest_areamap: Optional[MapName]
    dest_portal: Optional[Portal]

    def __init__(self, **attributes):
        self.image = get_image_from_path(attributes["image"])
        if "walkable" in attributes:
            self.walkable = attributes["walkable"]
        else:
            self.walkable = True
        
        if "dest_areamap" in attributes:
            self.dest_areamap = attributes["dest_areamap"]
        else:
            self.dest_areamap = None

        if "dest_portal" in attributes:
            self.dest_portal = attributes["dest_portal"]
        else:
            self.dest_portal = None
        
        self.y_movement_remaining = 40
        self.x_movement_remaining = 40

    @property
    def x(self):
        if self.dest_x > self.grid_x:
            return (self.grid_x * 40) + (40 - self.x_movement_remaining)
        return self.grid_x * 40 - (40 - self.x_movement_remaining)

    @property
    def y(self):
        if self.dest_y > self.grid_y:
            return (self.grid_y * 40) + (40 - self.y_movement_remaining)
        return self.grid_y * 40 - (40 - self.y_movement_remaining)


tile_db = {
    0: {"image": "test_grass_tile.png"},
    1: {"image": "test_water_tile.png", "walkable": False},
    2: {"image": "test_rock_tile.png", "walkable": False},
    3: {"image": "test_door_tile.png"},
    4: {"image": "test_door_tile.png"}
}

