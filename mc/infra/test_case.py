import ctypes

class BinaryInfo:
    def __init__(self, binary_dir: str, cdll: ctypes.CDLL | None = None):
        self.binary_dir = binary_dir
        self.cdll: ctypes.CDLL | None = cdll

class TestCase:
    def __init__(self):
        self.binary_infos: list[BinaryInfo] = []

    def setup(self, binary_infos: list[BinaryInfo]):
        self.binary_infos = binary_infos

    def run(self):
        raise NotImplementedError("Test case needs to implement run()")
