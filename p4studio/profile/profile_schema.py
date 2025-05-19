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
from build import ALL_SWITCH_PROFILES
from dependencies.dependency_manager import ALL_SOURCE_PACKAGES


def create_profile_schema(configuration_manager):
    return {
        'type': 'object',
        'required': ['global-options', 'features', 'architectures'],
        'properties': {
            'dependencies': _create_dependencies_schema(),
            'global-options': _create_global_options_schema(configuration_manager),
            'features': _create_features_schema(configuration_manager),
            'architectures': _create_architectures_schema(configuration_manager),
            'install-prefix': string_schema(),
        },
        "additionalProperties": False,
    }


def _create_dependencies_schema():
    return object_schema({
        'source-packages': array_schema(
            enum_schema(ALL_SOURCE_PACKAGES)
        )
    })


def _create_global_options_schema(configuration_manager):
    options = {
        d.p4studio_name: boolean_schema()
        for d in configuration_manager.definitions_by_category('Global')
    }

    options.update({
        'p4ppflags': nullable_string_schema(),
        'p4flags': nullable_string_schema(),
        'extra-cppflags': nullable_string_schema(),
        'kdir': nullable_string_schema(),
    })

    return object_schema(options)


def _create_features_schema(configuration_manager):
    return object_schema({
        category.lower(): _create_feature_schema(configuration_manager, category)
        for category in (configuration_manager.categories() | {'p4-examples'})
        if category not in ['Global', 'Architecture']
    })


def _create_feature_schema(configuration_manager, category):
    if category == 'p4-examples':
        return array_schema(string_schema())
    else:
        feature = object_schema({
            option.p4studio_name: boolean_schema()
            for option in configuration_manager.definitions_by_category(category)
        })

        if category == "BF-Platforms":
            feature['properties']['bsp-path'] = string_schema()
        elif category == 'Switch':
            feature['properties']['profile'] = enum_schema(ALL_SWITCH_PROFILES)

        result = {'oneOf': [feature]}
        result['oneOf'].append(boolean_schema())
        return result


def _create_architectures_schema(configuration_manager):
    return array_schema(
        enum_schema(
            d.p4studio_name
            for d in configuration_manager.definitions_by_category('Architecture')
        )
    )


def object_schema(properties):
    return {
        'type': 'object',
        'properties': dict(properties),
        'additionalProperties': False
    }


def array_schema(item_schema):
    return {'type': 'array', 'items': item_schema}


def boolean_schema():
    return {'type': 'boolean'}


def string_schema():
    return {'type': 'string'}


def nullable_string_schema():
    return {'type': ['string', 'null']}


def enum_schema(values):
    return {'type': 'string', 'enum': list(values)}
