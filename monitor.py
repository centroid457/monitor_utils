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
    monitor_value_last: Any = None
    monitor_msg_body: str = ""

    # DONT TOUCH! -------------------------------
    def run(self):
        while True:
            if self.check_state():
                self.smtp_send(subject=f"[ALERT] {self.MONITOR_NAME}", body=self.monitor_msg_body)

            time.sleep(self.MONITOR_INTERVAL_SEC)

    # OVERWRITE -------------------------------
    def check_state(self) -> bool:
        """
        True - if need ALERT!
        """
        raise NotImplementedError()


# =====================================================================================================================
# =====================================================================================================================
# =====================================================================================================================
class Monitor_DonorSvetofor(_MonitorURL):
    """
    MONITOR donor svetofor and alert when BloodCenter need your blood group!
    """
    # OVERWRITTEN NOW -------------------------------
    MONITOR_NAME: str = "DONOR_SVETOFOR"
    MONITOR_URL: str = "https://donor.mos.ru/donoru/donorskij-svetofor/"
    monitor_value_last: str = "green"
    MONITOR_INTERVAL_SEC: int = 1*60*60

    # OVERWRITING NEXT -------------------------------
    DONOR_GROUP: str = "3+"

    def check_state(self) -> bool:
        self.monitor_msg_body = time.strftime("%Y.%m.%d %H:%M:%S=")
        donor_groups: Dict[str, str] = {}

        try:
            response = requests.get(self.MONITOR_URL, timeout=10)
            html_text = response.text
            soup = BeautifulSoup(markup=html_text, features='html.parser')
        except Exception as exx:
            self.monitor_msg_body += f"LOST URL {exx!r}"
            return True

        tag_name = 'table'
        svetofor_table = soup.find(name=tag_name, attrs={"class": "donor-svetofor-restyle"})
        if not svetofor_table:
            self.monitor_msg_body += f"URL WAS CHANGED! cant find {tag_name=}"
            return True
        # print(svetofor_table)
        # print()
        """
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

        tag_name = "td"
        svetofor_value_tags = svetofor_table.find_all(name=tag_name)
        if not svetofor_value_tags:
            self.monitor_msg_body += f"URL WAS CHANGED! cant find {tag_name=}"
            return True
        if len(svetofor_value_tags) != 8:
            self.monitor_msg_body += f"URL WAS CHANGED! not enough {len(svetofor_value_tags)=}"
            return True
        # for tag in svetofor_value_tags:
        #     print(tag)
        # print()
        """
        <td class="green">Rh +</td>
        <td class="green">Rh –</td>
        <td class="green">Rh +</td>
        <td class="yellow">Rh –</td>
        <td class="green">Rh +</td>
        <td class="yellow">Rh –</td>
        <td class="red">Rh +</td>
        <td class="red">Rh –</td>
        """

        for i, td in enumerate(svetofor_value_tags, start=2):
            donor_groups.update({f"{i // 2}{td.text[-1:]}": td.get("class")[0]})
        # for key, value in donor_groups.items():
        #     print(f"{key}={value}")
        # print()
        """
        1+=green
        1–=green
        2+=green
        2–=yellow
        3+=green
        3–=yellow
        4+=red
        4–=red
        """

        value_new = donor_groups.get(self.DONOR_GROUP)
        alert_state = value_new != self.monitor_value_last

        if alert_state:
            self.monitor_msg_body += f"DETECTED CHANGE[{self.DONOR_GROUP}//{self.monitor_value_last}->{value_new}]"
        else:
            self.monitor_msg_body += f"SameState[{self.DONOR_GROUP}//{self.monitor_value_last}->{value_new}]"

        self.monitor_msg_body += f"{donor_groups}"

        print(self.monitor_msg_body)
        self.monitor_value_last = value_new
        return alert_state


# =====================================================================================================================
def main():
    Monitor_DonorSvetofor().start()


if __name__ == "__main__":
    main()
