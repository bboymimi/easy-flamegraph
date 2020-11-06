#!/usr/bin/python
import os
import re
import sys

# Count the arguments
arguments = len(sys.argv) - 1

# Output argument-wise
position = 1
filename = None
outputname = None
m_date = None
m_memfree = None
month = "\d+"
while (arguments >= position):
    # print("Parameter %i: %s" % (position, sys.argv[position]))
    if sys.argv[position] == "-f":
        filename = sys.argv[position + 1]
        position = position + 1
    elif sys.argv[position] == "-o":
        outputname = sys.argv[position + 1]
        position = position + 1
    elif sys.argv[position] == "-m":
        month = sys.argv[position + 1]
        position = position + 1
        # print(month)
    position = position + 1

# if filename:
#     print("filename:" + filename)
# if outputname:
#     print("outputname:" + outputname)

fp = open(filename, "r")
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
        # print("(\d+)\.(" + month + ")\.(\d+)\-(\d+)\.(\d+)\.(\d+)")
        m_date = re.search(r"(\d+)\.(" + month + ")\.(\d+)\-(\d+)\.(\d+)\.(\d+)", line)
        if m_date:
            date_msg = m_date.expand(r"\1-\2-\3-\4:\5:\6")
            # print(m_date.group(0))

    # MemFree:         3641416 kB
    if m_date is not None:
        if m_memfree is None:
            m_memfree = re.search(r"MemFree:\s+(\d+)\s+kB", line)
            if m_memfree:
                # print(m_memfree.group(0))
                memfree_msg = m_memfree.group(1)
                print("%s,%s" % (date_msg, memfree_msg))

    line = fp.readline()
    i = i + 1

fp.close()
# os._exit(0)
