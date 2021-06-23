import csv
import os
import pandas as pd
import pathlib
import re
from utils.regex import get_date
from utils.regex import get_value


def handle_pv_list(filetype, line, separate, meminfo_params, date_msg, fp):
    params, values = get_value(filetype, line)
    if params is not None and type(params) is list:
        param_pair = zip(params, values)
        for param, value in param_pair:
            meminfo_params[param] = meminfo_params.get(param, [])

            if separate:
                meminfo_params[param].append([date_msg, value])
            else:
                # Append the the value if the operation is normal
                meminfo_params[param].append(value)


def parse_mpstat_to_csv(filename, outputdir, month, separate):
    meminfo_params = {}
    m_date = None
    date_msg = None
    df_all = pd.DataFrame()
    filetype = "mpstat"

    try:
        with open(filename, 'r') as fp:
            print("Parsing " + filename)
            line = fp.readline()

            while line:
                # skip the label line
                label_line = re.search(r"Average:\s+CPU", line)
                if label_line:
                    line = fp.readline()
                    continue

                # scan the separate line '----'
                if(line[0] == "-"):
                    m = re.search("----------", line)
                    if m:
                        # clear the date and the recorded parameters
                        m_date = None
                        line = fp.readline()
                        continue

                # i.e. 2020.05.29-23.18.02
                if m_date is None:
                    date_msg = get_date(month, line)
                    if date_msg is not None:
                        m_date = 1
                        """We don't append the date here. It will dupliate at
                        the first insertion.
                        """
                    line = fp.readline()
                    continue
                else:
                    # Needs to append the date as there are many CPUs
                    meminfo_params["date"] = meminfo_params.get("date", [])
                    meminfo_params["date"].append(date_msg)

                handle_pv_list(filetype, line, separate, meminfo_params,
                               date_msg, fp)

                line = fp.readline()
    except OSError:
        if filename == "":
            print("[%s] Filename is empty! Please assign the file to parse or "
                  "check the default path." % filetype)
        else:
            print("[%s] Cannot read \"%s\", May be it doesn't exist!"
                  % (filetype, filename))
        return

    key = []
    keys = meminfo_params.keys()
    if list(keys) == []:
        print("[%s] No keys found in %s!, the format is not correct!" %
              (filetype, filename))
        return

    if separate:
        for key in list(keys):
            pathlib.Path(outputdir).mkdir(parents=True, exist_ok=True)
            with open(outputdir + '/' + key + '.csv', 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["date", "value"])
                writer.writerows(meminfo_params[key])
        print("The .csv file is separated under: " + os.getcwd())
    else:
        df_all = pd.DataFrame(meminfo_params)
        df_all.set_index('date', inplace=True)
        csv_output_file = os.path.join(outputdir, filetype + ".csv")
        df_all.to_csv(csv_output_file)
        print("The " + csv_output_file + " is generated")
