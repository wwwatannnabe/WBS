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

class OsInfo:
    CANONICAL_NAMES = {
        'ubuntu': 'Ubuntu',
        'centos': 'CentOS',
        'debian': 'Debian'
    }

    @staticmethod
    def os_release():
        with open('/etc/os-release', 'r') as file:
            return OsInfo(line for line in file)

    def __init__(self, lines):
        self.data = {}
        for line in lines:
            if not line or line.isspace():
                continue
            name, value = line.rstrip().split('=')
            self.data[name] = value.strip('"')

    @property
    def name(self):
        os_name = self.data['ID'].lower()
        return self.canonicalize(os_name)

    @property
    def version(self):
        return self.data['VERSION_ID']

    def canonicalize(self, os_name):
        return self.CANONICAL_NAMES.get(os_name, os_name)


os_info = OsInfo.os_release()
