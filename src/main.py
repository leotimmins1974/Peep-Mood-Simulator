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

from pathlib import Path
import math

import moderngl
import numpy as np
import pygame

import assets.obj as obj

import render.graphics as graphics

import tools.config as config
import tools.results as results

import simulation.simulation as sim

# Grab configs
SIMULATION_CONFIG_PATH = "./simulation.config" # using path now. had an issue with using str
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
BACKGROUND_CLEAR = tuple(channel / 255.0 for channel in BACKGROUND_RGB) # morderngl takes each rgb chanel as a 0.0->1.0 so instead of changing config ill just live with this
GLOBAL_LUMEN = 0.3
TICKRATE = int(configuration["tickrate"])
PEEP_MOVE_SPEED = float(configuration["peep_move_speed"])
SHADERS_FOLDER_PATH = Path("./shaders")

# Init PyGame and ModernGL
pygame.init()
pygame.display.set_caption("3D Peep Simulation")
window = pygame.display.set_mode((graphics.WIDTH, graphics.HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF)
ctx = moderngl.create_context()
ctx.enable(moderngl.DEPTH_TEST)
clock = pygame.time.Clock()

# Read shaders and returns content as a str. technicaly not a shader specific function but 
# i cant be bothered to port over all the other loading stuff to this. 
def load_shader_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")

# Transpose it now as moderngl requires it in column-major which is stupid, had this same issue with glam
# It also expects it as bytes obviously - this would be alot easier in rust. numpy is a real pain.
def matrix_bytes(matrix) -> bytes:
    return np.asarray(matrix, dtype="f4").T.tobytes()

# Creates the vertex buffer (VBO -> Vertex Buffer Objects) for the gpu
# also creates the VAO -> Vertex Array Object. basicly telling the gpu which shaders to apply.
# in this case the vetrex & fragment shader. annoyingly I cant really make this a method
# of mesh due to technical debt + im tired.
def upload_mesh(program, mesh):
    mesh.vbo = ctx.buffer(mesh.vertex_data.tobytes())
    mesh.vao = ctx.simple_vertex_array(program, mesh.vbo, "in_position")
    return mesh

# ENTRY POINT
def main() -> exit_code:
    # Load shaders as a program
    program = ctx.program(
        vertex_shader=load_shader_source(SHADERS_FOLDER_PATH / "vertex.glsl"),
        fragment_shader=load_shader_source(SHADERS_FOLDER_PATH / "fragment.glsl"),
    )

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
    ) # Looks at orgin
    camera.fov = CAMERA_FOV
    camera.update_projection()

    # Temporarily getting rid of lights. ill sort out a lighting pipeline once gl works. too many issues.

    test_peep = obj.load(MESHES_FOLDER_PATH + "peep.obj")
    test_peep_manager = sim.Peep(test_peep)
    test_peep.color = (255, 0, 0)
    test_peep_manager.move_speed = PEEP_MOVE_SPEED
    test_peep_manager.move_to((5, -0.5, 0))
    test_peep_manager.move_to((0, -0.5, -8))
    test_peep_manager.move_to((3, -0.5, -8))
    test_peep_manager.move_to((5, -0.5, -5))
    test_peep_manager.move_to((3, -0.5, 8))

    # Before adding to the render order, we must assingn the program and vertex data with upload_mesh
    render_order = [
        upload_mesh(program, test_peep),
        upload_mesh(program, church),
        upload_mesh(program, floor_mesh),
        upload_mesh(program, kfc),
    ]

    # Uploads our projection matrix to the gpu
    # Again: I should be doing this in the .update_projection() method 
    # but the technical debt makes it challenging
    program["projection"].write(matrix_bytes(camera.projection))
    
    peep_tick_order = [test_peep_manager]
    next_tick = pygame.time.get_ticks() + TICKRATE  # TIME OF FIRST TICK

    close = False
    while not close:
        # EVENT LOOP
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close = True

        # SIMULATION TICK. ticks every TICKRATE (ms)
        if pygame.time.get_ticks() >= next_tick:
            for p in peep_tick_order:
                p.tick()
            next_tick = pygame.time.get_ticks() + TICKRATE

            # Camera orbit
            camera_rotation += CAMERA_ROTATION_SPEED
            camera.transform.translate = np.array(
                [
                    CAMERA_XZ_DISTANCE * math.cos(camera_rotation),
                    CAMERA_Y_DISTANCE,
                    CAMERA_XZ_DISTANCE * math.sin(camera_rotation),
                ]
            )
            camera.look_at([0, 0, 0])
            program["view"].write(matrix_bytes(camera.view))

        test_peep.transform.rotate[1] += 0.0001
        test_peep.transform.update_model()

        # RENDER LOOP - MODERNGL
        ctx.clear(*BACKGROUND_CLEAR)
        
        for mesh in render_order:
            program["model"].write(matrix_bytes(mesh.transform.model))
            program["color"].value = tuple(channel / 255.0 for channel in mesh.color[:3])
            mesh.vao.render(moderngl.TRIANGLES)

        # Cant use fonts anymore so im just gonna have to do it in the title
        pygame.display.set_caption(
            f"3D Peep Simulation | fps: {int(clock.get_fps())} | objects: {len(render_order)}"
        )
        clock.tick(TARGET_FPS)
        pygame.display.flip()

    for mesh in render_order:
        mesh.vao.release()
        mesh.vbo.release()
    program.release()
    pygame.quit()
    return 0

exit_code = main()

print(f"terminated with exit code: {exit_code}")

match exit_code:
    case 0:
        print("-- SUCCESS --")
    case _:
        print("-- FAIL --")
        print("read exit_report.txt")
