from typing import *
from .monitor_url_tag import *


# =====================================================================================================================
class Monitor_DonorSvetofor(MonitorUrlTag):
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
    URL = "https://donor.mos.ru/donoru/donorskij-svetofor/"
    TAG_CHAINS = [
        TagAddressChain("table", {"class": "donor-svetofor-restyle"}, None, 0),
        TagAddressChain("td", {}, f"Rh {DONOR_BLOOD_RH}", DONOR_BLOOD_GROUP - 1),
    ]
    TAG_GET_ATTR = "class"
    tag_value_last = "green"


# =====================================================================================================================
class Monitor_CbrKeyRate(MonitorUrlTag):
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
class Monitor_ConquestS23_comments(MonitorUrlTag):
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
class Monitor_Sportmaster_AdidasSupernova2M(MonitorUrlTag):
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
