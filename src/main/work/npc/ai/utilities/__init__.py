from typing import Dict, Any, Optional


class Utilities:

    @staticmethod
    def withEnvironment(parameters: Dict[str, Any], errorIfNotFound=False) -> None:
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

                parameters[key] = value

    @staticmethod
    def md5Of(directory: str, verbose: bool = False) -> Optional[str]:
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
