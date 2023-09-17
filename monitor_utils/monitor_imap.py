import time
from typing import *
import threading
import re

import imaplib
import email

from private_values import *
from alerts_msg import *


# =====================================================================================================================
# TODO: realise MARK_AS_READ = False!


# =====================================================================================================================
class AddressImap(NamedTuple):
    ADDR: str
    PORT: int


class ServersImap:
    MAIL_RU: AddressImap = AddressImap("imap.mail.ru", 993)


# =====================================================================================================================
class MonitorImapMailSubjects(threading.Thread):
    INTERVAL: int = 1 * 1 * 10

    SERVER: AddressImap = ServersImap.MAIL_RU
    AUTH: PrivateJsonAuth = PrivateJsonAuth().get_section("AUTH_EMAIL")
    FOLDER: str = "!_TRADINGVIEW"
    SUBJECT_REGEXP: Optional[str] = None    # None - for all
    MARK_AS_READ: bool = True

    ALERT: Type[AlertBase] = AlertSelect.TELEGRAM
    _conn: Optional[imaplib.IMAP4_SSL] = None

    def __init__(self):
        super().__init__()

        self.start()

    # CONNECT =========================================================================================================
    def _connect(self) -> bool:
        if self._conn:
            return True

        print(f"\n _connect {self.__class__.__name__}")
        try:
            self._conn = imaplib.IMAP4_SSL(self.SERVER.ADDR, self.SERVER.PORT)
        except:
            pass

        if self._conn:
            print(self._conn.login(self.AUTH.USER, self.AUTH.PWD))
            print(self._conn.select(self.FOLDER))  # ('OK', [b'5'])
            print(self._conn.search(None, 'UNSEEN'))  # ('OK', [b''])

        return bool(self._conn)

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
                    if self.SUBJECT_REGEXP:
                        if re.fullmatch(self.SUBJECT_REGEXP, subject):
                            self.ALERT(subject)
                    else:
                        self.ALERT(subject)

            self._disconnect()
            time.sleep(self.INTERVAL)

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
