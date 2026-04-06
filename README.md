
#   Emotion Simulation

##  Leo Timmins | 23559213

### Instructions

    - To configure the simulation go to /simulation.config

    - Be careful when modifying the config, read the comments

    - To run program use `python3 src/main.py`

    - To view results go to /results.md (after running (AND FINISHING) succesfully)

    - If main() returns exit code !0 goto exit_report.txt // Not actualy implemented yet

### Note
    
    With the complexity of this program you may suspect AI usage. None was used. I have tracked my codebase with git so you can review the commits as proof if nessesary.

### Dependancys

    please run 

    ``` bash
    python3 -m pip install -r requirements.txt
    ```

### Scope

    The goal of my submission will be to use software rasturisation to create an interactive 3D simulation that can handle user input. I imagine there are likely Vulkan bindings for python, but I'd prefer to do it this way to increase code complexity and therefore get more marks.

    I'll be storing models for the sim as simple .obj, made in blender.

    Peeps will have a content score derived from factors like "sociability, hunger, temperature, crazyness, religion"
    Will change factors later to be based on actual psycological contentness

    Events can happen that might apply multiplyers or remove peeps.

    Maybe ill add audio reflective of global mood, events, whatever.

    Formatting with Black

    --------------------------

    Okay I making a big change. software rendering on python is way too slow. Im getting 2 fps on a ryzen 7 7700. Im not sure if this violates the rules assignment, but ill be using moderngl's OpenGL python bindings and moving the per pixel math and per face math and per vertex math to a shader. This is pretty much nessersary at this point. previously I was using the painters algorithim which was fast enough, but having switched to z-depth rasturising, it is now way to slow.

### Refrences

    - (Code I have written!) three-dimensional-rendering by Leo Timmins https://github.com/leotimmins1974/three-dimensional-rendering 
    
    - Transformation Matrix for Projection of 3d objects into a 2D plane (Projection Transform) https://www.mauriciopoppe.com/notes/computer-graphics/viewing/projection-transform/