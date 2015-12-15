#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)

import time
import Queue
from threading import Thread, Lock


class Misc(Thread):
    def __init__(self, log_path, queue=Queue.Queue(), put=True):
        Thread.__init__(self)
        self.log_path = log_path
        self.should_run = True
        self.run_is_running = False
        self.var = 0
        self.lock = Lock()
        self.queue = queue
        self.count = 0
        self.put = put

    def run(self):
        self.run_is_running = True
        # while self.should_run:
        #     print('in ReaderThread.run, waiting since', time.time())
        #     time.sleep(5)
        #
        # while self.should_run:
        #     if self.var != -1:
        #         self.var = -1
        #         print("var changed in run() !!", self.var)
        i = 0
        while self.should_run:
            if self.put:
                time.sleep(1)
                self.put_in_queue()
            else:
                time.sleep(1.5)
                self.get_from_queue()
            # self.lock.acquire()
            # print(i)
            # i +=1
            # self.lock.release()


        self.run_is_running = False

    def print_me(self, text):
        print(text, time.time(), '   is run running ?', self.run_is_running)

    def setVar(self, var):
        self.var = var
        print(self.var)
        print(self.run_is_running)
        print(self.var)

    def alphabet(self):
        self.lock.acquire()
        print(time.time())
        [print(a) for a in "abcdefgh"]
        time.sleep(2)
        self.lock.release()

    def put_in_queue(self):
        self.queue.put(self.count)
        print('PUTTER : ', self.count, 'put at', time.time())
        self.count +=1

    def get_from_queue(self):
        temp = self.queue.get()
        time.sleep(0.1)
        print('GETTER ', temp, 'got at', time.time())

if __name__ == '__main__':

    q = Queue.Queue()
    rth = Misc('../data/log_test', q, put=False)
    rth2 = Misc('../data/log_test', q)

    rth.start()
    # time.sleep(1)
    # rth.print_me('coucou')
    # time.sleep(1)
    # rth.print_me('coucou')

    # print(rth.var)
    # rth.setVar(2)
    # print(rth.var)

    # rth.alphabet()
    # rth.print_me("coucou")

    rth2.start()


    # rth.should_run = False