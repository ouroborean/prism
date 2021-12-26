from typing import Tuple
import enum
from prism import actor
from prism.portal import Portal
from prism.mapname import MapName
from prism.actor import Actor, actor_db
from prism.actor import move_actor
import sdl2.ext
import sdl2
import enum
from PIL import Image
from sdl2 import endian
import importlib.resources
import typing
from typing import Optional, Callable

if typing.TYPE_CHECKING:
    from prism.player import Player
    from prism.overworld_scene import OverworldScene


def get_image_from_path(file_name: str) -> Image:
    with importlib.resources.path('prism.resources', file_name) as path:
        return Image.open(path)

def default_pickup(scene: "OverworldScene", item: "Item"):
    scene.player.pick_up_item(item)
    print(f"You picked up {item.name}!")


def test_event_pickup(scene: "OverworldScene", item: "Item"):
    scene.event_running = True
    actor = item.actors[0]
    scene.player.pick_up_item(item)
    if not actor.movement_script:
        def test_event_movement(scene: "OverworldScene", actor: Actor):
            if actor.movement_phase == 1:
                move_actor(actor, (1, 0), (11, 4), 2)
            if actor.movement_phase == 2:
                move_actor(actor, (0, -1), (11, 2), 3)
            if actor.movement_phase == 3:
                scene.scene_manager.start_dialogue("Great job picking up that item, you shiiiiiit!", prompts=["Thanks", "Go Away", "Wicked Sick!"])
                
                actor.movement_phase = 4

            if actor.movement_phase == 4:
                if scene.scene_manager.current_scene != scene.scene_manager.dialogue:
                    response = scene.scene_manager.stored_prompt
                    print(response)
                    if response == "Go Away":
                        scene.scene_manager.start_dialogue("No, you go away!")
                    elif response == "Thanks":
                        scene.scene_manager.start_dialogue("Don't make this weird.")
                    elif response == "Wicked Sick!":
                        scene.scene_manager.start_dialogue("God, I hate that game.")
                    actor.movement_phase = 5
            if actor.movement_phase == 5:
                move_actor(actor, (0, 1), (11, 4), 6)
            if actor.movement_phase == 6:
                move_actor(actor, (-1, 0), (8, 4), 7)
            if actor.movement_phase == 7:
                scene.event_running = False
                
        actor.movement_script = test_event_movement

class Item:
    image: Image
    name: str
    pickup_script: Callable
    actors: list[Actor]
    def __init__(self, path: str, name: str, pickup_script: Callable = default_pickup, actors: list[Actor] = []):
        self.image = get_image_from_path(path)
        self.name = name
        self.pickup_script = pickup_script
        self.actors = actors

item_db = {
    "test_item": Item("test_item.png", "test item", pickup_script=test_event_pickup, actors=[actor_db[1]])
}

class Tile:
    image: Image.Image
    walkable: bool
    grid_x: int
    grid_y: int
    true_x: int
    true_y: int
    dest_x: int
    dest_y: int
    x_movement_remaining: int
    y_movement_remaining: int
    dest_areamap: Optional[MapName]
    dest_portal: Optional[Portal]
    dest_offset: Tuple[int, int]
    entry_map_offset: Tuple[int, int]
    item: Optional[Item]
    ramp_direction: Optional[Tuple[int, int]]
    occupied: bool
    player_occupied: bool
    actor: Optional[Actor]

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

        if "dest_offset" in attributes:
            self.dest_offset = attributes["dest_offset"]
        else:
            self.dest_offset = (0, 0)

        if "entry_map_offset" in attributes:
            self.entry_map_offset = attributes["entry_map_offset"]
        else:
            self.entry_map_offset = (200, 200)

        if "item" in attributes:
            self.item = attributes["item"]
        else:
            self.item = None

        if "ramp_direction" in attributes:
            self.ramp_direction = attributes["ramp_direction"]
        else:
            self.ramp_direction = None
        self.occupied = False
        self.player_occupied = False
        self.y_movement_remaining = 40
        self.x_movement_remaining = 40
        self.actor = None

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

    @property
    def has_item(self):
        return self.item

tile_db = {
    0: {
        "image": "test_grass_tile.png"
    },
    1: {
        "image": "test_water_tile.png",
        "walkable": False
    },
    2: {
        "image": "test_rock_tile.png",
        "walkable": False
    },
    3: {
        "image": "test_door_tile.png",
        "dest_areamap": MapName.TEST,
        "dest_portal": Portal.DOOR,
        "dest_offset": (-1, 0),
        "entry_map_offset": (200, 200)
    },
    4: {
        "image": "test_door_tile.png",
        "dest_areamap": MapName.CAVE,
        "dest_portal": Portal.DOOR,
        "dest_offset": (0, -1),
        "entry_map_offset": (200, 200)
    },
    5: {"image": "test_grass_tile.png",
        "item": item_db["test_item"]},
    6: {"image": "upper_left_stair_tile.png", "walkable": False},
    7: {"image": "lower_left_stair_tile.png", "walkable": False},
    8: {"image": "upper_middle_stair_tile.png", "ramp_direction": (-1, 1)},
    9: {"image": "lower_middle_stair_tile.png", "ramp_direction": (1, -1)},
    10: {"image": "lower_right_stair_tile.png", "walkable": False},
    11: {"image": "upper_right_stair_tile.png", "walkable": False},
    12: {"image": "test_grass_tile.png", "ramp_direction": (-1, 1)},
    13: {"image": "test_grass_tile.png", "ramp_direction": (1, -1)}
}

fg_db = {
    0: get_image_from_path("test_rock_foreground.png")
}

class AreaMap:

    map: list[list[Tile]]
    width: int
    height: int
    x_offset: int
    y_offset: int
    events: dict[Tuple[int, int], Callable]
    portals: dict[Portal, Tuple[int, int]]
    foreground_items: dict[Tuple[int, int], Image.Image]
    actors: list[Actor]

    def __init__(self, map: list[list[int]], offset: Tuple[int, int]):
        self.map = []
        for i, row in enumerate(map):
            map_row = []
            for j, info in enumerate(row):
                tile = Tile(**tile_db[info])
                tile.grid_x = j
                tile.grid_y = i
                tile.dest_x = j
                tile.dest_y = i
                tile.true_x = j
                tile.true_y = i
                map_row.append(tile)
            self.map.append(map_row)
        self.height = len(self.map[0])
        self.width = len(self.map)
        self.x_offset, self.y_offset = offset
        self.foreground_items = {}
        self.actors = []

    def __getitem__(self, coord: Tuple[int, int]):
        return self.map[coord[1]][coord[0]]

    def __iter__(self):
        for row in self.map:
            yield from row

    def populate(self):
        for actor in self.actors:
            self.map[actor.position[1]][actor.position[0]].occupied = True
            self.map[actor.position[1]][actor.position[0]].actor = actor

test_map = AreaMap(
    [[2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2], 
     [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
     [2, 0, 2, 0, 0, 0, 0, 0, 2, 0, 2],
     [2, 0, 2, 0, 1, 1, 1, 0, 0, 0, 2],
     [2, 0, 0, 0, 0, 0, 0, 0, 0, 4, 2], 
     [2, 2, 2, 2, 2, 2, 2, 2, 2, 2, 2]],
     
    (200, 200))


def reset_map_coords(map: list[list[Tile]], new_coords: Tuple[int, int]):
    for i, row in enumerate(map):
        for j, tile in enumerate(row):
            tile.grid_x = j - new_coords[0] + 1
            tile.grid_y = i - new_coords[1] + 1
            tile.dest_x = j - new_coords[0] + 1
            tile.dest_y = i - new_coords[1] + 1

def map_change_portal_event(player: "Player", area: AreaMap,
                            scene: "OverworldScene"):
    event_tile = area[player.x, player.y]
    new_map = map_db[event_tile.dest_areamap]
    new_map.x_offset, new_map.y_offset = event_tile.entry_map_offset
    portal_coord = new_map.portals[event_tile.dest_portal]
    offset = event_tile.dest_offset
    player.x = portal_coord[0] + offset[0]
    player.y = portal_coord[1] + offset[1]
    reset_map_coords(new_map.map, (player.x, player.y))
    scene.change_map(new_map)
    scene.event_running = False

test_map.foreground_items = {(2, 1): fg_db[0], (8, 1): fg_db[0]}

test_map.portals = {Portal.DOOR: (9, 4)}

test_map.events = {(9, 4): map_change_portal_event}

cave_map = AreaMap([[2, 2, 2, 2, 2, 2, 2, 2,  2, 2, 2, 2, 2, 2],
                    [2, 0, 0, 0, 0, 0, 2, 11, 12, 0, 0, 0, 5, 2],
                    [2, 0, 0, 0, 0, 0, 6, 8,  0, 0, 0, 0, 0, 2],
                    [2, 0, 0, 0, 0, 0, 9, 10, 0, 0, 0, 0, 0, 2],
                    [2, 0, 0, 0, 0, 13, 7, 2,  0, 0, 0, 0, 0, 2],
                    [2, 3, 2, 2, 2, 2, 2, 2,  2, 2, 2, 2, 2, 2],
                    [2, 2, 2, 2, 2, 2, 2, 2,  2, 2, 2, 2, 2, 2]], (200, 200))

cave_map.actors = [actor_db[0], actor_db[1]]

cave_map.populate()

cave_map.portals = {Portal.DOOR: (1, 5)}

cave_map.events = {(1, 5): map_change_portal_event}

map_db = {MapName.TEST: test_map, MapName.CAVE: cave_map}



