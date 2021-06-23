from utils.csv.meminfo import parse_meminfo_to_csv
from utils.csv.vmstat import parse_vmstat_to_csv
from utils.csv.mpstat import parse_mpstat_to_csv


def parse_to_csv(filetype=None, filename=None, outputdir=None, month=None,
                 separate=False):

    if filetype == "meminfo":
        parse_meminfo_to_csv(filename, outputdir, month, separate)
    elif filetype == "vmstat":
        parse_vmstat_to_csv(filename, outputdir, month, separate)
    elif filetype == "mpstat":
        parse_mpstat_to_csv(filename, outputdir, month, separate)
