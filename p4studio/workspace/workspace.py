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

import os
from abc import abstractmethod
from pathlib import Path
from typing import List, Dict

from utils.p4studio_path import p4studio_path


class Workspace:
    """
    Encapsulates knowledge about specific workspace like SDE package.
    It provides paths to well-known files that are important for p4studio.
    """

    def __init__(self):
        self._root_path = None
        for candidate in self._root_path_candidates():
            if self.check_if_root_path(candidate):
                self._root_path = candidate

    @property
    @abstractmethod
    def name(self):
        pass

    @property
    def is_valid(self):
        return self._root_path is not None

    @property
    def root_path(self) -> Path:
        if self._root_path is None:
            raise Exception("Not in {} directory".format(self.name()))
        return self._root_path

    def check_if_root_path(self, path: Path) -> bool:
        return path.is_dir() and \
               all((path / f).is_file() for f in self._required_files())

    @abstractmethod
    def _required_files(self) -> List[str]:
        pass

    @property
    def p4studio_path(self) -> Path:
        return p4studio_path()

    @property
    def build_path(self) -> Path:
        return self.root_path / 'build'

    @property
    def cmake_lists_txt(self) -> Path:
        return self.root_path / 'CMakeLists.txt'

    @property
    @abstractmethod
    def submodules_path(self) -> Path:
        pass

    @property
    def default_install_dir(self) -> Path:
        return self.root_path / 'install'

    def package_installation_script(self, name: str) -> Path:
        if name in ['boost', 'grpc', 'libcli', 'pi', 'thrift']:
            return self.p4studio_path / 'dependencies/source/install_{}.py'.format(name)
        elif name == 'bridge':
            return self.p4studio_path / 'dependencies/source/install_bridge_utils.py'
        else:
            raise Exception('Package {} is not supported'.format(name))

    @property
    def dependency_files(self) -> List[Path]:
        return [self.p4studio_path / 'dependencies/dependencies.yaml']

    @property
    @abstractmethod
    def p4_dirs(self) -> Dict[str, Path]:
        pass

    @staticmethod
    def _root_path_candidates() -> List[Path]:
        path = Path(os.getcwd())
        yield path
        while path.parent != path:
            path = path.parent
            yield path

    @property
    @abstractmethod
    def is_package_extraction_required(self) -> bool:
        pass
