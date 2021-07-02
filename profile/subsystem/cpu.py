#!/usr/bin/python

from bokeh.layouts import column, layout
from bokeh.plotting import ColumnDataSource, figure
from bokeh.palettes import magma
from bokeh.models import HoverTool, OpenURL, Panel, PreText, RangeTool, TapTool
import numpy as np
import os
import pandas as pd
import random
import re


def build_link(default_directory="/var/log/easy-flamegraph"):
    """The current link tap implementation is to show the svg file. Finally,
    the specific html for a time stamp replace the svg file to provide a more
    comprehensive summary.
    """

    link_filenames = []
    filenames = []
    filelist = {}
    link_dir = os.path.join(default_directory, 'cpu')

    if not os.path.isdir(link_dir):
        print("The {} to build the link tables isn't a "
              "folder!".format(link_dir))
        return {}

    """ Currently, the link is to open a svg file. I want to support the html
    summary in the future.
    """
    for f in os.scandir(link_dir):
        if f.name.endswith(".svg"):
            break
    else:
        """Scan all the files under the folder but doesn't find any .svg
        """
        print("There is no svg files in the {} directory!".format(link_dir))
        return {}

    for _, _, filenames in os.walk(link_dir):
        break

    """ '202105130058': '2021-05-13_005809.mem.memtrace.svg' """
    for f in filenames:
        m = None
        m = re.search(r"20\d{2}\-\d{2}\-\d{2}_\d{6}", f)
        if m:
            link_filenames.append(f)

    for f in link_filenames:
        numeric_date = ""
        for c in f:
            if c.isnumeric():
                numeric_date = numeric_date + c
        m = None
        m = re.search(r"cpu(\d{3})", f)
        if m:
            cpu = m.expand(r"\1")
            key = numeric_date[:12] + 'c' + cpu.zfill(3)
        else:
            key = numeric_date[:12]
        """The last two digits seconds part will be dropped"""
        filelist[key] = f

    return filelist


def link_list(df, link_table):
    links = []
    for date, cpu in zip(df['date'], df['CPU']):
        numeric_date = ""
        for c in date:
            if c.isnumeric():
                numeric_date = numeric_date + c
        """If cpu == all, just use the default whole system flamegraph"""
        if cpu != 'all':
            """The last two digits(seconds part will be dropped)"""
            key = numeric_date[:12] + 'c' + cpu.zfill(3)
        else:
            key = numeric_date[:12]

        if key not in link_table.keys():
            link_table[key] = None
            print("{} is not in link_table.".format(key))
        links.append(link_table[key])

    return links


def plot_mpstat_group(df_meminfo, group_list, color_dict, key, link_prefix,
                      x_label="", y_label=""):

    """ Set the figure high to 600 if it's bigger than 10 lines to be drawed"""
    plot_height = 600 if len(group_list) > 10 else 300
    source = {}
    TOOLBOX = "pan,wheel_zoom,box_zoom,reset"
    if "linkall" in df_meminfo.keys():
        TOOLBOX = TOOLBOX + ",tap"
    TOOLTIPS = [("(date, value)", "(@date{%F-%T}, @value)")]

    hover = HoverTool(
        tooltips=TOOLTIPS,
        formatters={'@date': 'datetime'},
        mode='vline'
    )

    df_meminfo['date'] = pd.to_datetime(df_meminfo['date'])
    dates = np.array(df_meminfo['date'], dtype=np.datetime64)

    """ Set the default window size to 500, or the length of the samples if
    bigger than 500.
    """
    date_max = 500 if len(dates) > 500 else len(dates) - 1
    p = figure(plot_height=plot_height, plot_width=800, tools=TOOLBOX,
               x_axis_type="datetime",
               x_axis_location="below", background_fill_color="#efefef",
               x_range=(dates[0], dates[date_max]), title=key)

    p.add_tools(hover)
    p.xaxis.axis_label = x_label
    p.yaxis.axis_label = y_label

    for i in group_list:
        df_meminfo[i] = pd.to_numeric(df_meminfo[i])
        # Don't use df_meminfo[i].diff() in the CPU performance visualization
        cs_dict = dict(date=dates, value=df_meminfo[i])
        key = 'link' + i
        if key in df_meminfo.keys():
            cs_dict['link'] = df_meminfo[key]
        source[i] = ColumnDataSource(data=cs_dict)

        p.line('date', 'value', source=source[i], legend=i,
               line_color=color_dict[i])

    p.legend.click_policy = "hide"

    if "linkall" in df_meminfo.keys():
        taptool = p.select(type=TapTool)
        url_tap = os.path.join(link_prefix, "cpu/")
        url_tap = url_tap + "@link"
        taptool.callback = OpenURL(url=url_tap)

    select = figure(title="Drag the middle and edges of the selection box to"
                    " change the range above",
                    plot_height=130, plot_width=800, y_range=p.y_range,
                    x_axis_type="datetime", y_axis_type=None, tools="",
                    toolbar_location=None, background_fill_color="#efefef")

    range_tool = RangeTool(x_range=p.x_range)
    range_tool.overlay.fill_color = "navy"
    range_tool.overlay.fill_alpha = 0.2

    for i in group_list:
        select.line('date', 'value', source=source[i],
                    line_color=color_dict[i])

    select.ygrid.grid_line_color = None
    select.add_tools(range_tool)
    select.toolbar.active_multi = range_tool
    return select, p


def plot_mpstat(csv_source, link_prefix, link_table={}):
    group_dict = {}
    plot_list = []
    mpstat_path = ""
    mpstat_pretext = "\tThe graphs are generated from the mpstat instruction"

    rand_parameter_colors = []

    pre = PreText(text=mpstat_pretext, width=500, height=20)
    plot_list.append(pre)

    mpstat_path = os.path.join(csv_source, 'mpstat.csv')
    df_mpstat = pd.read_csv(mpstat_path)
    for key in df_mpstat.keys():
        if key not in ("CPU", "date"):
            """If #CPUs >= 8 (8 + all), only draw the all CPU chart, the current
            implementation still cannot handle the scalable plots generation.
            """
            if len(set(df_mpstat["CPU"])) <= 9:
                group_dict[key] = [x for x in set(df_mpstat["CPU"]) if str(x) != 'nan']
            else:
                group_dict[key] = ['all']

    if link_table:
        df_mpstat['link'] = link_list(df_mpstat, link_table)

    """Get the list of total CPU cores to draw line.
    For example: ['1', 'all', '2', '3', '0']
    """
    parameter_name = group_dict[list(group_dict.keys())[0]]

    """create a color iterator"""
    parameter_colors = magma(len(parameter_name))
    parameter_colors = list(parameter_colors)

    """Create a random color list which makes the colors in the same set are
       easy to differentiate.
    """
    while parameter_colors:
        color = random.choice(parameter_colors)
        rand_parameter_colors.append(color)
        parameter_colors.remove(color)

    color_dict = {parameter: color for parameter, color in zip(
        parameter_name, rand_parameter_colors)}

    for key in group_dict.keys():
        for count, core in enumerate(group_dict[key]):
            if count == 0:
                """Only the first loop needs to set up the 'date' and 'link'"""
                if link_table:
                    df = df_mpstat[df_mpstat['CPU'] == core][['date', key,
                                                              'link']]
                else:
                    df = df_mpstat[df_mpstat['CPU'] == core][['date', key]]
            else:
                df[key] = list(df_mpstat[df_mpstat['CPU'] == core][key])
                if link_table:
                    df['link'] = list(df_mpstat[df_mpstat['CPU'] == core]['link'])

            df.rename(columns={key: core}, inplace=True)
            """Different cpu has different flamegraph"""
            if link_table:
                df.rename(columns={'link': 'link' + core}, inplace=True)

        select, p = plot_mpstat_group(df, group_dict[key], color_dict,
                                      key, link_prefix, "date", "util (%)")

        plot_list.append(column(select, p))

    return plot_list


def cpu_tab(input_folder, output_folder, csv_source, link_prefix):
    """Store the tap link for the chart"""
    link_table = {}
    link_table = build_link(input_folder)
    link_prefix = link_prefix if link_prefix else input_folder

    l_cpu = layout(
        [
            [plot_mpstat(csv_source, link_prefix, link_table)],
        ],
        sizing_mode='scale_both'
    )
    tab_cpu = Panel(child=l_cpu, title='CPU')

    return tab_cpu
