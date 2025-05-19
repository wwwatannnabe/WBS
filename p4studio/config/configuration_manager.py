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

from typing import List, Tuple

from utils.exceptions import ApplicationException
from .cmake import available_cmake_options
from .config_option import ConfigOption, ConfigOptionDefinition


class ConfigurationManager:
    """
    Allows to map p4studio config options to cmake options.
    Validates consistency between options (like switch and ^switch requested together).
    Checks if added options are defined in CMakeLists.txt.
    """

    def __init__(self, definitions: List[ConfigOptionDefinition]):
        self.definitions = definitions
        self.known_p4studio_options = [co.p4studio_name for co in definitions]
        self._options = []

    def add_option(self, p4studio_arg: str):
        option = ConfigOption.from_p4studio_arg(p4studio_arg)

        if option.p4studio_name not in self.known_p4studio_options:
            msg = "Unknown configuration option: {}".format(option.p4studio_name)
            raise ApplicationException(msg)

        if any(option.negate() == o for o in self._options):
            msg = "Ambiguous configuration for {} option".format(option.p4studio_name)
            raise ApplicationException(msg)

        if option not in self._options:
            self._options.append(option)

    def cmake_args(self) -> List[str]:
        return [o.cmake_arg for o in self._options]

    def known_p4studio_options_including_negated(self) -> List[str]:
        result = []
        for option in self.known_p4studio_options:
            result += [option, '^' + option]
        return result

    def definitions_by_category(self, name):
        return [d for d in self.definitions if d.category == name]

    def definition(self, name):
        for definition in self.definitions:
            if definition.p4studio_name == name:
                return definition
        message = "Unknown '{}' option".format(name)
        raise ApplicationException(message)

    def categories(self):
        return {d.category for d in self.definitions}

    @property
    def options(self) -> Tuple[ConfigOption]:
        return tuple(self._options)


_configuration_manager = None


def current_configuration_manager() -> ConfigurationManager:
    global _configuration_manager
    if _configuration_manager is None:
        options = [
            ConfigOptionDefinition(ConfigOption(o.name.lower(), o.default), o.category, o.description)
            for o in available_cmake_options()
        ]
        _configuration_manager = ConfigurationManager(options)
    return _configuration_manager
