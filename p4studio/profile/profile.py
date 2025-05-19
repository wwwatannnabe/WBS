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
from typing import Iterable

import yaml
from jsonschema import validate, ValidationError
from yaml.parser import ParserError

from config import ConfigOption
from config.configuration_manager import current_configuration_manager
from dependencies.merge import merge_all
from profile.backward_compatibility import adjust_for_backward_compatibility
from profile.profile_schema import create_profile_schema
from utils.collections import nested_get, nested_set
from utils.exceptions import ApplicationException


def load_profile_from_file(file):
    try:
        yaml_content = yaml.load(file, Loader=yaml.SafeLoader)
    except ParserError as e:
        message = "Profile is not valid YAML. Error at line {}, column {}".format(e.context_mark.line,
                                                                                  e.context_mark.column)
        raise ApplicationException(message)

    adjust_for_backward_compatibility(yaml_content)

    return Profile(current_configuration_manager(), yaml_content)


class Profile:
    def __init__(self, configuration_manager, raw=None):
        self._configuration_manager = configuration_manager
        if raw is None:
            self.raw = OrderedDict()
            self.raw['global-options'] = {}
            self.raw['features'] = {}
            self.raw['architectures'] = []
        else:
            self._validate_against_schema(raw)
            self.raw = (raw if raw is not None else {}).copy()

    def skip_dependencies(self):
        self.raw['dependencies'] = {'source-packages': []}

    def enable(self, name):
        self.set_option(name, True)

    def set_option(self, name, value):
        category = self._configuration_manager.definition(name).category.lower()
        category_path = 'features/{}'.format(category)
        if category == 'global':
            self._set_field('global-options/{}'.format(name), value)
        elif category == 'architecture':
            archs = self.raw.setdefault('architectures', [])
            if not value and name in archs:
                archs.remove(name)
            elif value and name not in archs:
                archs.append(name)
        elif name == category:
            if value:
                if not isinstance(self._get_field(category_path, None), dict):
                    self._set_field(category_path, {})
            else:
                self._set_field(category_path, False)
        else:
            if self._get_field(category_path, False) == False:  # noqa
                self._set_field(category_path, {})
            self._set_field('features/{}/{}'.format(category, name), value)

    def add_p4_program(self, name):
        self.raw['features'].setdefault('p4-examples', []).append(name)

    def source_packages(self):
        return self._get_field('dependencies/source-packages', self._calculate_source_packages())

    def config_args(self):
        return {
            ConfigOption(o, v).p4studio_arg
            for o, v in self.config_options().items()
        }

    def config_options(self):
        return merge_all(
            self.global_options_without_flags(),
            self.features_as_options(),
            self.architecture_options()
        )

    def global_options(self):
        return self._get_field('global-options', {}).copy()

    def global_options_without_flags(self):
        result = self.global_options()
        result.pop('p4ppflags', None)
        result.pop('p4flags', None)
        result.pop('extra-cppflags', None)
        result.pop('kdir', None)
        return result

    def features_as_options(self):
        result = {}
        for feature, options in self.features().items():
            if self._is_option(feature):
                result[feature] = False if options == False else True  # noqa
            if isinstance(options, Iterable):
                for attr in options:
                    # some attributes like 'profile' in 'switch' are not options
                    if self._is_option(attr):
                        result[attr] = options[attr]
        return result

    def _is_option(self, name):
        return name in self._configuration_manager.known_p4studio_options

    def architecture_options(self):
        return {
            definition.p4studio_name: (definition.p4studio_name in self.architectures())
            for definition in self._configuration_manager.definitions
            if definition.category == 'Architecture'
        }

    @property
    def switch_profile(self):
        return self._get_field('features/switch/profile', None)

    @switch_profile.setter
    def switch_profile(self, profile_name):
        self.set_option('switch', True)
        return self._set_field('features/switch/profile', profile_name)

    @property
    def bsp_path(self):
        return self._get_field('features/bf-platforms/bsp-path', None)

    @bsp_path.setter
    def bsp_path(self, path):
        return self._set_field('features/bf-platforms/bsp-path', path)

    @property
    def p4ppflags(self):
        return self._get_field('global-options/p4ppflags', None)

    @p4ppflags.setter
    def p4ppflags(self, value):
        return self._set_field('global-options/p4ppflags', value)

    @property
    def p4flags(self):
        return self._get_field('global-options/p4flags', None)

    @p4flags.setter
    def p4flags(self, value):
        return self._set_field('global-options/p4flags', value)

    @property
    def extra_cppflags(self):
        return self._get_field('global-options/extra-cppflags', None)

    @extra_cppflags.setter
    def extra_cppflags(self, value):
        return self._set_field('global-options/extra-cppflags', value)

    @property
    def kdir(self):
        return self._get_field('global-options/kdir', None)

    @kdir.setter
    def kdir(self, value):
        return self._set_field('global-options/kdir', value)

    def architectures(self):
        return self._get_field('architectures', [])

    def features(self):
        return self._get_field('features', {})

    def build_targets(self):
        result = self._get_field('features/p4-examples', []).copy()
        profile = self.switch_profile
        if profile:
            result.append(profile)
        return result

    def _get_field(self, path, default):
        return nested_get(self.raw, path, default)

    def _set_field(self, path, value):
        nested_set(self.raw, path, value)

    def _calculate_source_packages(self):
        result = ['bridge', 'libcli']

        if any([
            self.config_options().get('thrift-driver', True),
            self.config_options().get('switch', False) and self.config_options().get('thrift-switch', True),
            self.config_options().get('bf-diags', False) and self.config_options().get('thrift-diags', True),
        ]):
            result.append('thrift')

        if self.config_options().get('grpc', True):
            result.append('grpc')
        if self.config_options().get('pi', False) or self.config_options().get('p4rt', False):
            result.append('pi')

        return result

    def _validate_against_schema(self, yaml_content):
        try:
            validate(yaml_content, create_profile_schema(self._configuration_manager))
        except ValidationError as e:
            message = "[{}]: {}".format('/'.join(str(s) for s in e.path), e.message)
            raise ApplicationException(message) from e
