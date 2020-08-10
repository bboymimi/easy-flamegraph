# Linux Performance and Data Analysis Utilities

This is a light-weight utility used for performance profiling and data analysis.

## Table of Contents

- [Performance data capturing](#performance-data-capturing)
  - [easy-flamegraph configuration](#easy-flamegraph-configuration)
- [Flamegraph generation](#flamegraph-generation)
  - [gen-flamegraph.sh](#gen-flamegraphsh)

## Performance data capturing

The performance data capturing is currently based on Perf. By default, it will profile per-minute for one second period to capture the CPU/Memory/IO realated perf event data. Then, the log data will be translated to the files with specific formats(csv,tsv...) for further analysis(ScatterPlot/Flamegraph/LineChart...etc.).

After git clone the repo, the tool can be installed to the system by:
$ sudo make install

Then, the code will be put under:
$ ls /usr/lib/easy-flamegraph/
conditions  entry  ezcli  FlameGraph  gen-flamegraph.sh  lib  perf-output  sysinfo

The periodic sampling is implemented in the crontab config:
$ cat /etc/cron.d/easy-flamegraph-cron
\# Flamegraph-mem sample in 1 minute period
\*/1 * * * * root /usr/lib/easy-flamegraph/entry > /dev/null


### easy-flamegraph configuration
The configuration file is /etc/default/easy-flamegraph.conf.

There are global settings which can apply to each subsystems(cpu/mem/io...). And the name is started with G.

e.g.
\# Specify the sampling rate
G_SRATE=99

\# Specify PID for perf record
G_PID=

\# How many seconds perf record should run
G_PERF_PERIOD=1


## Flamegraph generation

### gen-flamegraph.sh
This is the wrapper used for the FlameGraph generation. The FlameGraph is invented by Brendan Greg. For more information, please refer to: https://github.com/brendangregg/FlameGraph

At first, you need to profile the system and get the perf.data:

```
# To get the all CPUs profiling callstack from user space to kernel space
$ sudo perf record -a --call-graph dwarf

# To get the all CPUs profiling of kernel space callstack
$ sudo perf record -a -g
```

By default, gen-flamegraph.sh will read the perf.data under the current folder or you can assign the perf.data by \"-i\":

It's preferred to add the \"sudo\" as reading the /proc/kallsyms need the root privilege if the kernel debug symbol isn't installed.

```
$ git clone https://github.com/bboymimi/perf-utils.git
$ sudo gen-flamegraph.sh -i perf.data
```

Or grep the specific string you are interested to generate the FlameGraph:

```
$ sudo ./gen-flamegraph.sh -g ssh
Use the /home/ubuntu/perf-utils/perf.data as the source of the FlameGraph.
###########
# The perf interactive .svg graph "/home/ubuntu/perf-output/2017-08-16_09:59:32.perf.data.foldedSssh.svg" has been generated.

# The FlameGraph can be viewed by:
# $ google-chrome-stable /home/ubuntu/perf-output/2017-08-16_09:59:32.perf.data.foldedSssh.svg
# or
# $ firefox /home/ubuntu/perf-output/2017-08-16_09:59:32.perf.data.foldedSssh.svg

```

Read the help page to get more detail:

```
$ ./gen-flamegraph.sh -h
usage: ./gen-flamegraph.sh -g <grep string to make specific flamegraph> -i <perf file> -k <kernel version #>
        d - drop the perf related data(include perf.data!!) and keep the .svg flamegraph file to save space
        g - grep strings - to grep specific strings e.g., kworker, to make flamegraph
        i - perf report file
        k - kernel version - specific kernel version number
        o - output directory - the output directory to save the .svg/script file
        s - symfs - to assign the directory to search for the debug symbol of kernel modules
        t - tar the /home/vin/os/easy-flamegraph/perf-output/
        p - generate the flamegraph for each CPU
        subtitle - the subtitle of the framegraph
        title - the title of the framegraph
```
