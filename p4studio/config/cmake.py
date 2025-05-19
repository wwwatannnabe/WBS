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
from pathlib import Path
from typing import List

import click
import cmakeast
from cmakeast.ast import FunctionCall

from utils.exceptions import ApplicationException
from utils.processes import execute
from workspace import current_workspace

BUILD_TYPES = ['debug', 'release', 'relwithdebinfo', 'minsizerel']


class CmakeOptionDefinition:
    DESCRIPTION_PATTERN = re.compile(r'^((?P<category>[a-zA-Z0-9-]+):)? +(?P<description>.+)$')

    def __init__(self, name: str, default: bool, description: str):
        self.name = name
        self.default = default

        match = self.DESCRIPTION_PATTERN.search(description)
        if match is not None:
            self.category = match.groupdict()['category'] or 'Global'
            self.description = match.groupdict()['description']
        else:
            self.category = 'Global'
            self.description = description


def available_cmake_options() -> List[CmakeOptionDefinition]:
    """
    Returns list of cmake options available in current workspace
    """
    file_content = current_workspace().cmake_lists_txt.read_text()
    ast = cmakeast.ast.parse(file_content)
    return [
        CmakeOptionDefinition(
            name=statement.arguments[0].contents,
            description=statement.arguments[1].contents.strip('"'),
            default=statement.arguments[2].contents.lower() == 'on'
        )
        for statement in ast.statements
        if isinstance(statement, FunctionCall)
        if statement.name == 'option'
    ]


def cmake(build_dir: Path, options: List[str]):
    if build_dir.exists():
        if not build_dir.is_dir():
            message = '{} does not exist or is not a directory'.format(build_dir)
            raise click.ClickException(message)
    else:
        build_dir.mkdir(parents=True)

    command = ['cmake', str(current_workspace().root_path)] + options
    if not execute(command, build_dir):
        raise ApplicationException("cmake completed unsuccessfully")
