#!/usr/bin/env python3
import argparse
import os
import sys
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
        help='The output folder with the .csv files(default: ./)',
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
        '-i', '--input-folder',
        type=str,
        help='The input folder of the captured data'
             '(default:/var/log/easy-flamegraph/sysinfo/mem-stat',
        default=argparse.SUPPRESS)
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


def init_default_paths(args, current_dir):
    ftype_name = {}
    ftypes = ["meminfo", "vmstat"]
    output_folder = ""
    search_folders = [ez_dir, current_dir]

    """Set up the output folder"""
    if hasattr(args, "output_folder"):
        if os.path.isdir(args.output_folder):
            output_folder = args.output_folder
        else:
            print("The output folder {} doesn't exist!!".format(
                args.output_folder))
            sys.exit(1)

    """If the specific file type is assigned, just skip the possible input file
    source search.
    """

    if hasattr(args, "meminfo"):
        if args.meminfo is not None:
            return ftype_name, output_folder
    if hasattr(args, "vmstat"):
        if args.vmstat is not None:
            return ftype_name, output_folder

    """Set up the default input folder"""
    if hasattr(args, "input_folder"):
        search_folders.clear()
        if os.path.isdir(args.input_folder):
            search_folders.insert(0, args.input_folder)
        else:
            print("The input folder {} doesn't exist!".format(
                args.input_folder))
            sys.exit(1)

    for folder in search_folders:
        for ftype in ftypes:
            if os.path.isfile(os.path.join(folder, ftype + '.log')):
                ftype_name[ftype] = os.path.join(folder, ftype + '.log')
            else:
                """If any ftype can't find the file, proceed to next folder"""
                break
        else:
            """If the ftype folders loop are all traversed, it means all the
            ftype files can be found in the folder.
            """
            break
    else:
        """All the folders are traversed, the ftype cannot find in all
        folders.
        """
        print("Cannot find the valid input file for parsing!!")
        print("{} don't have all required file type {}.log".format(
            search_folders, ftypes))

        sys.exit(1)

    return ftype_name, output_folder


def main():
    current_dir = os.getcwd()
    parser = initialize_arguments(current_dir)
    args = parser.parse_args()
    ftype_name, output_folder = init_default_paths(args, current_dir)
    show_usage = True

    # (1). Parse the meminfo.log
    if hasattr(args, "meminfo") or args.all:
        show_usage = False
        if args.all or args.meminfo is None:
            # The user just input the --meminfo and doesn't have any appends
            parse_to_csv("meminfo", ftype_name['meminfo'], output_folder,
                         args.month, args.separate)
        else:
            # Use the file name provided by the user
            parse_to_csv("meminfo", args.meminfo, output_folder,
                         args.month, args.separate)

    # (2). Parse the vmstat.log
    if hasattr(args, "vmstat") or args.all:
        show_usage = False
        if args.all or args.vmstat is None:
            # The user just input the --meminfo and doesn't have any appends
            parse_to_csv("vmstat", ftype_name['vmstat'], output_folder,
                         args.month, args.separate)
        else:
            # Use the file name provided by the user
            parse_to_csv("vmstat", args.vmstat, output_folder,
                         args.month, args.separate)

    if show_usage:
        print(parser.print_help())


if __name__ == '__main__':
    main()
