#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)

from threading import Thread

import time


class Displayer(Thread):
    def __init__(self, monitor):
        Thread.__init__(self)
        self.monitor = monitor

    def run(self):
        i = 0
        while True:
            print(i, time.time())
            i +=1
            time.sleep(3)


class InputThread(Thread):
    def __init__(self):
        Thread.__init__(self)
        self.daemon = True

    def run(self):
        while True:
            i = raw_input()
            print(i)

if __name__ == '__main__':
    th = Displayer()
    th.start()
    th2 = InputThread()
    th2.start()
