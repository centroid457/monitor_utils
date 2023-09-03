import os
from typing import *


# =====================================================================================================================
class EnvNotAccepted(Exception):
    pass


class EnvironsOsGetterClass:
    """
    get environs from OS or use default!
    if not exists some value of them - RAISE!

    # add all ENVS with type STR!

    firstly it will try to get value from OsEnv
    then if not will be used already seted as default!

    define env NAMES
        ENV__MAIL_USER: str = None  # will find ENV__MAIL_USER/MAIL_USER
        ENV__myEnv: str = None  # will find ENV__myEnv/myEnv
        MAIL_USER: str = None  # this is not expected as env!

    default VALUES
        ENV__MAIL_USER: str = None      # no default value
        ENV__MAIL_USER: str = "hello"   # def value set!
    """

    __env_name__prefix: str = "ENV__"

    def __init__(self):
        super().__init__()

        self._envs_detected: Dict[str, Optional[str]] = {}     # just for debug

        self.__env_names__detect()
        self.__env_values__update_from_os()
        self.__env_values__check_exists_or_raise()

    def __env_names__detect(self):
        for name in dir(self):
            if name.startswith(self.__env_name__prefix):
                self._envs_detected.update({name: getattr(self, name)})

    def __env_values__update_from_os(self):
        for name_w_prefix in self._envs_detected:
            name_wo_prefix = name_w_prefix.replace(self.__env_name__prefix, "", 1)

            env_name__os = None

            if name_w_prefix in os.environ:
                env_name__os = name_w_prefix
            elif name_wo_prefix in os.environ:
                env_name__os = name_wo_prefix

            if env_name__os:
                env_value__os = os.getenv(env_name__os)
                setattr(self, name_w_prefix, env_value__os)

                self._envs_detected.update({name_w_prefix: env_value__os})

    def __env_values__check_exists_or_raise(self):
        for name in self._envs_detected:
            if getattr(self, name) is None:
                msg = f"[CRITICAL]there is no [{name=}] in OsEnvs and not exists default value! add it manually!!!"
                print(msg)
                raise EnvNotAccepted(msg)


# =====================================================================================================================
