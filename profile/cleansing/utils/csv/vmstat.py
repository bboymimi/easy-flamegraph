from utils.csv.single_param import parse_single_param_to_csv


def parse_vmstat_to_csv(filename, outputdir, month, separate):
    parse_single_param_to_csv("vmstat", filename, outputdir, month, separate)
