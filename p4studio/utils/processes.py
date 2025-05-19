# !/usr/bin/env python3

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


import subprocess
from pathlib import Path
from typing import List
from timeit import default_timer as timer
from datetime import timedelta

from utils.exceptions import ApplicationException
from utils.logging import default_logger
from utils.terminal import print_debug

try:
    from shlex import quote as cmd_quote
except ImportError:
    from pipes import quote as cmd_quote


def execute(command: List[str], working_dir: Path = Path.cwd()) -> bool:
    try:
        print_debug("Executing: {}", ' '.join(command))
        start = timer()
        process = subprocess.Popen(command, cwd=str(working_dir), stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

        while process.poll() is None:
            while True:
                line = process.stdout.readline().decode()
                if line:
                    default_logger().debug(line.rstrip())
                else:
                    break

        end = timer()
        print_debug("Cmd '{}' took: {}", ' '.join(command), timedelta(seconds=end-start))
        return process.returncode == 0
    except FileNotFoundError as e:
        raise ApplicationException from e


def command_output(command: List[str]) -> str:
    try:
        return subprocess.check_output(command)
    except subprocess.CalledProcessError as e:
        raise ApplicationException from e


def cmd_args_to_str(args):
    return " ".join(map(cmd_quote, args))
