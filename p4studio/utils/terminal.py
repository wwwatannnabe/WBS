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

import click

from utils.logging import green_logger, default_logger


def print_green(formatter: str, *args):
    message = formatter.format(*args)
    green_logger().info(message)


def print_normal(formatter: str = "", *args, **kwargs):
    message = formatter.format(*args, **kwargs)
    default_logger().info(message)


def print_separator():
    print_normal()


def print_debug(formatter: str = "", *args):
    message = formatter.format(*args)
    default_logger().debug(message)


def print_warning(formatter: str = "", *args):
    message = formatter.format(*args)
    default_logger().warn(message)


def columnize(items, number_of_columns, gap=1) -> str:
    # add empty items to make sure that all columns can have the sie sizes
    column_alignment = number_of_columns - len(items) % number_of_columns
    if column_alignment < number_of_columns:
        items = items + column_alignment * ['']

    column_size = int(len(items) / number_of_columns)
    max_item_len = max(len(item) for item in items)
    item_formatter = "{:<%s}" % max_item_len

    rows = []
    for row_index in range(0, column_size):
        row = []
        for column_index in range(0, number_of_columns):
            index = column_index * column_size + row_index
            fixed_width_item = item_formatter.format(items[index])
            row.append(fixed_width_item)
        rows.append(row)

    column_separator = gap * ' '
    lines = [column_separator.join(row) for row in rows]
    return '\n'.join(lines)
