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
class Test_UrlTag:
    def test__1(self):
        Monitor_DonorSvetofor()

    def test__2(self):
        Monitor_CbrKeyRate()

    def test__3(self):
        Monitor_ConquestS23_comments()

    def test__4(self):
        Monitor_Sportmaster_AdidasSupernova2M()

    def test__5(self):
        Monitor_AcraRaiting_GTLC()


# =====================================================================================================================
@pytest.mark.parametrize(argnames="pattern", argvalues=[None, r"\[ALERT\]test1"])
def test__imap(pattern):
    _subj_name = "test1"

    AlertSmtp(_subj_name=_subj_name)

    victim = MonitorImap
    victim.stop_flag = True
    victim.SUBJECT_REGEXP = pattern

    for i in range(3):
        victim_inst = victim()
        victim_inst.wait_cycle()
        if f"[ALERT]{_subj_name}" in victim_inst._detected:
            break

    assert f"[ALERT]{_subj_name}" in victim_inst._detected


# =====================================================================================================================
# Monitor_DonorSvetofor()
# Monitor_CbrKeyRate()
Monitor_ConquestS23_comments()
# Monitor_AcraRaiting_GTLC()
