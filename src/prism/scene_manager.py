import sdl2
import sdl2.ext
from typing import Iterable, Tuple
import typing
import importlib.resources
from PIL import Image


def get_image_from_path(file_name: str) -> Image:
    with importlib.resources.path('prism.resources', file_name) as path:
        return Image.open(path)


if typing.TYPE_CHECKING:
    from prism.engine import Scene
    from prism.overworld_scene import OverworldScene
    from prism.dialogue_scene import DialogueScene


class SceneManager:
    """Manager for all game scenes"""
    window: sdl2.ext.Window
    spriterenderer: sdl2.ext.SpriteRenderSystem
    factory: sdl2.ext.SpriteFactory
    connected: bool
    surfaces: dict
    sounds: dict
    frame_count: int
    active_scenes: list["Scene"]
    dialogue: "DialogueScene"
    overworld: "OverworldScene"

    @property
    def current_scene(self):
        return self.active_scenes[-1]

    def renderables(self) -> Iterable[sdl2.ext.SoftwareSprite]:
        for scene in self.active_scenes:
            yield from scene.renderables()

    def __init__(self, window: sdl2.ext.Window = None):
        self.frame_count = 0
        self.surfaces = {}
        self.sounds = {}
        self.active_scenes = []
        if window:
            self.window = window
            self.factory = sdl2.ext.SpriteFactory(sdl2.ext.SOFTWARE,
                                                  free=False)
            self.spriterenderer = self.factory.create_sprite_render_system(
                window)

        self.surfaces["test_grass"] = get_image_from_path(
            "test_grass_tile.png")
        self.surfaces["test_water"] = get_image_from_path(
            "test_water_tile.png")
        self.surfaces["test_rock"] = get_image_from_path("test_rock_tile.png")

    def dispatch_key_press_event(self, key_event: int):
        self.current_scene.dispatch_key_press_event(key_event)

    def dispatch_key_release_event(self, key_event: int):
        self.current_scene.dispatch_key_release_event(key_event)

    def play_sound(self, file_name: str):
        # with importlib.resources.path('animearena.resources', file_name) as path:
        #     playsound(str(path), False)
        pass

    def close_scene(self, scene):
        self.active_scenes.remove(scene)

    def start_dialogue(self, message: str, prompts: list[str] = []):
        self.set_scene_to_active(self.dialogue)
        if prompts:
            self.dialogue.create_dialogue_with_prompt(message, prompts)
        else:
            self.dialogue.create_dialogue(message)

    def set_scene_to_active(self, scene):
        self.active_scenes.append(scene)

    def change_window_size(self, new_width: int, new_height: int):
        sdl2.SDL_SetWindowSize(self.window.window, new_width, new_height)
        self.spriterenderer = self.factory.create_sprite_render_system(
            self.window)

    def create_new_window(self, size: Tuple[int, int], name: str):
        self.window.close()
        self.window = sdl2.ext.Window(name, size)
        self.window.show()
        self.spriterenderer = self.factory.create_sprite_render_system(
            self.window)
