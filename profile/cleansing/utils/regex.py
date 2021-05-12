import re

regexp_arr = {
    "meminfo": "^(\w+\(*\w+\)*):\s+(\d+)",
    "vmstat": "^(\w+)\s+(\d+)",
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
            param = m_param.expand(r"\1")
            value = m_param.expand(r"\2")
    return param, value
