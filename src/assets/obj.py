# MANAGER FOR .obj FILES

import numpy as np

import render.graphics as graphics


def load(path) -> graphics.Mesh:
    data = open(path, "r").readlines()

    verticies = []
    faces = []

    for line in data:
        k = line.strip().split(" ", 1)

        match k[0]:
            case "o":
                print(f"Loading .obj {k[1]} .. ", end="")

            case "v":
                pos = []
                for p in k[1].split(" "):
                    pos.append(float(p))
                verticies.append(graphics.Vertex(np.array(pos)))

            case "vt":
                pass  # Maybe ill add UV textures at some point

            case "vn":
                pass  # Lighting once i get to it

            case "f":
                indicies = []
                for i in k[1].split(" "):
                    indicies.append(
                        int(i.split("/", 1)[0]) - 1
                    )  # -1 to convert to 0 index
                faces.append(graphics.Face(indicies))

    print("done!")
    return graphics.Mesh(verticies, faces)
