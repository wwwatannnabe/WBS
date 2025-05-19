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
import subprocess
from shutil import which

EXTERNAL_MODULES = [
    'click', 'click_logging', 'cmakeast', 'yaml', 'jsonschema'
]


def check_p4studio_dependencies():
    if not minimal_dependencies_are_installed():
        handle_missing_dependencies()


def minimal_dependencies_are_installed():
    if not python_packages_can_be_installed():
        return False

    missing_modules = []

    for module_name in EXTERNAL_MODULES:
        try:
            __import__(module_name)
        except ModuleNotFoundError:
            missing_modules += [module_name]

    if missing_modules:
        print("Cannot import following python modules:")
        for module in missing_modules:
            print("- {}".format(module))
        print()

    return not missing_modules


def handle_missing_dependencies():
    print("p4studio tool requires several dependencies to be installed before you start using it.")
    print("Be aware that list of minimal dependencies is much shorter than ", end='')
    print("list of all dependencies required to build and run SDE components.")

    if not python_packages_can_be_installed():
        print("p4studio tool could not install required dependencies because:")
        if not has_sudo():
            print(" - sudo command is missing")
        if not has_pip3():
            print(" - pip3 command is missing")
        exit(1)

    while True:
        print("Do you want install required dependencies? [Y/n]: ", end="")
        user_input = input()
        if user_input in ['N', 'n']:
            return
        elif user_input in ['Y', 'y', '']:
            break
    my_dir = os.path.dirname(os.path.realpath(__file__))
    process = subprocess.Popen(['sudo', '-E', 'pip3', 'install', '-r', my_dir + '/requirements.txt'])
    process.communicate()


def python_packages_can_be_installed():
    return has_sudo() or has_pip3()


def has_sudo():
    return which('sudo') is not None


def has_pip3():
    return which('pip3') is not None
