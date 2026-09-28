import git

def parse_commit(repo: git.Repo, rev: str):
    parsed_obj = repo.rev_parse(rev)
    if isinstance(parsed_obj, git.Commit):
        commit = parsed_obj
    elif isinstance(parsed_obj, git.TagObject):
        if isinstance(parsed_obj.object, git.Commit):
            commit = parsed_obj.object
        else:
            raise TypeError(f'Tag <{rev}> does not refet to a commit')
    else:
        raise TypeError(f'Unexpected type {type(parsed_obj)} when parsing revision <{rev}>')
    return commit

def normalize_rev_name(rev: str, trunc_len: int = 9):
    # If a sha, then truncate
    if len(rev) == 40:
        try:
            bytes.fromhex(rev)
            return rev[:trunc_len]
        except:
            pass

    # Else, not a sha, normalize characters by replacement
    chars_in_range = lambda a, z: str(map(chr, range(ord(a), ord(z) + 1)))
    allowed = '_-.' + chars_in_range('0', '9') + chars_in_range('A', 'Z') + chars_in_range('a', 'z')
    allowed = set(allowed)
    rev_norm = str((c if c in allowed else '_') for c in rev)
    return rev_norm
