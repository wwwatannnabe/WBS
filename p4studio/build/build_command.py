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
import os
from typing import List

import click
from click import Choice

from pathlib import Path

from build.targets import all_targets_by_group
from utils.exceptions import ApplicationException
from utils.logging import logging_options
from utils.processes import execute
from utils.terminal import print_green, columnize
from workspace import current_workspace, in_workspace, setup_path_variables


def _describe_build_command():
    result = "Build SDE components and P4 programs\n\n"
    result += "TARGET is the name of P4 program or switch profile\n\n"

    if in_workspace():
        result += "Following list cover all acceptable names:\n\n"
        for name, targets in all_targets_by_group().items():
            result += "\b\n{}:\n{}\n".format(name, columnize(targets, 2))
    return result


def _allowed_targets() -> List[str]:
    return sorted(sum(all_targets_by_group().values(), [])) if in_workspace() else []


@click.command(name='build', help=_describe_build_command(), short_help="Build SDE components and P4 programs\n\n")
@click.argument('targets', type=Choice(_allowed_targets()), nargs=-1, metavar='[TARGET]...')
@logging_options()
@click.option('--dependencies-dir', type=click.Path(file_okay=False, writable=True), default=None,
              help="Directory where dependencies were installed")
@click.option('--jobs', default=os.cpu_count(), help="Allow N jobs at once")
def build_command(targets, jobs, dependencies_dir):
    print_green("Building and installing {}...", current_workspace().name)

    dependencies_dir = Path(dependencies_dir) if dependencies_dir else current_workspace().default_install_dir

    setup_path_variables(dependencies_dir)

    build_dir = current_workspace().build_path

    if not build_dir.is_dir():
        msg = "Build not configured. check p4studio configure --help for more details"
        raise ApplicationException(msg)

    print_green("Building...")
    make("Build", build_dir, jobs, list(targets))
    print_green("Built successfully")
    print_green("Installing...")
    make("Installation", build_dir, jobs, ['install'])
    print_green("Installed successfully")
    print_green("{} built and installed.", current_workspace().name)


def make(name, working_dir, jobs, targets):
    jobs_arg = '--jobs={}'.format(jobs) if jobs else '--jobs'

    command = ['make', jobs_arg] + targets
    if not execute(command, working_dir):
        message = "{} completed unsuccessfully".format(name)
        raise ApplicationException(message)
