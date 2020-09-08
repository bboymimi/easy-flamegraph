# This file is part of FlameScope, a performance analysis tool created by the
# Netflix cloud performance team. See:
#
#    https://github.com/Netflix/flamescope
#
# Copyright 2018 Netflix, Inc.
#
#    Licensed under the Apache License, Version 2.0 (the "License");
#    you may not use this file except in compliance with the License.
#    You may obtain a copy of the License at
#
#    http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS,
#    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#    See the License for the specific language governing permissions and
#    limitations under the License.

from os.path import join, getmtime
from app.common.error import InvalidFileError
from app.perf.flame_graph import perf_generate_flame_graph
from app.cpuprofile.flame_graph import cpuprofile_generate_flame_graph
from app.nflxprofile.flame_graph import nflxprofile_generate_flame_graph
from app.trace_event.flame_graph import trace_event_generate_flame_graph
from app.common.flame_graph import get_differential_flame_graph
from app import config


def generate_differential_flame_graph(filename, file_type, compare_filename, compare_type, start, end, compare_start, compare_end):
    file_path_1 = join(config.PROFILE_DIR, filename)
    mtime_1 = getmtime(file_path_1)
    flame_graph_1 = None
    if file_type == 'perf':
        flame_graph_1 = perf_generate_flame_graph(file_path_1, start, end)
    elif file_type == 'cpuprofile':
        flame_graph_1 = cpuprofile_generate_flame_graph(file_path_1, start, end)
    elif file_type == 'trace_event':
        flame_graph_1 = trace_event_generate_flame_graph(file_path_1, mtime_1, start, end)
    elif file_type == 'nflxprofile':
        flame_graph_1 = nflxprofile_generate_flame_graph(file_path_1, start, end)
    else:
        raise InvalidFileError('Unknown file type.')

    file_path_2 = join(config.PROFILE_DIR, compare_filename)
    mtime_2 = getmtime(file_path_2)
    flame_graph_2 = None
    if compare_type == 'perf':
        flame_graph_2 = perf_generate_flame_graph(file_path_2, compare_start, compare_end)
    elif compare_type == 'cpuprofile':
        flame_graph_2 = cpuprofile_generate_flame_graph(file_path_2, compare_start, compare_end)
    elif compare_type == 'trace_event':
        flame_graph_2 = trace_event_generate_flame_graph(file_path_2, mtime_2, compare_start, compare_end)
    elif compare_type == 'nflxprofile':
        flame_graph_2 = nflxprofile_generate_flame_graph(file_path_2, compare_start, compare_end)
    else:
        raise InvalidFileError('Unknown file type.')

    return get_differential_flame_graph(flame_graph_1, flame_graph_2)
