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

import click
from click import Choice

from pathlib import Path

from packages.packages_command import extract_packages_command
from utils.collections import group_by_to_dict
from utils.logging import logging_options
from utils.terminal import print_green
from workspace import current_workspace, in_workspace, setup_path_variables
from .cmake import cmake, BUILD_TYPES
from .configuration_manager import current_configuration_manager


def _allowed_options():
    if not in_workspace():
        return []
    return current_configuration_manager().known_p4studio_options_including_negated()


def _describe_configure_command():
    result = 'Configure SDE build options'

    if in_workspace():
        definitions = current_configuration_manager().definitions
        definitions = group_by_to_dict(definitions, lambda d: d.category)

        result += "\n\nBuild can be configured with following CONFIG options:\n\n\b\n"
        for category, options in definitions.items():
            result += " {}\n".format(category)
            for option in options:
                default = 'enabled' if option.default else 'disabled'
                result += "  - {name:<27} {desc}. Default: {default}\n".format(
                    name=option.p4studio_name,
                    desc=option.description,
                    default=default
                )
    return result


@click.command('configure', help=_describe_configure_command(), short_help='Configure SDE build options')
@click.argument('options', type=Choice(_allowed_options()), nargs=-1, metavar="[CONFIG|^CONFIG]...")
@logging_options()
@click.option('--build-type', type=Choice(BUILD_TYPES), default='relwithdebinfo', help="Build type")
@click.option('--install-prefix', type=click.Path(file_okay=False, writable=True), default=None,
              help="Install files in DIRECTORY")
@click.option('--bsp-path', type=click.Path(exists=True), help="Install BSP package")
@click.option('--p4ppflags', help="P4 preprocessor flags")
@click.option('--extra-cppflags', help="Extra C++ compiler flags")
@click.option('--p4flags', help="P4 compiler flags")
@click.option('--kdir', type=click.Path(file_okay=False), help="Path to Kernel headers")
@click.pass_context
def configure_command(context, build_type, install_prefix, options, bsp_path, p4ppflags, p4flags, extra_cppflags, kdir):
    print_green("Configuring {} build...", current_workspace().name)

    cm = current_configuration_manager()
    for option in options:
        cm.add_option(option)

    if bsp_path:
        cm.add_option("bsp")

    context.invoke(extract_packages_command, bsp_path=bsp_path)

    install_prefix = Path(install_prefix) if install_prefix else current_workspace().default_install_dir

    args = cm.cmake_args()
    add_arg_if_not_none(args, "CMAKE_BUILD_TYPE", build_type)
    add_arg_if_not_none(args, "CMAKE_INSTALL_PREFIX", install_prefix)
    add_arg_if_not_none(args, "EXTRA_CPPFLAGS", extra_cppflags)
    add_arg_if_not_none(args, "P4FLAGS", p4flags)
    add_arg_if_not_none(args, "P4PPFLAGS", p4ppflags)
    add_arg_if_not_none(args, "KDIR", kdir)

    setup_path_variables(install_prefix)
    build_dir = current_workspace().root_path / 'build'
    cmake(build_dir, args)
    print_green("{} build configured.", current_workspace().name)


def add_arg_if_not_none(args, arg, value):
    if value is not None:
        args.append("-D{}='{}'".format(arg, value))
