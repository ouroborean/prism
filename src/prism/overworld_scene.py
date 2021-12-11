from pathlib import Path
from typing import Union
import os
import threading
import gc
import tkinter as tk
from tkinter import filedialog
import sdl2
import sdl2.ext
import sdl2.surface
import sdl2.sdlttf
import importlib.resources
from PIL import Image
from io import StringIO

from prism import engine

def get_path(file_name: str) -> Path:
    with importlib.resources.path('prism.resources', file_name) as path:
        return path

class OverworldScene(engine.Scene):


    def __init__(self, scene_manager, *args, **kwargs):
        super().__init__(*args, **kwargs)


def make_overworld_scene(scene_manager) -> OverworldScene:
    scene = OverworldScene(scene_manager, sdl2.ext.SOFTWARE)

    return scene