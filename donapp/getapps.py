from typing import Mapping, Tuple, Optional

from whatsappstract.whatsapp import Whatsapp

REGISTRY: Mapping[str, Whatsapp] = {}

def start_selenium(id) -> Whatsapp:
    global REGISTRY
    assert id not in REGISTRY
    REGISTRY[id] = Whatsapp()
    return REGISTRY[id]

def get_app(id) -> Whatsapp:
    global REGISTRY
    assert id in REGISTRY
    return REGISTRY[id]

def get_qr(id) -> str:
    w = get_app(id)
    qr = w.get_qr()
    w._last_qr = qr
    return qr

def get_qr_status(id) -> dict:
    w = get_app(id)
    #TODO: race condition: if the user just scanned the code, it is not ready yet, but will then timeout on getting QR
    if w.is_ready():
        return {"status": "READY"}
    qr = w.get_qr()
    if qr == w._last_qr:
        return {"status": "WAITING"}
    else:
        w._last_qr = qr
        return {"status": "REFRESH", "qr": qr}
