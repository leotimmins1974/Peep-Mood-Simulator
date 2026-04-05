#version 330 core

// Vertex Shader
// Gets applied to each vertex in a face

layout (location = 0) in vec3 in_position; // Position in Model Space
layout (location = 1) in vec3 in_normal; // Normal Vector for Vertex

uniform mat4 model;
uniform mat4 view;
uniform mat4 projection;

out vec3 frag_normal;
out vec3 frag_world_pos;

void main() {
    // World Space
    vec4 world_pos = model * vec4(in_position, 1.0);
    frag_world_pos = world_pos.xyz;

    // Normal
    mat3 normal_matrix = transpose(inverse(mat3(model)));
    frag_normal = normalize(normal_matrix * in_normal);

    gl_Position = projection * view * world_pos;
}
