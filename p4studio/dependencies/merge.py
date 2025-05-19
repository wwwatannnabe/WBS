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

def merge(a, b):
    """
    Takes two containers (dict or list) and merges their element together without duplicates.
    For dictionaries, in case of key collision:
    if both values are containers, they are merged recursively;
    otherwise the second one is assigned to this key.
    """
    if isinstance(a, dict) and isinstance(b, dict):
        result = a.copy()
        for (key, value) in b.items():
            result[key] = merge(result.get(key), value)
        return result
    elif isinstance(a, list) and isinstance(b, list):
        return a + b
    else:
        return b


def merge_all(*items):
    if len(items) == 0:
        return None
    else:
        result = make_copy_if_needed(items[0])
        for item in items[1:]:
            result = merge(result, item)
        return result


def make_copy_if_needed(obj):
    if isinstance(obj, list) or isinstance(obj, dict):
        return obj.copy()
    else:
        return obj
