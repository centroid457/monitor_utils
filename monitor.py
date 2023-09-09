# TODO: need save last value! maybe in file!
"""
before using add _SmtpSender.ENVirons into your OS!
"""

import time
from typing import *

import threading

import requests
from bs4 import BeautifulSoup

from email.mime.text import MIMEText

import smtplib

from private_values import PrivateValues


# =====================================================================================================================
class _SmtpSender(PrivateValues):
    """
    main class to work with smtp.
    """
    PV___SMTP_USER: str = None    # example@mail.ru
    PV___SMTP_PWD: str = None     # use thirdPartyPwd!

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
                result = self._smtp.login(self.PV___SMTP_USER, self.PV___SMTP_PWD)
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

        FROM = self.PV___SMTP_USER
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
    base class for final monitors!
    monitoring on URL some value.
    if found new value - remember it and send mail alert!
    """
    # OVERWRITING NEXT -------------------------------
    MONITOR_URL: str = "https://mail.ru/"
    MONITOR_INTERVAL_SEC: int = 1*60*60
    MONITOR_TAG__FIND_CHAIN: List[_TagAddressChunk] = []
    MONITOR_TAG__ATTR_GET: Optional[str] = None     # if need text from found tag - leave blank!
    monitor_tag__value_last: Any = None  # if need first Alert - leave blank!

    # internal ----------------------------------
    _monitor_source: str = ""
    _monitor_tag__found_last: Optional[BeautifulSoup] = None
    _monitor_tag__value_prelast: Any = None
    monitor_msg_body: str = ""
    monitor_alert_state: bool = None

    @property
    def MONITOR_NAME(self):
        return self.__class__.__name__

    # DONT TOUCH! -------------------------------
    def run(self):
        while True:
            if self.monitor_alert_state__check():
                self.smtp_send(subject=f"[ALERT]{self.MONITOR_NAME}", body=self.monitor_msg_body)

            print(self.monitor_msg_body)
            time.sleep(self.MONITOR_INTERVAL_SEC)

    def monitor_reinit_values(self) -> True:
        self.monitor_msg_body = time.strftime("%Y.%m.%d %H:%M:%S=")
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
            self.monitor_msg_body += f"LOST URL {exx!r}"

    def monitor_source__apply_chain(self) -> Optional[bool]:
        if self._monitor_source:
            try:
                self._monitor_tag__found_last = BeautifulSoup(markup=self._monitor_source, features='html.parser')
            except Exception as exx:
                self.monitor_msg_body += f"[CRITICAL] can't parse {self._monitor_source=}\n{exx!r}"
                return
        else:
            self.monitor_msg_body += f"[CRITICAL] empty {self._monitor_source=}"
            return

        try:
            for chunk in self.MONITOR_TAG__FIND_CHAIN:
                tags = self._monitor_tag__found_last.find_all(name=chunk.name, attrs=chunk.attrs, string=chunk.string, limit=chunk.index + 1)
                self._monitor_tag__found_last = tags[chunk.index]
        except Exception as exx:
            self.monitor_msg_body += f"URL WAS CHANGED! can't find {chunk=}\n{exx!r}"
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
    def monitor_alert_state__check(self) -> bool:
        """
        True - if need ALERT!
        the only one way to return False - all funcs get true(correctly finished) and old value == newValue.
        Otherwise need send email!!!
        """
        result = True
        if all([
            self.monitor_reinit_values(),
            self.monitor_source__load(),
            self.monitor_source__apply_chain(),
            self.monitor_tag__apply_value(),
            ]):

            if self.monitor_tag__value_last != self._monitor_tag__value_prelast:
                self.monitor_msg_body += f"DETECTED CHANGE[{self._monitor_tag__value_prelast}->{self.monitor_tag__value_last}]"
            else:
                self.monitor_msg_body += f"SameState[{self._monitor_tag__value_prelast}->{self.monitor_tag__value_last}]"
                result = False

        self.monitor_alert_state = result
        return result


# =====================================================================================================================
pass    # IMPLEMENTATIONS =============================================================================================
pass    # IMPLEMENTATIONS =============================================================================================
pass    # IMPLEMENTATIONS =============================================================================================
pass    # IMPLEMENTATIONS =============================================================================================
pass    # IMPLEMENTATIONS =============================================================================================
pass    # IMPLEMENTATIONS =============================================================================================


# IMPLEMENTATIONS =====================================================================================================

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
    _donor_blood_group: int = 3
    _donor_blood_rh: str = "+"

    # OVERWRITTEN NOW -------------------------------
    MONITOR_URL = "https://donor.mos.ru/donoru/donorskij-svetofor/"
    MONITOR_TAG__FIND_CHAIN = [
        _TagAddressChunk("table", {"class": "donor-svetofor-restyle"}, None, 0),
        _TagAddressChunk("td", {}, f"Rh {_donor_blood_rh}", _donor_blood_group - 1),
    ]
    MONITOR_TAG__ATTR_GET = "class"
    monitor_tag__value_last = "green"


# =====================================================================================================================
class Monitor_CbrKeyRate(_MonitorURL):
    """
    MONITOR CentralBankRussia KeyRate

    # STRUCTURE to find -------------------------------------
<div class="table-wrapper">
  <div class="table-caption gray">% годовых</div>
  <div class="table">
    <table class="data">
      <tr>
        <th>Дата</th>
        <th>Ставка</th>
      </tr>
      <tr>
        <td>17.08.2023</td>
        <td>12,00</td>
      </tr>
      <tr>
        <td>16.08.2023</td>
        <td>12,00</td>
      </tr>
      <tr>
        <td>15.08.2023</td>
        <td>12,00</td>
      </tr>
      <tr>
        <td>14.08.2023</td>
        <td>8,50</td>
      </tr>
      <tr>
        <td>11.08.2023</td>
        <td>8,50</td>
      </tr>
      <tr>
        <td>10.08.2023</td>
        <td>8,50</td>
      </tr>
    </table>
  </div>
  <div class="table-caption">
    <p>
	  Данные доступны с  17.09.2013 по 17.08.2023.
	  </p>
  </div>
</div>
    """
    # OVERWRITING NEXT -------------------------------
    # KEEP FIRST!

    # OVERWRITTEN NOW -------------------------------
    MONITOR_URL = "https://cbr.ru/hd_base/KeyRate/"
    MONITOR_TAG__FIND_CHAIN = [
        _TagAddressChunk("div", {"class": "table-wrapper"}, None, 0),
        _TagAddressChunk("td", {}, None, 1),
    ]
    MONITOR_TAG__ATTR_GET = None
    monitor_tag__value_last = "12,00"


# =====================================================================================================================
class Monitor_ConquestS23_comments(_MonitorURL):
    """
    MONITOR CentralBankRussia KeyRate

    # STRUCTURE to find -------------------------------------
<div class="table-wrapper">
  <div class="table-caption gray">% годовых</div>
  <div class="table">
    <table class="data">
      <tr>
        <th>Дата</th>
        <th>Ставка</th>
      </tr>
      <tr>
        <td>17.08.2023</td>
        <td>12,00</td>
      </tr>
      <tr>
        <td>16.08.2023</td>
        <td>12,00</td>
      </tr>
      <tr>
        <td>15.08.2023</td>
        <td>12,00</td>
      </tr>
      <tr>
        <td>14.08.2023</td>
        <td>8,50</td>
      </tr>
      <tr>
        <td>11.08.2023</td>
        <td>8,50</td>
      </tr>
      <tr>
        <td>10.08.2023</td>
        <td>8,50</td>
      </tr>
    </table>
  </div>
  <div class="table-caption">
    <p>
	  Данные доступны с  17.09.2013 по 17.08.2023.
	  </p>
  </div>
</div>
    """
    # OVERWRITING NEXT -------------------------------
    # KEEP FIRST!

    # OVERWRITTEN NOW -------------------------------
    MONITOR_URL = "https://exgad.ru/products/conquest-s23"
    MONITOR_TAG__FIND_CHAIN = [
        _TagAddressChunk("div", {"class": "comments-tab__quatity"}, None, 0),
    ]
    MONITOR_TAG__ATTR_GET = None
    monitor_tag__value_last = "48"


# =====================================================================================================================
class Monitor_Sportmaster_AdidasSupernova2M(_MonitorURL):
    """
    MONITOR SportMasterPrices

    # STRUCTURE to find -------------------------------------
    <span data-selenium="amount" class="sm-amount__value">13 699 ₽</span>
    """
    # TODO: need resolve StatusCode401
    # OVERWRITING NEXT -------------------------------
    # KEEP FIRST!

    # OVERWRITTEN NOW -------------------------------
    MONITOR_NAME = "SPORTMASTER_AdidasSupernova2M"
    MONITOR_URL = "https://www.sportmaster.ru/product/29647730299/"
    MONITOR_TAG__FIND_CHAIN = [
        _TagAddressChunk("span", {"class": "sm-amount__value"}, None, 0),
    ]
    MONITOR_TAG__ATTR_GET = None
    monitor_tag__value_last = "13 699 ₽"
    MONITOR_INTERVAL_SEC = 1*60*60


# =====================================================================================================================
def main():
    Monitor_DonorSvetofor().start()
    Monitor_CbrKeyRate().start()
    Monitor_ConquestS23_comments().start()
    # Monitor_Sportmaster_AdidasSupernova2M().start()


if __name__ == "__main__":
    main()
