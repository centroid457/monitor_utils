import time
from typing import *
import pathlib
import csv
import threading

import requests
from bs4 import BeautifulSoup

from alerts_msg import *


# =====================================================================================================================
# TODO: separate ClsBASE! see Imap!


# =====================================================================================================================
class TagAddressChain(NamedTuple):
    """
    structure to use as one step of full chain for finding Tag
    all types used as any available variant for function Tag.find_all and actually passed directly to it!

    :param NAME: tag name
    """
    NAME: str
    ATTRS: Dict[str, str]
    STRING: Optional[str]
    INDEX: int


# =====================================================================================================================
class MonitorUrlTag(threading.Thread):
    """
    base class for final monitors!
    monitoring on URL some value.
    if found new value - remember it and send mail alert!
    """
    # SETTINGS -------------------------------
    URL: str = None
    TIMEOUT: int = 10
    INTERVAL: int = 1 * 60 * 60
    TAG_CHAINS: List[TagAddressChain] = []
    TAG_GET_ATTR: Optional[str] = None     # if need text from found tag - leave blank!
    ALERT: Type[AlertBase] = AlertSelect.TELEGRAM_DEF

    DIRPATH: pathlib.Path = pathlib.Path("USERDATA")
    CSV_DELIMITER: str = ";"

    # internal ----------------------------------
    _source_data: str = ""
    _tag_found_last_chain: Optional[BeautifulSoup] = None
    value_last: str = None
    value_prelast: str = None
    msg: str = ""
    alert_state: bool = None

    def __init__(self):
        super().__init__(daemon=False)

        self.DIRPATH = pathlib.Path(self.DIRPATH)
        self.FILEPATH = self.DIRPATH.joinpath(f"{self.NAME}.csv")

        self.DIRPATH.mkdir(exist_ok=True)
        if not self.FILEPATH.exists():
            self.FILEPATH.touch(exist_ok=True)
        self.value_last__load()

        self.start()

    @property
    def NAME(self):
        return self.__class__.__name__

    def value_last__load(self) -> None:
        with open(self.FILEPATH, "rt", newline='') as ofilepath:

            reader = csv.reader(ofilepath, delimiter=self.CSV_DELIMITER)
            result = None
            for line_parsed in reader:
                result = line_parsed[1]
            self.value_last = self.value_prelast = result

    def value_last__save(self) -> None:
        with open(self.FILEPATH, "a", newline='') as ofilepath:
            writer = csv.writer(ofilepath, delimiter=self.CSV_DELIMITER)
            writer.writerow([time.strftime("%Y.%m.%d %H:%M:%S"), self.value_last])

    def run(self):
        while True:
            if self.alert_state__check():
                self.ALERT(subj_suffix=self.NAME, body=self.msg)

            print(self.msg)
            time.sleep(self.INTERVAL)

    def alert_state__check(self) -> bool:
        """
        True - if need ALERT!
        the only one way to return False - all funcs get true(correctly finished) and old value == newValue.
        Otherwise, need send email!!!
        """
        result = True
        if all([
            self.reinit_values(),
            self.source__load(),
            self.source__get_tag(),
            self.tag__get_value(),
            ]):

            if self.value_last != self.value_prelast:
                self.msg += f"DETECTED CHANGE[{self.value_prelast}->{self.value_last}]"
                self.value_last__save()
            else:
                self.msg += f"SameState[{self.value_prelast}->{self.value_last}]"
                result = False

        self.alert_state = result
        return result

    def reinit_values(self) -> True:
        self.msg = ""
        self._source_data = ""
        self._tag_found_last_chain = None
        return True

    def source__load(self) -> bool:
        self._source_data = ""
        try:
            response = requests.get(self.URL, timeout=self.TIMEOUT)
            self._source_data = response.text
            return True
        except Exception as exx:
            self.msg += f"LOST URL {exx!r}"

    def source__get_tag(self) -> Optional[bool]:
        if self._source_data:
            try:
                self._tag_found_last_chain = BeautifulSoup(markup=self._source_data, features='html.parser')
            except Exception as exx:
                self.msg += f"[CRITICAL] can't parse {self._source_data=}\n{exx!r}"
                return
        else:
            self.msg += f"[CRITICAL] empty {self._source_data=}"
            return

        try:
            for chain in self.TAG_CHAINS:
                tags = self._tag_found_last_chain.find_all(name=chain.NAME, attrs=chain.ATTRS, string=chain.STRING, limit=chain.INDEX + 1)
                self._tag_found_last_chain = tags[chain.INDEX]
        except Exception as exx:
            self.msg += f"URL WAS CHANGED! can't find {chain=}\n{exx!r}"
            return

        return True

    def tag__get_value(self) -> Optional[bool]:
        if not self._tag_found_last_chain:
            return

        self.value_prelast = self.value_last

        if self.TAG_GET_ATTR is None:
            self.value_last = self._tag_found_last_chain.string
        else:
            self.value_last = self._tag_found_last_chain[self.TAG_GET_ATTR][0]

        self.value_last = self.value_last.strip()
        return True


# =====================================================================================================================
