import regex as re

"""mpstat log example
Average:     CPU    %usr   %nice    %sys %iowait    %irq   %soft  %steal  %guest  %gnice   %idle
Average:     all    8.67    0.00    2.55    0.00    0.00    0.00    0.00    0.00    0.00   88.78
Average:       0    5.05    0.00    4.04    0.00    0.00    0.00    0.00    0.00    0.00   90.91
"""
regexp_arr = {
    "meminfo": r"^(\w+\(*\w+\)*):\s+(\d+)",
    "vmstat": r"^(\w+)\s+(\d+)",
    "mpstat": r"^Average\:\s+(\w+)(\s+(\d+\.\d+))+",
}


# i.e. 2020.05.29-23.18.02
def get_date(month, line):
    m_date = re.search(r"(\d+)\.(" + month + ")\.(\d+)\-(\d+)\.(\d+)\.(\d+)", line)

    if m_date:
        date_msg = m_date.expand(r"\1-\2-\3-\4:\5:\6")
        return date_msg
    return None


def get_value(filetype=None, line=None):
    m_param = None
    param = None
    value = None

    if filetype is not None:
        m_param = re.search(regexp_arr[filetype], line)
        if m_param:
            if filetype is "mpstat":
                param = ["CPU", "%usr", "%nice", "%sys", "%iowait", "%irq",
                         "%soft", "%steal", "%guest", "%gnice", "%idle"]

                value = m_param.group().split()
                value.remove("Average:")
                return param, value

            param = m_param.expand(r"\1")
            value = m_param.expand(r"\2")
    return param, value
