import os
import pytest
import pathlib
import shutil
from tempfile import TemporaryDirectory
from typing import *
import threading

from monitor_utils import *
from alerts_msg import *


# =====================================================================================================================
# TODO: create full auto test!


# =====================================================================================================================
def test__url_tag():
    Monitor_DonorSvetofor()
    Monitor_CbrKeyRate()
    Monitor_ConquestS23_comments()

    # Monitor_Sportmaster_AdidasSupernova2M()

@pytest.mark.parametrize(argnames="pattern", argvalues=[None, r"\[ALERT\]test1"])
def test__imap(pattern):
    subj_suffix = "test1"

    AlertSmtp(subj_suffix=subj_suffix)

    victim = MonitorImap
    victim.stop = True
    victim.SUBJECT_REGEXP = pattern

    for i in range(3):
        victim_inst = victim()
        victim_inst.wait_step(1)
        if f"[ALERT]{subj_suffix}" in victim_inst._detected:
            break

    assert f"[ALERT]{subj_suffix}" in victim_inst._detected


# =====================================================================================================================
