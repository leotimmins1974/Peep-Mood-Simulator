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
GLOBAL_LUMEN = 0.3

# ENTRY POINT
def main() -> exit_code:

    # Grab configs
    configuration = config.parse_config(SIMULATION_CONFIG_PATH)

    # TEST CUBE
    cube_mesh = obj.load(MESHES_FOLDER_PATH + "cube.obj")
    cube_mesh.transform.translate[0] = -3

    cam_light = graphics.Light(np.array([-1.,0.,0.]), np.array([0.,0.,0.]), 0.3)

    camera = graphics.Camera()

    render_order = [cube_mesh]
    light_order = [cam_light]

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
        
        # Draw Faces
        view_proj = camera.projection @ camera.view
        for mesh in render_order:
            view_proj_model = view_proj @ mesh.transform.model
            for face in mesh.faces:
                if len(face.indicies) !=3 :
                    print("IRREGULAR FACE (SKIP, NO PANIC)")
                    print(face.indicies)
                    continue


                # Get relevent Vertex
                v = (mesh.verticies[face.indicies[0]], mesh.verticies[face.indicies[1]], mesh.verticies[face.indicies[2]])
                
                # Calc normals
                v0_world = mesh.transform.model @ np.array([v[0].pos[0], v[0].pos[1], v[0].pos[2], 1.])
                v1_world = mesh.transform.model @ np.array([v[1].pos[0], v[1].pos[1], v[1].pos[2], 1.])
                v2_world = mesh.transform.model @ np.array([v[2].pos[0], v[2].pos[1], v[2].pos[2], 1.])
                
                edge1 = v1_world[:3] - v0_world[:3]
                edge2 = v2_world[:3] - v0_world[:3]
                
                normal = np.cross(edge1, edge2)
                normal /= np.linalg.norm(normal) #Normalise
                face_center = (v0_world[:3] + v1_world[:3] + v2_world[:3]) / 3
                
                view_dir = camera.transform.translate - face_center
                view_dir /= np.linalg.norm(view_dir)

                # Cull
                if np.dot(normal, view_dir) <= 0:
                    continue

                total_intensity = GLOBAL_LUMEN
                for light in light_order:
                    light_dir = light.direction - light.position
                    light_dir /= np.linalg.norm(light_dir) #Normalise
                    total_intensity += max(0, np.dot(normal, -light_dir)) * light.lumens

                # Draw polygons
                v = (
                    view_proj_model @ np.append(v[0].pos, 1.0),
                    view_proj_model @ np.append(v[1].pos, 1.0),
                    view_proj_model @ np.append(v[2].pos, 1.0),
                )
                #if v[0][3] < 0 or v[1][3] < 0 or v[2][3] < 0:
                #    continue

                p = (
                    graphics.to_screen_space(v[0], camera.resolution[0], camera.resolution[1]),
                    graphics.to_screen_space(v[1], camera.resolution[0], camera.resolution[1]),
                    graphics.to_screen_space(v[2], camera.resolution[0], camera.resolution[1]),
                )
                shaded_color = np.array(mesh.color[:3], dtype=float) * total_intensity
                shaded_color = np.clip(shaded_color, 0, 255).astype(int)
                pygame.draw.polygon(window, shaded_color, p)

        # Draw Points
        #for mesh in render_order:
        #    for v in mesh.verticies:
        #        clip_coordinates = camera.projection @ camera.view @ mesh.transform.model @ np.array([v.pos[0], v.pos[1], v.pos[2], 1.])
        #        if clip_coordinates[3] != 0:
        #            window.set_at(graphics.to_screen_space(clip_coordinates, camera.resolution[0], camera.resolution[1]), (255,255,255))

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