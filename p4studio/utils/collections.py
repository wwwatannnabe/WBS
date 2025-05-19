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

from collections import OrderedDict
from itertools import groupby


def group_by_to_dict(items, key_function):
    result = OrderedDict()
    for k, value in groupby(items, key_function):
        if k not in result:
            result[k] = []
        result[k] += list(value)
    return result


def nested_get(dictionary, path, default):
    segments = path.split('/')
    current = dictionary
    current_path = []
    for segment in segments:
        current_path.append(segment)
        if not isinstance(current, dict):
            raise _not_dict_exception(current_path)
        if segment not in current:
            return default
        current = current[segment]
    return current


def nested_set(dictionary, path, value):
    segments = path.split('/')
    current = dictionary
    current_path = []
    for segment in segments[:-1]:
        current_path.append(segment)
        if not isinstance(current, dict):
            raise _not_dict_exception(current_path)
        current = current.setdefault(segment, OrderedDict())

    if not isinstance(current, dict):
        raise _not_dict_exception(current_path)
    current[segments[-1]] = value
    return dictionary


def nested_del(dictionary, path):
    segments = path.split('/')
    current = dictionary
    current_path = []
    for segment in segments[:-1]:
        if not isinstance(current, dict):
            raise _not_dict_exception(current_path)
        if segment not in current:
            return dictionary
        current_path.append(segment)
        current = current[segment]

    if not isinstance(current, dict):
        raise _not_dict_exception(current_path)
    del current[segments[-1]]
    return dictionary


def _not_dict_exception(path):
    message = "value of '{}' should be an instance of dict".format('/'.join(path))
    return Exception(message)
