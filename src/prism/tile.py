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

    def __init__(self, image: Image):
        self.image = get_image_from_path(image)
        self.id = id

tile_image_db = {

    0: "test_grass_tile.png",
    1: "test_water_tile.png",
    2: "test_rock_tile.png"
}