import csv
import pathlib
import re
from .regex import get_date
from .regex import get_value


def parse_to_csv(filetype=None, filedir=None, outputdir=None, month=None):
    meminfo_params = {}
    m_date = None
    date_msg = None

    try:
        print("Parsing " + filedir + filetype + ".log...")
        with open(filedir + filetype + '.log', 'r') as fp:
            line = fp.readline()

            # i = 0
            # while i < 130:
            while line:
                # scan the separate line '----'
                if(line[0] == "-"):
                    m = re.search("----------", line)
                    # print("i = %d" % i)
                    if m:
                        # clear the date and the recorded parameters
                        m_date = None

                # i.e. 2020.05.29-23.18.02
                if m_date is None:
                    date_msg = get_date(month, line)
                    if date_msg is not None:
                        m_date = 1
                        # print("date_msg:" + date_msg)

                param, value = get_value(filetype, line)
                if param is not None:
                    meminfo_params[param] = meminfo_params.get(param, [])
                    meminfo_params[param].append([date_msg, value])

                line = fp.readline()
                # print("fp.readline:" + line)
                # i = i + 1
    except OSError:
        print("Cannot read the file: %s, May be it doesn't exist!" % (filedir +
              'meminfo1.log'))

    key = None
    keys = meminfo_params.keys()
    # print(list(keys))
    for key in list(keys):
        # print("~/Downloads/" + key + ".csv")
        # print(meminfo_params[key])
        pathlib.Path(outputdir).mkdir(parents=True, exist_ok=True)
        with open(outputdir + '/' + key + '.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            # print("~/Downloads/" + key + ".csv")
            # print(meminfo_params[key])
            writer.writerow(["date", "value"])
            writer.writerows(meminfo_params[key])
