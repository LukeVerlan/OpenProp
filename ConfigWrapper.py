# CONFIGWRAPPER
# Config wrapper used to work with open motor
# nessecary as open motor configs require a get property method to work

# features a getProperty method to interface with open motor
class ConfigWrapper:

    def __init__(self, config_dict):
        self._config = config_dict

    # Brief - return the property of a key
    def getProperty(self, key):
        return self._config.get(key, None)