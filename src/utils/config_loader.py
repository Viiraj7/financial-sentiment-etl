#
# src/utils/config_loader.py
#
# This script contains a function to load configuration settings from a YAML file.
# This allows us to manage settings like file paths and URLs in one central place.
#

# Import the PyYAML library, which is needed to read .yaml files
import yaml

# Define the path to our settings file
CONFIG_PATH = "config/settings.yaml"

def load_config():
    """
    Loads the configuration from the settings.yaml file.

    Returns:
        dict: A dictionary containing all the configuration settings.
              Returns an empty dictionary if the file cannot be found or read.
    """
    try:
        # 'with open(...)' is the standard, safe way to open files in Python.
        # It ensures the file is automatically closed even if errors occur.
        with open(CONFIG_PATH, 'r') as file:
            # yaml.safe_load() parses the YAML file and converts it into a Python dictionary.
            config = yaml.safe_load(file)
        return config
    except FileNotFoundError:
        # This error happens if 'config/settings.yaml' doesn't exist.
        print(f"Error: Configuration file not found at {CONFIG_PATH}")
        return {} # Return an empty dict to prevent the program from crashing
    except yaml.YAMLError as e:
        # This error happens if the YAML file has a syntax error.
        print(f"Error parsing YAML file: {e}")
        return {}