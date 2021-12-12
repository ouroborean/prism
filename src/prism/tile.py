import sdl2.ext
import sdl2
import copy
from PIL import Image
from sdl2 import endian
import importlib.resources
GREEN = sdl2.SDL_Color(50, 190, 50)
AQUA = sdl2.SDL_Color(30, 190, 210)

FACTORY = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE, free=False)

def get_image_from_path(file_name: str) -> Image:
    with importlib.resources.path('prism.resources', file_name) as path:
        return Image.open(path)

class Tile:
    id : int
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

    def __init__(self, image: Image, walkable=True):
        self.image = get_image_from_path(image)
        self.id = id
        self.walkable = walkable
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

tile_image_db = {

    0: ("test_grass_tile.png",),
    1: ("test_water_tile.png", False),
    2: ("test_rock_tile.png", False),
}