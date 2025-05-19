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

# !/usr/bin/env python3

class ApplicationException(Exception):
    def __str__(self):
        if super().__str__():
            return super().__str__()
        elif self.__cause__ and str(self.__cause__):
            return str(self.__cause__)
        else:
            return ""
