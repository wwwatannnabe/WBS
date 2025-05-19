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

from collections import OrderedDict

import click
from click import Option

import main
from utils.click_cmds import get_full_cmd_str
from utils.processes import cmd_args_to_str


class OrderedGroup(click.Group):
    def __init__(self, name=None, commands=None, **attrs):
        super().__init__(name, commands, **attrs)
        self.commands = commands or OrderedDict()

    def list_commands(self, ctx):
        return self.commands


def command_call_to_str(command, **kwargs):
    _, result = get_full_cmd_str(command, main.p4studio_cli.commands, ['p4studio'])

    params = {
        param.name: param
        for param in command.params
    }

    for arg, value in kwargs.items():
        if value in (None, ()):
            continue
        param = params[arg]
        if isinstance(param, Option):
            result += [param.opts[0]]

        result += list(value) if isinstance(value, tuple) else [value]

    return cmd_args_to_str(result)
