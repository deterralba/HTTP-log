#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)

from threading import Thread
import io
import time


class LogWriter(Thread):
    def __init__(self, log_path):
        Thread.__init__(self)
        self.log_path = log_path
        self.log_file = None
        self.pace = 2
        self.should_run = True

    def run(self):
        i = 1
        line_s = 0
        t = time.time()
        self.log_file = io.open(self.log_path, 'wt')
        while self.should_run and i <= 100:
            #if line_s <= self.pace:
            print(self.log_file.write('line{}\n'.format(i)))
            i += 1
            self.log_file.write('line{}\n'.format(i))
            self.log_file.flush()
            i += 1
            time.sleep(1/self.pace)
            print('written', i-2, i-1)
        print('logwriter end', time.time()-t)
        # self.log_file.close()

if __name__ == '__main__':
    log_path = '../data/wtest'
    lw = LogWriter(log_path)
    rd = reader.ReaderThread(log_path)
    lw.start()
    rd.start()

    time.sleep(5)
    # rd.should_run = False


    # try:
    #     log_file = io.open(log_path, 'rt')
    # except IOError:
    #     print('WRONG PATH TO LOG FILE')
    #     raise
    #
    # t = time.time()
    # i = 0
    # last_tell = log_file.tell()
    # EOF = False
    # while not EOF:
    #     # print('begining of line', i + 1, ':', self.log_file.tell(), '"',
    #     #       self.log_file.readline().strip(), '"', self.log_file.tell())
    #     log_file.readline()
    #     if last_tell == log_file.tell():
    #         print("EOF in line", i + 1)
    #         EOF = True
    #     else:
    #         i += 1
    #     last_tell = log_file.tell()
    # print(time.time() - t)
    # log_file.close()


    # log_file = io.open(log_path, 'rt')
    # t = time.time()
    # i = 0
    # log_file = io.open(log_path, 'rt')
    # for l in log_file:
    #     i += len(l)
    # print(time.time() - t, i)
    # log_file.close()



    # log_file = io.open(log_path, 'rt')
    # t = time.time()
    # should_run = True
    # i = 0
    # while should_run:
    #     # where = log_file.tell()
    #     line = log_file.readline()
    #     if not line:
    #         # time.sleep(0)
    #         # log_file.seek(where)
    #         should_run = False
    #     else:
    #         i += len(line)
    # print(time.time() - t, i, log_file.tell())


