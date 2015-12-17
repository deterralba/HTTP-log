#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)

from threading import Thread
import io
from random import randint
import time
import reader
import os


class LogWriter(Thread):
    def __init__(self, log_path, mode='HTTP', pace=1000, timeout=-1):
        """Writes line in the file given by the log_path"""
        Thread.__init__(self)

        self.log_path = log_path
        self.mode = mode
        self.pace = pace
        self.timeout = timeout

        self.should_run = True
        self.log_file = None

    def run(self):
        line_count = 0
        start_time = time.time()
        try:
            os.remove(self.log_path)
            print("Log file found and erased")
        except IOError:
            print("Log file not found, will be created")
        self.log_file = io.open(self.log_path, 'wt')

        if self.mode == 'HTTP':
            random_line = random_local_URL
        else:
            def random_line(): return 'line' + str(line_count)  # PEP8 says 'do not assign lambda expressions'...
            # faster than ''.join(['line', str(line_count)])

        if self.timeout == -1:
            def timeout_check(): return True
        else:
            def timeout_check(): return time.time() - start_time < self.timeout

        while self.should_run and timeout_check():
            line_count_second = 0
            start_time_second = time.time()
            print('start :', start_time_second)
            while line_count_second < self.pace:
                self.log_file.write(random_line() + '\n')
                self.log_file.flush()
                line_count += 1
                line_count_second += 1
                # print('written line', line_count-1)
                # time.sleep(1.0/self.pace)
            delta = time.time() - start_time_second
            print('delta :', delta)
            if delta < 1:
                print('waiting for :', 1-delta)
                time.sleep(1-delta)
            print('end :', time.time(), 'line_count :', line_count, '\n==========')

        print('LogWriter end after {} lines in {:.4f}s'.format(line_count, time.time()-start_time))
        self.log_file.close()


def random_local_URL(factor=3, max_depth=4):
    """Return a random local URL

    NB number of section = len(section) * factor, by default = 9
    NB max_depth is the highest number possible of /section/subsection/subsubsection/etc., by default = 4 (and min = 0)
    Ex /archive2/blog0/archive2/page1/ -> depth = 4

    Examples
    --------
    /              <- min_depth without URL_end
    /index.html    <- min_depth with URL_end
    /page0/
    /archive0/blog1/
    /blog0/picture.png
    /page0/archive1/archive2/index.html
    /archive2/archive0/archive2/archive2/form.php    <- max_depth with URL_end
     """
    section = ['page', 'blog', 'archive']
    URL_begging = [word + str(i) for i in xrange(factor) for word in section]
    URL_end = ['picture.png', 'index.html', 'form.php']
    return '/' + '/'.join([URL_begging[randint(0, len(URL_begging)-1)] for i in xrange(randint(0, max_depth))] +
                          [URL_end[randint(0, len(URL_end)-1)]*(randint(0, 4) >= 1)])


if __name__ == '__main__':
    # import reader
    log_path = '../data/wtest'
    lw = LogWriter(log_path, mode='HTTP', timeout=1, pace=5000)
    rd = reader.ReaderThread(log_path)
    lw.start()
    time.sleep(0.1)
    rd.start()
    time.sleep(5)
    # rd.should_run = False

    # import timeit
    # print(timeit.timeit("''.join(['line', str(1234)])", number=1000))
    # print(timeit.timeit("'line' + str(1234)", number=1000))


    # [print(random_local_URL()) for i in xrange(10)]
    #
    # line_count = 1
    # random_line = lambda : 'line' + str(line_count)
    # print(random_line())
    # line_count +=1
    # print(random_line())

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

    # timeout = 1
    # start_time = time.time()
    # if timeout == -1:
    #     timeout_check = lambda: True
    # else:
    #     timeout_check = lambda: time.time() - start_time < timeout
    #
    # print(timeout_check())
    # time.sleep(abs(timeout))
    # print(timeout_check())




