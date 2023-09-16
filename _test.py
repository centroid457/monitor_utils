import os
import pytest
import pathlib
import shutil
from tempfile import TemporaryDirectory
from typing import *
import threading

from monitor_utils import *


# =====================================================================================================================
def test__send_single():
    Monitor_DonorSvetofor().start()
    Monitor_CbrKeyRate().start()
    Monitor_ConquestS23_comments().start()
    # Monitor_Sportmaster_AdidasSupernova2M().start()


# =====================================================================================================================
