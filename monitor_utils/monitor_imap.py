import time
from typing import *
import threading
import re

import imaplib
import email

from private_values import *
from alerts_msg import *


# =====================================================================================================================
# TODO: SEPARATE BASE+INTERFACE!
# TODO: realise MARK_AS_READ = False!
# TODO: start reading from last read not just unseen!


# =====================================================================================================================
class AddressImap(NamedTuple):
    ADDR: str
    PORT: int


class ServersImap:
    MAIL_RU: AddressImap = AddressImap("imap.mail.ru", 993)


# =====================================================================================================================
class MonitorImap(threading.Thread):
    INTERVAL: int = 1 * 1 * 10

    SERVER: AddressImap = ServersImap.MAIL_RU
    AUTH: PrivateJsonAuth = PrivateJsonAuth().get_section("AUTH_EMAIL")
    FOLDER: Optional[str] = None    # None - for Inbox/Входящие!
    SUBJECT_REGEXP: Optional[str] = None    # None - for all, r"\[ALERT\]test1"
    MARK_AS_READ: bool = True

    ALERT: Type[AlertBase] = AlertSelect.TELEGRAM_DEF
    _conn: Optional[imaplib.IMAP4_SSL] = None
    stop: Optional[bool] = None
    step: int = 0

    def __init__(self):
        super().__init__(daemon=True)

        self._detected: List[str] = []
        self.start()

    # CONNECT =========================================================================================================
    def _connect(self) -> Union[bool, NoReturn]:
        if self._conn:
            return True

        print(f"\n _connect {self.__class__.__name__}")
        try:
            self._conn = imaplib.IMAP4_SSL(self.SERVER.ADDR, self.SERVER.PORT)
        except:
            pass

        if self._conn:
            print(self._conn.login(self.AUTH.USER, self.AUTH.PWD))
            self.folder_select(self.FOLDER)
            print(self._conn.search(None, 'UNSEEN'))  # ('OK', [b''])

        return bool(self._conn)

    def folder_select(self, name: Optional[str] = None) -> Optional[NoReturn]:
        try:
            if name:
                print(self._conn.select(name))  # ('OK', [b'5'])
            else:
                print(self._conn.select())  # ('OK', [b'5'])

        except Exception as exx:
            msg = f"[CRITICAL] not exists [folder={name}]"
            print(msg)
            raise Exception(msg)
            # raise exx

    def _disconnect(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn.logout()

    def _clear(self) -> None:
        self._conn = None

    def _conn_check_empty(self) -> bool:
        return self._conn is None

    # START ===========================================================================================================
    def run(self):
        while True:
            if self._connect():
                subjects = self.get_unseen_subject_list()
                for subject in subjects:
                    if not self.SUBJECT_REGEXP or re.fullmatch(self.SUBJECT_REGEXP, subject):
                        self._detected.append(subject)
                        self.ALERT(subject, subj_suffix=f"{self.__class__.__name__}/{self.FOLDER or 'Inbox'}")

            self._disconnect()

            self.step += 1

            if self.stop:
                return
            time.sleep(self.INTERVAL)
            if self.stop:
                return

    def wait_step(self, step_finish: Optional[int] = None, sleep: int = 1) -> None:
        if step_finish is None:
            step_finish = self.step + 1

        while self.step < step_finish:
            time.sleep(sleep)

    # MAIL ============================================================================================================
    def get_unseen_subject_list(self) -> List[str]:
        result = []

        try:
            for num in self._conn.search(None, "UNSEEN")[1][0].split():    # UNSEEN/ALL
                _, msg = self._conn.fetch(num, '(RFC822)')
                msg = email.message_from_bytes(msg[0][1])

                try:
                    # has russian
                    subject = email.header.decode_header(msg["Subject"])[0][0].decode()
                except Exception as exx:
                    # english only!
                    subject = msg["Subject"]

                subject = subject or ""
                result.append(subject)
        except Exception as exx:
            self._clear()

        return result

    # UNSORTED ========================================================================================================
    def _data_blocks__print(self):
        _, msg = self._conn.fetch("6", '(RFC822)')
        msg = email.message_from_bytes(msg[0][1])
        print(type(msg))  # <class 'email.message.Message'>
        print(list(
            msg))  # ['Delivered-To', 'Return-path', 'Received-SPF', 'Received', 'Received', 'DKIM-Signature', 'DKIM-Signature', 'Precedence', 'List-Id', 'List-Issue', 'List-Unsubscribe', 'List-Subscribe', 'List-Archive', 'List-Post', 'X-Felis-L', 'X-rpcampaign', 'X-Mailru-Msgtype', 'Feedback-Id', 'Message-Id', 'Date', 'From', 'To', 'Subject', 'MIME-Version', 'Content-Type', 'Content-Transfer-Encoding', 'X-Mailru-Src', 'X-4EC0790', 'X-6b629377', 'X-7564579A', 'X-77F55803', 'X-7FA49CB5', 'X-C1DE0DAB', 'X-C8649E89', 'X-D57D3AED', 'X-F696D7D5', 'X-Mailru-BIMI-Organization', 'X-Mailru-Dmarc-Auth', 'X-Mailru-ThreadID', 'X-Mras', 'X-Spam', 'Authentication-Results', 'X-Mailru-Intl-Transport']

        for name in list(msg):
            print(f"[{name}]===[{msg[name]}]")


# =====================================================================================================================
