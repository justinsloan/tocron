from dataclasses import dataclass
from typing import List
import json
from dataclasses_json import dataclass_json


@dataclass_json # <-- this injects to_dict/from_dict and to_json/from_json
@dataclass
class Node:
    title: str
    target: str
    #log: str

nodes: List[Node] = []

@dataclass_json
@dataclass
class Task:
    type: str
    log: str

tasks: List[Task] = []

# Usage: save_data("nodes.json", nodes)
def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        dicts = [i._get_properties() for i in data]        # convert all instances to a list of dicts
        keeps = [i for i in dicts if i["trash"] != 'true'] # keep only instances that are not trashed
        json.dump(keeps, f)#, indent=2)


# Usage:
# raw_data = load_data("nodes.json")
# nodes: List[Node] = [Node.from_dict(d) for d in raw_data]
def load_data(filename):
    with open(filename, "r", encoding="utf-8") as f:
        raw = json.load(f)

    return raw # [Person.from_dict(d) for d in raw] #load the raw data directly into class