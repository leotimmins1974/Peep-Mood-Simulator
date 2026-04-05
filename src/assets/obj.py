# MANAGER FOR .obj FILES

import render.graphics as graphics


def load(path) -> graphics.Mesh:
    data = open(path, "r").readlines()

    vertices = []
    normals = []
    vertex_data = []

    for line in data:
        k = line.strip().split(" ", 1)

        match k[0]:
            # o Object Name
            case "o":
                print(f"Loading .obj {k[1]} .. ", end="")

            # v Vertex Positions in Model Space
            case "v":
                pos = []
                for p in k[1].split():
                    pos.append(float(p))
                vertices.append(pos)

            # vt Forgot what this represents lowkey
            case "vt":
                pass

            # vn Face Normal (already normalised THANKYOU BLENDER)
            case "vn":
                pos = []
                for p in k[1].split():
                    pos.append(float(p))
                normals.append(pos)

            case "f":
                face = []
                for i in k[1].split():
                    parts = i.split("/")
                    vertex_index = int(parts[0]) -1
                    normal_index = int(parts[2]) -1
                    face.append((vertex_index, normal_index))

                for tri_index in range(1, len(face) - 1):
                    for vertex_index, normal_index in (
                        face[0],
                        face[tri_index],
                        face[tri_index + 1],
                    ):
                        vertex_data.extend(vertices[vertex_index])
                        vertex_data.extend(
                            normals[normal_index]
                        )  # now 6 signed floats per pixel

    print("done!")
    return graphics.Mesh(vertex_data)
