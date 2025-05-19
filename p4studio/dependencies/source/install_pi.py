#!/usr/bin/python

import os
import sys
import datetime
import yaml
import argparse
import multiprocessing

curr_dir = os.path.dirname(os.path.abspath(__file__))

import utils
import dependencies


# -----------------------------------------------------------------------------


def install_pi(os_name,
               os_version,
               jobs,
               sde_install,
               with_proto,
               logger=None,
               log_file=None,
               resume_build=False,
               progress_file=None):
    curr_date = datetime.date.today().strftime('%y%m%d')
    curr_time = datetime.datetime.now().strftime('%H%M%S')
    if log_file is None:
        log_file = '%s/PI_%s_%s.log' % (curr_dir, curr_date, curr_time)

    if resume_build:
        status = utils.check_progress(progress_file, install_pi.__name__)
        if status:
            return (True, '\t - Skipping installation of PI ...')

    # Get thrift source data from dependencies.yaml
    dp = dependencies.Dependencies('%s/../dependencies.yaml' % curr_dir)
    defaults = dp.get_defaults()
    os_defaults = dp.get_defaults(os_name)

    pi_data = defaults['source_packages']['pi']
    if os.path.exists('%s/PI' % curr_dir):
        os.makedirs('%s/PI.old-%s-%s' % (curr_dir, curr_date, curr_time))
        os.system('mv %s/PI %s/PI.old-%s-%s' % (curr_dir,
                                                curr_dir,
                                                curr_date,
                                                curr_time))

    # Extract PI
    os.chdir(curr_dir)
    line = '\t - Building PI ... '
    if logger is not None:
        logger.info(line)
    else:
        print (line)
    utils.write_to_log(log_file, line)

    cmd = '%s %s' % (pi_data['mode'], pi_data['url'])
    line = '\t\tCOMMAND: [%s]' % cmd
    if logger is not None:
        logger.info(line)
    else:
        print (line)
    utils.write_to_log(log_file, line)
    status = utils.exec_cmd(cmd, log_file)
    if status[2] != 0:
        return (False, 'Failed to extract PI, command - %s, error - %s ' \
                       % (cmd, status[1]))

    # Build PI
    os.chdir('%s/PI' % curr_dir)
    cmds = ['git checkout %s' % pi_data['default_sha'],
            'git submodule update --init --recursive',
            './autogen.sh']

    if os_name == 'CentOS' or os_name == 'Fedora':
        pkg_config_path = sde_install+'/lib/pkgconfig:/usr/lib/pkgconfig:/usr/local/lib/pkgconfig:/usr/share/pkgconfig:/usr/lib64/pkgconfig:$PKG_CONFIG_PATH'
    else:
        pkg_config_path = sde_install+'/lib/pkgconfig:$PKG_CONFIG_PATH'

    cmds += ['PKG_CONFIG_PATH=%s ./configure CPPFLAGS=-I%s/include --prefix=%s --with-proto=%s ' \
                 % (pkg_config_path, sde_install, sde_install, with_proto) + \
                 '--without-bmv2 --without-internal-rpc --without-cli']
    cmds += ['make -j%s' % jobs,
             'make install']

    for cmd in cmds:
        line = '\t\tCOMMAND: [%s]' % cmd
        if logger is not None:
            logger.info(line)
        else:
            print (line)
        utils.write_to_log(log_file, line)
        status = utils.exec_cmd(cmd, log_file)
        if status[2] != 0:
            return (False, 'Failed to build PI, command - %s, error - %s' \
                           % (cmd, status[1]))

    if progress_file:
        utils.update_progress(progress_file, install_pi.__name__)
    return (True, '\tSuccessfully built and installed PI')


# -----------------------------------------------------------------------------


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-os", "--os-name", required=True,
                        help="To be provided to specify the name of the OS")
    parser.add_argument("-ver", "--os-version", required=True,
                        help="To be provided to specify the version of the OS")
    parser.add_argument("-si", "--sde-install", required=True,
                        help="Path to SDE INSTALL")
    parser.add_argument("-wp", "--with-proto", required=False,
                        help="To be provided if P4 runtime is to be enabled",
                        default="no")
    parser.add_argument("-j", "--jobs", required=False,
                        help="To be provided to specify the number of jobs for \
                        parallel builds", default=multiprocessing.cpu_count()-1)

    args, unknown = parser.parse_known_args()
    os_name = args.os_name
    os_version = args.os_version
    jobs = args.jobs
    sde_install = args.sde_install
    with_proto = args.with_proto

    status = install_pi(os_name, os_version, jobs, sde_install, with_proto)
    if True not in status:
        print ('\tERROR: Failed to install p4lang/PI - %s' % status[-1])
        exit(1)
    else:
        print (status[-1])
