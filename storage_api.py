import json

DEFAULT_FILE_CONTENT = '{"To Do": [], "In Progress": [], "Done": []}'

def get_data(filename = ".tasks.json"):
    with open(filename, "r") as tasks:
        return json.load(tasks)

def write_data(data, filename = ".tasks.json"):
    with open(filename, "w") as tasks:
        json.dump(data, tasks)

def create_file(filename = ".tasks.json"):
    with open(filename, "w") as tasks:
        tasks.write(DEFAULT_FILE_CONTENT)
