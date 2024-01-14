from typing import *


# =====================================================================================================================
class PROJECT:
    # AUX --------------------------------------------------
    _VERSION_TEMPLATE: Tuple[int] = (0, 0, 2)

    # AUTHOR -----------------------------------------------
    AUTHOR_NAME: str = "Andrei Starichenko"
    AUTHOR_EMAIL: str = "centroid@mail.ru"
    AUTHOR_HOMEPAGE: str = "https://github.com/centroid457/"

    # PROJECT ----------------------------------------------
    NAME_IMPORT: str = "monitor_utils"
    NAME_INSTALL: str = NAME_IMPORT.replace("_", "-")
    KEYWORDS: List[str] = [
        "monitor changes", "monitor data",
        "url changes", "url tag changes", "url monitor",
        "imap changes", "email changes", "imap monitor", "email monitor",
        "alerts", "notifications", "email alerts", "telegram alerts",
    ]
    CLASSIFIERS_TOPICS_ADD: List[str] = [
        # "Topic :: Communications",
        # "Topic :: Communications :: Email",
    ]
    # GIT --------------------------------------------------
    DESCRIPTION_SHORT: str = "monotir exact data (urlTag/Email) and alert on changes by email/telegram (threading)"

    # README -----------------------------------------------
    pass

    # add DOUBLE SPACE at the end of all lines! for correct representation in MD-viewers
    DESCRIPTION_LONG: str = """
## IMPORTANT!
NOT ALL WEBSITES WORKS! Sportmaster/Acra-rating/...

## INSPIRATION
Suppose you wish to give blood to the Center.
So nowadays you need to make an appointment by website, BUT you can't do this while the Center actually don't need your group.
Group necessity shown on Center website and called DonorSvetofor.
And as result you need monitoring it manually, because there are no news, email notifications, subscriptions.
It's not difficult but if you do it as day routine (even once a day) its quite distracting.

So I created it first as Monitor_DonorSvetofor
    """
    FEATURES: List[str] = [
        # "feat1",
        # ["feat2", "block1", "block2"],

        "Threading each monitor",

        ["monitor",
         "website data changes (tag text/attribute)",
         "email received with subject (by regexp) in exact folder", ]

        ["Email/Telegram alert if",
        "monitored data changed (from last state)",
        "html structure was changed so parsing can't be finished",
        "url became unreachable",]

    ]

    # HISTORY -----------------------------------------------
    VERSION: Tuple[int, int, int] = (0, 0, 5)
    VERSION_STR: str = ".".join(map(str, VERSION))
    TODO: List[str] = [
        "..."
    ]
    FIXME: List[str] = [
        "..."
    ]
    NEWS: List[str] = [
        "apply new pypi template"
    ]


# =====================================================================================================================
if __name__ == '__main__':
    pass


# =====================================================================================================================
