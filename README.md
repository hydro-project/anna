# Anna

[![Build Status](https://travis-ci.com/hydro-project/anna.svg?branch=master)](https://travis-ci.com/hydro-project/anna)
[![codecov](https://codecov.io/gh/hydro-project/anna/branch/master/graph/badge.svg)](https://codecov.io/gh/hydro-project/anna)
[![License](https://img.shields.io/badge/license-Apache--2.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)

Anna is a low-latency, autoscaling key-value store developed in the [RISE Lab](https://rise.cs.berkeley.edu) at [UC Berkeley](https://berkeley.edu). 

## Design

The core design goal for Anna is to avoid expensive locking and lock-free atomic instructions, which have recently been [shown to be extremely inefficient](http://www.jmfaleiro.com/pubs/latch-free-cidr2017.pdf). Anna instead employs a wait-free, shared-nothing architecture, where each thread in the system is given a private memory buffer and is allowed to process requests unencumbered by coordination. To resolve potentially conflicting updates, Anna encapsulates all user data in [lattice](https://en.wikipedia.org/wiki/Lattice_(order)) data structures, which have associative, commutative, and idempotent merge functions. As a result, for workloads that can tolerate slightly stale data, Anna provides best-in-class performance. A more detailed description of the system design and the coordination-free consistency mechanisms, as well as an evaluation and comparison against other state-of-the-art systems can be found in our [ICDE 2018 paper](http://db.cs.berkeley.edu/jmh/papers/anna_ieee18.pdf).

Anna also is designed to be a cloud-native, autoscaling system. When deployed in a cluster, Anna comes with a monitoring subsystem that tracks workload volume, and responds with three key policy decisions: (1) horizontal swelasticity to add or remove resources from the cluster; (2) selective replication of hot keys; and (3) data movement across two storage tiers (memory- and disk-based) for cost efficiency. This enables Anna to maintain its extremely low latencies while also being orders of magnitude more cost efficient than systems like [AWS DynamoDB](https://aws.amazon.com/dynamodb). A more detailed description of the cloud-native design of the system can be found in our [VLDB 2019 paper](http://www.vikrams.io/papers/anna-vldb19.pdf).

## Using Anna

To run the Anna KVS locally, you need to first need to install its dependencies, which you can do with the `install-dependencies*.sh` scripts in the `hydro-project/common` repo, which is a submodule of this repository. You can build the project, which `scripts/build.sh`, and you can use `scripts/start-anna-local.sh` and `scripts/stop-anna-local.sh` scripts to start and stop the KVS respectively. This repository has an interactive CLI ([source](client/cpp/cli.cpp), executable compiles to `build/cli/anna-cli`) as well as a Python client ([source](client/python/anna/client.py)). The `common` repository has an importable C++ client that can embed into other applications.

More detailed instructions on [building](docs/building-anna.md) and [running](docs/local-mode.md) can be found in the [docs](docs) directory. This repository only explains how to run Anna on a single machine. For instructions on how to run Anna in cluster mode, please see the `hydro-project/cluster` [repository](https://github.com/hydro-project/cluster).

## License

The Hydro Project is licensed under the [Apache v2 License](LICENSE).
