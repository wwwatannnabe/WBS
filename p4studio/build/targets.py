#!/usr/bin/env python3

#  INTEL CONFIDENTIAL
#
#  Copyright (c) 2021 Intel Corporation
#  All Rights Reserved.
#
#  This software and the related documents are Intel copyrighted materials,
#  and your use of them is governed by the express license under which they
#  were provided to you ("License"). Unless the License provides otherwise,
#  you may not use, modify, copy, publish, distribute, disclose or transmit this
#  software or the related documents without Intel's prior written permission.
#
#  This software and the related documents are provided as is, with no express or
#  implied warranties, other than those that are expressly stated in the License.

from collections import OrderedDict
from typing import Dict, List

from program import all_p4_programs
from workspace import current_workspace

ALL_SWITCH_PROFILES = [
    'x1_tofino',
    'x2_tofino',
    'g1_tofino',
    'y1_tofino2',
    'y2_tofino2',
    'y3_tofino2',
    'z2_tofino2'
]


def all_targets_by_group() -> Dict[str, List[str]]:
    result = p4_program_names_by_group()
    # TODO read from file
    result['Profiles'] = ALL_SWITCH_PROFILES

    result['Grouped'] = list(current_workspace().p4_dirs.keys()) + ['p4-examples']
    return result


def p4_program_names_by_group() -> Dict[str, List[str]]:
    result = OrderedDict()
    programs = all_p4_programs()

    for program in programs:
        group = program.group
        if group not in result:
            result[group] = []
        result[group].append(program.name)

    return result
