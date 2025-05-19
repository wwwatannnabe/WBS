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
import sys

from system.check_system_command import check_system_command

try:
    import click
    from click import ClickException, Abort
except ImportError as e:
    print("Cannot import click module. Have you installed p4studio dependencies?")
    print("Run install-p4studio-dependencies.sh as root to install all dependencies required to run p4studio")
    sys.exit(1)

from app import app_command
from build import build_command
from config import configure_command
from dependencies import dependencies_command
from interactive.interactive_command import interactive_command
from profile import profile_command
from clean.clean_command import clean_command
from packages.packages_command import packages_command
from utils.exceptions import ApplicationException
from utils.logging import initialize_loggers
from workspace import configure_env_variables, in_workspace

try:
    from utils.click import OrderedGroup
except ApplicationException as e:
    click.secho('Error: {}'.format(e), err=True, fg='red')
    sys.exit(1)


@click.group(cls=OrderedGroup)
def p4studio_cli():
    """
    \b
    p4studio helps to manage SDE and its environment by:
    \b
    - installing dependencies,
    - building and installing SDE components,
    - building and installing P4 programs.
    """
    initialize_loggers()


P4STUDIO_COMMANDS = [
    app_command,
    check_system_command,
    packages_command,
    dependencies_command,
    configure_command,
    build_command,
    profile_command,
    interactive_command,
    clean_command
]

for command in P4STUDIO_COMMANDS:
    p4studio_cli.add_command(command)


def p4studio_main():
    if in_workspace():
        configure_env_variables()
    try:
        p4studio_cli.main(sys.argv[1:], standalone_mode=False)
    except (
            ClickException,
            ApplicationException,
            PermissionError
    ) as e:
        click.secho('Error: {}'.format(e), err=True, fg='red')
        sys.exit(1)
    except Abort:
        sys.exit(1)
