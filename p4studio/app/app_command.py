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
from os.path import abspath, dirname

import click
from click._bashcomplete import get_completion_script

from workspace import current_workspace


@click.group('app')
def app_command():
    """
    Manage p4studio application and its environment
    """


@click.command('activate')
@click.option('--with-workspace', is_flag=True, default=False,
              help="Configure workspace specific environment variables")
def activate_command(with_workspace):
    """
    Enable bash completion and configure environment variables
    """
    print(get_completion_script('p4studio', '_P4STUDIO_COMPLETE', 'bash'))
    print()
    print(_get_update_path_script('PATH', dirname(abspath(sys.argv[0]))))

    if with_workspace:
        print(_get_update_path_script('PATH', current_workspace().default_install_dir / 'bin'))
        print(_get_update_path_script('CMAKE_LIBRARY_PATH', current_workspace().default_install_dir / 'lib'))
        print(_get_update_path_script('CMAKE_INCLUDE_PATH', current_workspace().default_install_dir / 'include'))
        print(_get_update_path_script('LIBRARY_PATH', current_workspace().default_install_dir / 'lib'))
        print(_get_update_path_script('LD_RUN_PATH', current_workspace().default_install_dir / 'lib'))
        print(_get_update_path_script('CPLUS_INCLUDE_PATH', current_workspace().default_install_dir / 'include'))
        print(_get_update_path_script('PKG_CONFIG_PATH', current_workspace().default_install_dir / 'lib/pkgconfig'))


app_command.add_command(activate_command)


def _get_update_path_script(var_name, added_dir):
    template = 'if [ ":${var_name}:" != *":{added_dir}:"* ]; then export {var_name}="{added_dir}:${var_name}"; fi'
    return template.format(var_name=var_name, added_dir=added_dir)
