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
from pathlib import Path

from utils.exceptions import ApplicationException
from utils.processes import execute


class SubprocessBuilder:
    def __init__(self, command_name=None):
        self._name = command_name
        self._args = []

    def args(self, *args) -> 'SubprocessBuilder':
        self._args += [str(arg) for arg in args]
        return self

    def sudo(self) -> 'SubprocessBuilder':
        return self.args('sudo', '-E')

    def pip3(self):
        return self.args('env', 'pip3')

    def pip3_install(self, packages):
        packages = packages or []
        return self.pip3().args('install').args(*packages)

    def python3(self, script: Path):
        return self.args('env', 'python3', script)

    def run(self, working_dir: Path = Path.cwd()) -> int:
        return execute(self._args, working_dir)

    def run_or_raise(self, failure_message=None, working_dir: Path = Path.cwd()):
        if not execute(self._args, working_dir):
            if not failure_message:
                name = self._name or "running {}".format(self._args[0])
                failure_message = "Problem occurred while {}".format(name)
            raise ApplicationException(failure_message.format(' '.join(self._args)))


def subprocess_builder(command_name=None) -> SubprocessBuilder:
    return SubprocessBuilder(command_name)
