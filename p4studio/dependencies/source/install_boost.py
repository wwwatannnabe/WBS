#!/usr/bin/python3

import os
import datetime
import argparse
import multiprocessing

curr_dir = os.path.dirname(os.path.abspath(__file__))

import utils
import dependencies


# -----------------------------------------------------------------------------


def install_boost(jobs,
                  logger=None,
                  log_file=None,
                  resume_build=False,
                  progress_file=None):
    curr_date = datetime.date.today().strftime('%y%m%d')
    curr_time = datetime.datetime.now().strftime('%H%M%S')
    if log_file is None:
        log_file = '%s/boost_%s_%s.log' % (curr_dir, curr_date, curr_time)

    if resume_build:
        status = utils.check_progress(progress_file, install_boost.__name__)
        if status:
            return (True, '\t - Skipping installation of Boost ...')

    # Get all the dependencies to be installed from dependencies.yaml
    dp = dependencies.Dependencies('%s/../dependencies.yaml' % curr_dir)
    defaults = dp.get_defaults()

    line = '\t - Installing P4C boost dependency'
    if logger is not None:
        logger.info(line)
    else:
        print ('\t - Installing P4C boost dependency')
    utils.write_to_log(log_file, line)

    boost_data = defaults['source_packages']['boost']
    version = boost_data['version']
    ver = version.replace('.', '_')
    if os.path.exists('%s/boost_%s' % (curr_dir, ver)):
        os.makedirs('%s/boost_%s.old-%s-%s' % (curr_dir,
                                               ver,
                                               curr_date,
                                               curr_time))
        os.system('mv %s/boost_%s %s/boost_%s.old-%s-%s'
                  % (curr_dir,
                     ver,
                     curr_dir,
                     ver,
                     curr_date,
                     curr_time))

    # Extract and build boost
    os.chdir(curr_dir)
    cmds = ['%s %s/%s/boost_%s.tar.bz2 -O boost_%s.tar.bz2' \
            % (boost_data['mode'], boost_data['url'], version, ver, ver),
            'tar xvjf %s/boost_%s.tar.bz2' % (curr_dir, ver)]
    for cmd in cmds:
        line = '\t\tCOMMAND: [%s]' % cmd
        if logger is not None:
            logger.info(line)
        else:
            print ('\t\tCOMMAND: [%s]' % cmd)
        utils.write_to_log(log_file, line)

        status = utils.exec_cmd(cmd, log_file)
        if status[2] != 0:
            return (False, 'Extracting boost failed, command' + \
                           ' - %s, error - %s' % (cmd, status[1]))

    os.chdir('%s/boost_%s' % (curr_dir, ver))
    cmds = ['./bootstrap.sh --prefix=/usr/local --without-libraries=python',
            './b2 -j%s' % jobs,
            'sudo ./b2 --with-thread --with-test --with-system install --with-graph --with-iostreams',
            'sudo ldconfig']
    for cmd in cmds:
        if logger is not None:
            line = '\t\tCOMMAND: [%s]' % cmd
            logger.info(line); utils.write_to_log(log_file, line)
        else:
            print ('\t\tCOMMAND: [%s]' % cmd)
        status = utils.exec_cmd(cmd, log_file)
        if status[2] != 0:
            return (False, 'Building boost failed, command' + \
                           ' - %s, error - %s' % (cmd, status[1]))

    # Recursively change permissions of boost directory
    cmd = 'chmod -R a+rwx %s/boost_%s' % (curr_dir, ver)
    if logger is not None:
        line = '\t\tCOMMAND: [%s]' % cmd
        logger.info(line);
        utils.write_to_log(log_file, line)
    else:
        print('\t\tCOMMAND: [%s]' % cmd)
    status = utils.exec_cmd(cmd, log_file)

    if progress_file:
        utils.update_progress(progress_file, install_boost.__name__)
    return (True, '\tSuccessfully built and installed boost')

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-j", "--jobs", required=False,
                        help="To be provided to specify the number of jobs for \
                        parallel builds", default=multiprocessing.cpu_count()-1)

    args, unknown = parser.parse_known_args()
    jobs = args.jobs

    status = install_boost(jobs)
    if True not in status:
        print ('\tERROR: Failed to build boost - %s' % status[-1])
        exit(1)
    else:
        print (status[-1])
