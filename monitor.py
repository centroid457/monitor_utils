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
from email.header import Header

import smtplib


# =====================================================================================================================
class _Environs:
    """
    get environs from OS!
    if not exists some of them - RAISE!
    """
    # OVEWRITING -------------------------------
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

        self._environs_dict: Dict[str, Any] = {}

        for enveron_name in self.ENVS_REQUIRED:
            enveron_value = os.getenv(enveron_name, None)
            if enveron_value is not None:
                self._environs_dict.update({enveron_name: enveron_value})
                setattr(self, enveron_name, enveron_value)
            else:
                msg = f"[CRITICAL]there is no {enveron_name=} in OS! add it manually!!!"
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
        if self._smtp is None:
            print(f"\n _smtp_connect {self.__class__.__name__}")
            try:
                self._smtp = smtplib.SMTP_SSL(self.SMTP_SERVER, self.SMTP_PORT, timeout=5)
            except:
                pass

        if self._smtp is not None:
            result = self._smtp.login(self.ENV__MAIL_USER, self.ENV__MAIL_PWD)
            print(result)

        return result[0] in [235, 503]

    def _smtp_disconnect(self) -> None:
        if self._smtp:
            self._smtp.quit()
        self._smtp_clear()

    def _smtp_clear(self) -> None:
        self._smtp = None

    def _smtp_check_emply(self) -> bool:
        return self._smtp is None

    # MSG =============================================================================================================
    def smtp_send(self, subject: str, body: Any) -> bool:
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
        else:
            pass


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
    monitor_msg_body: Any = None

    # DONT TOUCH! -------------------------------
    def run(self):
        while True:
            if self.check_state():
                self.smtp_send(subject=f"[ALERT] {self.MONITOR_NAME}", body=self.monitor_msg_body)

            time.sleep(self.MONITOR_INTERVAL_SEC)

    # OVERWRITE -------------------------------
    def check_state(self) -> bool:
        raise NotImplementedError()


# =====================================================================================================================
class Monitor_DonorSvetofor(_MonitorURL):
    """
    MONITOR donor svetofor and alert when BloodCenter need your blood group!
    """
    # OVERWRITTEN NOW -------------------------------
    MONITOR_NAME: str = "DONOR_SVETOFOR"
    MONITOR_URL: str = "https://donor.mos.ru/donoru/donorskij-svetofor/"
    monitor_value_last: str = "green"

    # OVERWRITING NEXT -------------------------------
    DONOR_GROUP: str = "3+"

    def check_state(self) -> bool:
        response = requests.get(self.MONITOR_URL, timeout=10)
        soup = BeautifulSoup(markup=response.text, features='html.parser')

        svetofor_table = soup.find(name='table', attrs={"class": "donor-svetofor-restyle"})

        # print(svetofor_table)
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
        print()

        svetofor_value_tags = svetofor_table.find_all(name="td")
        # for tag in svetofor_value_tags:
        #     print(tag)

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

        self.monitor_msg_body = {}
        for i, td in enumerate(svetofor_value_tags, start=2):
            self.monitor_msg_body.update({f"{i // 2}{td.text[-1:]}": td.get("class")[0]})

        for key, value in self.monitor_msg_body.items():
            print(f"{key}={value}")
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
        print()

        value_new = self.monitor_msg_body.get(self.DONOR_GROUP)
        alert_state = value_new != self.monitor_value_last
        self.monitor_value_last = value_new

        print(f"[{self.MONITOR_NAME}]={alert_state}")
        return alert_state


# =====================================================================================================================
def main():
    Monitor_DonorSvetofor().start()


if __name__ == "__main__":
    main()
