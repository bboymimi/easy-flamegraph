#!/usr/bin/python
import glob
import os
import re
import shutil
import sys

# Count the arguments
arguments = len(sys.argv) - 1

# Output argument-wise
position = 1
inputdir = None
outputdir = None
m_date = None
m_memfree = None
while (arguments >= position):
    # print("Parameter %i: %s" % (position, sys.argv[position]))
    if sys.argv[position] == "-f":
        inputdir = sys.argv[position + 1]
        position = position + 1
    elif sys.argv[position] == "-o":
        outputdir = sys.argv[position + 1]
        position = position + 1
    position = position + 1

if inputdir:
    print("inputdir:" + inputdir)
else:
    inputdir = "/var/log/easy-flamegraph/cpu/"
    print("Default inputdir:" + inputdir)

if outputdir:
    print("outputdir:" + outputdir)
else:
    print("Please assign(-o) the outputdir!!")
    sys.exit(1)

# txtfiles = []
for file in glob.glob("/var/log/easy-flamegraph/cpu/*.script"):
    # txtfiles.append(file)
    strip_file = re.sub(r't\d+u\d+\.', '', file)
    strip_file = re.sub(r'\/var\/log\/easy\-flamegraph\/cpu\/', '', strip_file)
    m_strip_file = re.search(r"(\d+)\-(\d+)\-(\d+)_(\d{2})(\d{2})(\d{2})(.+)", strip_file)
    # i.e. /var/log/easy-flamegraph/cpu/2020-11-06_162003.cpu.t0.u4.script
    strip_file = m_strip_file.expand(r"\1-\2-\3-\4:\5\7")
    strip_file = outputdir + strip_file
    # print(strip_file)
    shutil.copy(file, strip_file)
    #print(strip_file)

sys.exit(0)
# os._exit(0)
fp = open(inputdir, "r")
line = fp.readline()

print("date,value")
i = 0
# while i < 1300:
while line:
    # scan the separate line '----'
    m = re.search("----------", line)
    if m:
        # clear the date and the recorded parameters
        m_date = None
        m_memfree = None
        # print(m.group(0))

    # i.e. 2020.05.29-23.18.02
    if m_date is None:
        m_date = re.search(r"(\d+)\.(\d+)\.(\d+)\-(\d+)\.(\d+)\.(\d+)", line)
        if m_date:
            date_msg = m_date.expand(r"\1-\2-\3-\4:\5:\6")
            # print(m_date.group(0))

    # MemFree:         3641416 kB
    if m_memfree is None:
        m_memfree = re.search(r"MemFree:\s+(\d+)\s+kB", line)
        if m_memfree:
            # print(m_memfree.group(0))
            memfree_msg = m_memfree.group(1)
            print("%s,%s" % (date_msg, memfree_msg))

    line = fp.readline()
    i = i + 1

fp.close()
