import json
def load_config(path="config.json"):
    with open(path, 'r') as f:
        return json.load(f)

def save_config(config, path="config.json"):
    with open(path, 'w') as f:
        json.dump(config, f, indent=4)
