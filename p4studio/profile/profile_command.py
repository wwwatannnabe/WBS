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
from collections import OrderedDict

import click
import yaml
from yaml.representer import SafeRepresenter

from build import build_command
from config import configure_command
from config.configuration_manager import current_configuration_manager
from dependencies.dependencies_command import install_command
from system.check_system_command import check_system_command
from utils.logging import logging_options, default_log_file_name
from utils.terminal import print_green, print_separator
from .profile import Profile, load_profile_from_file
from .profile_execution_plan import ProfileExecutionPlan


@click.group("profile")
def profile_command():
    """Manage SDE profiles"""


def _default_options():
    options = {
        o.p4studio_name: o.default
        for o in current_configuration_manager().definitions
    }
    options['switch'] = True
    options['bf-diags'] = True

    return ','.join([('' if v else '^') + o for o, v in options.items()])


@click.command('create')
@click.argument("file", type=click.File('w'))
@click.option('--configure', 'options', default=None,
              help="Configure profile with comma separated list of options"
              )
@click.option('--switch-profile', help="Switch profile")
@click.option('--p4-examples', default="tna_exact_match", help="Comma separated list of P4 programs")
@click.option("--bsp-path", type=click.Path(exists=True), help="BSP to be used and installed")
def profile_create_command(file, options, switch_profile, p4_examples, bsp_path):
    """
    Create default profile
    """
    config_manager = current_configuration_manager()
    profile = Profile(config_manager)

    if bsp_path:
        profile.bsp_path = str(bsp_path)

    if options is None:
        options = _default_options()
    if options:
        for option in options.split(','):
            config_manager.add_option(option)
        for option in config_manager.options:
            profile.set_option(option.p4studio_name, option.enabled)

    if switch_profile:
        profile.switch_profile = switch_profile

    if p4_examples:
        for program in p4_examples.split(','):
            profile.add_p4_program(program)

    file.write(yaml.dump(profile.raw))


@click.command('describe')
@click.argument("file", type=click.File('r'))
@click.option("--bsp-path", type=click.Path(exists=True), help="BSP to be used and installed")
def profile_describe_command(file, bsp_path):
    """Describe profile"""
    plan = create_plan(file, bsp_path)

    plan.describe_profile()
    plan.show_commands()


@click.command('apply')
@click.argument("file", type=click.File('r'))
@logging_options('INFO', default_log_file_name())
@click.option("--jobs", default=os.cpu_count(), help="Allow specific number of jobs to be used")
@click.option("--bsp-path", type=click.Path(exists=True), help="BSP to be used and installed")
@click.option('--skip-dependencies', default=False, is_flag=True, help="Do not install dependencies")
@click.option('--skip-system-check', default=False, is_flag=True, help="Do not check system")
@click.pass_context
def profile_apply_command(context, file, jobs, bsp_path, skip_dependencies, skip_system_check):
    """
    Apply profile
    """
    plan = create_plan(file, bsp_path, jobs)

    if not skip_system_check:
        asic = 'asic' in plan.profile.config_args()
        kdir = plan.profile.kdir
        context.invoke(check_system_command, asic=asic, kdir=kdir)

    execute_plan(context, plan, skip_dependencies)


def execute_plan(context, plan, skip_dependencies=False):
    print_separator()
    plan.describe_profile()
    print_separator()

    if not skip_dependencies:
        context.invoke(install_command, **plan.dependencies_install_args())
        print_separator()

    context.invoke(configure_command, **plan.configure_args())
    print_separator()
    context.invoke(build_command, **plan.build_args())


def create_plan(file, bsp_path=None, jobs='N'):
    print_green("Loading profile from {} file...", file.name)
    profile = load_profile_from_file(file)

    if bsp_path:
        profile.enable("bsp")

    plan = ProfileExecutionPlan(profile, bsp_path, jobs)
    print_green("Profile is correct.")
    print_separator()
    return plan


profile_command.add_command(profile_create_command)
profile_command.add_command(profile_apply_command)
profile_command.add_command(profile_describe_command)

yaml.add_representer(OrderedDict, lambda self, data: SafeRepresenter.represent_dict(self, data.items()))
