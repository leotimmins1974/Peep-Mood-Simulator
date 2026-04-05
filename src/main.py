#
# Student Name: Leo Timmins
# Student ID  : 23559213
#
# main.py - simulation of emotions as peeple moev through a world
#         - entry point for project
#
# Version information:
#    - 2026-03-30 - inital version supplied
#    - CHECK GIT HISTORY FOR VERSIONS
#
# Usage:
#   run "venv venv"
#   run "venv/bin/activate" on arch. might be differnent on ubuntu
#   run "pip install -r requirements.txt"
#   run "python3 src/main.py"

import pygame
import pygame.surfarray as surfarray
import numpy as np
import math as math

import assets.obj as obj

import render.graphics as graphics

import tools.config as config
import tools.results as results

import simulation.simulation as sim

# Grab configs
SIMULATION_CONFIG_PATH = "./simulation.config"
configuration = config.parse_config(SIMULATION_CONFIG_PATH)

# Apply config
CAMERA_ROTATION_SPEED = float(configuration["camera_rotation_speed"])
CAMERA_XZ_DISTANCE = float(configuration["camera_xz_distance"])
CAMERA_Y_DISTANCE = float(configuration["camera_y_distance"])
CAMERA_FOV = float(configuration["camera_fov"])
MESHES_FOLDER_PATH = configuration["meshes_folder_path"]
TARGET_FPS = int(configuration["target_fps"])
THREAD_USAGE = int(configuration["thread_usage"])
B_RRGGBB = configuration["background_rgb"]
BACKGROUND_RGB = (int(B_RRGGBB[0:3]), int(B_RRGGBB[4:6]), int(B_RRGGBB[7:]))
GLOBAL_LUMEN = 0.3
TICKRATE = int(configuration["tickrate"])
PEEP_MOVE_SPEED = float(configuration["peep_move_speed"])

# Window/Buffer manager
pygame.init()
pygame.display.set_caption("3D Peep Simulation")
window = pygame.display.set_mode((graphics.WIDTH, graphics.HEIGHT))
clock = pygame.time.Clock()


# ENTRY POINT
def main() -> exit_code:

    # Load assets
    floor_mesh = obj.load(MESHES_FOLDER_PATH + "floor.obj")
    floor_mesh.transform.scale = [4.0, 4.0, 4.0]
    floor_mesh.transform.translate = [0.0, -1.0, 0.0]
    floor_mesh.transform.update_model()

    church = obj.load(MESHES_FOLDER_PATH + "church.obj")
    church.color = (242, 245, 66)  # Yellow
    church.transform.translate = [-6, 0, -7]
    church.transform.rotate = (0, -1, 0)
    church.transform.update_model()

    kfc = obj.load(MESHES_FOLDER_PATH + "kfc.obj")
    kfc.color = (242, 50, 66)  # Red for KFC
    kfc.transform.translate = [5.2, 2.5, 6]
    kfc.transform.scale = [3.0, 3.0, 3.0]
    kfc.transform.rotate = (0, 4.7, 0)
    kfc.transform.update_model()

    camera_rotation = 0
    camera = graphics.Camera()
    camera.transform.translate = np.array(
        [
            CAMERA_XZ_DISTANCE * math.cos(camera_rotation),
            CAMERA_Y_DISTANCE,
            CAMERA_XZ_DISTANCE * math.sin(camera_rotation),
        ]
    )
    camera.look_at(
        np.array([0.0, 0.0, 0.0])
    )  # Looks at orgin no matter the translation
    camera.fov = CAMERA_FOV
    camera.update_projection()

    cam_light = graphics.Light(
        np.array([-1.0, 0.0, 0.0]), np.array([0.0, 0.0, 0.0]), 0.3
    )
    top_light = graphics.Light(
        np.array([0.0, -1.0, 0.0]), np.array([0.0, 5.0, 0.0]), 0.1
    )

    test_peep = obj.load(MESHES_FOLDER_PATH + "peep.obj")
    test_peep_manager = sim.Peep(
        test_peep
    )  # Not sure how refrences work in python, im assuming this passes ref and not val?
    test_peep.color = (255, 0, 0)
    test_peep_manager.move_speed = PEEP_MOVE_SPEED
    test_peep_manager.move_to((5, -0.5, 0))
    test_peep_manager.move_to((0, -0.5, -8))
    test_peep_manager.move_to((3, -0.5, -8))
    test_peep_manager.move_to((5, -0.5, -5))
    test_peep_manager.move_to((3, -0.5, 8))

    render_order = [test_peep, church, floor_mesh, kfc]
    light_order = [cam_light, top_light]
    peep_tick_order = [test_peep_manager]

    # pygame.time.get_ticks -> time since init()
    next_tick = pygame.time.get_ticks() + TICKRATE  # TIME OF FIRST TICK

    close = False
    while not close:
        # EVENT LOOP
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close = True
        # Buffer setup
        #window.fill(BACKGROUND_RGB)
        # TICK LOGIC
        ## ticks ever TICKRATE (ms) and doesnt tick on start
        if pygame.time.get_ticks() >= next_tick:
            # print("TICK !")
            for p in peep_tick_order:
                p.tick()
            next_tick = pygame.time.get_ticks() + TICKRATE

            # camera move
            camera_rotation += CAMERA_ROTATION_SPEED
            camera.transform.translate = np.array(
                [
                    CAMERA_XZ_DISTANCE * math.cos(camera_rotation),
                    CAMERA_Y_DISTANCE,
                    CAMERA_XZ_DISTANCE * math.sin(camera_rotation),
                ]
            )
            camera.look_at([0, 0, 0])
            camera.update_view()

        # SIM LOGIC

        test_peep.transform.rotate[1] += 0.0001
        test_peep.transform.update_model()

        # Draw Faces - SWAPPED PAINTERS ALGO FOR a Z BUFFER - This will likely obliterate preformance. will need to multithread and sort out some mutex type system
        rgb_buffer = [BACKGROUND_RGB] * (graphics.WIDTH * graphics.HEIGHT)
        depth_buffer = [camera.far + 1] * (graphics.WIDTH * graphics.HEIGHT)
        view_proj = camera.projection @ camera.view
        for mesh in render_order:
            view_model = camera.view @ mesh.transform.model
            view_proj_model = view_proj @ mesh.transform.model
            for face in mesh.faces:
                if len(face.indicies) != 3:
                    print("IRREGULAR FACE (SKIP, NO PANIC)")
                    print("Did you forget to triangulate the mesh before export")
                    print(face.indicies)
                    continue

                # Get relevent Verticies
                v = (
                    mesh.verticies[face.indicies[0]],
                    mesh.verticies[face.indicies[1]],
                    mesh.verticies[face.indicies[2]],
                )

                # Calc normals
                v0_world = mesh.transform.model @ np.array(
                    [v[0].pos[0], v[0].pos[1], v[0].pos[2], 1.0]
                )
                v1_world = mesh.transform.model @ np.array(
                    [v[1].pos[0], v[1].pos[1], v[1].pos[2], 1.0]
                )
                v2_world = mesh.transform.model @ np.array(
                    [v[2].pos[0], v[2].pos[1], v[2].pos[2], 1.0]
                )

                edge1 = v1_world[:3] - v0_world[:3]
                edge2 = v2_world[:3] - v0_world[:3]

                normal = np.cross(edge1, edge2)
                normal /= np.linalg.norm(normal)  # Normalise
                face_center = (v0_world[:3] + v1_world[:3] + v2_world[:3]) / 3

                view_dir = camera.transform.translate - face_center
                view_dir /= np.linalg.norm(view_dir)

                # Cull
                if np.dot(normal, view_dir) <= 0:
                    continue

                total_intensity = GLOBAL_LUMEN
                for light in light_order:
                    light_dir = light.direction - light.position
                    light_dir /= np.linalg.norm(light_dir)  # Normalise
                    total_intensity += max(0, np.dot(normal, -light_dir)) * light.lumens

                # Draw polygons
                v_view = (
                    view_model @ np.append(v[0].pos, 1.0),
                    view_model @ np.append(v[1].pos, 1.0),
                    view_model @ np.append(v[2].pos, 1.0),
                )
                v = [
                    view_proj_model @ np.append(v[0].pos, 1.0),
                    view_proj_model @ np.append(v[1].pos, 1.0),
                    view_proj_model @ np.append(v[2].pos, 1.0),
                ]
                if any(vertex[3] <= 0 for vertex in v):
                    continue

                v[0] = (
                    v[0][0] / v[0][3],
                    v[0][1] / v[0][3],
                    v[0][2] / v[0][3],
                )  # FIX PERSPECTIVE WARP???
                v[1] = (
                    v[1][0] / v[1][3], 
                    v[1][1] / v[1][3], 
                    v[1][2] / v[1][3],
                )
                v[2] = (
                    v[2][0] / v[2][3],
                    v[2][1] / v[2][3],
                    v[2][2] / v[2][3],
                )  # Z was previously ignored and i think needed for the buffer? not completely sure

                p = (
                    graphics.to_screen_space(
                        v[0], camera.resolution[0], camera.resolution[1]
                    ),
                    graphics.to_screen_space(
                        v[1], camera.resolution[0], camera.resolution[1]
                    ),
                    graphics.to_screen_space(
                        v[2], camera.resolution[0], camera.resolution[1]
                    ),
                )

                # Now for z-depth-buffer I need to iterate over each pixel
                # Had to change to add screen bounds so i dont render off screen pixels
                tri_bounds = (
                    max(0, min(p[0][0], p[1][0], p[2][0])),
                    min(graphics.WIDTH - 1, max(p[0][0], p[1][0], p[2][0])),
                    max(0, min(p[0][1], p[1][1], p[2][1])),
                    min(graphics.HEIGHT - 1, max(p[0][1], p[1][1], p[2][1])),
                )  # x min max, y min max

                # print(tri_bounds)
                # Edge Function Formula
                # this was so stupid - painters worked well enough
                
                area = edge(p[0], p[1], p[2])
                if area == 0:
                    continue

                inj_width = tri_bounds[1] - tri_bounds[0] + 1
                inj_height = tri_bounds[3] - tri_bounds[2] + 1
                
                # Prev shading logic from painters
                shaded_color = np.array(mesh.color[:3], dtype=float) * total_intensity
                shaded_color = np.clip(shaded_color, 0, 255).astype(int)

                for i in range(inj_width * inj_height):
                    local_pixel = index_to_buffer_xy(i, inj_width, inj_height)
                    pixel = (
                        tri_bounds[0] + local_pixel[0],
                        tri_bounds[2] + local_pixel[1],
                    )
                    e0 = edge(p[1], p[2], pixel)
                    e1 = edge(p[2], p[0], pixel)
                    e2 = edge(p[0], p[1], pixel)
                    inside = (
                        (e0 >= 0 and e1 >= 0 and e2 >= 0)
                        or (e0 <= 0 and e1 <= 0 and e2 <= 0)
                    )
                    if not inside:
                        continue

                    # calc relevent color and depth for the buffer # since not adding textures yet / ever? i could probably get awaty with just a depth buffer
                    # barycentric weighting: depth will be based on distance (En) from vertex (Vn)
                    w0 = e0 / area
                    w1 = e1 / area
                    w2 = e2 / area
                    p_depth = w0 * v[0][2] + w1 * v[1][2] + w2 * v[2][2]
                    conv_big_index = xy_to_buffer_index(pixel, graphics.WIDTH, graphics.HEIGHT)
                    prev_p_depth = depth_buffer[conv_big_index]
                    if p_depth < prev_p_depth:
                        rgb_buffer[conv_big_index] = shaded_color
                        depth_buffer[conv_big_index] = p_depth

                # Depreciated - painters algo
                # shaded_color = np.array(mesh.color[:3], dtype=float) * total_intensity
                # shaded_color = np.clip(shaded_color, 0, 255).astype(int)
                # depth = (v_view[0][2] + v_view[1][2] + v_view[2][2]) / 3.0
                # triangles_to_draw.append((depth, shaded_color, p))

        # Continuation of z-depth
        ## draw the buffer using a surface
        buffer = np.array(rgb_buffer, dtype=np.uint8).reshape(
            (graphics.HEIGHT, graphics.WIDTH, 3)
        ).swapaxes(0, 1) # Row-major buffer needs axes swapped for surfarray
        blit_surf = pygame.Surface((graphics.WIDTH, graphics.HEIGHT))
        surfarray.blit_array(blit_surf, buffer)
        window.blit(blit_surf, (0,0))

        # Text at top of screen
        render_text(
            "fps: " + str(int(clock.get_fps())), (255, 255, 255), (5, 5), size=18
        )  # FPS counter
        render_text(
            f"| Peep Mood Simulator | Leo Timmins | Student ID: 2559213 | COMP1005 | Simulation is in progress",
            (255, 255, 255),
            (70, 5),
            size=18,
        )  # Sim title
        render_text(
            f"Engine Info | target_fps: {TARGET_FPS} | tickrate: {TICKRATE} ms | threads: {THREAD_USAGE} | RenObj: {len(render_order)} | Lights: {len(light_order)} | ",
            (255, 255, 255),
            (5, 32),
            size=13,
        )  # Sim title

        # Draw Points
        # for mesh in render_order:
        #    for v in mesh.verticies:
        #        clip_coordinates = camera.projection @ camera.view @ mesh.transform.model @ np.array([v.pos[0], v.pos[1], v.pos[2], 1.])
        #        if clip_coordinates[3] != 0:
        #            window.set_at(graphics.to_screen_space(clip_coordinates, camera.resolution[0], camera.resolution[1]), (255,255,255))

        clock.tick(TARGET_FPS)
        pygame.display.update()

    pygame.quit()
    return 0


# Helper function for rendering text with screen space coordinates
# Will eventualy maybe have an option for world coordinates with rotation
def render_text(
    string, rgb, xy, size=30, font_src="./assets/fonts/roboto_slab/RobotoSlab-Light.ttf"
):
    font = pygame.font.Font(font_src, size)
    text = font.render(string, 1, pygame.Color(rgb))
    window.blit(text, xy)

# e > 0: Left of AB | e < 0: Right of AB
def edge(a, b, p):
    return (p[0] - a[0]) * (b[1] - a[1]) - (p[1] - a[1]) * (b[0] - a[0])

# Given index for a buffer, and its dimentions, return xy pos
def index_to_buffer_xy(index, b_width, b_height):
    rows = index // b_width
    index -= b_width * rows
    return (index, rows) # Should be xy of a buffer

# inverse of index_to_buffer_xy()
def xy_to_buffer_index(xy, b_width, b_height):
    return (xy[1] * b_width) + xy[0] # Should be index for a buffer

exit_code = main()

print(f"terminated with exit code: {exit_code}")

match exit_code:
    case 0:
        print("-- SUCCESS --")
    case _:
        print("-- FAIL --")
        print("read exit_report.txt")
