# Running Anna in Local Mode
## Starting Anna
This document assumes you have already built Anna locally; you can find those docs [here](building-anna.md). 
Once you have built Anna, you can use the `scripts/start-anna-local.sh` script to start the KVS server. 

By default, the `conf/anna-local.yml` config file is used, which only specifies one routing thread and one storage thread. 
You are welcome to modify this file if you would like, but we generally do not recommend running more than one 
thread per process in local mode.

`scripts/start-anna-local.sh {build} {start-cli}` takes two arguments. 
* If `{build}` is set to `y` (or `yes`) the build scripts will be run before start the Anna server. 
* If `{start-cli}` is specified, the interactive Anna CLI will be started in this context after the server is started.

## Stopping Anna
You can stop the running background processes by using the `anna` CLI `stop` command

If you have the `anna` crate installed, just use
```bash
> anna stop
```

If you have not installed it, then you can build and run the development version using
```bash
> cargo run -- stop
```