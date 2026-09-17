import contextlib
import ctypes
import git
import glob
import importlib
import os
import re
import signal
import shutil
import subprocess
import traceback

from ..infra import defaults
from ..infra.user_config import UserConfig
from ..infra.test_case import BinaryInfo, TestCase
from ..infra.test_suite import TestSuiteConfig

def git_rev_parse(build_dir: str, rev: str):
    repo_dir = os.path.join(build_dir, defaults.REPO_SUBDIR)
    repo = git.Repo(repo_dir)
    commit = repo.rev_parse(rev)
    if not isinstance(commit, git.objects.commit.Commit):
        raise TypeError(f'Expected commit for revision: {rev}')
    bytes.fromhex(commit.hexsha)
    return commit.hexsha

# Creates a context manager which, on enter, starts processes specified in the
# test suite config with CWD as `running_dir`. On context managager close, sends
# a SIGINT to the child processes, then waits for them to terminate.
def start_processes(binary_dirs: list[str], running_dir: str, test_suite: TestSuiteConfig) -> contextlib.ExitStack:
    @contextlib.contextmanager
    def sigint_popen(*args, **kwargs):
        proc = subprocess.Popen(*args, **kwargs)
        try:
            yield proc
        finally:
            proc.send_signal(signal.SIGINT)
            proc.wait()

    stack = contextlib.ExitStack()
    for bg_process in test_suite.bg_processes:
        binary_dir = binary_dirs[bg_process.build_index]
        cmd = [os.path.join(binary_dir, bg_process.cmd)]
        cmd.extend(bg_process.args)
        stack.enter_context(sigint_popen(cmd, cwd=running_dir))
    return stack

@contextlib.contextmanager
def pushd(newdir):
    """https://gist.github.com/T1T4N/26732d878baa2704112b948924450c59"""
    old_path = os.getcwd()
    os.chdir(newdir)
    try:
        yield
    finally:
        os.chdir(old_path)

def matches_glob_filter(filter, v):
    regex = glob.translate(filter)
    return bool(re.match(regex, v))

def run_suite(results: dict, cdlls: dict, build_dir: str, test_suite_name: str, filter: str, commit1: str, commit2: str):
    # Get suite module
    top_level_pkg = __name__.split('.')[0]
    test_suite_module = importlib.import_module(f'.cases.{test_suite_name}', top_level_pkg)
    test_suite_config = test_suite_module.suite_config

    # Once forward, once backwards...
    for test_reversed in (False, True):
        if test_reversed and not test_suite_config.is_reversible:
            continue

        if test_reversed:
            eff_commits = (commit2, commit1)
        else:
            eff_commits = (commit1, commit2)

        # Setup running directory
        assert os.path.exists(build_dir)
        running_dir = os.path.join(build_dir, defaults.RUNNING_DATA_SUBDIR,
            eff_commits[1], test_suite_name, eff_commits[0])
        if os.path.exists(running_dir):
            shutil.rmtree(running_dir)
        os.makedirs(running_dir, exist_ok=True)

        # Setup background processes (w/ auto teardown)
        binary_upper_dir = os.path.join(build_dir, defaults.BINARY_SUBDIR)
        binary_dirs = [os.path.join(binary_upper_dir, commit) for commit in eff_commits]
        binary_infos = [BinaryInfo(d) for d in binary_dirs]
        with start_processes(binary_dirs, running_dir, test_suite_config):
            # For each case...
            for test_case_name in test_suite_config.test_cases:
                # Filter
                full_name = f'{test_suite_name}.{test_case_name}.{commit1}'
                if test_reversed:
                    full_name += '.bak'
                assert full_name not in results, 'Duplicate case: ' + full_name
                if not matches_glob_filter(filter, full_name):
                    continue

                # Load and set CDLL, if applicable
                if test_suite_config.needs_cdll:
                    for binary_info in binary_infos:
                        if binary_info.cdll is not None:
                            continue
                        cddl_path = os.path.join(binary_info.binary_dir, defaults.SHARED_LIBRARY_BINARY_PATH)
                        if cddl_path not in cdlls:
                            cdlls[cddl_path] = ctypes.CDLL(cddl_path)
                        binary_info.cdll = cdlls[cddl_path]
                        assert binary_info.cdll is not None

                # Run and set result
                test_case: TestCase = getattr(test_suite_module, test_case_name)()
                print('[ RUN ]', full_name)
                try:
                    test_case.setup(binary_infos)
                    with pushd(running_dir):
                        ret = test_case.run()
                        assert ret is None, "Test cases shouldn't return anything"
                        results[full_name] = True
                except Exception as e:
                    print(f'Caught exception running {full_name}:')
                    traceback.print_exc()
                    results[full_name] = False
                if results[full_name]:
                    print('[ SUCCESS ]', full_name)
                else:
                    print('[ FAILURE ]', full_name)

def test(build_dir: str, config: UserConfig):
    assert os.path.exists(build_dir)
    assert config.control_commits
    target_commit = git_rev_parse(build_dir, config.target_commit)
    cases_dir = os.path.realpath(os.path.join(__file__, '..', '..', 'cases'))

    # For each suite...
    results = {}
    cdlls = {}
    for test_suite_name in os.listdir(cases_dir):
        if test_suite_name.startswith('__'):
            continue

        # Convert file to module name
        if os.path.isfile(os.path.join(cases_dir, test_suite_name)):
            if test_suite_name.endswith('.py'):
                test_suite_name = test_suite_name[:-3]
            else:
                continue

        # For each control commit...
        for control_commit in config.control_commits:
            # Run suite
            control_commit = git_rev_parse(build_dir, control_commit)
            run_suite(results, cdlls, build_dir, test_suite_name, '*', control_commit, target_commit)

    # Print results
    fails = [t for t in results if not results[t]]
    print('================')
    print(f'Version control testing results against {target_commit}')
    print('================')
    print(f'Ran {len(results)} tests, {len(results) - len(fails)} succeeded')
    if fails:
        print('Failures:')
        for fail in fails:
            print(f'  - {fail}')

def test_main():
    build_dir = defaults.BUILD_DIR
    config = UserConfig.load(build_dir)
    test(build_dir, config)
