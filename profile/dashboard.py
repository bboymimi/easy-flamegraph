#!/usr/bin/env python3

import argparse
import os
import sys
from bokeh.plotting import output_file, show
from bokeh.models.widgets import Tabs

from subsystem.cpu import cpu_tab
from subsystem.memory import memory_tab
from subsystem.io import io_tab

ez_dir = "/var/log/easy-flamegraph/"


def initialize_arguments():
    """ Assign the default search folder and the arguments """

    parser = argparse.ArgumentParser(
        description='Description for dashboard generation tool')
    parser.add_argument(
        '-a', '--all',
        action='store_true',
        help='To generate the all dashboard (cpu, mem, io...)',
        default=False)
    parser.add_argument(
        '-c', '--csv-source',
        type=str,
        help='The folder saving all the csv data (default: ./)',
        default=os.getcwd())
    parser.add_argument(
        '-i', '--input-folder',
        type=str,
        help='The input folder of the captured data '
             '(default:/var/log/easy-flamegraph/)',
        default=ez_dir)
    parser.add_argument(
        '-l', '--link-prefix',
        type=str,
        help='This is http address prefix used for the tap function when '
             'clicking on the dot. (It\'s used when the summary.html is '
             'opened in a website). If the summary.html is opened locally, '
             'the input folder will be used as prefix.',
        default=argparse.SUPPRESS)
    parser.add_argument(
        '-o', '--output-folder',
        type=str,
        help='The output folder with the dashboard (default: ./)',
        default=os.getcwd())

    return parser


def init_default_paths():
    parser = initialize_arguments()
    args = parser.parse_args()

    """Set up the output folder"""
    if os.path.isdir(args.output_folder):
        pass
    else:
        print("The output folder {} doesn't exist!!".format(
            args.output_folder))
        sys.exit(1)

    """Set up the default input folder"""
    if os.path.isdir(args.input_folder):
        pass
    else:
        print("The input folder {} doesn't exist!".format(
            args.input_folder))
        sys.exit(1)

    """Set up the default csv folder"""
    if os.path.isdir(args.csv_source):
        pass
    else:
        print("The csv source folder {} doesn't exist!".format(
            args.csv_source))
        sys.exit(1)

    """Set up the link prefix"""
    link_prefix = args.link_prefix if hasattr(args, "link_prefix") else ""

    return args.input_folder, args.output_folder, args.csv_source, link_prefix


def main():
    input_folder, output_folder, csv_source, link_prefix = init_default_paths()

    tab_cpu = cpu_tab()
    tab_memory = memory_tab(input_folder, output_folder, csv_source,
                            link_prefix)
    tab_io = io_tab()
    tabs = Tabs(tabs=[tab_cpu, tab_memory, tab_io])

    # output to static HTML file
    output_file(os.path.join(output_folder, "summary.html"))

    show(tabs)


if __name__ == '__main__':
    main()
