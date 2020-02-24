import json
import os  

DEFAULT_CONFIG = {"tesseract_url" : "", "show_steps" : False}

def check_config():
    #if config.json doesn't exist
    if not os.path.isfile("config.json"):
        print("[!] Config not found. Creating one...")
        with open("config.json", "w") as cfg:
            cfg.writelines(json.dumps(DEFAULT_CONFIG, indent=2))
            print("[!] Config created. Ensure it is filled out and try again.")
    try:
        with open("config.json", "r") as cfg: 
            #try getting content only if the json is not empty
            if len(cfg.read()) > 0: 
                content = json.loads(open("config.json", "r").read())

    except json.decoder.JSONDecodeError:
        print("[!] Error loading config file. If the file is empty, remove it and launch the program again.")
        return False

    #check if tesseract url is valid
    if not os.path.isfile(content["tesseract_url"]):
        print("[!] tesseract.exe not found. Enter a valid tesseract_url and try again.")
        return False

    #check if show_steps is bool
    if type(content["show_steps"]) is not bool: 
        print("[!] Invalid show_steps value in config. Value must be true/false.")
        return False

    print(content)


