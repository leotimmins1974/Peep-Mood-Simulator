import pygame
import numpy as np

import assets.obj as obj

import render.math as math
import render.graphics as graphics

import tools.config as config
import tools.results as results

MESHES_FOLDER_PATH = "./meshes/"
SIMULATION_CONFIG_PATH = "./simulation.config"
TARGET_FPS = 60
BACKGROUND_RGB = (15,15,30)

# ENTRY POINT
def main() -> exit_code:

    # Grab configs
    configuration = config.parse_config(SIMULATION_CONFIG_PATH)

    # TEST CUBE
    cube_mesh = obj.load(MESHES_FOLDER_PATH + "cube.obj")
    cube_mesh.transform.translate[0] = -3

    camera = graphics.Camera()

    render_order = [cube_mesh]

    # Window/Buffer manager 
    pygame.init()
    pygame.display.set_caption("3D Peep Simulation")

    window = pygame.display.set_mode((graphics.WIDTH, graphics.HEIGHT))

    close = False
    while not close:
        # EVENT LOOP
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close = True

        window.fill(BACKGROUND_RGB)
        # SIM LOGIC
        cube_mesh.transform.rotate[0] += 0.01
        cube_mesh.transform.rotate[1] += 0.01
        cube_mesh.transform.rotate[2] += 0.01
        cube_mesh.transform.update_model()
        #cube_mesh.transform.translate[0] -= 1
        # DRAW
        for mesh in render_order:
            for v in mesh.verticies:
                clip_coordinates = camera.projection @ camera.view @ mesh.transform.model @ np.array([v.pos[0], v.pos[1], v.pos[2], 1.])
                if clip_coordinates[3] != 0:
                    window.set_at(graphics.to_screen_space(clip_coordinates, camera.resolution[0], camera.resolution[1]), (255,255,255))

        pygame.time.delay(TARGET_FPS)
        pygame.display.update()

    pygame.quit()
    return(0)


exit_code = main()

print(f"terminated with exit code: {exit_code}")

match exit_code:
    case 0: 
        print("-- SUCCESS --")
    case _:
        print("-- FAIL --")
        print("read exit_report.txt")