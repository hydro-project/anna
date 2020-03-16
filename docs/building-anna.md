# Building Anna

**NOTE**: If you are trying to start an Anna cluster, that does not require you to build Anna on your local machine. You can find instructions for running a Hydro cluster [here](https://github.com/hydro-project/cluster/blob/master/docs/getting-started-aws.md).

## Prerequisites

Anna has the Hydro common directory as a git submodule. After cloning anna, init and update the submodules to install the `commmon` subdirectory:
```bash
git submodule init; git submodule update
```

In order to build Anna, there are a variety of C++ and other dependencies that are required. Most can be installed with standard package managers like `brew` on macOS and `apt` on Debian. Prepackaged scripts to install dependencies on Fedora, Debian, and macOS can be found in `common/scripts/install-dependencies(-osx).sh`. If you would like to customize the installed packages, everything except for CMake and Protobuf can be installed via standard package managers. Any version of Protobuf 3 should be supported, and we require CMake to be at least version 3.6.

## Running the Build Script

Anna can be built with Clang (version 5 or newer) or gcc (version 7 or newer). `scripts/build.sh` automatically configures and runs the standard CMake build for you, with 3 clangs.

* `-b` specifies the build type, either `Release` or `Debug`.
* `-j` specifies the parallelism to be used by `make`. The default value is `-j1`.
* `-t` enables testing; note that testing requires the build to be run in `Debug` mode. 
* `-g` builds the project using `g++` instead of `clang++`. 

By default, the script will run as `bash scripts/build.sh -bRelease -j1`. 

This will generate a variety of executables, primarily in `build/target`, which houses all of the KVS server executables, and in `build/client`, which has the CPP-based interactive CLI for Anna. Once Anna is built, you can run it in [local mode](local-mode.md).
