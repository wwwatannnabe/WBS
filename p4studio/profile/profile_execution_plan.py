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
import string

from build import build_command
from config import configure_command
from dependencies.dependencies_command import install_command
from utils.click import command_call_to_str
from utils.terminal import print_green, print_normal, print_separator


class ProfileExecutionPlan:
    def __init__(self, profile, bsp_path, jobs):
        self.profile = profile
        self.bsp_path = bsp_path or profile.bsp_path
        self.jobs = jobs

    def describe_profile(self):
        print_green('Source packages to install: ')
        for package in self.profile.source_packages():
            print_normal(" - {}", package)

        print_green('Configuration options: ')
        for option, enabled in self.profile.config_options().items():
            print_normal(" {} {}", '✓' if enabled else '✗', option)

        print_green('Targets to build: ')
        for target in self.profile.build_targets():
            print_normal(" - {}", target)

        print_separator()

    def show_commands(self):
        commands = [
            command_call_to_str(install_command, **self.dependencies_install_args()),
            command_call_to_str(configure_command, **self.configure_args()),
            command_call_to_str(build_command, **self.build_args()),
        ]

        print_green("Profile is equivalent to below list of commands:")
        for command in commands:
            print_normal(command)

    def dependencies_install_args(self):
        return {
            'source_packages': ','.join(self.profile.source_packages()),
            'jobs': self.jobs
        }

    def configure_args(self):
        return {
            'options': tuple(self.profile.config_args()),
            'bsp_path': self.bsp_path,
            'p4ppflags': self.profile.p4ppflags,
            'p4flags': self.profile.p4flags,
            'extra_cppflags': self.profile.extra_cppflags,
            'kdir': self.profile.kdir
        }

    def build_args(self):
        return {
            'jobs': self.jobs,
            'targets': tuple(self.profile.build_targets())
        }
