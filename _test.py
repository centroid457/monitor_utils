import os
import pytest
import pathlib
import shutil
from tempfile import TemporaryDirectory
from typing import *
import threading

from monitor_utils import *


# =====================================================================================================================
# TODO: create better/auto test!


# =====================================================================================================================
def test__url_tag():
    Monitor_DonorSvetofor()
    Monitor_CbrKeyRate()
    Monitor_ConquestS23_comments()

    # Monitor_Sportmaster_AdidasSupernova2M()


def test__imap():
    MonitorImap()


# =====================================================================================================================
