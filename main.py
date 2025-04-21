import os
import sys
import json
import template
import email_handler

def register():
    import getpass
    import hashlib
    import binascii

    email = input("email: ")
    password = getpass.getpass("app password: ")

    salt = os.urandom(16)
    hashed = hashlib.pbkdf2_hmac("sha256", password.encode(), salt, 100_000)

    salt_hex = binascii.hexlify(salt).decode()
    hash_hex = binascii.hexlify(hashed).decode()

    with open("config.json", "w") as file:
        json.dump({
            "salt": salt_hex,
            "hash": hash_hex,
            "email": email,
            "show_help": True
        }, file)

    print("done!\n")

def toggle_help(config):
    config["show_help"] = not config["show_help"]

    with open("config.json", "w") as file:
        json.dump(config, file)

def show_help():
    print("new - new template")
    print("load <template> - load from email")
    print("send <template> - send save in email")
    print("login - login for the session")
    print("toggle-help - toggle this list on startup")
    print("edit <template> <property (optional)> - edit one or all properties")
    print("help - display this list")
    print()

if __name__ == "__main__":
    password = ""

    print("I~~~~~~~~~~~~~~~~~~~~~~~~~I")
    print("I welcome to save mailer! I")
    print("I~~~~~~~~~~~~~~~~~~~~~~~~~I\n")

    if not os.path.exists("config.json"):
        print("this is the first time you use this program.")
        print("please follow the setup steps!")
        print("passwords are stored securely.\n")
        register()

    with open("config.json") as file:
        config = json.load(file)

    if config["show_help"]: show_help()

    while True:
        user_input = input("# ").strip().split() 
        match user_input[0]:
            case "login":
                password = email_handler.get_password()
            case "new":
                template.create_template()
            case "edit":
                template.edit_template()
            case "send":
                email_handler.send_save(user_input[1], password)
            case "load":
                email_handler.load_save(user_input[1], password)
            case "config":
                register()
            case "toggle-help":
                toggle_help(config)
            case "help":
                show_help()
            case "exit":
                break
    