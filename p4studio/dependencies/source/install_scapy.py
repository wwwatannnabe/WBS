#!/usr/bin/python

import os
import sys
import datetime
import argparse
python_v = (sys.version_info)


curr_dir = os.path.dirname(os.path.abspath(__file__))

import utils


# -----------------------------------------------------------------------------


def install_scapy(logger=None,
                  log_file=None,
                  resume_build=False,
                  progress_file=None):
    if resume_build:
        status = utils.check_progress(progress_file, install_scapy.__name__)
        if status:
            return (True, '\t - Skipping installation of Scapy ...')

    curr_date = datetime.date.today().strftime('%y%m%d')
    curr_time = datetime.datetime.now().strftime('%H%M%S')

    if log_file is None:
        log_file = '%s/scapy-vxlan_%s_%s.log' % (curr_dir, curr_date, curr_time)

    line = '\t - Installing Scapy'
    if logger is not None:
        logger.info(line)
    else:
        print ('\t - Installing Scapy')
    utils.write_to_log(log_file, line)

    if os.path.exists('%s/scapy-vxlan' % curr_dir):
        os.makedirs('%s/scapy-vxlan.old-%s-%s' % (curr_dir,
                                                  curr_date,
                                                  curr_time))
        os.system('mv %s/scapy-vxlan %s/scapy-vxlan.old-%s-%s'
                  % (curr_dir, curr_dir, curr_date, curr_time))
    if python_v.major == 2:

    # Remove old scapy version
        os.chdir(curr_dir)
        cmds = ['sudo rm -rf /usr/lib/python2.7/dist-packages/scapy-2.2.0.egg-info',
                'sudo rm -rf /usr/lib/python2.7/dist-packages/scapy']
        for cmd in cmds:
            line = '\t\tCOMMAND: [%s]' % cmd
            if logger is not None:
                logger.info(line)
            else:
                print ('\t\tCOMMAND: [%s]' % cmd)
            utils.write_to_log(log_file, line)
            status = utils.exec_cmd(cmd, log_file)
            if status[2] != 0:
                return (False, 'Removeing old scapy version failed, command - ' + \
                               '%s, error - %s' % (cmd, status[1]))

    # Install Scapy
        cmds = ['pip install --ignore-installed scapy==2.4.4']
        for cmd in cmds:
            line = '\t\tCOMMAND: [%s]' % cmd
            if logger is not None:
                logger.info(line)
            else:
                print ('\t\tCOMMAND: [%s]' % cmd)
            utils.write_to_log(log_file, line)
            status = utils.exec_cmd(cmd, log_file)
            if status[2] != 0:
                return (False, 'Building scapy failed with command - ' + \
                               '%s, error - %s' % (cmd, status[1]))
        if progress_file:
            utils.update_progress(progress_file, install_scapy.__name__)
        return (True, '\tSuccessfully built scapy')


    if python_v.major == 3:

    # Extract Scapy
        os.chdir(curr_dir)
        cmds = ['sudo rm -rf /usr/lib/python3/dist-packages/scapy-2.2.0.egg-info',
                'sudo rm -rf /usr/lib/python3/dist-packages/scapy',
                'git clone https://github.com/p4lang/scapy-vxlan']
        for cmd in cmds:
            line = '\t\tCOMMAND: [%s]' % cmd
            if logger is not None:
                logger.info(line)
            else:
                print ('\t\tCOMMAND: [%s]' % cmd)
            utils.write_to_log(log_file, line)
            status = utils.exec_cmd(cmd, log_file)
            if status[2] != 0:
                return (False, 'Extracting scapy failed, command - ' + \
                               '%s, error - %s' % (cmd, status[1]))

    # Build Scapy
        os.chdir('%s/scapy-vxlan' % curr_dir)
        cmds = ['git checkout master',
                'python3 %s/scapy-vxlan/setup.py build' % curr_dir,
                'sudo -E python3 %s/scapy-vxlan/setup.py install' % curr_dir]
        for cmd in cmds:
            line = '\t\tCOMMAND: [%s]' % cmd
            if logger is not None:
                logger.info(line)
            else:
                print ('\t\tCOMMAND: [%s]' % cmd)
            utils.write_to_log(log_file, line)
            status = utils.exec_cmd(cmd, log_file)
            if status[2] != 0:
                return (False, 'Building scapy failed with command - ' + \
                               '%s, error - %s' % (cmd, status[1]))
        if progress_file:
            utils.update_progress(progress_file, install_scapy.__name__)
        return (True, '\tSuccessfully built scapy')

# -----------------------------------------------------------------------------

if __name__ == "__main__":
    status = install_scapy()
    if True not in status:
        print ('\tERROR: Failed to build scapy - %s' % status[-1])
        exit(1)
    else:
        print (status[-1])
