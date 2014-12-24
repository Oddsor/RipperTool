__author__ = 'Odd'

import configparser

config = configparser.ConfigParser()
config.read('settings.ini')
if "DEFAULT" not in config:
    config.add_section("DEFAULT")

def get_setting(key):
    if config.has_option("DEFAULT", key):
        return config['DEFAULT'][key]
    else:
        return None

def set_setting(key, value):
    config["DEFAULT"][key] = value
    config.write(open("settings.ini", 'w'))