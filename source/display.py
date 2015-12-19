#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)

from threading import Thread
from random import randint

import time

from log_writer import random_HTTP_request
from statistician import get_section


class Displayer(Thread):
    def __init__(self, statistician, display_period=10):
        Thread.__init__(self)

        self.statistician = statistician
        self.display_period = display_period

        self.should_run = True

    def run(self):
        last_display_time = time.time()
        while self.should_run:
            delta = time.time() - last_display_time
            # print(delta)
            if delta >= self.display_period:
                print(self.stat_string())
                last_display_time = time.time()
            else:
                time.sleep(self.display_period - delta)

    def stat_string(self):
        stat = self.statistician.stat.get_last_stats()
        separation = '='*60
        res = '{0}\nMost visited section: {1[0]} with {1[1]} hits.\n{0}'.format(separation, stat)
        print(self.statistician.stat.section)
        return res


if __name__ == '__main__':

    th = Displayer(None, display_period=1)
    th.stat_string = lambda: '{0}\nMost visited section: {1[0]} ' \
                             'with {1[1]} hits.\n{0}'.format('='*60, (get_section(random_HTTP_request()), randint(0, 1e4)))
    th.start()


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