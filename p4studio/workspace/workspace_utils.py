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
import importlib
import os
from pathlib import Path

from utils.exceptions import ApplicationException
from utils.processes import command_output
from workspace.workspace import Workspace


def _possible_workspaces():
    result = []
    for file in Path(__file__).parent.iterdir():
        if file.name.endswith("_workspace.py"):
            result.append(_create_instance_from_module(file))
    return result


def _create_instance_from_module(path):
    module_name = path.name[:-3]
    __package__
    module = importlib.import_module('{}.{}'.format(__package__, module_name))
    return getattr(module, 'get_{}'.format(module_name))()


_CURRENT_WORKSPACE = next((w for w in _possible_workspaces() if w.is_valid), None)


def in_workspace() -> bool:
    """
    Indicates if current working directory is inside workspace
    """
    return _CURRENT_WORKSPACE is not None


def current_workspace() -> Workspace:
    if not in_workspace():
        message = "{} is not a SDE directory".format(os.getcwd())
        raise ApplicationException(message)
    return _CURRENT_WORKSPACE


def configure_env_variables():
    if 'LANG' not in os.environ:
        supported_locales = command_output(['locale', '-a'])
        preferred_locales = [b'C.UTF-8', b'C.utf8', b'en_US.utf8']
        for locale in preferred_locales:
            if locale in supported_locales:
                os.environ['LANG'] = locale.decode("utf-8")
                break
    if 'LC_ALL' not in os.environ:
        os.environ['LC_ALL'] = os.environ['LANG']

def _add_path(variable_name, path):
    current = os.environ.get(variable_name)
    if not current or path not in current.split(os.pathsep):
        os.environ[variable_name] = (current + os.pathsep if current else '') + str(path)

def setup_path_variables(install_dir):
    _add_path('PATH', install_dir / 'bin')
    _add_path('CMAKE_LIBRARY_PATH', install_dir / 'lib')
    _add_path('CMAKE_INCLUDE_PATH', install_dir / 'include')
    _add_path('LIBRARY_PATH', install_dir / 'lib')
    _add_path('LD_RUN_PATH', install_dir/ 'lib')
    _add_path('CPLUS_INCLUDE_PATH', install_dir / 'include')
    _add_path('PKG_CONFIG_PATH', install_dir / 'lib/pkgconfig')