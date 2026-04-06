
#   Emotion Simulation

##  Leo Timmins | 23559213


### Dependancys

please run 

``` bash
python3 -m pip install -r requirements.txt
```

### Instructions

- Install dependancys (see `Dependancys` section)
 
- To run program use `python3 ./main.py`

- To configure the simulation go to /simulation.config

- Be careful when modifying the config, read the comments

- To view results go to /results.md (after running program and then closing it)

### Notes

With the complexity of this program you may suspect AI usage. None was used. I have tracked my codebase with git so you can review the commits as proof if nessesary. Contact `23559213@student.curtin.edu.au` for the .git

I primarily program in Rust, and it has been some time since i've written a large Python project. As such, this project's structure will be familiar to those who know Rust. Modules are held within ./src/

My original implementation of 3D rendering was single-threaded software rendering. After switching from painter's algorithim to a Z-buffering implementation, preformance had dropped from 60 fps to 3 fps on a ryzen 7 7700. As such I decided to remove my own rendering loop and replace it with OpenGL's vertex and fragment shaders which run on the GPU. FPS is practicaly unlimited now on a 5070ti. ModernGL is used as an API to OpenGL.

My desision to use PyGame instead of ModernGL_Window was PyGames accesible APIs for input handling, and audio playback. I originaly intended to have music play based on the average mood of the Peeps. However I've lost intrest in this project.

A consequence of using my own OpenGL context is PyGames font blitting feature no longer works so I've resorted to just using the window title bar as a text box.

I prefer to use Markdown (.md) format for text documents, I recomend using a Markdown renderer to view the results file. However, due to the nature of Markdown, you can view it as plain text if you wish.

### Scope

- Emotion Simulator: Simulates the mood of Peeps

- Each Peep has 4 attributes (Social, Hunger, Wealth, Religion)

- These attributes are weighted by the Peeps prefrences to calculate a mood

- Moods influence behaviours and nearby peeps

- Peeps can take differnet actions like eating, praying, socialising, attacking, or fleeing

- Decisions are influenced by attribute levels, cooldowns, prefrences, and events

- Events occur randomly and may include Actors (such as God, or the Devil)

- Simulation runs continously until the user closes the window

- I've setup behaviours in such a way that peeps have a herd like mentality

### Refrences

`Please refer to the report attached to this submition`