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
from click import confirm, prompt, Choice, Path, File

from build import ALL_SWITCH_PROFILES
from config.configuration_manager import current_configuration_manager
from profile.profile import Profile
from profile.profile_command import execute_plan
from profile.profile_execution_plan import ProfileExecutionPlan
from utils.logging import logging_options, default_log_file_name
from utils.terminal import print_normal, print_separator


@click.command('interactive')
@logging_options('INFO', default_log_file_name())
@click.pass_context
def interactive_command(context):
    """
        Run p4studio in interactive mode
    """
    profile = Profile(current_configuration_manager())

    if not confirm("Do you want to install dependencies?", default=True):
        profile.skip_dependencies()

    if confirm("Do you want to build switch-p4-16?", default=False):
        profile.enable('switch')
        profile.switch_profile = prompt(
            "Please provide the profile to build switch with",
            type=Choice(ALL_SWITCH_PROFILES),
            default='x1_tofino'
        )

    architecture_required = False
    if confirm("Do you want to build bf-diags?", default=False):
        profile.enable('bf-diags')
        architecture_required = True

    if confirm("Do you want to build P4-14 examples?", default=False):
        profile.add_p4_program('p4-14-programs')
        architecture_required = True

    if confirm("Do you want to build P4-16 examples?", default=True):
        profile.add_p4_program('p4-16-programs')
        architecture_required = True

    if architecture_required:
        architecture = prompt(
            "Please provide architecture for bf-diags and p4-examples",
            type=Choice(supported_architectures() + ['all']),
            default='tofino'
        )
        if architecture == 'all':
            for arch in supported_architectures():
                profile.enable(arch)
        else:
            profile.enable(architecture)

    if confirm("Do you want to build for HW?"):
        profile.enable('asic')

        if confirm("Do you want to build BSP?"):
            profile.bsp_path = str(prompt("Please provide the path to BSP", type=Path(exists=True)))
        if confirm("Do you want to use custom kernel headers?"):
            profile.kdir = str(prompt("Please provide path to kernel headers", type=Path(exists=True)))

    if confirm("Do you want to enable P4Runtime?"):
        profile.enable('p4rt')

    print_separator()
    print_normal("Created profile:\n{}", yaml.dump(profile.raw))

    if confirm('Do you want to write it to a file?', default=False):
        file = prompt('Please provide the profile filename - [Example:profiles/my-profile.yaml]', type=File('w'))
        file.write(yaml.dump(profile.raw))

    if confirm('Do you want to continue building SDE?', default=False):
        plan = ProfileExecutionPlan(profile, None, os.cpu_count())
        execute_plan(context, plan)


def supported_architectures():
    return [d.p4studio_name for d in current_configuration_manager().definitions_by_category("Architecture")]
