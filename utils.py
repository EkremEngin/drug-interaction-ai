import json
import re

def normalize_name(name):
    return re.sub(r'[^a-z0-9]', '', name.lower())

def load_json(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

severity_map = {"minor": 0, "moderate": 1, "major": 2}
inverse_map = {0: "minor", 1: "moderate", 2: "major"}
