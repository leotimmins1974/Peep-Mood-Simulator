# Read settings from a `.config` file.


# Parse the config file into a hashmap.
def parse_config(path):
    # Load file contents.
    with open(path, "r", encoding="utf-8") as file:
        config_str = file.read()

    # Remove all spaces.
    config_str = config_str.replace(" ", "")

    config = {}
    for line in config_str.split("\n"):
        # Remove headers, blanks, and comments
        if line == "" or line[0] == "[" or line[0] == "#":
            continue

        split_line = line.split("#", 1)[0].split("=")
        if len(split_line) == 2:
            config[split_line[0]] = split_line[1]
        else:
            # Error handling incase someone messes up the configuration.
            print("--FORCE EXIT--")
            print("simulation.configuration is not properly configured: name = value")
            print(split_line)
            exit()

    return config


# Testing
if __name__ == "__main__":
    parse_config("./simulation.config")
