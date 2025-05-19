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

import locale
import logging
import os
from datetime import datetime

import click
import click_logging
from click import Choice
from click_logging import ClickHandler

from utils.decorators import multiple_decorators
from utils.p4studio_path import p4studio_path

_DEFAULT_LOGGER = None
_GREEN_LOGGER = None


def default_logger():
    global _DEFAULT_LOGGER
    return _DEFAULT_LOGGER


def green_logger():
    global _GREEN_LOGGER
    return _GREEN_LOGGER


def initialize_loggers():
    global _DEFAULT_LOGGER
    global _GREEN_LOGGER

    _DEFAULT_LOGGER = logging.getLogger("default-logger")
    _GREEN_LOGGER = logging.getLogger("green-logger")

    for logger in [_DEFAULT_LOGGER, _GREEN_LOGGER]:
        logger.setLevel(logging.DEBUG)
        click_logging.basic_config(logger)

    _GREEN_LOGGER.handlers[0].formatter = SingleColorFormatter('green')


class SingleColorFormatter(logging.Formatter):
    def __init__(self, color):
        self.color = color

    def format(self, record):
        if not record.exc_info:
            msg = record.getMessage()
            return click.style(msg, fg=self.color)
        return logging.Formatter.format(self, record)


def _set_verbose(ctx, param, value):
    level = logging.getLevelName(value)
    for logger in [_DEFAULT_LOGGER, _GREEN_LOGGER]:
        for handler in logger.handlers:
            if isinstance(handler, ClickHandler):
                handler.setLevel(level)


def _set_log_file(ctx, param, value):
    if value is None:
        return

    filename = str(value)

    os.makedirs(os.path.dirname(filename), exist_ok=True)
    file_handler = logging.FileHandler(filename, encoding=locale.getpreferredencoding(True))
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(logging.Formatter('%(asctime)s: %(message)s'))

    for logger in [_DEFAULT_LOGGER, _GREEN_LOGGER]:
        logger.addHandler(file_handler)


def p4studio_logs_dir():
    return p4studio_path() / 'logs'


def default_log_file_name():
    return datetime.now().strftime(str(p4studio_logs_dir() / 'p4studio_%Y-%m-%d_%H:%M:%S.log'))


def logging_options(verbosity='DEBUG', log_file=None):
    return multiple_decorators(
        click.option(
            '--verbosity',
            type=Choice(['INFO', 'DEBUG']),
            default=verbosity,
            help='Show more information',
            show_default=True,
            callback=_set_verbose,
            expose_value=False
        ),
        click.option(
            '--log-file',
            type=click.Path(writable=True, dir_okay=False),
            default=log_file,
            help='Save logs to file',
            show_default=True,
            callback=_set_log_file,
            expose_value=False
        )
    )
