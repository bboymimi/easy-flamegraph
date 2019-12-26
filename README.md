# Linux Flamegraph Utilities

Utilities used for performance profiling.

1\. easy-flamegraph.sh
=====================
This is the wrapper used for the FlameGraph generation. The FlameGraph is invented by Brendan Greg. For more information, please refer to: https://github.com/brendangregg/FlameGraph

At first, you need to profile the system and get the perf.data:

```
# To get the all CPUs profiling callstack from user space to kernel space
$ sudo perf record -a --call-graph dwarf

# To get the all CPUs profiling of kernel space callstack
$ sudo perf record -a -g
```

By default, easy-flamegraph.sh will read the perf.data under the current folder or you can assign the perf.data by \"-i\":

It's preferred to add the \"sudo\" as reading the /proc/kallsyms need the root privilege if the kernel debug symbol isn't installed.

```
$ git clone https://github.com/bboymimi/perf-utils.git
$ sudo easy-flamegraph.sh -i perf.data
```

Or grep the specific string you are interested to generate the FlameGraph:

```
$ sudo ./easy-flamegraph.sh -g ssh
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
$ ./easy-flamegraph.sh -h
usage: ./easy-flamegraph.sh -g <grep string to make specific flamegraph> -i <perf file> -k <kernel version #>
        i - perf report file
        k - kernel version - specific kernel version number
        g - grep strings - to grep specific strings e.g., kworker, to make flamegraph
        t - tar the /home/ubuntu/perf-output/
```
