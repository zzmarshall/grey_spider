#!/usr/bin/env python 
# -*- encoding:utf-8 -*-

import os
import sys
import time
import errno
import fcntl
import atexit
import signal
import socket
from datetime import datetime

from logger import get_log_path

class Daemon(object):
    ''' build daemon process step by step '''

    def __init__(self, pid_file, logger,
                 stdin_file='/dev/null',
                 stdout_file='/dev/null',
                 stderr_file='/dev/null'
                 ):
        self.logger = logger
        self._pid_filename    = pid_file
        self._stdin_filename  = stdin_file
        self._stdout_filename = stdout_file
        self._stderr_filename = stderr_file

        if sys.flags.debug:
            self.logger.info('Conf:daemon pid file: {}'.format(self._pid_filename))
            self.logger.info('Conf:daemon stdin file: {}'.format(self._stdin_filename))
            self.logger.info('Conf:daemon stdout file: {}'.format(self._stdout_filename))
            self.logger.info('Conf:daemon stderr file: {}'.format(self._stderr_filename))


    def _lock_pid_file(self):
        pid_file = self._open_file(self._pid_filename, mode='a+')
        try:
            fcntl.lockf(pid_file, fcntl.LOCK_EX|fcntl.LOCK_NB)
            if sys.flags.debug:
                self.logger.info('Successed:lockf:{}:{}:{}.'.format(pid_file.name, pid_file.mode, 'EX|NB'))
        except IOError as e:
            if e.errno in (errno.EACCES, errno.EAGAIN):
                self.logger.info('Failed:lockf:{}:{}:already locked.'.format(pid_file.name, 'EX|NB'))
                self.logger.info('Aborted:server already running:pid file:{}.'.format(pid_file.name))
            else:
                self.logger.info(e)
            exit(1)
        self._pid_file = pid_file
        self._pid_file.seek(0, os.SEEK_SET)
        self._pid_file.truncate()
        self._pid = os.getpid()
        print >>self._pid_file, self._pid
        self.logger.info("PID_FILE:{}, PID:{}".format(self._pid_file, self._pid))
        self._pid_file.flush()
        if sys.flags.debug:
            self.logger.info('Recorded:daemon pid:{}.'.format(self._pid))


    def _open_file(self, filename, mode='r', buffering=0, quit_on_error=True):
        try:
            fileop = open(filename, mode, buffering)
            if sys.flags.debug:
                self.logger.info('Successed:open:{}:{}:{}.'.format(fileop.name, fileop.mode, buffering))
        except IOError as e:
            if quit_on_error:
                self.logger.info('Fatal:open:{}:{}:{}.'.format(e.filename, e.errno, e.strerror))
                exit(1)
            else:
                if sys.flags.debug:
                    self.logger.info('Failed:open:{}:{}:{}.'.format(filename, mode, buffering))
                return None
        return fileop


    def _daemon_fork(self):
        try:
            pid = os.fork()
            if pid > 0: exit(0)
        except OSError as e:
            self.logger.info('Fatal:daemon fork:{}:{}.'.format(e.errno, e.strerror))
            exit(1)
        if sys.flags.debug:
            self.logger.info('Successed:daemon fork')


    def _handle_files(self):
        self._stdin = self._open_file(self._stdin_filename, buffering=1)
        self._stdout = self._open_file(self._stdout_filename, mode='a+', buffering=0)
        self._stderr = self._open_file(self._stderr_filename, mode='a+', buffering=0)

        os.dup2(self._stdin.fileno(), sys.stdin.fileno())
        os.dup2(self._stdout.fileno(), sys.stdout.fileno())
        os.dup2(self._stderr.fileno(), sys.stderr.fileno())


    def _daemonize(self):
        self._daemon_fork()
        os.umask(0)
        os.setsid()
        os.chdir('/')
        self._daemon_fork()
        self._lock_pid_file()
        atexit.register(self._remove_pid_file)
        self._handle_files()


    def _remove_pid_file(self):
        os.remove(self._pid_filename)


    def run(self, _interval):
        self.logger.info("------------------------------")
        self.logger.info("--{}--{} start: pid:[{}]".format(self.hostname, self.__class__, self._pid))
        self.logger.info("--LOG_PATH: {}".format(get_log_path(self.logger)))
        self.logger.info("------------------------------")


    def start(self, _interval):
        self._daemonize()
        self.run(_interval)


    def snooze(self, _interval=0):
        self.logger.info("Sleep for %ss", _interval)
        time.sleep(_interval)
        self.logger.info("Scheduler Awake")


    @property
    def hostname(self):
        return socket.gethostname()


    def send_alarm(self, name):
        self.logger.info("send_alarm")
        msg = str(datetime.datetime.now())
        msg += "\nOps! {} dead... come and see see...".format(name)
#        send_mail(
#            subject="[ pl-alarm ]",
#            message=msg,
#            recipient_list=Config["recipient_list"],
#            subtype="plain"
#            )
        for tel in Config["tels"]:
            (status, count) = send_sms(
                Config["appid"],
                Config["key"],
                tel,
                msg.decode('utf-8').encode('gbk')
                )
        return None


if __name__ == '__main__':
    class DaemonIns(Daemon):
        def run(self, _interval):
            print "Ins run"
            while True:
                print "Thread start"
                time.sleep(_interval)

    DaemonIns('', stdout_file='', stderr_file='').start(5)
