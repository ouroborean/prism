import enum


@enum.unique
class Stat(enum.IntEnum):
    """A component describing various combat statistics"""
    ATK = 0
    DEF = 1
    SPATK = 2
    SPDEF = 3
    SPD = 4
    HP = 5
    EVAS = 6
    ACC = 7