# MANAGER FOR .obj FILES

import render.graphics as graphics


def load(path) -> graphics.Mesh:
    data = open(path, "r").readlines()

    vertices = []
    vertex_data = []

    for line in data:
        k = line.strip().split(" ", 1)

        match k[0]:
            case "o":
                print(f"Loading .obj {k[1]} .. ", end="")

            case "v":
                pos = []
                for p in k[1].split(" "):
                    pos.append(float(p))
                vertices.append(pos)

            case "vt":
                pass

            case "vn":
                pass

            case "f":
                indicies = []
                for i in k[1].split(" "):
                    indicies.append(
                        int(i.split("/", 1)[0]) - 1 # -1 to convert to 0
                    )
                for tri_index in range(1, len(indicies) - 1):
                    for vertex_index in (
                        indicies[0],
                        indicies[tri_index],
                        indicies[tri_index + 1],
                    ):
                        vertex_data.extend(vertices[vertex_index])

    print("done!")
    return graphics.Mesh(vertex_data)
