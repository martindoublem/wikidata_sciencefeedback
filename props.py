import json

props_dict = {}

with open("props_raw.json") as f:
    d = json.load(f)
    for item in d:
        props_dict[item['id']] = item['label']

with open("props.json", "w") as outfile:
    json.dump(props_dict, outfile)

if __name__ == '__main__':
    print(props_dict)
