import typing
from PIL import Image
from prism.pokemon import pokespawn


if typing.TYPE_CHECKING:
    from prism.pokemon import Pokemon



class Trainer:

    name: str
    team: list["Pokemon"]

    def __init__(self, name: str, team: list["Pokemon"]):
        self.name = name
        self.team = team

trainer_db = {

    0: Trainer("Test Trainer", [])

}