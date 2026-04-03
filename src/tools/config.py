# READS 'simulation.config' AND RETURNS A HASHMAP

def parse_config(path):
    config_str = open(path,'r').read()

    config_str = config_str.replace(" ", "") # strip all white spaces
    
    # Remove comments and blank lines and headings
    config = {}
    for line in config_str.split('\n'):
        if line == '' or line[0] == '[' or line[0] == "#":
            continue # strip all blank lines, lonely comments, and headings

        # Verification
        split_line = line.split("#", 1)[0].split('=')
        if len(split_line) == 2:
            config[split_line[0]] = int(split_line[1]) # remove comments
        else:
            print("--FORCE EXIT--")
            print("simulation.configuration is not properly configured: name = int")
            print(split_line)
            exit()

    print(f"Loaded '{path}' -> {config}")
    return(config)

if __name__ == "__main__":
    parse_config("./simulation.config")