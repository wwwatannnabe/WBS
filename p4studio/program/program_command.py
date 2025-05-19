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
from typing import List

import click

from utils.exceptions import ApplicationException
from workspace import current_workspace


@click.group('program')
def program_command():
    """Manage P4 programs"""


@click.command('list')
@click.option('--format', default="{group:<24} {name:<41}", help='List programs using specific template')
@click.option('--skip-header', is_flag=True, default=False, help='Do not print header in the first line')
def list_programs_command(format, skip_header):
    """
    List available programs
    """

    if not skip_header:
        header = format.format(name='NAME:', group='GROUP:', path='PATH:')
        click.secho(header, color='green', bold=True)
    for program in all_p4_programs():
        try:
            entry = format.format(
                name=program.name,
                group=program.group,
                path=program.path
            )
        except KeyError as e:
            available_keys = ', '.join(program.__dict__.keys())
            message = "Incorrect key. {} does not match any of: {}.".format(e, available_keys)
            raise ApplicationException(message)
        except Exception as e:
            raise ApplicationException(e)
        print(entry)


program_command.add_command(list_programs_command)


class P4ProgramInfo:
    def __init__(self, name, group, path):
        self.name = name
        self.group = group
        self.path = path


def all_p4_programs() -> List[P4ProgramInfo]:
    result = []
    for group_name, group_path in current_workspace().p4_dirs.items():
        if not group_path.exists():
            continue
        for path in group_path.iterdir():
            if not path.is_dir():
                continue
            program_name = path.name + '.p4'
            if (path / program_name).is_file():
                program = P4ProgramInfo(path.name, group_name, path)
                result.append(program)
    result.sort(key=lambda p: (p.group, p.name))
    return result
