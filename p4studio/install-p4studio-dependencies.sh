#!/bin/bash
#
# INTEL CONFIDENTIAL
#
# Copyright (c) 2021 Intel Corporation
# All Rights Reserved.
#
# This software and the related documents are Intel copyrighted materials,
# and your use of them is governed by the express license under which they
# were provided to you ("License"). Unless the License provides otherwise,
# you may not use, modify, copy, publish, distribute, disclose or transmit this
# software or the related documents without Intel's prior written permission.
#
# This software and the related documents are provided as is, with no express or
# implied warranties, other than those that are expressly stated in the License.
#

# this script should install OS specific dependencies that are required to run p4studio

set -e

readonly MY_PATH=$(realpath "$0")
readonly MY_DIR=$(dirname "$MY_PATH")

if command -v python3 &>/dev/null; then
  PYTHON3_VERSION=$(python3 -V 2>&1 | sed 's/.* \([0-9]\).\([0-9]\).*/\1\2/')
else
  PYTHON3_VERSION=0
fi

install_python_packages() {
  env pip3 install -r "$MY_DIR/requirements.txt"
}

install_ubuntu_dependencies() {
  apt-get update
  apt-get install -y \
    python3 \
    python3-pip \
    sudo
  install_python_packages
}

install_debian_dependencies() {
  apt-get update
  apt-get install -y \
    python3 \
    python3-pip \
    sudo

  install_python_packages
}

install_ubuntu_16.04_dependencies() {
  install_ubuntu_dependencies
}

install_ubuntu_18.04_dependencies() {
  install_ubuntu_dependencies
}

install_ubuntu_20.04_dependencies() {
  apt-get update
  apt-get install -y \
    python3 \
    python3-dev \
    python3-pip \
    sudo
  install_python_packages
}

install_centos_8_dependencies() {
  yum --enablerepo=extras install -y epel-release
  yum clean expire-cache
  yum --setopt=skip_missing_names_on_install=False install -y \
    python3 \
    python3-pip \
    sudo

  install_python_packages
}

install_debian_9_dependencies() {
  install_debian_dependencies
}

install_debian_10_dependencies() {
  install_debian_dependencies
}

# main

if [ "$EUID" -ne 0 ]
  then echo "ERROR: Please run as root"
  exit 1
fi

echo "Checking OS:"
. /etc/os-release
cat /etc/os-release

readonly INSTALLER="install_${ID}_${VERSION_ID}_dependencies"

if declare -f -F "$INSTALLER" >/dev/null; then
  $INSTALLER
else
  echo "ERROR: OS not supported"
  exit 1
fi
