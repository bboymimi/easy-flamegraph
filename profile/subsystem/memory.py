#!/usr/bin/env python3

from __future__ import print_function
from bokeh.layouts import column, layout
from bokeh.plotting import ColumnDataSource, figure
from bokeh.palettes import magma
from bokeh.models import HoverTool, OpenURL, Panel, PreText, RangeTool, TapTool
import numpy as np
import os
import pandas as pd
import random


def build_link(default_directory="/var/log/easy-flamegraph"):
    """The current link tap implementation is to show the svg file. Finally,
    the specific html for a time stamp replace the svg file to provide a more
    comprehensive summary.
    """

    filenames = []
    filelist = {}
    link_dir = os.path.join(default_directory, 'mem')

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
        numeric_date = ""
        for c in f:
            if c.isnumeric():
                numeric_date = numeric_date + c
        """The last two digits seconds part will be dropped"""
        filelist[numeric_date[:-2]] = f

    return filelist


def link_list(df, link_table):
    links = []
    for date in df['date']:
        numeric_date = ""
        for c in date:
            if c.isnumeric():
                numeric_date = numeric_date + c
        """The last two digits(seconds part will be dropped)"""
        if numeric_date[:-2] not in link_table.keys():
            link_table[numeric_date[:-2]] = None
            print("{} is not in link_table.".format(numeric_date[:-2]))
        links.append(link_table[numeric_date[:-2]])

    return links


def plot_meminfo_group(df_meminfo, group_list, color_dict, key, x_label="",
                       y_label=""):

    """ Set the figure high to 600 if it's bigger than 10 lines to be drawed"""
    plot_height = 600 if len(group_list) > 10 else 300
    source = {}
    TOOLBOX = "pan,wheel_zoom,box_zoom,reset"
    if "link" in df_meminfo.keys():
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
        cs_dict = dict(date=dates, value=df_meminfo[i].diff())
        if "link" in df_meminfo.keys():
            cs_dict['link'] = df_meminfo['link']
        source[i] = ColumnDataSource(data=cs_dict)

        p.line('date', 'value', source=source[i], legend=i,
               line_color=color_dict[i])

    p.legend.click_policy = "hide"

    if "link" in df_meminfo.keys():
        taptool = p.select(type=TapTool)
        url_tap = "/var/log/easy-flamegraph/mem/@link"
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


def plot_meminfo(link_table={}):
    group_dict = {}
    plot_list = []
    meminfo_path = ""
    meminfo_pretext = "\tThe graphs are generated from the /proc/meminfo"

    rand_parameter_colors = []

    group_dict["LRU list"] = ["MemFree", "MemAvailable", "Active", "Inactive",
                              "Active(anon)", "Active(file)", "Inactive(anon)",
                              "Inactive(file)"]
    group_dict["Mem Basic Counters"] = ["MemAvailable", "MemFree", "SwapFree",
                                        "Buffers", "Cached"]
    group_dict["Slab"] = ["Slab", "SReclaimable", "SUnreclaim", "KReclaimable"]
    group_dict["Combined"] = ["MemAvailable", "MemFree", "SwapFree", "Buffers",
                              "Cached", "Active", "Inactive", "Active(anon)",
                              "Active(file)", "Inactive(anon)",
                              "Inactive(file)", "Slab", "SReclaimable",
                              "SUnreclaim"]
    group_dict["Swap"] = ["SwapTotal", "SwapFree", "SwapCached"]
    group_dict["User"] = ["AnonPages", "Mapped", "Mlocked", "Shmem"]
    group_dict["MISC type"] = ["Dirty", "Writeback"]
    group_dict["kernel type"] = ["KernelStack", "PageTables", "NFS_Unstable",
                                 "Bounce", "WritebackTmp", "Percpu"]
    group_dict["commit"] = ["CommitLimit", "Committed_AS"]
    group_dict["vmalloc"] = ["VmallocTotal", "VmallocUsed", "VmallocChunk"]
    group_dict["HardwareCorrupted"] = ["HardwareCorrupted"]
    group_dict["THP"] = ["AnonHugePages", "ShmemHugePages", "ShmemPmdMapped",
                         "FileHugePages", "FilePmdMapped"]
    group_dict["persistent hugepage"] = ["HugePages_Total", "HugePages_Free",
                                         "HugePages_Rsvd", "HugePages_Surp",
                                         "Hugepagesize", "Hugetlb"]
    group_dict["DirectMap"] = ["DirectMap4k", "DirectMap2M", "DirectMap1G"]
    group_dict["cma"] = ["CmaTotal", "CmaFree"]

    pre = PreText(text=meminfo_pretext, width=500, height=20)
    plot_list.append(pre)

    meminfo_path = os.path.join(os.getcwd(), 'meminfo.csv')
    df_meminfo = pd.read_csv(meminfo_path)
    if link_table:
        df_meminfo['link'] = link_list(df_meminfo, link_table)
    parameter_name = df_meminfo.keys()

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
        select, p = plot_meminfo_group(df_meminfo, group_dict[key],
                                       color_dict, key, "date", "KB/count")

        plot_list.append(column(select, p))

    return plot_list


def plot_vmstat(link_table):
    group_dict = {}
    plot_list = []
    vmstat_path = ""
    vmstat_pretext = "\tThe graphs are generated from the /proc/vmstat"

    rand_parameter_colors = []

    group_dict["VMSTAT LRU list"] = ["nr_free_pages", "nr_zone_inactive_anon",
                                     "nr_zone_active_anon",
                                     "nr_zone_inactive_file",
                                     "nr_zone_active_file",
                                     "nr_zone_unevictable",
                                     "nr_file_pages",
                                     "nr_anon_pages",
                                     "nr_inactive_anon",
                                     "nr_active_anon",
                                     "nr_inactive_file",
                                     "nr_active_file",
                                     "nr_unevictable",
                                     "nr_free_cma",
                                     "nr_slab_reclaimable",
                                     "nr_slab_unreclaimable",
                                     "nr_kernel_misc_reclaimable"]

    group_dict["VMSTAT pgsteal, pgscan"] = ["pgsteal_kswapd", "pgsteal_direct",
                                            "pgrefill", "pgscan_kswapd",
                                            "pgscan_direct",
                                            "pgscan_direct_throttle",
                                            "pginodesteal", "slabs_scanned",
                                            "kswapd_inodesteal"]

    group_dict["VMSTAT compact1"] = ["compact_migrate_scanned",
                                     "compact_free_scanned",
                                     "compact_isolated"]

    group_dict["VMSTAT compact2"] = ["compact_stall", "compact_fail",
                                     "compact_success", "compact_daemon_wake",
                                     "compact_daemon_migrate_scanned",
                                     "compact_daemon_free_scanned"]

    group_dict["VMSTAT high/low watermark"] = ["kswapd_low_wmark_hit_quickly",
                                               "kswapd_high_wmark_hit_quickly"]

    group_dict["VMSTAT NUMA"] = ["numa_hit", "numa_miss", "numa_foreign",
                                 "numa_interleave", "numa_local", "numa_other",
                                 "numa_pte_updates", "numa_huge_pte_updates",
                                 "numa_hint_faults", "numa_hint_faults_local",
                                 "numa_pages_migrated", "pgmigrate_success",
                                 "pgmigrate_fail"]

    group_dict["VMSTAT workingset"] = ["workingset_nodes",
                                       "workingset_refault",
                                       "workingset_activate",
                                       "workingset_restore",
                                       "workingset_nodereclaim"]

    group_dict["VMSTAT pgalloc/pgfree"] = ["pgalloc_dma", "pgalloc_dma32",
                                           "pgalloc_normal",
                                           "allocstall_movable", "pgfree"]

    group_dict["VMSTAT allocstall"] = ["allocstall_dma", "allocstall_dma32",
                                       "allocstall_normal", "pgalloc_movable"]

    group_dict["VMSTAT drop{cache,slab} oomkill"] = ["drop_pagecache",
                                                     "drop_slab", "oom_kill"]

    group_dict["VMSTAT {swap,pg}{in,out}"] = ["pgpgin", "pgpgout", "pswpin",
                                              "pswpout", "pageoutrun"]

    group_dict["VMSTAT user pages"] = ["nr_mapped", "nr_shmem", "nr_shmem"]

    group_dict["VMSTAT dirty/write pages"] = ["nr_dirtied", "nr_dirty",
                                              "nr_dirty_threshold",
                                              "nr_dirty_background_threshold",
                                              "nr_vmscan_write",
                                              "nr_vmscan_immediate_reclaim",
                                              "nr_written",
                                              "zone_reclaim_failed"]

    group_dict["VMSTAT nr_misc1"] = ["nr_isolated_anon", "nr_isolated_file",
                                     "nr_writeback", "nr_writeback_temp",
                                     "nr_shmem", "nr_shmem_hugepages",
                                     "nr_shmem_pmdmapped", "nr_file_hugepages",
                                     "nr_file_pmdmapped",
                                     "nr_anon_transparent_hugepages",
                                     "nr_unstable"]

    group_dict["VMSTAT nr_misc2"] = ["nr_mlock", "nr_page_table_pages",
                                     "nr_kernel_stack", "nr_bounce",
                                     "nr_zspages", "pglazyfree", "pglazyfreed"]

    group_dict["VMSTAT nr_misc3"] = ["pgactivate", "pgdeactivate", "pgfault",
                                     "pgmajfault", "pgrotated",
                                     "pgmigrate_success", "pgmigrate_fail"]

    group_dict["VMSTAT pgskip"] = ["pgskip_dma", "pgskip_dma32",
                                   "pgskip_normal", "pgskip_movable"]

    group_dict["VMSTAT thp"] = ["thp_fault_alloc", "thp_fault_fallback",
                                "thp_collapse_alloc",
                                "thp_collapse_alloc_failed", "thp_file_alloc",
                                "thp_file_mapped", "thp_split_page",
                                "thp_split_page_failed",
                                "thp_deferred_split_page", "thp_split_pmd",
                                "thp_split_pud", "thp_zero_page_alloc",
                                "thp_zero_page_alloc_failed", "thp_swpout",
                                "thp_swpout_fallback"]

    group_dict["VMSTAT swap_{ra,ra_hit}"] = ["swap_ra", "swap_ra_hit"]

    group_dict["VMSTAT balloon"] = ["balloon_inflate", "balloon_deflate",
                                    "balloon_migrate"]

    group_dict["VMSTAT unevictable"] = ["unevictable_pgs_culled",
                                        "unevictable_pgs_scanned",
                                        "unevictable_pgs_rescued",
                                        "unevictable_pgs_mlocked",
                                        "unevictable_pgs_munlocked",
                                        "unevictable_pgs_cleared",
                                        "unevictable_pgs_stranded"]

    group_dict["VMSTAT htlb"] = ["htlb_buddy_alloc_success",
                                 "htlb_buddy_alloc_fail"]

    pre = PreText(text=vmstat_pretext, width=500, height=20)
    plot_list.append(pre)

    vmstat_path = os.path.join(os.getcwd(), 'vmstat.csv')
    df_vmstat = pd.read_csv(vmstat_path)
    if link_table:
        df_vmstat['link'] = link_list(df_vmstat, link_table)
    parameter_name = df_vmstat.keys()

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
        select, p = plot_meminfo_group(df_vmstat, group_dict[key],
                                       color_dict, key, "date",
                                       "KB/count/pages")

        plot_list.append(column(select, p))

    return plot_list


def memory_tab():
    """Store the tap link for the chart"""
    link_table = {}
    link_table = build_link()

    l_mem = layout(
        [
            [plot_meminfo(link_table), plot_vmstat(link_table)],
        ],
        sizing_mode='scale_both'
    )
    tab_memory = Panel(child=l_mem, title='Mem')

    return tab_memory
