from prism.tile import Tile, tile_image_db
from typing import Tuple

class AreaMap:

    map: list[list[Tile]]
    width: int
    height: int

    def __init__(self, map: list[list[int]]):
        self.map = []
        for row in map:
            map_row = []
            for info in row:
                map_row.append(Tile(*tile_image_db[info]))
            self.map.append(map_row)
        self.width = len(self.map[0])
        self.height = len(self.map)

    def __getitem__(self, coord: Tuple[int, int]):
        return self.map[coord[1]][coord[0]]


test_map = AreaMap([
    [2, 2, 2, 2, 2, 2],
    [2, 0, 0, 0, 0, 2],
    [2, 0, 2, 2, 0, 2],
    [2, 0, 2, 0, 0, 2],
    [2, 0, 0, 0, 0, 2],
    [2, 2, 2, 2, 2, 2]
])