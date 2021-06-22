#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys

ez_dir = "/var/log/easy-flamegraph/"


def initialize_arguments(current_dir):
    """ Assign the default search folder and the arguments """

    parser = argparse.ArgumentParser(
        description='Description for Perf data summary')
    parser.add_argument(
        '-i', '--input-folder',
        type=str,
        help='The input folder with captured /var/log/easy-flamegraph',
        default=argparse.SUPPRESS)
    parser.add_argument(
        '-m', '--month',
        type=str,
        help='The month of the data to be parsed to generate .csv files',
        default="\\d+")
    parser.add_argument(
        '-o', '--output-folder',
        type=str,
        help='The output folder with all the files(include .csv, html...) ',
        default=argparse.SUPPRESS)
    parser.add_argument(
        '--cpu',
        action='store_true',
        help='Generate the CPU dash board',
        default=argparse.SUPPRESS)
    parser.add_argument(
        '--io',
        action='store_true',
        help='Generate the IO dash board',
        default=argparse.SUPPRESS)
    parser.add_argument(
        '--mem',
        action='store_true',
        help='Generate the MEM dash board',
        default=argparse.SUPPRESS)

    return parser


def main():
    current_dir = os.getcwd()
    parser = initialize_arguments(current_dir)
    args = parser.parse_args()

    # By default, generate all subsystems summary
    gen_all, gen_cpu, gen_io, gen_mem = True, False, False, False

    if hasattr(args, "cpu"):
        gen_cpu, gen_all = True, False
    if hasattr(args, "io"):
        gen_io, gen_all = True, False
    if hasattr(args, "mem"):
        gen_mem, gen_all = True, False

    realpath = os.path.realpath(sys.argv[0])
    dirname = os.path.dirname(realpath)
    extra_mem = [dirname + "/profile/cleansing/mem-extract.py"]
    dashboard = [dirname + "/profile/dashboard.py"]

    if hasattr(args, "input_folder"):
        input_dir = args.input_folder
    else:
        input_dir = ez_dir

    mem_stat_dir = os.path.join(input_dir, "sysinfo/mem-stat")
    if os.path.isdir(mem_stat_dir):
        extra_mem.append("--input-folder")
        extra_mem.append(mem_stat_dir)
    else:
        print("The input folder {} doesn't exist!!".format(mem_stat_dir))
        sys.exit(1)

    if hasattr(args, "output_folder"):
        output_dir = args.output_folder
    else:
        """Generate the intermediate files(csv,summary.html) to the designated
        folder unless assigned it in the command manually
        """
        output_dir = input_dir

    if os.path.isdir(output_dir):
        extra_mem.append("--output-folder")
        extra_mem.append(output_dir)
        """The ouput folder is the place to put csv. It's the input folder to
        get csv to generate the dashboard
        """
        dashboard.append("--input-folder")
        dashboard.append(output_dir)
        dashboard.append("--output-folder")
        dashboard.append(output_dir)
        dashboard.append("--csv-source")
        dashboard.append(output_dir)
    else:
        print("The output folder {} doesn't exist!!".format(output_dir))
        sys.exit(1)

    """Generate all the memory chart"""
    extra_mem.append("-a")

    if gen_all:
        print("Generate all subsystems summary:")

        """Currently, we only have memory extraction tool"""
        subprocess.check_call(extra_mem)
        subprocess.check_call(dashboard)
        return

    """Todo: Generate a specific type needs to be implemented"""
    if gen_cpu:
        pass
    if gen_io:
        pass
    if gen_mem:
        subprocess.check_call(extra_mem)
        subprocess.check_call(dashboard)


if __name__ == '__main__':
    main()
