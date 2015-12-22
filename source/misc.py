#!/usr/bin/env python
# coding: utf8

"""
This is a storage for now useless pieces of code that used to be, or could be useful one day.
"""

from __future__ import (unicode_literals, absolute_import, division, print_function)

from Queue import Queue
from threading import Thread

import time
import io


class InputThread(Thread):
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            i = raw_input()
            print(i)


class Monitor(Thread):
    def __init__(self, input_queue):
        Thread.__init__(self)

        self.should_run = True
        self.input_queue = input_queue
        self.reader = True

    def run(self):
        print(self.name, self.reader)
        if self.reader:
            print(self.input_queue.get())
        else:
            self.input_queue.put(123)


def EOF_reader():
    """this is far too slow because tell() is bugged in python 2.x"""
    with io.open('../data/test') as f:
        last_tell = f.tell()
        EOF = False
        i = 0

        while not EOF:
            print('begining of line ', i + 1, f.tell(), f.readline().strip(), f.tell())
            if last_tell == f.tell():
                print("EOF in line", i + 1)
                EOF = True
            last_tell = f.tell()
            i += 1


def read_log(log_name):
    """Read the log file given and return a list of all the non-empty line that are not starting with '#'

    Notes
    -----
    The returned line are ``.strip()``-ed
    """
    with io.open(log_name, 'rt') as log_file:  # encoding can be set with 'utf_8'
        return [line.strip() for line in log_file if not line.strip().startswith('#') and len(line.strip()) > 0]


if __name__ == '__main__':
    q = Queue()
    m1 = Monitor(q)
    m2 = Monitor(q)
    print('q.qsize:', q.qsize())

    m2.start()
    time.sleep(0.01)
    print('q.qsize:', q.qsize())

    m1.reader = False
    m1.start()
    time.sleep(0.01)
    print('q.qsize:', q.qsize())

    time.sleep(1)
    print('q.qsize:', q.qsize())
