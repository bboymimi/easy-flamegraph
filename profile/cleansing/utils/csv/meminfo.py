from utils.csv.single_param import parse_single_param_to_csv

def parse_meminfo_to_csv(filename, outputdir, month, separate):
    parse_single_param_to_csv("meminfo", filename, outputdir, month, separate)
