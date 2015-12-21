#!/usr/bin/env python
# coding: utf8

from __future__ import (unicode_literals, absolute_import, division, print_function)

from threading import Thread, Lock
from string import center

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
                 console_print_program_log=False, write_program_log_file=True, log_level=LogLevel.WARNING,
                 debug=False):
        Thread.__init__(self)

        self.statistician = statistician
        self.display_period = display_period
        self.console_print_program_log = console_print_program_log
        self.write_program_log_file = write_program_log_file
        self.log_level = log_level

        self.program_log_path = '../log/log'
        self.program_log_opened = False

        self.alert_log_path = '../log/alert_log'
        self.alert_log_opened = False

        self.should_run = True
        self.registered_object = []
        self.console_lock = Lock()
        self.display_width = 80
        self.name = 'displayer thread'

        if debug:
            self.log_level = LogLevel.DEBUG
            self.console_print_program_log = True
            self.write_program_log_file = False

        if self.write_program_log_file:
            try:
                os.remove(self.program_log_path)
            except OSError:
                pass
            try:
                self.output_log = io.open(self.program_log_path, 'at')
                self.program__log_opened = True
            except Exception:
                temp_c_print = self.console_print_program_log
                self.console_print_program_log = True
                self.log(self, LogLevel.WARNING, "Output log file couldn't have been opened")
                self.console_print_program_log = temp_c_print

        if self.statistician is None:
            self.log(self, LogLevel.WARNING, 'No statistician given')

        # TODO explain this !
        global displayer
        displayer = self

    def run(self):
        program_stat = ' - '.join(
                ['{} is {}started'.format(thread.__class__.__name__, (not thread.is_alive()) * '*not* ')
                 for thread in self.registered_object])
        welcome_msg = '=' * self.display_width + '\n' + \
                      center('Welcome! HTTP-log Displayer is now running', self.display_width) + '\n' + \
                      center(program_stat, self.display_width) + '\n' + '=' * self.display_width
        self.lock_print(welcome_msg)

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
                time.sleep(min(self.display_period - delta, 0.1))

    def stat_string(self):
        stats = self.statistician.stat.get_last_stats()

        self.statistician.stat.reset_short_stat()

        # stats['separation'] = '='*self.display_width
        stats['time'] = datetime.datetime.now()
        stats['total_MB_bytes'] = stats['total_bytes'] / (1024 ** 2)
        stats['display_period'] = self.display_period

        if stats['total_hits']:
            res = '{time:%X} - Most visited section in the past {display_period}s is ' \
                  '\'{max_section}\' with {max_hit} hits.' \
                  '\n\tTotal hits: {total_hits},' \
                  '\n\tTotal sent bytes: {total_bytes}, i.e. {total_MB_bytes:.03f} MB.' \
                  ''.format(**stats)
        else:
            res = '{time:%X} - No request in the last {display_period}s!'.format(**stats)
        return res

    def log(self, sender, level, message):
        if level >= self.log_level:
            log_line = " : ".join((datetime.datetime.now().isoformat(),
                                   LogLevel.level_name[level],
                                   sender.__class__.__name__,
                                   message))
            if self.console_print_program_log:
                self.lock_print(log_line)
                # print('statistician', self.statistician, self.console_print_program_log, self.log_level)
            if self.write_program_log_file and self.program_log_opened:
                self.output_log.write(log_line + '\n')
                self.output_log.flush()

    def lock_print(self, *args, **kwargs):
        with self.console_lock:
            print(*args, **kwargs)

    def stat_of_registered_object(self):
        return '; '.join([': '.join((obj.__class__.__name__, obj.state())) for obj in self.registered_object])

    def print_new_alert(self, alert_param, long_average, short_average):
        high_outflow = short_average / (1024 ** 2) / (alert_param.time_resolution * alert_param.short_median)

        res = center('/' * 17 + ' ALERT ' + '\\' * 17, self.display_width) + '\n' + \
              center('High traffic detected at {:%X}: outflow {:.03}MB/s'
                     ''.format(datetime.datetime.now(), high_outflow), self.display_width)
        self.lock_print(res)

    def print_end_alert(self, alert_param, long_average, short_average):
        low_outflow = long_average / (1024 ** 2) / (alert_param.time_resolution * alert_param.long_median)
        res = center('\\' * 15 + ' ALERT OVER ' + '/' * 15, self.display_width) + '\n' + \
              center('Traffic at {:%X} is {:.03}MB/s'.format(datetime.datetime.now(), low_outflow), self.display_width)
        self.lock_print(res)


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

    # from random import randint
    # random_URL = uniform_random_local_URL_maker()
    # th.stat_string = lambda: '{0}\n' \
    #                          'Most visited section: {1[0]} with {1[1]} hits.\n' \
    #                          '{0}'.format('='*60, (get_section(random_HTTP_request(random_URL())), randint(0, 1e4)))
    #
    # th.console_print_program_log = True
    #
    # th.start()
    #
    # th.log(LogLevel.DEBUG, th, 'Je suis un debug 1')
    # th.log_level = LogLevel.DEBUG
    # th.log(LogLevel.DEBUG, th, 'Je suis un debug 2')
