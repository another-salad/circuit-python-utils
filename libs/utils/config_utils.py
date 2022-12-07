"""Generic config utils for Circuit python projects"""

import json


def get_config_from_json_file(json_file="config.json"):
    """Gets the config from config.json"""
    with open(json_file, "r", encoding="UTF-8") as json_file:
        return json.load(json_file)
