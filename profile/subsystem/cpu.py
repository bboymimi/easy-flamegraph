#!/usr/bin/python
# @lint-avoid-python-3-compatibility-imports

from __future__ import print_function
from bokeh.layouts import layout
from bokeh.palettes import magma
from bokeh.models import HoverTool, Panel, TapTool, OpenURL


def plot_cpu(view):

    # show the results
    # p.legend.location = "top_left"
    # p.legend.click_policy = "hide"
    # taptool = p.select(type=TapTool)
    # # taptool.callback = callback1
    # url = "http://google.com"
    # taptool.callback = OpenURL(url=url)
    return


def cpu_tab():
    l_cpu = layout(
        [
            # [plot_cpu("tsp")],
        ],
        sizing_mode='scale_both'
    )
    tab_cpu = Panel(child=l_cpu, title='CPU')
    return tab_cpu
