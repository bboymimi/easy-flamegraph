#!/usr/bin/python
# @lint-avoid-python-3-compatibility-imports

import pandas as pd

from bokeh.plotting import ColumnDataSource, output_file, show
from bokeh.models.widgets import Tabs

from subsystem.cpu import cpu_tab
from subsystem.memory import memory_tab
from subsystem.io import io_tab

tab_cpu = cpu_tab()
tab_memory = memory_tab()
tab_io = io_tab()
tabs = Tabs(tabs = [tab_cpu, tab_memory, tab_io])
# tabs = Tabs(tabs=[tab_cpu])

# output to static HTML file
output_file("summary.html")

show(tabs)
