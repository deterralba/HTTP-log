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


class Displayer(Thread):
    def __init__(self, statistician, display_period=10,
                 console_print_log=False, write_file_log=True, log_level=LogLevel.WARNING):
        Thread.__init__(self)

        self.statistician = statistician
        self.display_period = display_period

        self.log_level = LogLevel
        self.console_print_log = console_print_log
        self.write_file_log = write_file_log
        self.output_log_path = '../log/log'

        self.output_log_opened = False
        self.should_run = True

        self.console_lock = Lock()

        if self.write_file_log:
            try:
                os.remove(self.output_log_path)
            except Exception:
                pass
            try:
                self.output_log = io.open(self.output_log_path, 'at')
                self.output_log_opened = True
            except Exception:
                pass

    def run(self):
        last_display_time = time.time()
        while self.should_run:
            delta = time.time() - last_display_time
            # print(delta)
            if delta >= self.display_period:
                self.lock_print(self.stat_string())
                last_display_time = time.time()
            else:
                time.sleep(self.display_period - delta)

    def stat_string(self):
        stat = self.statistician.stat.get_last_stats()
        print(self.statistician.stat.section)
        self.statistician.stat.reset_stat()
        separation = '='*60
        res = '{0}\nMost visited section: {1[0]} with {1[1]} hits.\n{0}'.format(separation, stat)
        return res

    def log(self, level, sender, message):
        if level >= self.log_level:
            log_line = " : ".join((datetime.datetime.now().isoformat(), sender.__class__.__name__, message))
            if self.console_print_log:
                self.lock_print(log_line)
            if self.write_file_log and self.output_log_opened:
                self.output_log.write(log_line + '\n')
                self.output_log.flush()

    def lock_print(self, *args, **kwargs):
        with self.console_lock:
            print(*args, **kwargs)


if __name__ == '__main__':
    from log_writer import random_HTTP_request, uniform_random_local_URL_maker
    from statistician import get_section

    th = Displayer(None, display_period=1)

    random_URL = uniform_random_local_URL_maker()
    th.stat_string = lambda: '{0}\n' \
                             'Most visited section: {1[0]} with {1[1]} hits.\n' \
                             '{0}'.format('='*60, (get_section(random_HTTP_request(random_URL())), randint(0, 1e4)))

    th.console_print_log = True

    th.start()

    th.log(LogLevel.DEBUG, th, 'Je suis un debug 1')
    th.log_level = LogLevel.DEBUG
    th.log(LogLevel.DEBUG, th, 'Je suis un debug 2')



#
#
# class InputThread(Thread):
#     def __init__(self):
#         Thread.__init__(self)
#         self.daemon = True
#
#     def run(self):
#         while True:
#             i = raw_input()
#             print(i)