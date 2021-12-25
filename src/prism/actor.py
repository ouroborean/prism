import typing
from typing import Callable, Optional, Tuple
from PIL import Image
import importlib.resources


if typing.TYPE_CHECKING:
    from prism.overworld_scene import OverworldScene
    from prism.areamap import Tile, AreaMap

def get_image_from_path(file_name: str) -> Image.Image:
    with importlib.resources.path('prism.resources', file_name) as path:
        return Image.open(path)

def default_dialogue(scene: "OverworldScene"):
    scene.scene_manager.start_dialogue("I have nothing to say to you! Why do you keep coming back here wondering if I'll have something to say? AAAAAAA AAA? AAAAAAAAAA AAA AA A AAAAAAAAAAA AAAAAAAAAAAAAAA")

def test_move(scene: "OverworldScene", actor: "Actor"):
    if actor.movement_phase == 1:
        move_actor(actor, (1, 0), (5, 2), 2)
    elif actor.movement_phase == 2:
        move_actor(actor, (-1, 0), (1, 2), 1)
    

def move_actor(actor: "Actor", direction: Tuple[int, int], destination: Tuple[int, int], next_phase: int = 0):
    if actor.position == (destination):
        actor.movement_phase = next_phase
    elif not actor.moving:
        actor.moving = True
        actor.direction = direction
        actor.dest_x, actor.dest_y = (actor.position[0] + actor.direction[0], actor.position[1] + actor.direction[1])







class Actor:
    
    dest_x: int
    dest_y: int
    dialogue_script: Optional[Callable]
    movement_script: Optional[Callable]
    image: Image.Image
    position: Tuple[int, int]
    x_movement_remaining: int
    y_movement_remaining: int
    movement_speed: int
    moving: bool
    bonking: bool
    direction: Tuple[int, int]
    movement_phase: int
    interactable: bool

    def __init__(self, image: str, position: Tuple[int, int], movement: Optional[Callable] = None, dialogue: Optional[Callable] = None):
        self.interactable = True
        self.movement_speed = 8
        self.movement_phase = 1
        self.x_movement_remaining = 40
        self.y_movement_remaining = 40
        self.moving = False
        self.bonking = False
        if movement:
            self.movement_script = movement
        else:
            self.movement_script = None
        self.position = position
        self.dest_x, self.dest_y = self.position
        self.image = get_image_from_path(image)
        if dialogue:
            self.dialogue_script = dialogue
        else:
            self.dialogue_script = default_dialogue

actor_db = {

    0: Actor("test_npc.png", (3, 2), movement = test_move),
    1: Actor("test_event_npc.png", (8, 4)),
}
