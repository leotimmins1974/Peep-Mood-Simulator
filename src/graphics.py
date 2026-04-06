# Graphics data structures.

import numpy as np
import math as mth

WIDTH, HEIGHT = (1200, 800)


# Stores model transfroms and crafts the model matrix.
class Transform:
    # Default transform.
    def __init__(self):
        self.translate = [0.0, 0.0, 0.0]
        self.rotate = [0.0, 0.0, 0.0]  # Radians.
        self.scale = [1.0, 1.0, 1.0]
        self.update_model()

    # Build the model matrix from translate, rotate, and scale.
    def update_model(self):
        scale = np.array(
            [
                [self.scale[0], 0.0, 0.0, 0.0],
                [0.0, self.scale[1], 0.0, 0.0],
                [0.0, 0.0, self.scale[2], 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )

        rotate_x = np.array(
            [
                [1.0, 0.0, 0.0, 0.0],
                [0.0, mth.cos(self.rotate[0]), -mth.sin(self.rotate[0]), 0.0],
                [0.0, mth.sin(self.rotate[0]), mth.cos(self.rotate[0]), 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )

        rotate_y = np.array(
            [
                [mth.cos(self.rotate[1]), 0.0, mth.sin(self.rotate[1]), 0.0],
                [0.0, 1.0, 0.0, 0.0],
                [-mth.sin(self.rotate[1]), 0.0, mth.cos(self.rotate[1]), 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )

        rotate_z = np.array(
            [
                [mth.cos(self.rotate[2]), -mth.sin(self.rotate[2]), 0.0, 0.0],
                [mth.sin(self.rotate[2]), mth.cos(self.rotate[2]), 0.0, 0.0],
                [0.0, 0.0, 1.0, 0.0],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )

        translate = np.array(
            [
                [1.0, 0.0, 0.0, self.translate[0]],
                [0.0, 1.0, 0.0, self.translate[1]],
                [0.0, 0.0, 1.0, self.translate[2]],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )

        self.model = translate @ rotate_z @ rotate_y @ rotate_x @ scale


# Holds mesh data.
class Mesh:
    # Store mesh data and its transform.
    def __init__(self, vertex_data: [float]):
        self.transform = Transform()
        self.color = [200, 200, 200]  # Default RGB colour (grey).
        self.vertex_data = np.asarray(
            vertex_data, dtype="f4"
        )  # f4 -> f32 in rust (STUPID!).
        self.vertex_count = (
            self.vertex_data.size // 3
        )  # Using // instead of / to avoid casting.


class Camera:
    # Camera defaults.
    def __init__(self):
        self.transform = Transform()
        self.fov = 1.6  # Radians.
        self.up = [0.0, 1.0, 0.0]
        self.forward = [-1.0, 0.0, 0.0]
        self.right = [0.0, 0.0, -1.0]
        self.resolution = [WIDTH, HEIGHT]
        self.aspect = float(WIDTH) / float(HEIGHT)
        self.near = 0.1
        self.far = 100.0
        self.update_projection()
        self.update_view()

    # Build the projection matrix.
    def update_projection(self):
        t = mth.tan(self.fov / 2)
        self.projection = np.array(
            [
                [(1.0 / (self.aspect * t)), 0.0, 0.0, 0.0],
                [0.0, 1.0 / t, 0.0, 0.0],
                [
                    0.0,
                    0.0,
                    -(self.far + self.near) / (self.far - self.near),
                    -2.0 * self.far * self.near / (self.far - self.near),
                ],
                [0.0, 0.0, -1.0, 0.0],
            ]
        )

    # Build the view matrix.
    def update_view(self):
        self.view = np.array(
            [
                [
                    self.right[0],
                    self.right[1],
                    self.right[2],
                    -np.dot(self.right, self.transform.translate),
                ],
                [
                    self.up[0],
                    self.up[1],
                    self.up[2],
                    -np.dot(self.up, self.transform.translate),
                ],
                [
                    self.forward[0],
                    self.forward[1],
                    self.forward[2],
                    -np.dot(self.forward, self.transform.translate),
                ],
                [0.0, 0.0, 0.0, 1.0],
            ]
        )

    # Targets the camera.
    def look_at(self, target):
        position = np.array(self.transform.translate, dtype=float)
        target = np.array(target, dtype=float)
        world_up = np.array([0.0, 1.0, 0.0])

        forward = target - position
        forward /= np.linalg.norm(forward)

        right = np.cross(forward, world_up)
        if np.linalg.norm(right) == 0:
            # Avoid a zero cross product when looking straight up or down.
            world_up = np.array([0.0, 0.0, 1.0])
            right = np.cross(forward, world_up)
        right /= np.linalg.norm(right)

        up = np.cross(right, forward)
        up /= np.linalg.norm(up)

        self.forward = -forward
        self.right = right
        self.up = up
        self.update_view()
