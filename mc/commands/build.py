import git
import multiprocessing
import os
import subprocess

from ..infra import defaults
from ..infra.user_config import UserConfig

def submodule_nofetch_is_supported() -> bool:
    # See: https://github.com/gitpython-developers/GitPython/pull/2244
    gitv = tuple(map(int, git.__version__.split('.')))
    assert len(gitv) == 3
    return gitv > (3, 1, 62) or 'no_fetch' in git.Submodule.update.__doc__

def try_decode(line):
    try:
        return line.decode()
    except:
        return line

# Run a command, showing 1 line of stdout at time, and dump stderr on fail
def cmd_streamed_out(args):
    max_stdout_len = 120
    proc = subprocess.Popen(args, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    while True:
        line = proc.stdout.readline()
        if not line:
            break
        line = try_decode(line).strip()
        line = line[:max_stdout_len].ljust(max_stdout_len)
        print('\r  ', line, sep='', end='')
    print()
    if proc.wait() != 0:
        while True:
            line = proc.stderr.readline()
            if not line:
                break
            print(try_decode(line))
        raise RuntimeError("Subprocess returned a non-zero exit code")

def build(build_dir, config: UserConfig, this_commit: str, num_jobs: int = 1, force: bool = False):
    assert os.path.exists(build_dir)
    print(f'Will compile with concurrenncy {num_jobs}.')
    repo_dir = os.path.join(os.path.realpath(build_dir), defaults.REPO_SUBDIR)
    repo = git.Repo(repo_dir)
    binary_top_dir = os.path.join(build_dir, defaults.BINARY_SUBDIR)
    commit_revs = config.control_commits + [config.target_commit]
    built = set()
    for commit_rev in commit_revs:
        commit = repo.rev_parse(commit_rev)
        if not isinstance(commit, git.objects.commit.Commit):
            raise TypeError(f'Expected commit for revision: {commit_rev}')
        if str(commit) in built:
            continue
        print(f'Checking out {str(commit)}...')
        index_file = git.index.base.IndexFile.new(repo, commit.tree)
        index_file.checkout()
        binary_dir = os.path.join(binary_top_dir, str(commit))
        os.makedirs(binary_dir, exist_ok=True)
        skip_file = os.path.join(binary_dir, defaults.BUILD_SKIP_FILE)
        if os.path.exists(skip_file):
            with open(skip_file) as inf:
                skip_commit = inf.read().strip()
                if skip_commit == this_commit:
                    print("Already compiled against current testing codebase, skipping...")
                    continue
                else:
                    print("This commit was compiled against a different version of testing codebase, re-compiling...")
        # TODO: apply patches
        # TODO: make cmake project which depends on repo
        print("Updating submodules...")
        if submodule_nofetch_is_supported():
            repo.submodule_update(recursive=True, no_fetch=True)
        else:
            repo.submodule_update(recursive=True)
        print("Configuring...")
        cmd_streamed_out(['cmake', '-B', binary_dir, f'-DCMAKE_BUILD_TYPE={config.build_type}',
            f'-DMONERO_ROOT_DIR={repo_dir}', '.'])
        print("Compiling...")
        cmd_streamed_out(['make', f'-j{num_jobs}', '-C', binary_dir] + defaults.MAKE_TARGETS)
        if this_commit:
            with open(skip_file, 'w') as outf:
                outf.write(this_commit)
        built.add(str(commit))

def get_testing_repo_head_commit():
    # TODO: return None when has unstaged changes
    try:
        this_repo = git.Repo(os.path.join(__file__, '..', '..', '..'))
        head = git.refs.head.HEAD(this_repo)
        head_commit = head.object
        if not isinstance(head_commit, git.objects.commit.Commit):
            raise TypeError(f'Expected commit for HEAD')
        return head_commit.hexsha
    except:
        return None

def build_main():
    build_dir = defaults.BUILD_DIR
    config = UserConfig.load(build_dir)
    this_commit = get_testing_repo_head_commit()
    try:
        num_jobs = multiprocessing.cpu_count() - 1
        num_jobs = max(num_jobs, 1)
    except NotImplementedError:
        num_jobs = 1
    build(build_dir, config, this_commit, num_jobs)
