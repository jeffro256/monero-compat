import git
import os.path

from ..infra import defaults
from ..infra.user_config import UserConfig

def update(build_dir, config: UserConfig):
    assert os.path.exists(build_dir)
    repo_dir = os.path.join(build_dir, defaults.REPO_SUBDIR)
    if os.path.exists(repo_dir):
        print(f'Opening repository at {repo_dir}...')
        repo = git.Repo(repo_dir)
    else:
        remote = config.remote[0]
        print(f'Cloning from {remote[1]}...')
        clone_options = [f'--origin={remote[0]}'] 
        repo = git.Repo.clone_from(remote[1], repo_dir)

    for remote_config in config.remotes:
        try:
            remote = repo.remote(remote_config[0])
            # TODO: check URL against URL config, and set if not matching
        except ValueError:
            print(f'Creating new remote {remote_config[0]} with URL {remote_config[1]}...')
            remote = git.remote.Remote.create(repo, remote_config[0], remote_config[1])

        print(f'Fetching recursively from {remote_config[1]}...')
        remote.fetch(recurse_submodules='yes')

def update_main():
    build_dir = defaults.BUILD_DIR
    config = UserConfig.load(build_dir)
    update(build_dir, config)
