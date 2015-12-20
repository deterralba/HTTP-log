#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)

from threading import Thread
from Queue import Queue

from display import LogLevel, Displayer

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
    def __init__(self, log_path, sleeping_time=0.1, parse=False):
        Thread.__init__(self)

        self.log_path = log_path
        self.sleeping_time = sleeping_time
        self.parse = parse

        self.should_run = True
        self.output_queue = Queue()

    def run(self):
        try:
            log_file = io.open(self.log_path, 'rt')
        except IOError:
            print('WRONG PATH TO LOG FILE')
            raise

        if self.parse:
            import statistician

        i = 0

        # print sys 2
        last_printed_time = time.time()
        since_last_printed = 0
        last_EOF = 0
        last_EOF_time = time.time()

        while self.should_run:
            # print('reader started')
            EOF = False
            # t = time.time()
            # temp_count = 0
            while not EOF:
                # if temp_count == 500:
                #     temp_count = 0
                #     print('lines read up to', i)
                # temp_count += 1

                line = log_file.readline()
                if not line:
                    # print("EOF in line", i + 1)
                    EOF = True

                    # sys1 EOF info
                    last_EOF = 0
                    last_EOF_time = time.time()
                else:
                    i += 1

                    # sys1 EOF info
                    last_EOF += 1
                    if last_EOF % 10000 == 0:
                        print('last EOF', last_EOF, 'lines ago !', time.time()-last_EOF_time,' ago')

                    # sys2 EOF info
                    since_last_printed += 1
                    if since_last_printed % 100 == 0:
                        delta = time.time() - last_printed_time
                        if delta > 1:
                            print(since_last_printed, 'lines parsed last', delta, 's')
                            last_printed_time = time.time()
                            since_last_printed = 0


                    line = line.strip()
                    if not line.startswith('#') and len(line) > 0:
                        if self.parse:
                            self.output_queue.put(statistician.parse_line(line))
                        else:
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
