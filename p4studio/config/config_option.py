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

from utils.exceptions import ApplicationException


class ConfigOption:
    """
    Provides abstraction for configurable build option.
    Encapsulates knowledge about differences between naming conventions: cmake vs p4studio
    Example: ( -DSWITCH=off vs ^switch)
    Exposed methods make it explicit if we work with cmake or p4studio names.
    """
    OPTION_PATTERN = re.compile(r'^(?P<off>\^)?(?P<name>[a-zA-Z_][a-zA-Z0-9_-]*)$')

    @staticmethod
    def from_p4studio_arg(arg: str):
        match = ConfigOption.OPTION_PATTERN.search(arg)
        if match is None:
            message = "Incorrect format of configuration option: {}".format(arg)
            raise ApplicationException(message)

        groups = match.groupdict()
        enabled = groups['off'] is None
        p4studio_name = groups['name']

        return ConfigOption(p4studio_name, enabled)

    def __init__(self, p4studio_name: str, enabled: bool):
        self.p4studio_name = p4studio_name
        self.cmake_name = p4studio_name.upper()
        self.enabled = enabled

    @property
    def cmake_value(self):
        return 'ON' if self.enabled else 'OFF'

    @property
    def cmake_arg(self):
        return '-D{}={}'.format(self.cmake_name, self.cmake_value)

    @property
    def p4studio_arg(self):
        return self._caret + self.p4studio_name

    @property
    def _caret(self):
        return '^' if not self.enabled else ''

    def __eq__(self, other):
        return isinstance(other, ConfigOption) and \
               self.p4studio_name == other.p4studio_name and \
               self.cmake_name == other.cmake_name and \
               self.enabled == other.enabled

    def __hash__(self):
        return hash((self.p4studio_name, self.enabled))

    def negate(self):
        return ConfigOption(self.p4studio_name, not self.enabled)


class ConfigOptionDefinition:
    def __init__(self, option: ConfigOption, category: str, description: str):
        self._option = option
        self.category = category
        self.description = description

    @property
    def cmake_name(self) -> str:
        return self._option.cmake_name

    @property
    def p4studio_name(self) -> str:
        return self._option.p4studio_name

    @property
    def default(self) -> bool:
        return self._option.enabled
