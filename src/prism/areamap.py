from prism.tile import Tile, tile_image_db
from typing import Tuple

class AreaMap:

    map: list[list[Tile]]
    width: int
    height: int
    start_offset: int

    def __init__(self, map: list[list[int]], start_offset: int):
        self.map = []
        for i, row in enumerate(map):
            map_row = []
            for j, info in enumerate(row):
                tile = Tile(*tile_image_db[info])
                tile.grid_x = j
                tile.grid_y = i
                tile.dest_x = j
                tile.dest_y = i
                map_row.append(tile)
            self.map.append(map_row)
        self.height = len(self.map[0])
        self.width = len(self.map)
        self.start_offset = start_offset

    def __getitem__(self, coord: Tuple[int, int]):
        return self.map[coord[1]][coord[0]]

    def __iter__(self):
        for row in self.map:
            yield from row

test_map = AreaMap([
    [2, 2, 2, 0, 0, 0, 0, 0, 2, 2, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 2, 0, 0, 0, 0, 0, 2, 0, 2],
    [2, 0, 2, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 0, 0, 0, 0, 0, 0, 0, 0, 0, 2],
    [2, 2, 2, 0, 0, 0, 0, 0, 2, 2, 2]
], 200)