[![Build Status](https://travis-ci.org/andrewdavidmackenzie/anna.svg?branch=master)](https://travis-ci.org/andrewdavidmackenzie/anna)
[![codecov](https://codecov.io/gh/andrewdavidmackenzie/anna/branch/master/graph/badge.svg)](https://codecov.io/gh/andrewdavidmackenzie/anna)
[![Generic badge](https://img.shields.io/badge/macos-supported-Green.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/linux-supported-Green.svg)](https://shields.io/)
[![Generic badge](https://img.shields.io/badge/Rust-stable-Green.svg)](https://shields.io/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

# Welcome!
 `anna` is a Command Line Utility for interacting with the `anna` key-value store.

# Installing
`anna` is published to [crates.io](http://crates.io/crates/anna) so the binary can be installed using:
```bash
> cargo install anna
```

# Running
You can get the available commands and usage options by running:
```bash
> anna --help
```

# Building Yourself
## Clone the repo
From your command line:

```bash
git clone https://github.com/andrewdavidmackenzie/anna.git
```

### Build
Go into the `cli` subdirectory and build using `cargo`
```bash
> cd anna/cli
> cargo build
```

### Run
Check it works by displaying the help message:
```bash
> cargo run -- --help
```
(the `--` marks the end of options to `cargo` and the start of options to pass to `anna`)