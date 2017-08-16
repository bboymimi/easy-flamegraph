#!/bin/bash

CHK_PKG=""
FPERF="`pwd`/perf-output"
PERF_DATA="$FPERF/perf.mem"
FPATH="$HOME/os/FlameGraph/"
GREP_STRINGS=""
PERF_CMD=""
PID=""

while getopts "a:g:p:h" opt; do
    case $opt in
        a) APPEND_STRINGS=$OPTARG ;;
        g) GREP_STRINGS=$OPTARG ;;
        p) PID=$OPTARG ;;
        h|*)
            echo "usage: $0 -a <append string> -g <partial process name for pgrep > -p <process ID>"
            echo "	a - append process name strings - to append specific strings e.g., qemu/compiz, to easily differentiate perf.data"
            echo "	g - grep strings - to grep specific strings e.g., qemu, to profile"
            echo "	p - process id strings - to profile the specific process"
            exit 0
            ;;
    esac
done

[ $(id -u) -ne 0 ] && echo "Must be root!!" && exit 1

# append the string of the profiled process name to differentiate the perf.data
[[ $APPEND_STRINGS != "" ]] && PERF_DATA=$PERF_DATA.$APPEND_STRINGS

mkdir -p $FPERF

# return 1 if linux-tools-generic is installed, else return 0
CHK_PKG=$(dpkg-query -W -f='${Status}' linux-tools-common 2>/dev/null | grep -c "ok installed")
[ $CHK_PKG -eq 0 ] && apt-get install -y linux-tools-common

# add the probe point related to the memory alloction
perf probe -x /lib/x86_64-linux-gnu/libc-2.23.so malloc bytes=%di
perf probe -x /lib/x86_64-linux-gnu/libc-2.23.so realloc bytes=%di
perf probe -x /lib/x86_64-linux-gnu/libc-2.23.so calloc bytes=%di

perf probe -x /lib/x86_64-linux-gnu/libc-2.23.so brk bytes=%di
perf probe -x /lib/x86_64-linux-gnu/libc-2.23.so sbrk bytes=%di
perf probe -x /lib/x86_64-linux-gnu/libc-2.23.so __sbrk bytes=%di

perf probe -x /lib/x86_64-linux-gnu/libc-2.23.so mmap addr=%di len=%si
perf probe -x /lib/x86_64-linux-gnu/libc-2.23.so mmap64 addr=%di len=%si
perf probe -x /lib/x86_64-linux-gnu/libc-2.23.so __mmap64 addr=%di len=%si

# add the new probe point of the kernel symbol do_mmap
perf probe do_mmap addr=%si len=%dx prot=%cx

# add the handle_mm_fault kernel function
perf probe handle_mm_fault addr=%si

perf probe -x /lib/x86_64-linux-gnu/libc-2.23.so free addr=%di

# press ctrl+c when you want to stop the profiling
PERF_CMD="perf record -e probe_libc:malloc* -e probe_libc:realloc* -e probe_libc:calloc \
            -e probe_libc:brk -e probe_libc:sbrk -e probe_libc:__sbrk \
            -e probe_libc:mmap -e probe_libc:mmap64 -e probe_libc:__mmap64 \
            -e probe:do_mmap \
            -e probe:handle_mm_fault \
            -e probe_libc:free \
            -a --call-graph dwarf \
            -o $PERF_DATA"

[[ $PID != "" ]] && PERF_CMD="$PERF_CMD -p $PID"
[[ $GREP_STRINGS != "" ]] && PERF_CMD="$PERF_CMD -p `pgrep $GREP_STRINGS`"

echo "###########"
echo "# The Perf file will be generated to \"$PERF_DATA\""
echo "# Profiling..."
echo "###########"

$PERF_CMD
