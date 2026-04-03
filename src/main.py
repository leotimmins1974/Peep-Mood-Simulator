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

    # Load assets
    floor_mesh = obj.load(MESHES_FOLDER_PATH + "floor.obj")
    floor_mesh.transform.scale = [4.,4.,4.]
    floor_mesh.transform.translate = [0.,-1.,0.]
    floor_mesh.transform.update_model()

    church = obj.load(MESHES_FOLDER_PATH + "church.obj")
    church.color = (242,245,66) # Yellow
    church.transform.translate = [-6,1,7]
    church.transform.rotate = (0,1,0)
    church.transform.update_model()

    kfc = obj.load(MESHES_FOLDER_PATH + "kfc.obj")
    kfc.color = (242,50,66) # Red for KFC
    kfc.transform.translate = [5,3.5,6]
    kfc.transform.scale = [3.,3.,3.]
    kfc.transform.rotate = (0,4.7,0)
    kfc.transform.update_model()

    camera = graphics.Camera()
    camera.transform.translate = np.array([14.,6.,0.])
    camera.look_at(np.array([0.,0.,0.]))
    camera.fov = 1.1
    camera.update_projection()

    cam_light = graphics.Light(np.array([-1.,0.,0.]), np.array([0.,0.,0.]), 0.3)
    top_light = graphics.Light(np.array([0.,-1.,0.]), np.array([0.,5.,0.]), 0.1)

    test_peep = obj.load(MESHES_FOLDER_PATH + "peep.obj")
    test_peep.color = (255,0,0)

    render_order = [test_peep,church ,floor_mesh,kfc]
    light_order = [cam_light, top_light]

    # Window/Buffer manager 
    pygame.init()
    pygame.display.set_caption("3D Peep Simulation")

    window = pygame.display.set_mode((graphics.WIDTH, graphics.HEIGHT))
    clock = pygame.time.Clock()

    close = False
    while not close:
        # EVENT LOOP
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close = True

        window.fill(BACKGROUND_RGB)
        # SIM LOGIC
        
        # Draw Faces
        view_proj = camera.projection @ camera.view
        triangles_to_draw = []
        for mesh in render_order:
            view_model = camera.view @ mesh.transform.model
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
                v_view = (
                    view_model @ np.append(v[0].pos, 1.0),
                    view_model @ np.append(v[1].pos, 1.0),
                    view_model @ np.append(v[2].pos, 1.0),
                )
                v = (
                    view_proj_model @ np.append(v[0].pos, 1.0),
                    view_proj_model @ np.append(v[1].pos, 1.0),
                    view_proj_model @ np.append(v[2].pos, 1.0),
                )
                if any(vertex[3] <= 0 for vertex in v):
                    continue

                p = (
                    graphics.to_screen_space(v[0], camera.resolution[0], camera.resolution[1]),
                    graphics.to_screen_space(v[1], camera.resolution[0], camera.resolution[1]),
                    graphics.to_screen_space(v[2], camera.resolution[0], camera.resolution[1]),
                )
                shaded_color = np.array(mesh.color[:3], dtype=float) * total_intensity
                shaded_color = np.clip(shaded_color, 0, 255).astype(int)

                depth = (v_view[0][2] + v_view[1][2] + v_view[2][2]) / 3.0
                triangles_to_draw.append((depth, shaded_color, p))

        triangles_to_draw.sort(key=lambda triangle: triangle[0])
        for _, shaded_color, p in triangles_to_draw:
            pygame.draw.polygon(window, shaded_color, p)

        # Draw Points
        #for mesh in render_order:
        #    for v in mesh.verticies:
        #        clip_coordinates = camera.projection @ camera.view @ mesh.transform.model @ np.array([v.pos[0], v.pos[1], v.pos[2], 1.])
        #        if clip_coordinates[3] != 0:
        #            window.set_at(graphics.to_screen_space(clip_coordinates, camera.resolution[0], camera.resolution[1]), (255,255,255))

        clock.tick(TARGET_FPS)
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
