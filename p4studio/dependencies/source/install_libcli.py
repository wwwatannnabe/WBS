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


def install_libcli(os_name,
               os_version,
               jobs,
               logger=None,
               log_file=None,
               resume_build=False,
               progress_file=None):
    curr_date = datetime.date.today().strftime('%y%m%d')
    curr_time = datetime.datetime.now().strftime('%H%M%S')
    if log_file is None:
        log_file = '%s/Libcli_%s_%s.log' % (curr_dir, curr_date, curr_time)

    if resume_build:
        status = utils.check_progress(progress_file, install_libcli.__name__)
        if status:
            return (True, '\t - Skipping installation of Libcli ...')

    # Get libcli source data from dependencies.yaml
    dp = dependencies.Dependencies('%s/../dependencies.yaml' % curr_dir)
    defaults = dp.get_defaults()
    os_defaults = dp.get_defaults(os_name)

    libcli_data = defaults['source_packages']['libcli']
    if os.path.exists('%s/libcli' % curr_dir):
        old_dir="libcli.old-%s-%s" % (curr_date, curr_time)
        os.makedirs('%s/%s' % (curr_dir, old_dir))
        os.system('mv %s/libcli %s/%s' % (curr_dir,
                                          curr_dir,
                                          old_dir))
        # Recursively change permissions of libcli directory
        cmd = 'chmod -R a+rwx %s/%s' % (curr_dir, old_dir)
        if logger is not None:
            line = '\t\tCOMMAND: [%s]' % cmd
            logger.info(line);
            utils.write_to_log(log_file, line)
        else:
            print('\t\tCOMMAND: [%s]' % cmd)
        status = utils.exec_cmd(cmd, log_file)


    # Extract libcli
    os.chdir(curr_dir)
    line = '\t - Building Libcli ... '
    if logger is not None:
        logger.info(line)
    else:
        print (line)
    utils.write_to_log(log_file, line)

    cmd = '%s %s' % (libcli_data['mode'], libcli_data['url'])
    line = '\t\tCOMMAND: [%s]' % cmd
    if logger is not None:
        logger.info(line)
    else:
        print (line)
    utils.write_to_log(log_file, line)
    status = utils.exec_cmd(cmd, log_file)
    if status[2] != 0:
        return (False, 'Failed to extract Libcli, command - %s, error - %s ' \
                       % (cmd, status[1]))

    # Build Libcli
    os.chdir('%s/libcli' % curr_dir)

    cmds = ['git checkout %s' % libcli_data['default_sha'],
            'make -j%s' % jobs,
            'sudo make install',
            'sudo ldconfig']

    for cmd in cmds:
        line = '\t\tCOMMAND: [%s]' % cmd
        if logger is not None:
            logger.info(line)
        else:
            print (line)
        utils.write_to_log(log_file, line)
        status = utils.exec_cmd(cmd, log_file)
        if status[2] != 0:
            return (False, 'Failed to build Libcli, command - %s, error - %s' \
                           % (cmd, status[1]))

    # Recursively change permissions of libcli directory
    cmd = 'chmod -R a+rwx %s/libcli' % (curr_dir)
    if logger is not None:
        line = '\t\tCOMMAND: [%s]' % cmd
        logger.info(line);
        utils.write_to_log(log_file, line)
    else:
        print('\t\tCOMMAND: [%s]' % cmd)
    status = utils.exec_cmd(cmd, log_file)

    if progress_file:
        utils.update_progress(progress_file, install_libcli.__name__)
    return (True, '\tSuccessfully built and installed Libcli')


# -----------------------------------------------------------------------------


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-os", "--os-name", required=True,
                        help="To be provided to specify the name of the OS")
    parser.add_argument("-ver", "--os-version", required=True,
                        help="To be provided to specify the version of the OS")
    parser.add_argument("-j", "--jobs", required=False,
                        help="To be provided to specify the number of jobs for \
                        parallel builds", default=multiprocessing.cpu_count()-1)

    args, unknown = parser.parse_known_args()
    os_name = args.os_name
    os_version = args.os_version
    jobs = args.jobs

    status = install_libcli(os_name, os_version, jobs)
    if True not in status:
        print ('\tERROR: Failed to install libcli - %s' % status[-1])
        exit(1)
    else:
        print (status[-1])
