from typing import Any


class BeeError(Exception):
    def __init__(self, message: str):
        super().__init__(message)


class BeeArgumentError(BeeError):
    def __init__(self, message: str, value: Any):
        super().__init__(message)
        self.value = value
