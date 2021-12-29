import logging
import asyncio
import contextvars
import time
import sdl2
import sdl2.ext
import sdl2.sdlttf
from prism.menu_scene import MenuScene
from prism.scene_manager import SceneManager
from prism import dialogue_scene, overworld_scene, menu_scene, battle_scene


def main():
    """Main game entry point"""

    logging.basicConfig(
        level=logging.DEBUG,
        format="%(levelname)s:%(relativeCreated)d:%(module)s:%(message)s")
    logging.getLogger("PIL").setLevel(69)  # turn off PIL logging

    sdl2.ext.init()
    logging.debug("SDL2 video system initialized")
    sdl2.sdlttf.TTF_Init()
    logging.debug("SDL2 font system initialized")

    window = sdl2.ext.Window("Pokemon Prism", size=(800, 700))
    window.show()

    uiprocessor = sdl2.ext.UIProcessor()
    scene_manager = SceneManager(window)

    #TODO Initialize scenes
    scene_manager.overworld = overworld_scene.make_overworld_scene(
        scene_manager)
    scene_manager.dialogue = dialogue_scene.make_dialogue_scene(scene_manager)
    scene_manager.menu = menu_scene.make_menu_scene(scene_manager)
    scene_manager.battle = battle_scene.make_battle_scene(scene_manager)
    
    scene_manager.set_scene_to_active(scene_manager.battle)
    scene_manager.spriterenderer.render(
        scene_manager.current_scene.renderables())

    asyncio.run(game_loop(scene_manager, uiprocessor, window))


target_fps = contextvars.ContextVar('target_fps', default=60)


async def game_loop(scene_manager: SceneManager,
                    uiprocessor: sdl2.ext.UIProcessor,
                    window: sdl2.ext.Window):
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
                    scene_manager.dispatch_key_press_event(
                        event.key.keysym.sym)
                if event.type == sdl2.SDL_KEYUP:
                    scene_manager.dispatch_key_release_event(
                        event.key.keysym.sym)
        if scene_manager.current_scene == scene_manager.dialogue:
            if scene_manager.current_scene.printing_dialogue and scene_manager.frame_count % scene_manager.current_scene.dialogue_speed == 0 and scene_manager.current_scene.not_waiting():
                scene_manager.current_scene.full_render()                        
        elif scene_manager.current_scene == scene_manager.overworld:
            scene_manager.current_scene.check_for_player_movement()
            scene_manager.current_scene.check_for_actor_movement()
            scene_manager.current_scene.full_render()
        elif scene_manager.current_scene == scene_manager.battle:
            if scene_manager.current_scene.enemy_ticking_health or scene_manager.current_scene.player_ticking_health:
                p_poke = scene_manager.current_scene.player_pokemon
                e_poke = scene_manager.current_scene.enemy_pokemon
                if p_poke.display_hp > p_poke.current_hp:
                    p_poke.display_hp -= 1
                elif p_poke.display_hp < p_poke.current_hp:
                    p_poke.display_hp += 1
                
                if e_poke.display_hp > e_poke.current_hp:
                    e_poke.display_hp -= 1
                elif e_poke.display_hp < e_poke.current_hp:
                    e_poke.display_hp += 1

                if e_poke.current_hp == e_poke.display_hp:
                    scene_manager.current_scene.enemy_ticking_health = False
                if p_poke.current_hp == p_poke.display_hp:
                    scene_manager.current_scene.player_ticking_health = False
                
                scene_manager.current_scene.render_player_pokemon_info_region()
                scene_manager.current_scene.render_enemy_pokemon_info_region()
                if scene_manager.current_scene.enemy_ticking_health == False and scene_manager.current_scene.player_ticking_health == False:
                    scene_manager.current_scene.render_battle_regions()
            if scene_manager.current_scene.printing and scene_manager.current_scene.message_queue:
                scene_manager.current_scene.render_battle_info_region()
            elif scene_manager.current_scene.executing_turn:
                scene_manager.current_scene.execution_loop()
            
        scene_manager.spriterenderer.render(
            scene_manager.renderables())
        window.refresh()
        done = time.monotonic()
        elapsed_time = start - done
        
        scene_manager.frame_count += 1
        if scene_manager.frame_count > 60:
            scene_manager.frame_count = 0
        sleep_duration = max((1.0 / target_fps.get()) - elapsed_time, 0)
        await asyncio.sleep(sleep_duration)
    logging.debug("Broke game loop!")


main()