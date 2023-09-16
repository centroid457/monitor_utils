# TODO: need save last value! maybe in file!

import time
from typing import *

import threading

import requests
from bs4 import BeautifulSoup

from alerts_msg import *


# =====================================================================================================================
class TagAddressChain(NamedTuple):
    """
    structure to use as one step of full chain for finding Tag
    all types used as any available variant for function Tag.find_all and actually passed directly to it!
    """
    NAME: str
    ATTRS: Dict[str, str]
    STRING: Optional[str]
    INDEX: int


# =====================================================================================================================
class MonitorURL(threading.Thread):
    """
    base class for final monitors!
    monitoring on URL some value.
    if found new value - remember it and send mail alert!
    """
    # SETTINGS -------------------------------
    URL: str = "https://mail.ru/"
    INTERVAL: int = 1 * 60 * 60
    TAG_CHAINS: List[TagAddressChain] = []
    TAG_GET_ATTR: Optional[str] = None     # if need text from found tag - leave blank!
    tag_value_last: Any = None  # if need first Alert - leave blank!

    ALERT: Union[AlertSmtp, Type[AlertSmtp]] = AlertSmtp

    # internal ----------------------------------
    _source_data: str = ""
    _tag_found_last_chain: Optional[BeautifulSoup] = None
    _tag_value_prelast: Any = None
    msg_body: str = ""
    alert_state: bool = None

    @property
    def NAME(self):
        return self.__class__.__name__

    # DONT TOUCH! -------------------------------
    def run(self):
        while True:
            if self.alert_state__check():
                self.ALERT(subj_suffix=self.NAME, body=self.msg_body)

            print(self.msg_body)
            time.sleep(self.INTERVAL)

    def reinit_values(self) -> True:
        self.msg_body = time.strftime("%Y.%m.%d %H:%M:%S=")
        self._source_data = ""
        self._tag_found_last_chain = None

        return True

    def source__load(self) -> bool:
        self._source_data = ""
        try:
            response = requests.get(self.URL, timeout=10)
            self._source_data = response.text
            return True
        except Exception as exx:
            self.msg_body += f"LOST URL {exx!r}"

    def source__apply_chain(self) -> Optional[bool]:
        if self._source_data:
            try:
                self._tag_found_last_chain = BeautifulSoup(markup=self._source_data, features='html.parser')
            except Exception as exx:
                self.msg_body += f"[CRITICAL] can't parse {self._source_data=}\n{exx!r}"
                return
        else:
            self.msg_body += f"[CRITICAL] empty {self._source_data=}"
            return

        try:
            for chain in self.TAG_CHAINS:
                tags = self._tag_found_last_chain.find_all(name=chain.NAME, attrs=chain.ATTRS, string=chain.STRING, limit=chain.INDEX + 1)
                self._tag_found_last_chain = tags[chain.INDEX]
        except Exception as exx:
            self.msg_body += f"URL WAS CHANGED! can't find {chain=}\n{exx!r}"
            return

        return True

    def tag__apply_value(self) -> Optional[bool]:
        if not self._tag_found_last_chain:
            return

        self._tag_value_prelast = self.tag_value_last

        if self.TAG_GET_ATTR is None:
            self.tag_value_last = self._tag_found_last_chain.string
        else:
            self.tag_value_last = self._tag_found_last_chain[self.TAG_GET_ATTR][0]

        return True

    # OVERWRITE -------------------------------
    def alert_state__check(self) -> bool:
        """
        True - if need ALERT!
        the only one way to return False - all funcs get true(correctly finished) and old value == newValue.
        Otherwise need send email!!!
        """
        result = True
        if all([
            self.reinit_values(),
            self.source__load(),
            self.source__apply_chain(),
            self.tag__apply_value(),
            ]):

            if self.tag_value_last != self._tag_value_prelast:
                self.msg_body += f"DETECTED CHANGE[{self._tag_value_prelast}->{self.tag_value_last}]"
            else:
                self.msg_body += f"SameState[{self._tag_value_prelast}->{self.tag_value_last}]"
                result = False

        self.alert_state = result
        return result


# =====================================================================================================================
if __name__ == "__main__":
    pass
