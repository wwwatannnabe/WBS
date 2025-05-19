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

import click
import yaml

from pathlib import Path

from dependencies.dependency_installer import DependencyInstaller
from dependencies.dependency_manager import ALL_DEPENDENCY_GROUPS, dependency_manager
from utils.logging import logging_options
from utils.os_info import os_info
from utils.terminal import print_green, print_normal, print_separator
from workspace import current_workspace, in_workspace, setup_path_variables


@click.group('dependencies')
def dependencies_command():
    """Manage SDE dependencies"""


@click.command('list')
@click.option("--os-name", default=os_info.name, help="OS Name (Ubuntu, CentOS)")
@click.option("--os-version", default=os_info.version, help="OS Version (16.04, 18.04, 9)")
@click.option("--raw", is_flag=True, help="List dependencies in YAML format")
def list_dependencies_command(os_name, os_version, raw):
    """Show all dependencies that should be satisfied"""

    manager = dependency_manager(os_name, os_version)

    if raw:
        click.secho(yaml.dump(manager.data))
        return

    types = [
        ("os_packages", "OS"),
        ("pip3_packages", "pip3"),
        ("source_packages", "Source")
    ]

    for installer_type, name in types:
        print_green("{} dependencies:", name)
        print_normal(' '.join(manager.packages(installer_type, ALL_DEPENDENCY_GROUPS)))
        print_separator()


def describe_source_packages_option():
    result = "Comma separated list of source packages that should be built"
    if in_workspace():
        source_packages = dependency_manager().packages('source_packages', ALL_DEPENDENCY_GROUPS)
        result += ': ' + ', '.join(source_packages)
    return result


SUPPORTED_DEPENDENCY_TYPES = ['os', 'pip3', 'source']


def _split_types(ctx, param, types):
    # split columns by ',' and remove whitespace
    types = types.split(',') if types else []

    for type in types:
        if type not in SUPPORTED_DEPENDENCY_TYPES:
            raise click.BadOptionUsage("types", "Invalid dependency type: {}".format(type))

    return types


@click.command('install')
@logging_options()
@click.option("--os-name", default=os_info.name, help="OS Name (Ubuntu, CentOS)")
@click.option("--os-version", default=os_info.version, help="OS Version (16.04, 18.04, 9)")
@click.option("--jobs", default=os.cpu_count(), help="Allow specific number of jobs used to build dependencies")
@click.option("--install-dir", default=None, metavar="DIR", help="Install source packages in specific location",
              type=click.Path(file_okay=False, writable=True))
@click.option("--source-packages", default=None, metavar="PKG1,PKG2,...",
              help=describe_source_packages_option())
@click.option("--types",
              default="os,pip3,source",
              metavar="TYPE1,TYPE2,...",
              help="Comma separated list containing types of dependencies that should be installed: os, pip3, source",
              callback=_split_types
              )
def install_command(os_name, os_version, types, source_packages, install_dir, jobs):
    """
    Install dependencies required to build and run SDE
    """

    print_green("Installing {} dependencies...", current_workspace().name)
    install_dir = Path(install_dir) if install_dir else current_workspace().default_install_dir

    setup_path_variables(install_dir)
    manager = dependency_manager(os_name, os_version)
    installer = DependencyInstaller(os_name, os_version, jobs, manager.os_package_manager, install_dir)

    os_packages = manager.packages('os_packages', ALL_DEPENDENCY_GROUPS)
    pip3_packages = manager.packages('pip3_packages', ALL_DEPENDENCY_GROUPS)

    if source_packages is None:
        source_packages = manager.packages('source_packages', ALL_DEPENDENCY_GROUPS)
    elif source_packages == "":
        source_packages = []
    else:
        source_packages = source_packages.split(',')

    if 'os' in types:
        print_green("Updating list of packages...")
        installer.update_list_of_packages()
        print_green("List of packages updated")
        run_installation_in_log_section("OS", lambda: installer.install_os_dependencies(os_packages))
    if 'pip3' in types:
        run_installation_in_log_section("pip3", lambda: installer.install_pip3_dependencies(pip3_packages))
    if 'source' in types:
        run_installation_in_log_section("source", lambda: installer.install_source_dependencies(source_packages))
    print_green("{} dependencies installed.", current_workspace().name)


def run_installation_in_log_section(name, procedure):
    print_green("Installing {} dependencies...", name)
    procedure()
    print_green("{} dependencies installed", name)


dependencies_command.add_command(list_dependencies_command)
dependencies_command.add_command(install_command)
