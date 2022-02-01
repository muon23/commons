import json
import logging
from optparse import OptionParser
from typing import Dict, Any, Optional, List, Union, Tuple

import yaml


class Utilities:

    @classmethod
    def withEnvironment(cls, parameters: Dict[str, Any], errorIfNotFound=False) -> None:
        """
        Replaces all ${...} in the parameter values with environment variables
        :param parameters: A dictionary of parameters
        :param errorIfNotFound: Raises ValueError if an environment variable is not defined and no default value is given
        :return: Parameters with values substituted.
        """
        import os
        import re

        pattern = r"(\${([^}:]+)(:([^}]+))?})"

        for key in parameters:
            value = parameters[key]
            if isinstance(value, dict):
                Utilities.withEnvironment(value)
            elif isinstance(value, str):
                matches = re.findall(pattern, value)

                for match in matches:
                    if match[1] in os.environ:
                        value = value.replace(match[0], os.environ.get(match[1]))
                    elif match[3]:
                        value = value.replace(match[0], match[3])
                    elif errorIfNotFound:
                        raise ValueError(f"Environment {match[1]} not found and without a default value")
                    else:
                        value = value.replace(match[0], "")

                parameters[key] = value

    @classmethod
    def md5Of(cls, directory: str, verbose: bool = False) -> Optional[str]:
        import hashlib
        import os

        md5 = hashlib.md5()
        if not os.path.exists(directory):
            return None

        for root, dirs, files in os.walk(directory):
            for names in files:
                if verbose:
                    print('Hashing', names)

                filepath = os.path.join(root, names)
                fd = open(filepath, 'rb')

                while True:
                    # Read file in as little chunks
                    buf = fd.read(4096)
                    if not buf:
                        break
                    md5.update(hashlib.md5(buf).hexdigest().encode("utf-8"))
                fd.close()

        return md5.hexdigest()

    @classmethod
    def getConfig(
            cls,
            cliOptions: Dict[str, Tuple[Union[str, List[str]], Any, str]] = None,
            providedConfig: dict = None,
            providedArgs: List[str] = None
    ) -> dict:
        config = None

        # Get configuration from the command line argument
        optParser = OptionParser('usage: %prog [options]')
        optParser.add_option(
            '-c', '--conf', '--parameters',
            dest='configFile', help='configuration file', default='vectorize.yml'
        )

        # Get additional CLI options
        if cliOptions is not None:
            for option in cliOptions:
                flags, default, description = cliOptions[option]
                if isinstance(flags, str):
                    flags = [flags]
                if isinstance(default, bool):
                    # if default is true, giving the flag should set the variable to false,
                    # therefore "store_false" for the action.
                    action = "store_false" if default else "store_true"
                    optParser.add_option(*flags, dest=option, action=action)
                elif default is None:
                    optParser.add_option(*flags, dest=option, help=description)
                else:
                    optParser.add_option(*flags, dest=option, help=description, default=default)

        # Parse options from arguments
        (options, args) = optParser.parse_args() if providedArgs is None else optParser.parse_args(providedArgs)

        # Get configuration parameters
        configFileName = options.configFile

        try:
            with open(configFileName) as configFile:
                config = yaml.full_load(configFile)
                Utilities.withEnvironment(config)
        except FileNotFoundError:
            print('Configuration file %s not found' % configFileName)
            exit(1)

        # Additional CLI options overrides configuration file
        if cliOptions is not None:
            for option in cliOptions:
                cliArgValue = getattr(options, option)
                if cliArgValue is not None:
                    config[option] = cliArgValue

        config["configFile"] = configFileName

        # Override configuration for testing/debugging
        if providedConfig is not None:
            config.update(providedConfig)

        # Set up logger
        logFormat = '[%(asctime)s] %(levelname)s - %(message)s'
        logFileName = config.get('logFile', '')
        if logFileName == '':
            logging.basicConfig(level=logging.INFO, format=logFormat)
        else:
            logging.basicConfig(level=logging.INFO, filename=logFileName, format=logFormat)

        logging.info(f"Configuration: {json.dumps(config, indent=2)}")

        return config

    @classmethod
    def printObject(cls, obj: Any, level=0, indent="    ", name=""):
        indent = indent * level

        if not name:
            name = type(obj).__name__

        if isinstance(obj, list):
            if len(obj) == 0:
                print(f"{indent}{name}=[]")
            else:
                for i in range(len(obj)):
                    cls.printObject(obj[i], level=level, name=f"{name}[{i}]")
        # elif type(obj).__name__ == 'JavaArray':
        #     print(obj)
        elif hasattr(obj, '__dict__') and obj.__dict__:
            print(f"{indent}{name}:")
            for k, v in obj.__dict__.items():
                cls.printObject(v, level=level+1, name=k)
        else:
            if name:
                name += "="
            print(f"{indent}{name}{obj}")
