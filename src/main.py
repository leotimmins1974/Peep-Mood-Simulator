import assets.obj as obj

import render.math as math
import render.graphics as graphics

import tools.config as config
import tools.results as results


MESHES_FOLDER_PATH = "./meshes/"
SIMULATION_CONFIG_PATH = "./simulation.config"

# Grab configs
config = config.parse_config(SIMULATION_CONFIG_PATH)

# ENTRY POINT
def main() -> exit_code:



    return(0)


exit_code = main()

print(f"terminated with exit code: {exit_code}")

match exit_code:
    case 0: 
        print("-- SUCCESS --")
    case _:
        print("-- FAIL --")
        print("read exit_report.txt")