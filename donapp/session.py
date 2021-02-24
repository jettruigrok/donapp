import logging
import threading
from subprocess import TimeoutExpired
from threading import Thread
from typing import Mapping, Tuple, Optional

from selenium.common.exceptions import TimeoutException

from whatsappstract.whatsapp import Whatsapp

class WhatsappSession:
    """Wrapper around the Whatsapp class to remember state and do background scraping"""
    def __init__(self, n_chats=2):
        self.w = Whatsapp()
        self._last_qr: str = None
        self.links = None
        self.lock = threading.Lock()
        self._thread: Thread = None
        self.status: str = "NOTSTARTED"
        self._progress: int = None
        self._message: str = None
        self.n_chats: int = n_chats

    def get_qr(self) -> str:
        """Go to whatsapp web and get the QR code"""
        self._last_qr = self.w.get_qr()
        return self._last_qr

    def get_qr_status(self) -> dict:
        """Check if the user logged in and/or if a new QR code is displayed"""
        if self.w.is_qr_scanned():
            return {"status": "READY"}
        try:
            qr = self.w.get_qr()
        except TimeoutException:
            # Check if the app was loading the ready screen and is ready now
            if self.w.is_qr_scanned():
                return {"status": "READY"}
            raise
        if qr == self._last_qr:
            return {"status": "WAITING"}
        else:
            self._last_qr = qr
            return {"status": "REFRESH", "qr": qr}

    def do_scrape(self):
        logging.info("Starting scraper")
        with self.lock:
            if self.links is not None:
                raise ValueError("Scraping already in progress")
            self.links = []
            self.status = "STARTED"
            self._progress = 0
        try:
            self._do_scrape()
        except Exception as e:
            logging.exception("Error in scraper thread")
            with self.lock:
                self.status = "ERROR"
                self._message = str(e)
                self._progress = 0
        else:
            logging.info("Done!")
            with self.lock:
                self.status = "DONE"
                self._message = f"Done, found {len(self.links)} in total"
                self._progress = 100

    def _do_scrape(self):
        for i, (name, chat) in enumerate(self.w.get_all_chats()):
            if i >= self.n_chats:
                break
            msg = f"Scraping contact {i + 1}/{self.n_chats}: {name} [{len(self.links)} links found so far]"
            logging.info(msg)
            with self.lock:
                self._progress = round(i * 100 / self.n_chats)
                self._message = msg
            links = list(self.w.get_links_per_chat(chat))
            with self.lock:
                self.links += links

    def get_progress(self):
        with self.lock:
            return dict(status=self.status, progress=self._progress, message=self._message)

    def start_scraping(self):
        self._thread = threading.Thread(target=self.do_scrape)
        logging.info("Starting thread")
        self._thread.start()




# Each 'session' should have one object that stays in memory
# No, it's not the way HTTP should work, but what do you do about it.
REGISTRY: Mapping[str, WhatsappSession] = {}

def start_session(id: str) -> WhatsappSession:
    global REGISTRY
    assert id not in REGISTRY
    REGISTRY[id] = WhatsappSession()
    return REGISTRY[id]

def get_session(id: str) -> WhatsappSession:
    global REGISTRY
    assert id in REGISTRY
    return REGISTRY[id]
