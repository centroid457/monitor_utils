from typing import *

from email.mime.text import MIMEText
import smtplib
from private_values import *


# =====================================================================================================================
class SmtpAddress(NamedTuple):
    ADDR: str
    PORT: int


class SmtpServers:
    MAIL_RU: SmtpAddress = SmtpAddress("smtp.mail.ru", 465)


# =====================================================================================================================
class SmtpSender:
    """
    main class to work with smtp.
    """
    SMTP_USER: str = EnvValues.get("SMTP_USER")    # example@mail.ru
    SMTP_PWD: str = EnvValues.get("SMTP_PWD")     # use thirdPartyPwd!

    SERVER: SmtpAddress = SmtpServers.MAIL_RU
    RECONNECT_TIMEOUT: int = 60
    RECONNECT_TIMES: int = 10

    _smtp: Optional[smtplib.SMTP_SSL] = None

    def __init__(self):
        super().__init__()
        self._connect()

    # CONNECT =========================================================================================================
    def _connect(self) -> bool:
        result = None

        if self._check_empty():
            print(f"_connect {self.__class__.__name__}")
            try:
                self._smtp = smtplib.SMTP_SSL(self.SERVER.ADDR, self.SERVER.PORT, timeout=5)
            except Exception as exx:
                print(f"[CRITICAL] CONNECT {exx!r}")
                self._clear()

        if not self._check_empty():
            try:
                result = self._smtp.login(self.SMTP_USER, self.SMTP_PWD)
            except Exception as exx:
                print(f"[CRITICAL] LOGIN {exx!r}")

            print(result)
            print("="*100)

        return result and result[0] in [235, 503]

    def _disconnect(self) -> None:
        if self._smtp:
            self._smtp.quit()
        self._clear()

    def _clear(self) -> None:
        self._smtp = None

    def _check_empty(self) -> bool:
        return self._smtp is None

    # MSG =============================================================================================================
    def send(self, subject: str, body: Any) -> bool:
        result = False

        FROM = self.SMTP_USER
        TO = FROM
        SUBJECT = subject
        BODY = str(body)

        msg = MIMEText(BODY, 'plain')
        msg['Subject'] = SUBJECT
        msg["From"] = FROM
        msg["To"] = TO

        counter = 0
        while not result and counter <= self.RECONNECT_TIMES:
            counter += 1
            if self._connect():
                print(self._smtp.send_message(msg))
                print("-"*80)
                print(msg)
                print("-"*80)
                result = True
            else:
                print(f"[WARNING]{counter=}")
                print("="*100)
                print()
                time.sleep(self.RECONNECT_TIMEOUT)
                pass    # don't add print msg! it's already ON!

        return result


# =====================================================================================================================
