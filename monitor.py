"""
before using add _SmtpSender.ENVS_REQUIRED into your OS!
"""

import os
import time
from typing import *

import threading

import requests
from bs4 import BeautifulSoup

from email.mime.text import MIMEText

import smtplib


# =====================================================================================================================
class _Environs:
    """
    get environs from OS!
    if not exists some of them - RAISE!
    """
    # OVERWRITING NEXT -------------------------------
    ENVS_REQUIRED: List[str] = []
    """
    # add all ENVS with types STR!!! so usable in IDE!!!
    # EXAMPLE:
    ENVS_REQUIRED = ["ENV__MAIL_USER", "ENV__MAIL_PWD"]
    ENV__MAIL_USER: str
    ENV__MAIL_PWD: str
    """

    def __init__(self):
        super().__init__()

        for environ_name in self.ENVS_REQUIRED:
            environ_value = os.getenv(environ_name, None)
            if environ_value is not None:
                setattr(self, environ_name, environ_value)
            else:
                msg = f"[CRITICAL]there is no {environ_name=} in OS! add it manually!!!"
                print(msg)
                raise Exception(msg)


# =====================================================================================================================
class _SmtpSender(_Environs):
    """
    main class to work with smtp.
    """
    # OVERWRITTEN NOW -------------------------------
    ENVS_REQUIRED: List[str] = ["ENV__MAIL_USER", "ENV__MAIL_PWD"]
    ENV__MAIL_USER: str     # example@mail.ru
    ENV__MAIL_PWD: str      # use thirdPartyPwd!

    # OVERWRITING NEXT -------------------------------
    SMTP_SERVER = "smtp.mail.ru"
    SMTP_PORT = 465

    def __init__(self):
        super().__init__()

        self._smtp: Optional[smtplib.SMTP_SSL] = None

    # CONNECT =========================================================================================================
    def _smtp_connect(self) -> bool:
        result = None

        if self._smtp is None:
            print(f"_smtp_connect {self.__class__.__name__}")
            try:
                self._smtp = smtplib.SMTP_SSL(self.SMTP_SERVER, self.SMTP_PORT, timeout=5)
            except Exception as exx:
                print(f"[CRITICAL] CANT CONNECT {exx!r}")
                self._smtp_clear()

        if self._smtp is not None:
            try:
                result = self._smtp.login(self.ENV__MAIL_USER, self.ENV__MAIL_PWD)
            except Exception as exx:
                print(f"[CRITICAL] CANT CONNECT {exx!r}")

            print(result)

        return result and result[0] in [235, 503]

    def _smtp_disconnect(self) -> None:
        if self._smtp:
            self._smtp.quit()
        self._smtp_clear()

    def _smtp_clear(self) -> None:
        self._smtp = None

    def _smtp_check_empty(self) -> bool:
        return self._smtp is None

    # MSG =============================================================================================================
    def smtp_send(self, subject: str, body: Any) -> bool:
        result = False

        FROM = self.ENV__MAIL_USER
        TO = FROM
        SUBJECT = subject
        BODY = str(body)

        msg = MIMEText(BODY, 'plain')
        msg['Subject'] = SUBJECT
        msg["From"] = FROM
        msg["To"] = TO

        if self._smtp_connect():
            print(self._smtp.send_message(msg))
            print("-"*80)
            print(msg)
            print("-"*80)
            result = True
        else:
            pass    # don't add print msg! it's already ON!

        return result


# =====================================================================================================================
class _TagAddressChunk(NamedTuple):
    """
    structure to use as one step of full chain for finding Tag
    all types used as any available variant for function Tag.find_all and actually passed directly to it!
    """
    name: Any
    attrs: Any
    string: Any
    index: int


# =====================================================================================================================
class _MonitorURL(_SmtpSender, threading.Thread):
    """
    last interface!
    monitoring on URL some value.
    if found new value - remember it and send mail alert!
    """
    # OVERWRITING NEXT -------------------------------
    MONITOR_NAME: str = "MONITOR_NAME"
    MONITOR_URL: str = "https://mail.ru/"
    MONITOR_INTERVAL_SEC: int = 1*1*60
    MONITOR_TAG__FIND_CHAIN: List[_TagAddressChunk] = []
    MONITOR_TAG__ATTR_GET: Optional[str] = None     # if need text from found tag - leave blank!
    _monitor_source: str = ""
    _monitor_tag__found_last: Optional[BeautifulSoup] = None
    monitor_tag__value_last: Any = None  # if need first Alert - leave blank!
    _monitor_tag__value_prelast: Any = None

    _monitor_msg_body: str = ""

    # DONT TOUCH! -------------------------------
    def run(self):
        while True:
            if self.monitor_check_state_need_alert():
                self.smtp_send(subject=f"[ALERT] {self.MONITOR_NAME}", body=self._monitor_msg_body)

            print(self._monitor_msg_body)
            time.sleep(self.MONITOR_INTERVAL_SEC)

    def monitor_reinit_values(self) -> True:
        self._monitor_msg_body = time.strftime("%Y.%m.%d %H:%M:%S=")
        self._monitor_source = ""
        self._monitor_tag__found_last = None

        return True

    def monitor_source__load(self) -> bool:
        self._monitor_source = ""
        try:
            response = requests.get(self.MONITOR_URL, timeout=10)
            self._monitor_source = response.text
            return True
        except Exception as exx:
            self._monitor_msg_body += f"LOST URL {exx!r}"

    def monitor_source__apply_chain(self) -> Optional[bool]:
        if self._monitor_source:
            try:
                self._monitor_tag__found_last = BeautifulSoup(markup=self._monitor_source, features='html.parser')
            except Exception as exx:
                self._monitor_msg_body += f"URL WAS corrupted! can't parse {self._monitor_source=}\n{exx!r}"
                return

        try:
            for chunk in self.MONITOR_TAG__FIND_CHAIN:
                self._monitor_tag__found_last = self._monitor_tag__found_last.find_all(name=chunk.name, attrs=chunk.attrs, string=chunk.string)[chunk.index]
        except Exception as exx:
            self._monitor_msg_body += f"URL WAS CHANGED! can't find {chunk=}\n{exx!r}"
            return

        return True

    def monitor_tag__apply_value(self) -> Optional[bool]:
        if not self._monitor_tag__found_last:
            return

        self._monitor_tag__value_prelast = self.monitor_tag__value_last

        if self.MONITOR_TAG__ATTR_GET is None:
            self.monitor_tag__value_last = self._monitor_tag__found_last.string
        else:
            self.monitor_tag__value_last = self._monitor_tag__found_last[self.MONITOR_TAG__ATTR_GET][0]

        return True

    # OVERWRITE -------------------------------
    def monitor_check_state_need_alert(self) -> bool:
        """
        True - if need ALERT!
        the only one way to return False - all funcs get true(correctly finished) and old value == newValue.
        Otherwise need send email!!!
        """
        if all([
            self.monitor_reinit_values(),
            self.monitor_source__load(),
            self.monitor_source__apply_chain(),
            self.monitor_tag__apply_value(),
            ]):

            if self.monitor_tag__value_last != self._monitor_tag__value_prelast:
                self._monitor_msg_body += f"DETECTED CHANGE[{self._monitor_tag__value_prelast}->{self.monitor_tag__value_last}]"
            else:
                self._monitor_msg_body += f"SameState[{self._monitor_tag__value_prelast}->{self.monitor_tag__value_last}]"
                return False

        return True


# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================
class Monitor_DonorSvetofor(_MonitorURL):
    """
    MONITOR donor svetofor and alert when BloodCenter need your blood group!

    # STRUCTURE to find -------------------------------------
    <table class="donor-svetofor-restyle">
        <tbody>
            <tr>
                <th colspan="2">O (I)</th>
                <th colspan="2">A (II)</th>
                <th colspan="2">B (III)</th>
                <th colspan="2">AB (IV)</th>
            </tr>
            <tr>
                <td class="green">Rh +</td>
                <td class="green">Rh –</td>
                <td class="green">Rh +</td>
                <td class="yellow">Rh –</td>
                <td class="green">Rh +</td>
                <td class="yellow">Rh –</td>
                <td class="red">Rh +</td>
                <td class="red">Rh –</td>
            </tr>
        </tbody>
    </table>
    """
    # OVERWRITING NEXT -------------------------------
    # KEEP FIRST!
    DONOR_BLOOD_GROUP: int = 3
    DONOR_BLOOD_RH: str = "+"

    # OVERWRITTEN NOW -------------------------------
    MONITOR_NAME = "DONOR_SVETOFOR"
    MONITOR_URL = "https://donor.mos.ru/donoru/donorskij-svetofor/"
    MONITOR_TAG__FIND_CHAIN = [
        _TagAddressChunk("table", {"class": "donor-svetofor-restyle"}, None, 0),
        _TagAddressChunk("td", {}, f"Rh {DONOR_BLOOD_RH}", DONOR_BLOOD_GROUP - 1),
    ]
    MONITOR_TAG__ATTR_GET = "class"
    monitor_tag__value_last = "green"
    MONITOR_INTERVAL_SEC = 1*60*60


# =====================================================================================================================
def main():
    Monitor_DonorSvetofor().start()


if __name__ == "__main__":
    main()
