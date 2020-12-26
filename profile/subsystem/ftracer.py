#!/usr/bin/python
# @lint-avoid-python-3-compatibility-imports

import subprocess
import sys
import time

# Count the arguments
arguments = len(sys.argv) - 1
debug_enabled = False
decode_trace = False
func_graph = ""
output_file = "./trace_result.log"
position = 1
# Set default sampling period to 1s
sample_period = 1


def debug_log(message):
    if debug_enabled:
        print(message)


def ftrace_stack_parser():
    p = subprocess.run(["cat", "/sys/kernel/debug/tracing/trace"],
                       stdout=subprocess.PIPE, universal_newlines=True)

    for line in list(iter(p.stdout.splitlines())):
        print(line)


def trace_handler():
    if not decode_trace:
        print("Cat the trace result to %s" % output_file)
        with open(output_file, 'w') as f_trace_result:
            subprocess.run(["cat", "/sys/kernel/debug/tracing/trace"],
                           stdout=f_trace_result, universal_newlines=True)
    else:
        ftrace_stack_parser()


while (arguments >= position):
    # print("Parameter %i: %s" % (position, sys.argv[position]))
    if sys.argv[position] == "-g":
        func_graph = sys.argv[position + 1]
        position = position + 1
    elif sys.argv[position] == "-s":
        sample_period = sys.argv[position + 1]
        position = position + 1
    elif sys.argv[position] == "-d":
        decode_trace = True
    elif sys.argv[position] == "-D":
        debug_enabled = True
    position = position + 1

debug_log("Set function_graph as the default tracer")
with open("/sys/kernel/debug/tracing/current_tracer", 'w') as f_current_tracer:
    subprocess.run(["echo", "function_graph"], stdout=f_current_tracer)

debug_log("Clear the filter!")
with open("/sys/kernel/debug/tracing/set_ftrace_filter", 'w') as f_ftrace_filter:
    subprocess.run(["echo"], stdout=f_ftrace_filter)

debug_log("Clear the set_graph_function")
with open("/sys/kernel/debug/tracing/set_graph_function", 'w') as f_graph_func:
    subprocess.run(["echo"], stdout=f_graph_func)

debug_log("Clear the trace buffer!")
with open("/sys/kernel/debug/tracing/trace", 'w') as f_trace_buffer:
    subprocess.run(["echo"], stdout=f_trace_buffer)

debug_log("Set the graph function!")
with open("/sys/kernel/debug/tracing/set_graph_function", 'w') as f_graph_func:
    subprocess.run(["echo", func_graph], stdout=f_graph_func)

debug_log("Start the tracing")
with open("/sys/kernel/debug/tracing/tracing_on", 'w') as f_trace_on:
    subprocess.run(["echo", "1"], stdout=f_trace_on)

# Sleep sample_period seconds for Ftrace to capture the trace
print("Sleep %f seconds" % float(sample_period))
time.sleep(float(sample_period))

debug_log("Stop the tracing")
with open("/sys/kernel/debug/tracing/tracing_on", 'w') as f_trace_on:
    subprocess.run(["echo", "0"], stdout=f_trace_on)

trace_handler()

debug_log("Clear the trace buffer!")
with open("/sys/kernel/debug/tracing/trace", 'w') as f_trace_buffer:
    subprocess.run(["echo"], stdout=f_trace_buffer)
