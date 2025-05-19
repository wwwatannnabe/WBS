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

from utils.subprocess_builder import subprocess_builder
from workspace import current_workspace


class DependencyInstaller:
    DEPENDENCIES_OF_DEPENDENCIES = {
        'grpc': ['boost'],
        'thrift': ['boost'],
    }

    def __init__(self, os_name, os_version, jobs, os_package_manager, install_dir):
        self.os_name = os_name
        self.os_version = os_version
        self.jobs = jobs
        self.os_package_manager = os_package_manager
        self.install_dir = install_dir

    def update_list_of_packages(self):
        name = "updating list of packages"
        if self.os_name == 'CentOS':
            self.command(name) \
                .args('yum', 'install', '-y', 'dnf-plugins-core') \
                .run_or_raise()
            if self.os_version == '7':
                self.command(name) \
                    .args('yum-config-manager', '--enable', 'PowerTools') \
                    .run_or_raise()
            else:
                self.command(name) \
                    .args('yum', 'config-manager', '--set-enabled', 'PowerTools') \
                    .run_or_raise()
        else:
            self.command(name) \
                .args(self.os_package_manager, 'update') \
                .run_or_raise()

    def install_os_dependencies(self, deps):
        self.command("installing OS dependencies") \
            .args(self.os_package_manager, 'install', '-y', *deps) \
            .run_or_raise()

    def install_pip3_dependencies(self, deps):
        self.command("installing pip3 dependencies") \
            .pip3_install(deps) \
            .run_or_raise()

    def install_source_dependencies(self, deps):
        deps = self.resolve_dependencies(deps)
        for dependency in deps:
            script = current_workspace().package_installation_script(dependency)
            subprocess_builder().python3(script).args(
                '--os-name', self.os_name,
                '--os-version', self.os_version,
                '--jobs', self.jobs,
                '--sde-install', self.install_dir,
                '--keyword', self.os_package_manager,
                '--with-proto', 'yes' if 'grpc' in deps else 'no'
            ).run_or_raise("Problem occurred while installing {}".format(dependency))

    def resolve_dependencies(self, dependencies):
        pending = dependencies[::-1]
        result = []
        while pending:
            dependency = pending.pop()
            if dependency in result:
                continue
            missing = [d for d in self._dependencies_of(dependency, dependencies) if d not in result]
            if missing:
                pending.append(dependency)
                pending.extend(missing)
            else:
                result.append(dependency)
        return result

    def _dependencies_of(self, dependency, all_dependencies):
        result = self.DEPENDENCIES_OF_DEPENDENCIES.get(dependency, [])

        # in case when installing both PI and GRPC, GRPC should be installed first -
        # it will allow to build PI with "--with-proto" option
        if dependency == 'pi' and 'grpc' in all_dependencies:
            result.append('grpc')

        return result

    @staticmethod
    def command(name):
        return subprocess_builder(name).sudo()
