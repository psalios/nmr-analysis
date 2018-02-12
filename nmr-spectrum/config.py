import logging
import os
import re
import sys

SETTINGS_FILE = "settings.properties"
envRegex = re.compile(r"\$\{(.+?)}")
logger = logging.getLogger()
class ConfigurationReadException(Exception):
    pass

class Properties:

    if len(sys.argv) > 1:
        settingsArgs = [s for s in sys.argv if "nomad.settings=" in s]
        if len(settingsArgs) > 0:
            settingArg = settingsArgs[0].split("=", 1)
            if len(settingArg) > 1:
                if len(settingArg[1]) > 0:
                    SETTINGS_FILE = settingArg[1]
                    logger.info("Setting settings file path from command line: " + SETTINGS_FILE)
    with open(SETTINGS_FILE) as infile:
        lines = infile.readlines()
    prop = dict([line.strip().split('=') for line in lines if not line.startswith('#') and not line.startswith('\n')])

    @staticmethod
    def GetProperty(propertyName, default=None, throwError=False):
        if propertyName in Properties.prop:
            value = Properties.prop[propertyName]
            offset = 0
            for match in envRegex.finditer(value):
                envValue = os.environ[match.group(1)]
                value = value[:match.start() + offset] + envValue + value[match.end() + offset:]
                offset += len(envValue) - len(match.group(0))
            return value
        else:
            if throwError:
                raise ConfigurationReadException()
            else:
                logger.warning("Did not find value for parameter: " + propertyName +" Resorting to default: " + default)
                return default
