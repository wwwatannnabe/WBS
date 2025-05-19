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
from typing import List

import yaml

from dependencies.merge import merge_all, merge
from utils.collections import nested_get
from utils.exceptions import ApplicationException
from utils.os_info import os_info
from workspace import current_workspace

ALL_DEPENDENCY_GROUPS = [
    'minimal',
    'optional_packages',
    'source_packages',
    'bf_diags',
    'bf_platforms',
    'grpc',
    'thrift',
    'switch',
    'pi',
    'switch_p4_16',
    'p4i',
]

ALL_SOURCE_PACKAGES = [
    'boost',
    'grpc',
    'thrift',
    'bridge',
    'libcli',
    'pi',
]

STANDARD_INSTALLER_TYPES = [
    'os_packages',
    'pip3_packages',
]

# as every source package has a separate installation script,
# it is assumed to be separate installer type
ALL_INSTALLER_TYPES = STANDARD_INSTALLER_TYPES + ALL_SOURCE_PACKAGES


class DependencyManager:
    """
    Reads single or multiple dependency files
    and provides simple method to get a list of packages of given type and group
    that are relevant for specific OS
    """
    def __init__(self, os_name, os_version, paths: List[Path]):
        self.os_name = os_name
        self.os_version = os_version
        deps = self._merge_files(paths)

        if not self._is_os_supported(deps, os_name, os_version):
            raise ApplicationException("detected OS {}:{} not supported".format(os_name, os_version))

        self.data = self._filter_os_specific(deps, os_name, os_version)
        self.os_package_manager = deps.get('OS_based', {}).get(os_name, {}).get('keyword')

    def packages(self, installer_type, groups):
        if installer_type == "source_packages":
            packages = self.data.get('source_packages', {}).keys()
            return [p for p in ALL_SOURCE_PACKAGES if p in packages]
        result = []
        for group in groups:
            group_dependencies = self.data.get(group, {}).get(installer_type, [])
            result = merge(result, group_dependencies)
        return result

    @staticmethod
    def _filter_os_specific(deps, os_name, os_version):
        os_based = deps.get('OS_based', {})
        defaults_deps = os_based.get('defaults', {})
        os_specific_deps = os_based.get(os_name, {}).get('defaults', {})
        os_version_specific_deps = os_based.get(os_name, {}).get(os_version, {})

        return merge_all(defaults_deps, os_specific_deps, os_version_specific_deps)

    @staticmethod
    def _merge_files(paths):
        deps = {}
        for path in paths:
            with path.open() as f:
                next_yaml = yaml.load(f, Loader=yaml.BaseLoader)
                deps = merge(deps, next_yaml)
        return deps

    @staticmethod
    def _is_os_supported(deps, os_name, os_version):
        return nested_get(deps, 'OS_based/{}/{}'.format(os_name, os_version), None) is not None


def dependency_manager(os_name=None, os_version=None):
    os_name = os_info.canonicalize(os_name) or os_info.name
    os_version = os_version or os_info.version
    files = current_workspace().dependency_files
    return DependencyManager(os_name, os_version, files)
