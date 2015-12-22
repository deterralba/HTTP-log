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
    """ An always waiting for input tread, printing what it gets."""
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            i = raw_input()
            print(i)


class Monitor(Thread):
    """A thread used to demonstrate how a queue object is working"""
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


def EOF_reader(path):
    """Read a file until the EOF.

    Warnings
    --------
    This is far too slow because tell() is bugged in python 2.x !
    """
    with io.open(path) as f:
        last_tell = f.tell()
        EOF = False
        i = 0

        while not EOF:
            print('beginning of line ', i + 1, f.tell(), f.readline().strip(), f.tell())
            if last_tell == f.tell():
                print("EOF in line", i + 1)
                EOF = True
            last_tell = f.tell()
            i += 1


def read_log(log_name):
    """A "two liner" that read the log file given. Fun.

    Returns
    -------
    list of strings:
        A list of all the non-empty line that are not starting with '#'

    Note
    ----
    The returned line are ``.strip()``-ed
    """
    with io.open(log_name, 'rt') as log_file:  # encoding can be set with 'utf_8'
        return [line.strip() for line in log_file if not line.strip().startswith('#') and len(line.strip()) > 0]


if __name__ == '__main__':

    # The following code uses Monitor()
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
