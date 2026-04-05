#version 330 core

in vec3 frag_normal;
in vec3 frag_world_pos;

out vec4 FragColor;

uniform vec3 color;

void main() {
    vec3 light_dir = normalize(vec3(1.0,1.0,1.0)); // will make this static because this program doesnt need fancy lights
    float diffuse = max(0.5, dot(normalize(frag_normal), light_dir));
    FragColor = vec4(color * diffuse, 1.0);
}
