# Simple OBJ loader for positions and normals.

import src.graphics as graphics


# Load a mesh from an OBJ file.
def load(path) -> graphics.Mesh:
    with open(path, "r", encoding="utf-8") as file:
        data = file.readlines()

    vertices = []
    normals = []
    vertex_data = []

    for line in data:
        parts = line.strip().split(" ", 1)

        match parts[0]:
            case "o":
                #print(f"Loading .obj {parts[1]} .. ", end="")
                pass

            case "v":
                values = []
                for value in parts[1].split():
                    values.append(float(value))
                vertices.append(values)

            case "vt":
                pass

            case "vn":
                values = []
                for value in parts[1].split():
                    values.append(float(value))
                normals.append(values)

            case "f":
                face = []
                for entry in parts[1].split():
                    indices = entry.split("/")
                    vertex_index = int(indices[0]) - 1
                    normal_index = int(indices[2]) - 1
                    face.append((vertex_index, normal_index))

                # Renamed to f_index because its itering over 6 floats now.
                for f_index in range(1, len(face) - 1):
                    for vertex_index, normal_index in (
                        face[0],
                        face[f_index],
                        face[f_index + 1],
                    ):
                        vertex_data.extend(vertices[vertex_index])
                        vertex_data.extend(normals[normal_index])

    #print("done!")
    return graphics.Mesh(vertex_data)
