# Monero Version Compatibility Testing

> WE DO NOT BREAK USERSPACE!
>  - Linus Torvalds

Think of the Monero Core codebase as the kernel, and the node network and
blockchain as the hardware. Monero Core should aim to make as few breakages as
possible as is necessary to maintain the core mission of the Monero Project.
This tool aims to help catch regressions which break compatibility with previous
versions of Monero.

## Usage

### Creation

To get started, run:
```bash
python -m mc.create
```

This creates the `build` directory in your CWD, which contains a `config.json`
file. You can edit `config.json` to configure how this version testing framework
operates.

### Updating

The next thing we need to do is to pull Monero source code from the specified
remote repos:
```bash
python -m mc.update
```
Re-run this command whenever the specified remotes push new changes and you
would like to pull and test them.

### Building

Once the code is fetched, we build binaries for each control and target commit:
```bash
python -m mc.build
```
Re-run this command whenever you would like to build new commits.

### Running

Finally, we can run the tests with:
```bash
python -m mc.test
```

### Debugging

The `config.json` file has a `build_type` field. It defaults to `Release`, but
can be set to `Debug` in order to build the Monero core repo, and the C++ code
in the testing framework with debug symbols. Once the targets have been built
in `Debug` mode, then you can test with the following command on Linux:
```bash
gdb --args python -m mc.test
```
You can then use `gdb` like normally to break on certain C++ functions, step
instruction-by-instruction, etc.
