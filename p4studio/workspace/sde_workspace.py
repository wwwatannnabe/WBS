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
from typing import List, Dict

from workspace.workspace import Workspace


def get_sde_workspace() -> Workspace:
    return SdeWorkspace()


class SdeWorkspace(Workspace):
    @property
    def name(self):
        return 'SDE'

    @property
    def p4_dirs(self) -> Dict[str, Path]:
        return {
            'p4-14-programs': self.submodules_path / 'p4-examples/programs',
            'p4-16-programs': self.submodules_path / 'p4-examples/p4_16_programs'
        }

    @property
    def submodules_path(self) -> Path:
        return self.root_path / 'pkgsrc'

    @property
    def compressed_packages_path(self) -> Path:
        return self.root_path / 'packages'

    def _required_files(self) -> List[str]:
        return [
            'p4studio/dependencies/dependencies.yaml',
            'CMakeLists.txt'
        ]

    @property
    def is_package_extraction_required(self) -> bool:
        return True
