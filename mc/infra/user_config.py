import json
import os

from . import defaults

class UserConfig:
    FIELD_NAMES = ['target_commit', 'control_commits', 'remotes', 'build_type']

    def __init__(self,
            target_commit:str=defaults.TARGET_COMMIT,
            control_commits:list[str]=defaults.CONTROL_COMMITS,
            remotes:list[list[str]]=defaults.REMOTES,
            build_type:str='Release'):
        self.target_commit: str = target_commit
        self.control_commits: list[str] = control_commits
        self.remotes: list[str] = remotes
        self.build_type: str = build_type

    def dump(self, build_dir, force = False):
        config_path = os.path.join(build_dir, defaults.CONFIG_FILE)
        mode = 'wt' if force else 'xt'
        with open(config_path, mode) as outf:
            json.dump(self, outf, cls=UserConfigEncoder, indent=defaults.JSON_INDENT)

    @classmethod
    def load(cls, build_dir):
        config_path = os.path.join(build_dir, defaults.CONFIG_FILE)
        with open(config_path) as inf:
            return json.load(inf, object_hook=decode_user_config)

class UserConfigEncoder(json.JSONEncoder):
    def default(self, config):
        if not isinstance(config, UserConfig):
            return super().default(config)
        obj = {}
        for field_name in UserConfig.FIELD_NAMES:
            obj[field_name] = getattr(config, field_name)
        return obj

def decode_user_config(obj):
    config = UserConfig()
    for field_name in UserConfig.FIELD_NAMES:
        if field_name in obj:
            setattr(config, field_name, obj[field_name])
    return config
