from dataclasses import dataclass
from typing import List
import json
from dataclasses_json import dataclass_json


@dataclass_json # <-- this injects to_dict/from_dict and to_json/from_json
@dataclass
class Node:
    #id: int
    title: str
    target: str
    #log: str

nodes: List[Node] = []

@dataclass_json
@dataclass
class Task:
    #id: int
    type: str
    log: str

tasks: List[Task] = []

# Usage: save_data("nodes.json", nodes)
def save_data(filename, data):
    with open(filename, "w", encoding="utf-8") as f:
        # Convert each Person to a plain dict
        dicts = [i.to_dict() for i in data]
        json.dump(dicts, f)#, indent=2)


# Usage:
# raw_data = load_data("nodes.json")
# nodes: List[Node] = [Node.from_dict(d) for d in raw_data]
def load_data(filename):
    with open(filename, "r", encoding="utf-8") as f:
        raw = json.load(f)

    return raw # [Person.from_dict(d) for d in raw] #load the raw data directly into class