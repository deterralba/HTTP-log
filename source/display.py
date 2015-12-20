#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)

from threading import Thread, Lock
from random import randint

import datetime
import io
import os
import time


class LogLevel:
    DEBUG = 10
    INFO = 20
    WARNING = 30
    ERROR = 40
    CRITICAL = 50
    level_name = {10: 'DEBUG', 20: 'INFO', 30: 'WARNING', 40: 'ERROR', 50: 'CRITICAL'}


class Displayer(Thread):
    def __init__(self, statistician=None, display_period=10,
                 console_print_log=False, write_file_log=True, log_level=LogLevel.WARNING,
                 debug=True):
        Thread.__init__(self)

        self.statistician = statistician
        self.display_period = display_period

        self.log_level = log_level
        self.console_print_log = console_print_log
        self.write_file_log = write_file_log
        self.output_log_path = '../log/log'

        self.output_log_opened = False
        self.should_run = True

        self.registered_object = []

        self.console_lock = Lock()

        if self.statistician is None and debug:
                self.log_level = LogLevel.DEBUG
                self.console_print_log = True
                self.write_file_log = False

        if self.write_file_log:
            try:
                os.remove(self.output_log_path)
            except Exception:
                pass
            try:
                self.output_log = io.open(self.output_log_path, 'at')
                self.output_log_opened = True
            except Exception:
                temp_c_print = self.console_print_log
                self.console_print_log = True
                self.log(self, LogLevel.WARNING, 'Output log file couldn\'t have been opened')
                console_print_log = temp_c_print

        if self.statistician is None:
            self.log(self, LogLevel.WARNING, 'No statistician given')

        # TODO explain this !
        global displayer
        displayer = self

    def run(self):
        last_display_time = time.time()
        while self.should_run:
            delta = time.time() - last_display_time
            # print(delta)
            if delta >= self.display_period:

                if self.registered_object:
                    self.log(self, LogLevel.INFO, self.stat_of_registered_object())

                self.lock_print(self.stat_string())
                last_display_time = time.time()
            else:
                time.sleep(self.display_period - delta)

    def stat_string(self):
        stat = self.statistician.stat.get_last_stats()
        self.statistician.stat.reset_stat()
        separation = '='*60
        res = '{0}\nMost visited section: {1[0]} with {1[1]} hits.\n{0}'.format(separation, stat)
        return res

    def log(self, sender, level, message):
        if level >= self.log_level:
            log_line = " : ".join((datetime.datetime.now().isoformat(),
                                   LogLevel.level_name[level],
                                   sender.__class__.__name__,
                                   message))
            if self.console_print_log:
                self.lock_print(log_line)
                # print('statistician', self.statistician, self.console_print_log, self.log_level)
            if self.write_file_log and self.output_log_opened:
                self.output_log.write(log_line + '\n')
                self.output_log.flush()

    def lock_print(self, *args, **kwargs):
        with self.console_lock:
            print(*args, **kwargs)

    def stat_of_registered_object(self):
        return ' ;'.join([' :'.join((obj.__class__.__name__, obj.state())) for obj in self.registered_object])


if __name__ == '__main__':
    pass
    # print(displayer)
    # print(displayer.__dict__)
    # displayer.log(int, 1000, 'test1')
    # displayer.log(datetime.datetime.now(), 1000, 'test2')


    # from log_writer import random_HTTP_request, uniform_random_local_URL_maker
    # from statistician import get_section
    #
    th = Displayer(display_period=1)
    #
    # random_URL = uniform_random_local_URL_maker()
    # th.stat_string = lambda: '{0}\n' \
    #                          'Most visited section: {1[0]} with {1[1]} hits.\n' \
    #                          '{0}'.format('='*60, (get_section(random_HTTP_request(random_URL())), randint(0, 1e4)))
    #
    # th.console_print_log = True
    #
    # th.start()
    #
    # th.log(LogLevel.DEBUG, th, 'Je suis un debug 1')
    # th.log_level = LogLevel.DEBUG
    # th.log(LogLevel.DEBUG, th, 'Je suis un debug 2')





# class InputThread(Thread):
#     def __init__(self):
#         Thread.__init__(self)
#         self.daemon = True
#
#     def run(self):
#         while True:
#             i = raw_input()
#             print(i)