# monitor_utils

## IMPORTANT!
NOT ALL WEBSITES WORKS! Sportmaster/Acra-rating/...

## INSPIRATION
Suppose you wish to give blood to the Center.
So nowadays you need to make an appointment by website, BUT you can't do this while the Center actually don't need your group.
Group necessity shown on Center website and called DonorSvetofor.
And as result you need monitoring it manually, because there are no news, email notifications, subscriptions.
It's not difficult but if you do it as day routine (even once a day) its quite distracting.

So I created it first as Monitor_DonorSvetofor


## Features
1. Threading each monitor
2. monitor 
   * website data changes
      * tag text
      * tag attribute
   * email received with subject (by regexp) in exact folder
3. Email/Telegram alert if
   * monitored data changed (from last state)
   * html structure was changed so parsing can't be finished
   * url became unreachable


## License
See the [LICENSE](LICENSE) file for license rights and limitations (MIT).


## Release history
See the [HISTORY.md](HISTORY.md) file for release history.


## Installation
```commandline
pip install monitor-utils
```

## Import
```python
from monitor_utils import *
```


## GUIDE
See tests and source for other examples.

### 1. change or apply auth private data (see `private_values`)

### 2. create new desired class for your purpose
See [monitor_url_tag__implements.py](monitor_utils%2Fmonitor_url_tag__implements.py) for examples.

#### MonitorUrlTag
```python
from monitor_utils import *

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
    URL = "https://cbr.ru/hd_base/KeyRate/"
    TAG_CHAINS = [
        TagAddressChain("div", {"class": "table-wrapper"}, None, 0),
        TagAddressChain("td", {}, None, 1),
    ]
    TAG_GET_ATTR = None
    value_last = "12,00"
```

#### MonitorImap
see source