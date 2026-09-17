from mc.infra.test_suite import TestSuiteConfig
from ..infra.test_case import TestCase
from ..infra.test_suite import TestSuiteConfig

class Serialization(TestCase):
    def run(self):
        ret = self.binary_infos[0].cdll.mc_PendingTx_write("ptx_blob.dat")
        assert 0 == ret, ret
        ret = self.binary_infos[1].cdll.mc_PendingTx_read_and_compare("ptx_blob.dat")
        assert 0 == ret, ret

suite_config = TestSuiteConfig(True, [], ['Serialization'], True)
