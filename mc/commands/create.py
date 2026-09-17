import os

from ..infra import defaults
from ..infra.user_config import UserConfig

def create(build_dir):
    os.mkdir(build_dir)
    config = UserConfig()
    config.dump(build_dir)

def create_main():
    build_dir = defaults.BUILD_DIR
    create(build_dir)
