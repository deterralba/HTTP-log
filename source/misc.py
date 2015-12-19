#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)

import time
import Queue
import io
from threading import Thread, Lock


class Monitor(Thread):
    """ """

    def __init__(self, input_queue):
        Thread.__init__(self)

        self.should_run = True
        self.input_queue = input_queue
        self.reader = True

    def run(self):
        """ """
        print(self.name, self.reader)
        if self.reader:
            print(self.input_queue.get())
        else:
            self.input_queue.put(123)

if __name__ == '__main__':
    # m = Monitor(Queue())
    # m.input_queue.put(123)
    # print(m.input_queue)

    q = Queue()
    m1 = Monitor(q)
    m2 = Monitor(q)
    print(q.qsize())

    m2.start()
    time.sleep(0.01)
    print(q.qsize())

    m1.reader = False
    m1.start()
    time.sleep(0.01)
    print(q.qsize())


    time.sleep(1)
    print(q.qsize())


def EOF_reader():
    """this is far too slow because tell() is bugged in python 2.x"""
    with io.open('../data/test') as f:
        last_tell = f.tell()
        EOF = False
        i=0

        while not EOF:
            print('begining of line ', i+1, f.tell(), f.readline().strip(), f.tell())
            if last_tell == f.tell():
                print("EOF in line", i+1)
                EOF = True
            last_tell = f.tell()
            i+=1
