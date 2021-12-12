from asyncio.exceptions import CancelledError
import logging
import asyncio
import contextvars
import time
import sdl2
import sdl2.ext
import sdl2.sdlttf
import typing
from prism.scene_manager import SceneManager
from prism import overworld_scene

def main():
    """Main game entry point"""

    logging.basicConfig(level=logging.DEBUG,
                        format="%(levelname)s:%(relativeCreated)d:%(module)s:%(message)s")
    logging.getLogger("PIL").setLevel(69) # turn off PIL logging

    sdl2.ext.init()
    logging.debug("SDL2 video system initialized")
    sdl2.sdlttf.TTF_Init()
    logging.debug("SDL2 font system initialized")

    window = sdl2.ext.Window("Pokemon Prism", size=(800, 700))
    window.show()

    uiprocessor = sdl2.ext.UIProcessor()
    scene_manager = SceneManager(window)

    #TODO Initialize scenes
    scene_manager.overworld = overworld_scene.make_overworld_scene(scene_manager)

    scene_manager.set_scene_to_current(scene_manager.overworld)
    scene_manager.spriterenderer.render(scene_manager.current_scene.renderables())

    asyncio.run(game_loop(scene_manager, uiprocessor, window))

target_fps = contextvars.ContextVar('target_fps', default=60)

async def game_loop(scene_manager: SceneManager, uiprocessor: sdl2.ext.UIProcessor, window: sdl2.ext.Window):
    running = True
    while running:
        start = time.monotonic()
        scene_manager.current_scene.triggered_event = False
        events = sdl2.ext.get_events()
        for event in events:
            if event.type == sdl2.SDL_QUIT:
                running = False
            else:
                if event.type == sdl2.SDL_KEYDOWN:
                    scene_manager.dispatch_key_press_event(event.key.keysym.sym)
                if event.type == sdl2.SDL_KEYUP:
                    scene_manager.dispatch_key_release_event(event.key.keysym.sym)
        if scene_manager.current_scene == scene_manager.overworld:
            scene_manager.current_scene.check_for_player_movement()
                            
        scene_manager.spriterenderer.render(scene_manager.current_scene.renderables())
        window.refresh()
        done = time.monotonic()
        elapsed_time = start - done
        scene_manager.frame_count += 1
        if scene_manager.frame_count > 60:
            scene_manager.frame_count = 0
        sleep_duration = max((1.0/ target_fps.get()) - elapsed_time, 0)
        await asyncio.sleep(sleep_duration)
    logging.debug("Broke game loop!")

main()