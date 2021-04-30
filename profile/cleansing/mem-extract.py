#!/usr/bin/python
import sys
from utils.parser import parse_to_csv

# Count the arguments
arguments = len(sys.argv) - 1

# Output argument-wise
position = 1
filedir = "/var/log/easy-flamegraph/sysinfo/mem-stat/"
outputdir = "./"
month = "\d+"
separate = None

# entry point
while (arguments >= position):
    # print("Parameter %i: %s" % (position, sys.argv[position]))
    if sys.argv[position] == "-f":
        filedir = sys.argv[position + 1]
        position = position + 1
    elif sys.argv[position] == "-o":
        outputdir = sys.argv[position + 1]
        position = position + 1
    elif sys.argv[position] == "-m":
        month = sys.argv[position + 1]
        position = position + 1
        # print(month)
    elif sys.argv[position] == "-s":
        separate = 1
    position = position + 1

if filedir:
    print("input directory: " + filedir)
if outputdir is None:
    print("Please input the output direcotry by using \"-o dirname\" option.")
    sys.exit(1)
print("outputdir: " + outputdir)


# (1). Parse the meminfo.log
parse_to_csv("meminfo", filedir, outputdir, month, separate)

# (2). Parse the vmstat.log
parse_to_csv("vmstat", filedir, outputdir, month, separate)

# sys.exit(0)
