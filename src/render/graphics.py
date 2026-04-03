# PYGAME OR SDL2 (ILL CHOOSE LATER) HELPER FUNCTIONS AND STRUCTS

WIDTH,HEIGHT = (600,500)

class Transform:
    translate = [0.,0.,0.]
    rotate = [0.,0.,0.] # Radians
    scale = [1.,1.,1.] 


class Mesh:
    transform = Transform()
    color = [200,200,200,255] # RGBA | Defaults to grey

    def __init__(self, verticies: [Vertex], faces: [Face]):
        self.verticies = verticies
        self.faces = faces


class Face:
    def __init__(self, indicies: [float,float,float]):
        self.indicies = indicies

class Vertex:
    def __init__(self, pos: [float, float, float]):
        self.pos = pos

class Camera:
    transform = Transform()
    fov = 1.6 # Radians
    up = [0.,1.,0.]
    forward = [-1.,0.,0.]
    right = [0.,0.,-1.]
    resolution = [WIDTH,HEIGHT]
    aspect = float(WIDTH) / float(HEIGHT)
    near = 0.1
    far = 1000. # Might lower to improve preformance

