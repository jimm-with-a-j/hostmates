# Handles reading configuration yaml file

import yaml

CONFIG_FILE = r"hostgroups.yaml"


class Config:

    def __init__(self):
        with open(CONFIG_FILE) as config_file:
            config = yaml.load(config_file, Loader=yaml.FullLoader)
            self.token = config["apiToken"]
            self.delimiter = config["delimiter"]
            self.components = config["components"]