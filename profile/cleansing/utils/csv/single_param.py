import csv
import os
import pandas as pd
import pathlib
import re
from utils.regex import get_date
from utils.regex import get_value


def parse_single_param_to_csv(filetype, filename, outputdir, month, separate):
    meminfo_params = {}
    m_date = None
    date_msg = None
    df_all = pd.DataFrame()

    try:
        with open(filename, 'r') as fp:
            print("Parsing " + filename)
            line = fp.readline()

            count = 0
            while line:
                # scan the separate line '----'
                if(line[0] == "-"):
                    m = re.search("----------", line)
                    if m:
                        # clear the date and the recorded parameters
                        m_date = None

                # i.e. 2020.05.29-23.18.02
                if m_date is None:
                    date_msg = get_date(month, line)
                    if date_msg is not None:
                        count = 0
                        m_date = 1
                        meminfo_params["date"] = meminfo_params.get("date", [])
                        meminfo_params["date"].append(date_msg)
                    line = fp.readline()
                    continue

                param, value = get_value(filetype, line)
                if param is not None:
                    meminfo_params[param] = meminfo_params.get(param, [])

                    if separate:
                        meminfo_params[param].append([date_msg, value])
                    else:
                        count = count + 1
                        if count > len(meminfo_params.keys()):
                            if count == len(meminfo_params.keys()) + 1:
                                print(date_msg, count)
                                print("Drop the remaining data")

                            # Just proceed to read the next line and don't
                            # append the value as it's already replicated. Only
                            # save one record and skip the remaining.
                            # Error log example:
                            # ---------------------------------------------
                            # ---------------------------------------------
                            # 2020.12.22-16.11.41
                            # 2020.12.22-16.11.41
                            line = fp.readline()
                            continue

                        # Append the the value if the operation is normal
                        meminfo_params[param].append(value)

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
        df_all = pd.DataFrame.from_dict(meminfo_params, orient='index')
        df_all = df_all.transpose()
        df_all.set_index('date', inplace=True)
        csv_output_file = os.path.join(outputdir, filetype + ".csv")
        df_all.to_csv(csv_output_file)
        print("The " + csv_output_file + " is generated")
