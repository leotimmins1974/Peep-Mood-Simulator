# PYGAME OR SDL2 (ILL CHOOSE LATER) HELPER FUNCTIONS AND STRUCTS

import numpy as np
import math as mth

WIDTH,HEIGHT = (600,500)

class Transform:
    def __init__(self):
        self.translate = [0.,0.,0.]
        self.rotate = [0.,0.,0.] # Radians
        self.scale = [1.,1.,1.] 
        self.update_model()

    def update_model(self):
        scale = np.array([
            [self.scale[0],0.,0.,0.],
            [0.,self.scale[1],0.,0.],
            [0.,0.,self.scale[2],0.],
            [0.,0.,0.,1.],
        ])

        rotate_x = np.array([
            [1.,0.,0.,0.],
            [0., mth.cos(self.rotate[0]), -mth.sin(self.rotate[0]), 0.],
            [0., mth.sin(self.rotate[0]), mth.cos(self.rotate[0]), 0.],
            [0.,0.,0.,1.]
        ])

        rotate_y = np.array([
            [mth.cos(self.rotate[1]), 0., mth.sin(self.rotate[1]), 0.],
            [0., 1., 0., 0.],
            [-mth.sin(self.rotate[1]), 0., mth.cos(self.rotate[1]), 0.],
            [0., 0., 0., 1.]
        ])

        rotate_z = np.array([
            [mth.cos(self.rotate[2]), -mth.sin(self.rotate[2]), 0., 0.],
            [mth.sin(self.rotate[2]),  mth.cos(self.rotate[2]), 0., 0.],
            [0., 0., 1., 0.],
            [0., 0., 0., 1.]
        ])

        translate = np.array([
            [1., 0., 0., self.translate[0]],
            [0., 1., 0., self.translate[1]],
            [0., 0., 1., self.translate[2]],
            [0., 0., 0., 1.]
        ])

        self.model = translate @ rotate_z @ rotate_y @ rotate_x @ scale


class Mesh:
    def __init__(self, verticies: [Vertex], faces: [Face]):
        self.transform = Transform()
        self.color = [200,200,200,255] # RGBA | Defaults to grey
        self.verticies = verticies
        self.faces = faces


class Face:
    def __init__(self, indicies: [float,float,float]):
        self.indicies = indicies

class Vertex:
    def __init__(self, pos):
        self.pos = pos

class Camera:
    def __init__(self):
        self.transform = Transform()
        self.fov = 1.6 # Radians
        self.up = [0.,1.,0.]
        self.forward = [-1.,0.,0.]
        self.right = [0.,0.,-1.]
        self.resolution = [WIDTH,HEIGHT]
        self.aspect = float(WIDTH) / float(HEIGHT)
        self.near = 0.1
        self.far = 1000. # Might lower to improve preformance
        self.update_projection()
        self.update_view()

    def update_projection(self):
        t = mth.tan(self.fov/2)
        self.projection = np.array([
            [(1./(self.aspect * t)), 0., 0., 0.],
            [0., 1./t, 0.,0.],
            [0.,0.,-(self.far + self.near) / (self.far - self.near), -2. * self.far * self.near / (self.far - self.near)],
            [0.,0.,-1.,0.]
        ])

    def update_view(self):
        self.view = np.array([
            [self.right[0], self.right[1], self.right[2], -np.dot(self.right, self.transform.translate)],
            [self.up[0], self.up[1], self.up[2], -np.dot(self.up, self.transform.translate)],
            [self.forward[0], self.forward[1], self.forward[2], -np.dot(self.forward, self.transform.translate)],
            [0.,0.,0.,1.]
        ])

    def look_at(self, target):
        position = np.array(self.transform.translate, dtype=float)
        target = np.array(target, dtype=float)
        world_up = np.array([0., 1., 0.])

        forward = target - position
        forward /= np.linalg.norm(forward)

        right = np.cross(forward, world_up)
        if np.linalg.norm(right) == 0:
            world_up = np.array([0., 0., 1.])
            right = np.cross(forward, world_up)
        right /= np.linalg.norm(right)

        up = np.cross(right, forward)
        up /= np.linalg.norm(up)

        self.forward = -forward
        self.right = right
        self.up = up
        self.update_view()

class Light:
    def __init__(self, direction, position, lumens):
        self.direction = direction
        self.position = position
        self.lumens = lumens

def to_screen_space(clip_coord, width, height):
    return((int(round((clip_coord[0]/clip_coord[3]+1) / 2. * width,0)), int(round((1.-clip_coord[1] / clip_coord[3])/2.*height,0)) ))
