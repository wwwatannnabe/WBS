#!/usr/bin/python

import os
import sys
import datetime
import yaml
import argparse
import multiprocessing
import time

curr_dir = os.path.dirname(os.path.abspath(__file__))

import utils
import dependencies


# -----------------------------------------------------------------------------


def install_bridge_utils(jobs,
                         logger=None,
                         log_file=None,
                         resume_build=False,
                         progress_file=None):
    curr_date = datetime.date.today().strftime('%y%m%d')
    curr_time = datetime.datetime.now().strftime('%H%M%S')
    if log_file is None:
        log_file = '%s/bridge_utils_%s_%s.log' % (curr_dir, curr_date, curr_time)

    if resume_build:
        status = utils.check_progress(progress_file, install_bridge_utils.__name__)
        if status:
            return (True, '\t - Skipping installation of Bridge-utils ...')

    # Get all the dependencies to be installed from dependencies.yaml
    dp = dependencies.Dependencies('%s/../dependencies.yaml' % curr_dir)
    defaults = dp.get_defaults()

    line = '\t - Installing Bridge-utils dependency'
    if logger is not None:
        logger.info(line)
    else:
        print ('\t - Installing Bridge-utils dependency')
    utils.write_to_log(log_file, line)

    bridge_data = defaults['source_packages']['bridge']
    version = bridge_data['version']
    ver = version.replace('.', '_')
    if os.path.exists('%s/bridge-utils_%s' % (curr_dir, ver)):
        os.makedirs('%s/bridge-utils_%s.old-%s-%s' % (curr_dir,
                                                      ver,
                                                      curr_date,
                                                      curr_time))
        os.system('mv %s/bridge-utils_%s %s/bridge-utils_%s.old-%s-%s'
                  % (curr_dir,
                     ver,
                     curr_dir,
                     ver,
                     curr_date,
                     curr_time))
# Extract and build bridge-utils
    os.chdir(curr_dir)
    cmds = ['%s %s -O bridge-utils-%s.tar.xz' \
            % (bridge_data['mode'], bridge_data['url'], version),
            'tar xf %s/bridge-utils-%s.tar.xz' % (curr_dir, version)]
    for cmd in cmds:
        line = '\t\tCOMMAND: [%s]' % cmd
        if logger is not None:
            logger.info(line)
        else:
            print ('\t\tCOMMAND: [%s]' % cmd)
        utils.write_to_log(log_file, line)

        status = utils.exec_cmd(cmd, log_file)
        if status[2] != 0:
            return (False, 'Extracting bridge-utils failed, command' + \
                           ' - %s, error - %s' % (cmd, status[1]))

    os.chdir('%s/bridge-utils-1.6' % (curr_dir))
    cmds = ['autoconf  && ./configure --prefix=/usr/local',
            'make -j%s' % jobs,
            'sudo make install',
            'sudo ldconfig']
    for cmd in cmds:
        if logger is not None:
            line = '\t\tCOMMAND: [%s]' % cmd
            logger.info(line); utils.write_to_log(log_file, line)
        else:
            print ('\t\tCOMMAND: [%s]' % cmd)
        status = utils.exec_cmd(cmd, log_file)
        if status[2] != 0:
            return (False, 'Building bridge failed, command' + \
                           ' - %s, error - %s' % (cmd, status[1]))

# Recursively change permissions of bridge-utils directory
    cmd = 'chmod -R a+rwx %s/bridge-utils-%s' % (curr_dir, version)
    if logger is not None:
        line = '\t\tCOMMAND: [%s]' % cmd
        logger.info(line);
        utils.write_to_log(log_file, line)
    else:
        print('\t\tCOMMAND: [%s]' % cmd)
    status = utils.exec_cmd(cmd, log_file)

    if progress_file:
        utils.update_progress(progress_file, install_bridge_utils.__name__)
    return (True, '\tSuccessfully built and installed bridge-utils')

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--jobs", required=False,
                        help="To be provided to specify the number of jobs for \
                        parallel builds", default=multiprocessing.cpu_count()-1)

    args, unknown = parser.parse_known_args()
    jobs = args.jobs

    status = install_bridge_utils(jobs)
    if True not in status:
        print ('\tERROR: Failed to build boost - %s' % status[-1])
        exit(1)
    else:
        print (status[-1])
