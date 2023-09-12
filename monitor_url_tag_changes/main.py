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
    # OVERWRITING NEXT -------------------------------
    URL: str = "https://mail.ru/"
    INTERVAL: int = 1 * 60 * 60
    TAG_CHAINS: List[TagAddressChain] = []
    TAG_GET_ATTR: Optional[str] = None     # if need text from found tag - leave blank!
    tag_value_last: Any = None  # if need first Alert - leave blank!

    ALERT_CLS: Union[AlertSmtp, Type[AlertSmtp]] = AlertSmtp

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
                self.ALERT_CLS(subj_suffix=self.NAME, body=self.msg_body)

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
pass    # IMPLEMENTATIONS =============================================================================================
pass    # IMPLEMENTATIONS =============================================================================================
pass    # IMPLEMENTATIONS =============================================================================================
pass    # IMPLEMENTATIONS =============================================================================================
pass    # IMPLEMENTATIONS =============================================================================================
pass    # IMPLEMENTATIONS =============================================================================================


# IMPLEMENTATIONS =====================================================================================================

# =====================================================================================================================
class Monitor_DonorSvetofor(MonitorURL):
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
    URL = "https://donor.mos.ru/donoru/donorskij-svetofor/"
    TAG_CHAINS = [
        TagAddressChain("table", {"class": "donor-svetofor-restyle"}, None, 0),
        TagAddressChain("td", {}, f"Rh {_donor_blood_rh}", _donor_blood_group - 1),
    ]
    TAG_GET_ATTR = "class"
    tag_value_last = "green"


# =====================================================================================================================
class Monitor_CbrKeyRate(MonitorURL):
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
    URL = "https://cbr.ru/hd_base/KeyRate/"
    TAG_CHAINS = [
        TagAddressChain("div", {"class": "table-wrapper"}, None, 0),
        TagAddressChain("td", {}, None, 1),
    ]
    TAG_GET_ATTR = None
    tag_value_last = "12,00"


# =====================================================================================================================
class Monitor_ConquestS23_comments(MonitorURL):
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
    URL = "https://exgad.ru/products/conquest-s23"
    TAG_CHAINS = [
        TagAddressChain("div", {"class": "comments-tab__quatity"}, None, 0),
    ]
    TAG_GET_ATTR = None
    tag_value_last = "48"


# =====================================================================================================================
class Monitor_Sportmaster_AdidasSupernova2M(MonitorURL):
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
    URL = "https://www.sportmaster.ru/product/29647730299/"
    TAG_CHAINS = [
        TagAddressChain("span", {"class": "sm-amount__value"}, None, 0),
    ]
    TAG_GET_ATTR = None
    tag_value_last = "13 699 ₽"
    INTERVAL = 1 * 60 * 60


# =====================================================================================================================
if __name__ == "__main__":
    Monitor_DonorSvetofor().start()
    Monitor_CbrKeyRate().start()
    Monitor_ConquestS23_comments().start()
    # Monitor_Sportmaster_AdidasSupernova2M().start()
