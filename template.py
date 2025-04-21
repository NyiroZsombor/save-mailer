import os
import json
import uuid

def input_body():
    body = input("body (escape: [end]):\n")
    while not body.strip().endswith("[end]\\n"):
        body += input() + "\\n"
    body = body.removesuffix("[end]\\n") + "\\n"

    return body

def input_save_path():
    prompt = "path to save folder: "
    path = input(prompt)
    while not os.path.exists(path):
        print("invalid path!")
        path = input(prompt)

    return path

def input_save_name(save_path):
    prompt = "save file name: "
    path = input(prompt)
    while not os.path.exists(os.path.join(save_path, path)):
        print("invalid path!")
        path = input(prompt)

    return path

def create_template():
    template = {}

    template["name"] = input("template name: ").strip().replace(" ", "-")
    template["subject"] = input("subject: ")
    template["body"] = input_body()
    template["save_path"] = input_save_path()
    template["save_name"] = input_save_name(template["save_path"])
    print()

    with open(template["name"] + ".template.json", "w") as file:
        json.dump(template, file)

def edit_template(template_name, property=None):
    with open(template_name + ".template.json") as file:
        template = json.load(file)
    
    if property is None:
        for prop in template.keys():
            edit_template(template_name, prop)
        return

    match property:
        case "body":
            template["body"] = input_body()
        case "save_path":
            template["save_path"] = input_save_path()
        case "save_name":
            template["save_name"] = input_save_name(template["save_path"])
        case "name":
            template["name"] = input("template name: ")
        case _:
            template[property] = input(property + ": ")

    with open(template_name + ".template.json", "w") as file:
        json.dump(template, file)
