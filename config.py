import json
import os
import log

DEFAULT_CONFIG = {"tesseract_url" : "", "show_steps" : False}
LOGGER = log.get_logger(__name__)

def create_default_config(): 
    with open("config.json", "w") as cfg: 
        cfg.writelines(json.dumps(DEFAULT_CONFIG, indent=3))
        LOGGER.info("Default config created. Ensure it is filled out and try again.")
        return False

def check_config():
    #if config doesnt exist, create one with default values
    if not os.path.isfile("config.json"):
        LOGGER.info("Config not found. Creating one...")
        create_default_config()
        return False

    if len(open("config.json", "r").read()) <= 0: 
        LOGGER.info("Config.json empty. Creating a new one...")
        create_default_config()
        return False
    
    try:
        content = json.loads(open("config.json", "r").read())
    except json.JSONDecodeError as ex: 
        LOGGER.critical(f"Could not read config.json. Remove the file, launch the program and try configuring again. JSON ERROR: {ex}")
        return False

    if "tesseract_url" not in content:
        LOGGER.critical("Variable tesseract_url not in config. Value ignored and config recreated...")
        create_default_config()
        return False
    
    if not os.path.isfile(content["tesseract_url"]):
        LOGGER.critical("Tesseract.exe not found. Check config.json and enter a valid url.")
        return False
    
    if "show_steps" not in content:
        LOGGER.critical("Variable show_steps not in config. Value ignored and config recreated...")
        create_default_config()
        return False

    if type(content["show_steps"]) is not bool:
        LOGGER.critical("show_steps invalid. Value should be true/false")
        return False

    return content