REMOTES = [
    ['monero-project', 'https://github.com/monero-project/monero.git'],
    ['seraphis-migration', 'https://github.com/seraphis-migration/monero.git'],
    ['jeffro256', 'https://github.com/jeffro256/monero.git']
]

TARGET_COMMIT = REMOTES[0][0] + '/master'

CONTROL_COMMITS = [
    "monero-project/release-v0.18", # branch
    "monero-project/release-v0.19", # branch
    "monero-project/master",        # branch
    "v0.18.0.0",                    # tag
]

JSON_INDENT = 4

MAKE_TARGETS = ['daemon', 'wallet_rpc_server', 'monero_compat']

BUILD_DIR = 'build'

BINARY_SUBDIR = 'binary'

SHARED_LIBRARY_BINARY_PATH = 'src/libmonero_compat.so'

REPO_SUBDIR = 'monero.git'

CONFIG_FILE = 'config.json'

RUNNING_DATA_SUBDIR = 'arena'

BUILD_SKIP_FILE = 'skip_build.txt'
