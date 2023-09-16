# monitor_utils


## INSPIRATION
Suppose you wish to give blood to the Center.
So nowadays you need to make an appointment by website, BUT you can't do this while the Center actually don't need your group.
Group necessity shown on Center website and called DonorSvetofor.
And as result you need monitoring it manually, because there are no news, email notifications, subscriptions.
It's not difficult but if you do it as day routine (even once a day) its quite distracting.

So I created it first as Monitor_DonorSvetofor


## Features
1. Threading each monitor
2. monitor website data changes
   * tag text
   * tag attribute
3. Email alert if
   * monitored data changed (from last state)
   * html structure was changed so parsing can't be finished
   * url became unreachable


## IMPORTANT
Now it works as Monitor_DonorSvetofor GBUZ "O.K. Gavrilov DZM Blood Center".  
For each new monitor (URL) you need to create new instance and change settings.


## What do you need to use it as Monitor_DonorSvetofor
1. install python
2. download project
3. apply project requirements
4. add ENVIRONS on your OS for your email account (log/pwd)
5. add script to OS autostart
6. correct your BloodGroup and RH directly in code
7. start script
8. wait email notification



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

### ___
#### 1. add new ___ if not exists