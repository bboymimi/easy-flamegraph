#!/usr/bin/env python3
import argparse
import os
from utils.parser import parse_to_csv

ez_dir = "/var/log/easy-flamegraph/sysinfo/mem-stat/"


def initialize_arguments(current_dir):
    """ Assign the default search folder and the arguments """

    parser = argparse.ArgumentParser(
        description='Description for csv generation tool')
    parser.add_argument(
        '-m', '--month',
        type=str,
        help='The month of the data to be parsed to generate .csv files',
        default="\\d+")
    parser.add_argument(
        '-o', '--output-folder',
        type=str,
        help='The output folder with the .csv files',
        default=current_dir)
    parser.add_argument(
        '-s', '--separate',
        action='store_true',
        help='To break the union csv into a separate one',
        default=False)
    parser.add_argument(
        '-a', '--all',
        action='store_true',
        help='To generate the all filetype(meminfo/vmstat...) csv',
        default=False)
    parser.add_argument(
        '--diff',
        action='store_true',
        help='To generate the diff value csv')
    parser.add_argument(
        '--meminfo',
        type=str,
        nargs='?',
        help='The /proc/meminfo file to be transferred to csv',
        default=argparse.SUPPRESS)
    parser.add_argument(
        '--vmstat',
        type=str,
        nargs='?',
        help='The /proc/vmstat file to be transferred to csv',
        default=argparse.SUPPRESS)

    return parser


def init_default_paths(current_dir):
    ftype_name = {}

    for ftype in ("meminfo", "vmstat"):
        if os.path.isfile(os.path.join(current_dir, ftype + '.log')):
            ftype_name[ftype] = os.path.join(current_dir, ftype + '.log')
        elif os.path.isfile(os.path.join(ez_dir, ftype + '.log')):
            ftype_name[ftype] = os.path.join(ez_dir, ftype + '.log')
        else:
            ftype_name[ftype] = ""

    return ftype_name


def main():
    current_dir = os.getcwd()
    parser = initialize_arguments(current_dir)
    args = parser.parse_args()
    ftype_name = init_default_paths(current_dir)
    show_usage = True

    # (1). Parse the meminfo.log
    if hasattr(args, "meminfo") or args.all:
        show_usage = False
        if args.all or args.meminfo is None:
            # The user just input the --meminfo and doesn't have any appends
            parse_to_csv("meminfo", ftype_name['meminfo'], args.output_folder,
                         args.month, args.separate)
        else:
            # Use the file name provided by the user
            parse_to_csv("meminfo", args.meminfo, args.output_folder,
                         args.month, args.separate)

    # (2). Parse the vmstat.log
    if hasattr(args, "vmstat") or args.all:
        show_usage = False
        if args.all or args.vmstat is None:
            # The user just input the --meminfo and doesn't have any appends
            parse_to_csv("vmstat", ftype_name['vmstat'], args.output_folder,
                         args.month, args.separate)
        else:
            # Use the file name provided by the user
            parse_to_csv("vmstat", args.vmstat, args.output_folder,
                         args.month, args.separate)

    if show_usage:
        print(parser.print_help())


if __name__ == '__main__':
    main()
