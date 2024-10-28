import signal


class SigTermException(Exception):
    pass


class SigIntException(Exception):
    pass


def signal_handler(sig: int, frame):
    if sig == signal.SIGTERM:
        raise SigTermException('SIGTERM received')
    elif sig == signal.SIGINT:
        raise SigIntException('SIGINT received')


signal.signal(signal.SIGTERM, signal_handler)
signal.signal(signal.SIGINT, signal_handler)
