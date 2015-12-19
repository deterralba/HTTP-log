#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)

from threading import Thread
from Queue import Queue

import io
import re

import datetime
import time


class LogReader(Thread):
    """
    ====================TODO===============
    comment and clean this code !
    ====================TODO===============
    """
    def __init__(self, log_path, sleeping_time=0.1):
        Thread.__init__(self)
        self.log_path = log_path

        self.sleeping_time = sleeping_time
        self.should_run = True
        self.output_queue = Queue()

    def run(self):
        try:
            log_file = io.open(self.log_path, 'rt')
        except IOError:
            print('WRONG PATH TO LOG FILE')
            raise

        i = 0
        while self.should_run:
            # print('reader started')
            # last_tell = self.log_file.tell()
            EOF = False
            # t = time.time()
            #
            # self.log_file = io.open(self.log_path, 'rt')
            # for line in self.log_file:
            #     print("resd", line)


            # self.log_file.seek(0,0)
            temp_count = 0
            while not EOF:
                # if temp_count == 500:
                #     temp_count = 0
                #     print('lines read up to', i)
                # temp_count += 1


                # print(self.log_file.tell())
                # print('begining of line', i + 1, ':', self.log_file.tell(), '"',
                #       self.log_file.readline().strip(), '"', self.log_file.tell())
                line = log_file.readline()
                if not line:
                    # print("EOF in line", i + 1)
                    EOF = True
                else:
                    i += 1
                    line = line.strip()
                    if not line.startswith('#') and len(line) > 0:
                        self.output_queue.put(line)
                    # print('read:', line)

            # print("empty queue")
            # self.output_queue = Queue()
            # print(time.time() - t)
            # print('qsize', self.output_queue.qsize())
            time.sleep(self.sleeping_time)

        log_file.close()


def read_log(log_name):
    """Read the log file given and return a list of all the non-empty line that are not starting with '#'

    Notes
    -----
    The returned line are ``.strip()``-ed
    """
    with io.open(log_name, 'rt') as log_file:  # encoding can be set with 'utf_8'
        return [line.strip() for line in log_file if not line.strip().startswith('#') and len(line.strip()) > 0]


if __name__ == '__main__':
    pass

    # ===== HTTP access log line parser =====
    # print(parse_line('127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326'))
    # print(get_section("GET /section123/image.png HTTP/1.1"))


    # might be useful to know the encoding
    # ====================================
    # import locale
    # print(locale.getpreferredencoding())


    # date correction process : %z doesn't work in python<3.2
    # =======================================================
    # date = '10/Oct/2000:13:55:36 -0700'
    # delta = datetime.timedelta(hours=int(date[-5:]) / 100)
    # dt = datetime.datetime.strptime(date[:-6], '%d/%b/%Y:%X') - delta
    # print(dt)

    # test the LogReader
    # ==================
    rth = LogReader('../data/wtest')
    rth.start()
    time.sleep(1)
    rth.should_run = False
