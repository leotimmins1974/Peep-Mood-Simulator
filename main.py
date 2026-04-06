#
# Student Name: Leo Timmins
# Student ID  : 23559213
#
# main.py - simulation of emotions as peeple moev through a world
#         - entry point for project
#
# Version information:
#    - 2026-04-03 - init
#    - 2026-04-03 - config parsing
#    - 2026-04-03 - load .obj
#    - 2026-04-03 - working point rendering
#    - 2026-04-03 - polygon faces
#    - 2026-04-03 - lighting and shading
#    - 2026-04-03 - peep class and church
#    - 2026-04-03 - kfc
#    - 2026-04-05 - fps counter and info
#    - 2026-04-05 - proper .config support
#    - 2026-04-05 - lerped movement for peeps
#    - 2026-04-05 - camera rotation
#    - 2026-04-05 - reformat + depricate painters
#    - 2026-04-05 - proper z-depth rendering (v. slow)
#    - 2026-04-05 - ported to opengl
#    - 2026-04-05 - shading
#    - 2026-04-05 - project cleanup
#    - 2026-04-06 - events, reporting, refractors, release cleanup
#    - 2026-04-06 - readme update
#    - 2026-04-06 - peeps rotate + misc
#    - 2026-04-06 - color changes
#    - 2026-04-06 - misc
#
# Usage:
#   run "venv venv"
#   run "source venv/bin/activate" on arch. might be differnent on ubuntu
#   run "pip install -r requirements.txt"
#   run "python3 main.py"

from pathlib import Path
import math
import moderngl
import numpy as np
import pygame

import src.obj as obj
import src.graphics as graphics
import src.config as config
import src.results as results
import src.simulation as sim

# Load configuration as a hashmap.
configuration = config.parse_config("./simulation.config")

# Copy config values into Constants.
CAMERA_ROTATION_SPEED = float(configuration["camera_rotation_speed"])
CAMERA_XZ_DISTANCE = float(configuration["camera_xz_distance"])
CAMERA_Y_DISTANCE = float(configuration["camera_y_distance"])
CAMERA_FOV = float(configuration["camera_fov"])
MESHES_FOLDER_PATH = configuration["meshes_folder_path"]
TARGET_FPS = int(configuration["target_fps"])
B_RRGGBB = configuration["background_rgb"]
BACKGROUND_RGB = (int(B_RRGGBB[0:3]), int(B_RRGGBB[3:6]), int(B_RRGGBB[6:]))
BACKGROUND_CLEAR = tuple(
    channel / 255.0 for channel in BACKGROUND_RGB
)  # ModernGL expects each rgb channel in the 0.0 to 1.0 range.
TICKRATE = int(configuration["tickrate"])
PEEP_POPULATION = int(configuration["peep_population"])
SHADERS_FOLDER_PATH = Path("./shaders")


# Set up PyGame and ModernGL context.
pygame.init()
pygame.display.set_caption("3D Peep Simulation")
window = pygame.display.set_mode(
    (graphics.WIDTH, graphics.HEIGHT), pygame.OPENGL | pygame.DOUBLEBUF
)
ctx = moderngl.create_context()
ctx.enable(moderngl.DEPTH_TEST)
clock = pygame.time.Clock()


# Read a shader from path.
def load_shader_source(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# Convert a numpy mat4 into the layout expected by ModernGL.
def matrix_bytes(matrix) -> bytes:
    return np.asarray(matrix, dtype="f4").T.tobytes()


# Upload a mesh to the buffer and bind it to the shaders.
def upload_mesh(program, mesh):
    mesh.vbo = ctx.buffer(mesh.vertex_data.tobytes())
    mesh.vao = ctx.vertex_array(
        program, [(mesh.vbo, "3f 3f", "in_position", "in_normal")]
    )
    return mesh


# Release a mesh's OpenGL buffers.
# Pythons garbage collector does not manage GPU recources.
# This will be called when removing event actors from the render list.
def release_mesh(mesh):
    if hasattr(mesh, "vao"):
        mesh.vao.release()
    if hasattr(mesh, "vbo"):
        mesh.vbo.release()


# Update the active event mesh within the render list.
def sync_event_mesh(program, render_order, active_event_mesh):
    current_event_mesh = None

    # Get current event related mesh.
    if sim.event_actor is not None:
        current_event_mesh = sim.event_actor.mesh

    # Mesh is correct.
    if active_event_mesh is current_event_mesh:
        return active_event_mesh

    # Remove old event mesh.
    if active_event_mesh is not None:
        if active_event_mesh in render_order:
            render_order.remove(active_event_mesh)
        release_mesh(active_event_mesh)

    # Add event mesh to render list.
    if current_event_mesh is not None:
        render_order.append(upload_mesh(program, current_event_mesh))

    return current_event_mesh


# Event countdown text for the window title.
def event_timer_text():
    if sim.current_event == sim.EVENT_NONE:
        ticks_left = sim.event_roll_ticks
        seconds_left = (ticks_left * TICKRATE) / 1000.0
        return f"next chance: {seconds_left:.1f}s"
    else:
        ticks_left = sim.event_ticks_left
        seconds_left = (ticks_left * TICKRATE) / 1000.0
        return f"event ends: {seconds_left:.1f}s"


# Apply event-based colours to the world meshes.
def update_world_colors(church, kfc):
    church.color = sim.DEFAULT_CHURCH_COLOR
    kfc.color = sim.DEFAULT_KFC_COLOR

    if sim.current_event == sim.EVENT_DEVIL_RISEN:
        church.color = sim.DEVIL_CHURCH_COLOR
    elif sim.current_event == sim.EVENT_CHURCH_CLOSED:
        church.color = sim.CLOSED_BUILDING_COLOR
    elif sim.current_event == sim.EVENT_KFC_CLOSED:
        kfc.color = sim.CLOSED_BUILDING_COLOR


# Entry Point for the program.
def main():
    render_order = []
    peeps = []
    active_event_mesh = None

    # Compile the shader program.
    program = ctx.program(
        vertex_shader=load_shader_source(SHADERS_FOLDER_PATH / "vertex.glsl"),
        fragment_shader=load_shader_source(SHADERS_FOLDER_PATH / "fragment.glsl"),
    )

    # Load scene meshes.
    floor_mesh = obj.load(MESHES_FOLDER_PATH + "floor.obj")
    floor_mesh.transform.scale = [4.0, 4.0, 4.0]
    floor_mesh.transform.translate = [0.0, -1.0, 0.0]
    floor_mesh.transform.update_model()
    floor_mesh.color = (255, 255, 255)

    church = obj.load(MESHES_FOLDER_PATH + "church.obj")
    church.color = (242, 245, 66)
    church.transform.translate = [-6, 0, -7]
    church.transform.rotate = (0, -1, 0)
    church.transform.update_model()

    kfc = obj.load(MESHES_FOLDER_PATH + "kfc.obj")
    kfc.color = (242, 50, 66)
    kfc.transform.translate = [0, 2.5, 6]
    kfc.transform.scale = [3.0, 3.0, 3.0]
    kfc.transform.rotate = (0, 4.7, 0)
    kfc.transform.update_model()

    # Allows Peeps to find the locations.
    sim.configure_world(
        church_position=church.transform.translate, kfc_position=kfc.transform.translate
    )
    update_world_colors(church, kfc)

    # Initialise the Camera.
    camera_rotation = 0
    camera = graphics.Camera()
    camera.transform.translate = np.array(
        [
            CAMERA_XZ_DISTANCE * math.cos(camera_rotation),
            CAMERA_Y_DISTANCE,
            CAMERA_XZ_DISTANCE * math.sin(camera_rotation),
        ]
    )
    camera.look_at(np.array([0.0, 0.0, 0.0]))
    camera.fov = CAMERA_FOV
    camera.update_projection()

    # Upload the default meshes first and add to render list.
    render_order = [
        upload_mesh(program, church),
        upload_mesh(program, floor_mesh),
        upload_mesh(program, kfc),
    ]

    # Spawn peeps into the simulation and add to the render list.
    for _ in range(PEEP_POPULATION):
        peep = sim.Peep()
        peeps.append(peep)
        render_order.append(upload_mesh(program, peep.mesh))

    # Results tracking initilisation.
    tracker = results.SessionTracker(configuration, TICKRATE)

    # Upload the initial camera matrices to the GPU.
    program["projection"].write(matrix_bytes(camera.projection))
    program["view"].write(matrix_bytes(camera.view))

    # Offset the first tick.
    next_tick = pygame.time.get_ticks() + TICKRATE

    close = False
    while not close:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                close = True

        # Simulation ticking.
        if pygame.time.get_ticks() >= next_tick:
            sim.tick_events()

            # Peep ticking.
            for peep in peeps:
                peep.tick()

            # Event syncing.
            active_event_mesh = sync_event_mesh(
                program, render_order, active_event_mesh
            )
            update_world_colors(church, kfc)

            # Report tracking.
            tracker.record_tick(
                peeps,
                sim.current_event,
                sim.average_happiness(),
            )

            # Offset next tick.
            next_tick = pygame.time.get_ticks() + TICKRATE

            # Orbit the camera around the scene.
            camera_rotation += CAMERA_ROTATION_SPEED
            camera.transform.translate = np.array(
                [
                    CAMERA_XZ_DISTANCE * math.cos(camera_rotation),
                    CAMERA_Y_DISTANCE,
                    CAMERA_XZ_DISTANCE * math.sin(camera_rotation),
                ]
            )
            camera.look_at([0, 0, 0])

            # Update the GPUs view matrix.
            program["view"].write(matrix_bytes(camera.view))

        # Render the frame.
        ctx.clear(*BACKGROUND_CLEAR)

        # Update the GPUs mesh model matrix colors and then render.
        for mesh in render_order:
            program["model"].write(matrix_bytes(mesh.transform.model))
            program["color"].value = tuple(
                channel / 255.0 for channel in mesh.color[:3]
            )
            mesh.vao.render(moderngl.TRIANGLES)

        # Runtime stats in the window title.
        pygame.display.set_caption(
            f"3D Peep Simulation"
            + f" | fps: {int(clock.get_fps())}"
            + f" | avg happiness: {sim.average_happiness():.1f}"
            + f" | event: {sim.current_event}"
            + f" | {event_timer_text()}"
        )

        clock.tick(TARGET_FPS)
        pygame.display.flip()

    tracker.write_results(peeps)

    # Free the meshes from VRAM
    if program is not None:
        active_event_mesh = sync_event_mesh(program, render_order, active_event_mesh)
    for mesh in render_order:
        release_mesh(mesh)
    if program is not None:
        program.release()

    pygame.quit()


main()
