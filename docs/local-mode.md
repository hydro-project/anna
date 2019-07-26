# Running Anna in Local Mode

This document assumes you have already built Anna locally; you can find those docs [here](docs/building-anna.md). Once you have built Anna, you can use the `scripts/start-anna-local.sh` script to start the KVS server. By default, the `conf/anna-local.yml` config file is used, which only specifies one routing thread and one storage thread. You are welcome to modify this file if you would like, but we generally do not recommend running more than one thread per process in local mode.

`scripts/start-anna-local.sh {build} {start-cli}` takes two arguments. If `build` is set to `y` (or `yes`) the build scripts will be run before start the Anna server. If `{start-cli}` is specified, the interactive Anna CLI will be started in this context after the server is started.

`scripts/stop-anna-local.sh {remove-logs}` can be used to stop the Anna server. If `remove-logs` is specified, all logs will be deleted. Otherwise they will be left in place -- this is primarily used for debugging purposes.