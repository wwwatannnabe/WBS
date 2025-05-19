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
from utils.collections import nested_get, nested_set, nested_del
from utils.terminal import print_warning


def adjust_for_backward_compatibility(profile):
    _move(profile, 'global-options/bsp', 'features/bf-platforms/bsp')
    _move(profile, 'global-options/newport', 'features/bf-platforms/newport')
    _move(profile, 'global-options/tclonly', 'features/bf-platforms/tclonly')
    _move(profile, 'global-options/accton-diags', 'features/bf-platforms/accton-diags')
    _move(profile, 'global-options/newport-diags', 'features/bf-platforms/newport-diags')


def _move(dictionary, old_path, new_path):
    value = nested_get(dictionary, old_path, None)
    if value is not None:
        print_warning("-" * 120)
        print_warning("'{}' has been deprecated and will be removed in future. Use '{}'.", old_path, new_path)
        print_warning("-" * 120)
        nested_set(dictionary, new_path, value)
        nested_del(dictionary, old_path)
