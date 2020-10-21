import typing


class FakeFile(typing.IO):
    def __init__(self, source: bytes):
        self._source = source
        self._offset = 0

    def open(self):
        pass

    def close(self):
        pass

    def read(self, n_bytes: int = -1) -> typing.AnyStr:
        self._offset += n_bytes
        return self._source[self._offset - n_bytes : self._offset]  # noqa: E203


DEFAULT_DATETIME_PATTERN = "%d-%m-%Y %H:%M:%S"
