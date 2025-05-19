# Copyright 2013-2021 Intel Corporation.
#
# This software and the related documents are Intel copyrighted materials,
# and your use of them is governed by the express license under which they
# were provided to you ("License"). Unless the License provides otherwise,
# you may not use, modify, copy, publish, distribute, disclose or transmit this
# software or the related documents without Intel's prior written permission.
#
# This software and the related documents are provided as is, with no
# express or implied warranties, other than those that are expressly stated
# in the License.

# define the set of macros that provide info about compiler version
# to be exposed to the P4 program
#
# __p4c__ defined as 1
p4c_major=9
p4c_minor=7
p4c_patchlevel=0
p4c_version="9.7.0"
# and finally, a string that defines the entire set
macro_defs = '-D__p4c__=1 -D__p4c_major__={} -D__p4c_minor__={} \
              -D__p4c_patchlevel__={} -D__p4c_version__=\\"{}\\"'. \
              format(p4c_major, p4c_minor, p4c_patchlevel, p4c_version)
