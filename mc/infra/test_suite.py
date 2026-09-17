class TestSuiteBackgroundProcess:
    def __init__(self, build_index: int, cmd_name: str, cmd_args: list[str]):
        self.build_index = build_index
        self.cmd_name = cmd_name
        self.cmd_args = cmd_args

class TestSuiteConfig:
    def __init__(self,
            is_reversible: bool = True,
            bg_processes: list[TestSuiteBackgroundProcess] = [],
            test_cases: list[str] = [],
            needs_cdll: bool = True
        ):
        self.is_reversible = is_reversible
        self.bg_processes = bg_processes
        self.test_cases = test_cases
        self.needs_cdll = needs_cdll
