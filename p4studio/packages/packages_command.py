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

import re
import tarfile
import tempfile
from fnmatch import fnmatch
from pathlib import Path
from shutil import rmtree

import click

from utils.exceptions import ApplicationException
from utils.processes import execute
from utils.terminal import print_normal, print_green
from workspace import current_workspace


@click.group('packages')
def packages_command():
    """
    Manage SDE packages
    """


@click.command('list')
def list_packages_command():
    """
    List available packages
    """
    packages = {
        'bf-syslibs': {'desc': 'System utilities for logging, memory management, etc.'},
        'bf-utils': {'desc': 'Third-party libraries adapted for Intel P4 Studio SDE and internal tools'},
        'bf-drivers': {'desc': 'Low-level driver package including BF Runtime, pipemgr, etc.'},
        'bf-diags': {'desc': 'Diagnostics package for the Intel Tofino ASIC'},
        'switch-p4.16': {
            'desc': 'A reference, feature-rich data plane program, written in P4-16, ' +
                    'the semantic API for it and the SAI implementation on top of it'
        },
        'p4-examples': {'desc': 'P4 examples for Intel Tofino features in p4-14 and p4-16 languages'},
        'ptf-modules': {'desc': 'Intel-specific fork of Packet Test Framework (PTF)'},
        'p4-compilers': {'desc': 'Intel P4 compiler (bf-p4c) and associated files', 'binary': True},
        'tofino-model': {'desc': 'Intel Tofino ASIC simulation model', 'binary': True}
    }

    formatter = "{:<13} {:<12} {}"
    print_green(formatter, "name", "type", 'description')
    for (name, attrs) in packages.items():
        package_type = 'binary' if attrs.get('binary') else 'source code'
        print_normal(formatter, name, package_type, attrs['desc'])


@click.command('extract')
@click.option('--force', is_flag=True, default=False, help="Extract packages even if they exist")
@click.option('--bsp-path', type=click.Path(exists=True), help="Install BSP package")
def extract_packages_command(force, bsp_path):
    """
    Extract packages to pkgsrc directory
    """
    if not current_workspace().is_package_extraction_required:
        return

    packages = current_workspace().compressed_packages_path
    submodules = current_workspace().submodules_path

    package_pattern = re.compile(r'^(?P<name>[a-z0-9-]+)-(.*)\.tgz$')

    for package in packages.iterdir():
        match = package_pattern.search(package.name)
        if not match:
            continue
        destination = submodules / match.groupdict()['name']
        if not destination.exists() or force:
            print_normal("Extracting {}", package)
            _extract(package, destination)

    if bsp_path:
        destination = submodules / 'bf-platforms'
        if not destination.exists() or force:
            print_normal("Installing BSP from {}", bsp_path)
            _install_bsp(bsp_path, destination)


packages_command.add_command(list_packages_command)
packages_command.add_command(extract_packages_command)


def _install_bsp(bsp_path, destination):
    with tarfile.open(str(bsp_path)) as tar:
        inner_tar = next(Path(file) for file in tar.getnames() if fnmatch(file, '*/packages/*.tgz'))
    if inner_tar:
        tmp = Path(tempfile.mkdtemp())
        _extract(bsp_path, tmp)
        bsp_path = tmp / Path(*inner_tar.parts[1:])

    _extract(bsp_path, destination)
    if tmp:
        rmtree(tmp, ignore_errors=True)


def _extract(package, destination):
    if not destination.exists():
        destination.mkdir(parents=True)
    args = ['tar', 'xf', str(package), '-C', str(destination), '--strip-components', '1']
    if not execute(args):
        msg = "Problem occurred while extracting package."
        raise ApplicationException(msg)
