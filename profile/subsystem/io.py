#!/usr/bin/env python3

from __future__ import print_function
from bokeh.layouts import layout
from bokeh.models import Panel


def plot_io(view):
    return


def io_tab():
    l_io = layout(
        [
            # [plot_io("order"), plot_io("tsp")],
        ],
        sizing_mode='scale_both'
    )
    tab_io = Panel(child=l_io, title='IO')
    return tab_io
