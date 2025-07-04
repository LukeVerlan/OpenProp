
class ConfigWrapper:
    def __init__(self, config_dict):
        self._config = config_dict

    def getProperty(self, key):
        return self._config.get(key, None)