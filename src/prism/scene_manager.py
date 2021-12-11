import sdl2
import sdl2.ext
import sdl2dll
from typing import Tuple
import typing
import importlib.resources
from PIL import Image

def get_image_from_path(file_name: str) -> Image:
    with importlib.resources.path('prism.resources', file_name) as path:
        return Image.open(path)

if typing.TYPE_CHECKING:
    from prism.engine import Scene
    from prism.overworld_scene import OverworldScene

class SceneManager:
    """Manager for all game scenes"""
    window: sdl2.ext.Window
    spriterenderer: sdl2.ext.SpriteRenderSystem
    factory: sdl2.ext.SpriteFactory
    connected: bool
    surfaces: dict
    sounds: dict
    frame_count: int
    current_scene: "Scene"
    overworld: "OverworldScene"
    def __init__(self, window: sdl2.ext.Window = None):
        self.frame_count = 0
        self.surfaces = {}
        self.sounds = {}

        if window:
            self.window = window
            self.factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE, free=False)
            self.spriterenderer = self.factory.create_sprite_render_system(window)

    def dispatch_key_event(self, key_event: int):
        self.current_scene.key_events[key_event]()

    def play_sound(self, file_name: str):
        # with importlib.resources.path('animearena.resources', file_name) as path:
        #     playsound(str(path), False)
        pass

    def set_scene_to_current(self, scene):
        self.current_scene = scene

    def change_window_size(self, new_width: int, new_height: int):
        sdl2.SDL_SetWindowSize(self.window.window, new_width, new_height)
        self.spriterenderer = self.factory.create_sprite_render_system(self.window)

    def create_new_window(self, size: Tuple[int, int], name: str):
        self.window.close()
        self.window = sdl2.ext.Window(name, size)
        self.window.show()
        self.spriterenderer = self.factory.create_sprite_render_system(self.window)