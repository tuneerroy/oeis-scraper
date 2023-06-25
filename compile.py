import json
import os


def compile():
    files = os.listdir("data")
    res = []
    for file in files:
        path = os.path.join("data", file)
        with open(path, "r") as f:
            data = json.load(f)
            res.append(data)
    return res


if __name__ == "__main__":
    data = compile()
    with open("compiled.json", "w") as f:
        json.dump(data, f, indent=4)
