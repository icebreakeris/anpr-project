import json
import os
import log

DEFAULT_CONFIG = {"tesseract_url" : "", "show_steps" : False, "save_images" : False}
LOGGER = log.get_logger(__name__)

def create_default_config(): 
    with open("config.json", "w") as cfg: 
        cfg.writelines(json.dumps(DEFAULT_CONFIG, indent=3))
        LOGGER.info("Default config created. Ensure it is filled out and try again.")
        return False

def set_tesseract_url(url):
    if not url: 
        return False

    config = check_config()
    if not config:
        return False

    with open("config.json", "w") as cfg:
        config["tesseract_url"] = url
        print(config)
        cfg.writelines(json.dumps(config, indent=3))
        return True

def set_save_images(boolean):
    config = check_config()

    if not config:
        return 
    
    with open("config.json", "w") as cfg: 
        config["save_images"] = boolean
        print(config)
        cfg.writelines(json.dumps(config, indent=3))
        return 

def set_steps(steps):
    print(steps)
    config = check_config()

    if not config:
        return 

    with open("config.json", "w") as cfg:
        config["show_steps"] = steps
        print(config)
        cfg.writelines(json.dumps(config, indent=3))
        return 

def check_config():
    #if config doesnt exist, create one with default values
    if not os.path.isfile("config.json"):
        LOGGER.info("Config not found. Creating one...")
        create_default_config()
        return False

    #if config exists but is empty
    if len(open("config.json", "r").read()) <= 0: 
        LOGGER.info("Config.json empty. Creating a new one...")
        create_default_config()
        return False
    
    try:
        content = json.loads(open("config.json", "r").read())
    except json.JSONDecodeError as ex: 
        LOGGER.critical(f"Could not read config.json. Remove the file, launch the program and try configuring again. JSON ERROR: {ex}")
        return False

    #checks if config contains necessary variables
    for a in DEFAULT_CONFIG:
        if a not in content: 
            LOGGER.critical(f"Variable {a} not in config. Value ignored and config recreated...")
            create_default_config()
            return False

    if type(content["show_steps"]) is not bool:
        LOGGER.critical("show_steps invalid. Value should be true/false")
        return False

    #return the configuration if it has passed all the checks
    return content
