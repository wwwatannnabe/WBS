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

from os import statvfs
from pathlib import Path

import click

from utils.exceptions import ApplicationException
from utils.processes import command_output
from utils.terminal import print_normal, print_green
from workspace import current_workspace


@click.command("check-system", short_help="Verify that system is capable to build and install SDE")
@click.option("--install-dir", help="Directory where SDE should be installed")
@click.option("--asic", is_flag=True, default=False, help="Check if system can be used to build for ASIC")
@click.option('--kdir', type=click.Path(file_okay=False), help="Path to Kernel headers")
def check_system_command(install_dir, asic, kdir):
    """
    Perform basic checks to verify that system is capable to build and install SDE
    """

    checks = []

    if not install_dir:
        install_dir = current_workspace().p4studio_path
    checks.append(check_disk_space(install_dir))

    if asic:
        if kdir:
            kdir = Path(kdir)
        checks.append(check_kernel_headers(kdir))

    print_green("Checking system capabilities to build and install SDE:")
    for name, value, ok in checks:
        print_normal(" {} {}: {}", '✓' if ok else '✗', name, value)

    if any(not check[2] for check in checks):
        raise ApplicationException("At least one check failed")
    else:
        print_green("Checking system completed successfully.")


def check_disk_space(path):
    fs = statvfs(str(path))
    free_space_gb = fs.f_bsize * fs.f_bavail / 1024 / 1024 / 1024
    min_free_space_gb = 20

    name = "Free space >= {}GB".format(min_free_space_gb)
    info = "{:.2f}GB".format(free_space_gb)
    ok = free_space_gb >= min_free_space_gb
    return name, info, ok


def check_kernel_headers(kdir):
    if not kdir:
        kernel_version = command_output(["uname", "-r"]).decode().strip()
        kdir = Path("/lib/modules/{}/build".format(kernel_version))
    ok = kdir.exists()
    info = str(kdir) + (" exists" if ok else " not exist")

    return "Kernel headers installed", info, kdir.exists()
