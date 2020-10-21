#!/usr/bin/python
# @lint-avoid-python-3-compatibility-imports

from __future__ import print_function
from bcc import BPF
from datetime import datetime, timedelta
from time import strftime
from bokeh.layouts import layout
from bokeh.plotting import ColumnDataSource, figure, output_file, show
from bokeh.palettes import Category20_16, cividis, Turbo256, Plasma256, magma
from bokeh.models import HoverTool, Panel
from bokeh.models.widgets import Tabs
import pandas as pd

# define BPF program
prog = """
#include <uapi/linux/ptrace.h>
#include <linux/sched.h>

struct val_t {
    u32 pid;
    u32 order;
    char comm[TASK_COMM_LEN];
    u64 ts;
};

struct data_t {
    u32 pid;
    u32 order;
    u64 delta;
    u64 ts;
    char comm[TASK_COMM_LEN];
};

BPF_HASH(start, u32, struct val_t);
BPF_PERF_OUTPUT(events);

int do_entry(struct pt_regs *ctx) {

    struct val_t val = {};
    u32 pid = bpf_get_current_pid_tgid();

    if (bpf_get_current_comm(&val.comm, sizeof(val.comm)) == 0) {
        val.pid = bpf_get_current_pid_tgid();
        val.ts = bpf_ktime_get_ns();
        val.order = ctx->si;
        start.update(&pid, &val);
    }

    return 0;
}

int do_return(struct pt_regs *ctx) {
    struct val_t *valp;
    struct data_t data = {};
    u64 delta;
    u32 pid = bpf_get_current_pid_tgid();

    u64 tsp = bpf_ktime_get_ns();

    valp = start.lookup(&pid);
    if (valp == 0)
        return 0;       // missed start

    //bpf_probe_read_kernel(&data.comm, sizeof(data.comm), valp->comm);
    bpf_get_current_comm(&data.comm, sizeof(data.comm));
    data.pid = valp->pid;
    data.order = valp->order;
    data.delta = tsp - valp->ts;
    data.ts = valp->ts;
    events.perf_submit(ctx, &data, sizeof(data));
    start.delete(&pid);
    return 0;
}
"""

b = BPF(text=prog)

#b.attach_kprobe(event="huge_pte_alloc", fn_name="trace_hugepte")
b.attach_kprobe(event="__alloc_pages_nodemask", fn_name="do_entry")
b.attach_kretprobe(event="__alloc_pages_nodemask", fn_name="do_return")


time = [ ]
pid = [ ]
comm = [ ]
latns = [ ]
host = [ ]
tsp = [ ]
order = [ ]
print("%-9s %-6s %-16s %10s %s %-3s" % ("TIME", "PID", "COMM", "LATns", "TS", "ORDER"))

def print_event(cpu, data, size):
    event = b["events"].event(data)
    time.append(strftime("%H:%M:%S"))
    pid.append(event.pid)
    comm.append(event.comm.decode('utf-8', 'replace'))
    latns.append(float(event.delta))
    tsp.append(event.ts)
    order.append(int(event.order))
    print("%-9s %-6d %-16s %10.2f %-5s %-3d" % (strftime("%H:%M:%S"), event.pid,
        event.comm.decode('utf-8', 'replace'), float(event.delta),
        event.ts, int(event.order)))
    # event.host.decode('utf-8', 'replace')))


# loop with callback to print_event
b["events"].open_perf_buffer(print_event, page_cnt=64)
i = 0
while 1:
    try:
        b.perf_buffer_poll()
        i += 1
        if i >= 5:
            break
    except KeyboardInterrupt:
        exit()


TOOLS = "crosshair,pan,wheel_zoom,box_zoom,reset"
TOOLTIPS = [("(x, y)", "x:$x y:$y"), ("tsp", "@tsp"), ("pid", "@pid"),
            ("comm", "@comm"), ("lat", "@latns"), ("order", "@order")]

hover = HoverTool(
    tooltips=TOOLTIPS
)

process_name= list(set(comm))

# create a color iterator
process_colors = magma(len(process_name))

color_dict = {process: proc_color for process, proc_color in zip(
    process_name, process_colors)}

colors = [color_dict[x] for x in comm]

all_data = {"time": time, "pid": pid, "comm": comm,
            "latns": latns, "tsp": tsp, "order": order, "colors": colors}

df = pd.DataFrame(all_data)

def plot_cpu(view):
    p = figure(title = view, plot_width=400, plot_height=200, tools=TOOLS, active_scroll = 'wheel_zoom', tooltips=TOOLTIPS)
    p.add_tools(hover) #Add the instance of HoverTool that we modified
    p.xaxis.axis_label = view
    p.yaxis.axis_label = 'Latency'

    # add a circle renderer with a size, color, and alpha
    for c in set(df["colors"]):
        mask = df["colors"] == c
        df_draw = df[mask]
        source_draw = ColumnDataSource(df_draw)
        p.circle(view, "latns", size=10, color="colors", alpha=0.9,
                 legend=df_draw.iloc[0]["comm"], source=source_draw)

    # show the results
    p.legend.location = "top_left"
    p.legend.click_policy = "hide"
    return p


def cpu_tab():
    l_cpu = layout(
        [
            [plot_cpu("tsp")],
        ],
        sizing_mode='scale_both'
    )
    tab_cpu = Panel(child=l_cpu, title='CPU')
    return tab_cpu
