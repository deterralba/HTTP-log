#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)

import io
import re
import datetime
import time
from threading import Thread, Lock
import Queue


class HTTPFormatError(Exception):
    pass


class ReaderThread(Thread):
    def __init__(self, log_path):
        Thread.__init__(self)
        self.log_path = log_path
        self.log_file = None
        self.should_run = True
        self.lock = Lock()
        self.reader_queue = Queue.Queue()

    def run(self):
        try:
            self.log_file = io.open(self.log_path, 'rt')
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
                if temp_count == 500:
                    temp_count = 0
                    print('lines read up to', i)
                temp_count += 1
                # print(self.log_file.tell())
                # print('begining of line', i + 1, ':', self.log_file.tell(), '"',
                #       self.log_file.readline().strip(), '"', self.log_file.tell())
                line = self.log_file.readline()
                if not line:
                    print("EOF in line", i + 1)
                    EOF = True
                else:
                    i += 1
                    # print('read:', line)
                    self.reader_queue.put(line)
                # last_tell = self.log_file.tell()
            print("empty queue")
            # self.reader_queue = Queue.Queue()
            # print(time.time() - t)
            time.sleep(0.1)
        self.log_file.close()


def read_log(log_name):
    """Read the log file given and return a list of all the non-empty line that are not starting with '#'

    NB: the returned line are .strip()-ed"""
    with io.open(log_name, 'rt') as log_file:  # encoding can be set with 'utf_8'
        return [line.strip() for line in log_file if not line.strip().startswith('#') and len(line.strip()) > 0]


def parse_line(line):
    """Parse a HTTP w3c formatted line and return a dictionary with the following keys:
    ('remote_host', 'remote_log_name', 'auth_user', 'date', 'request', 'status', 'bytes')

    NB date is converted in a datetime object, UTC-time
    NB status and bytes are converted to int"""
    # 127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326

    parsed = re.match(r'^(?P<remote_host>\S*)\s*(?P<remote_log_name>\S*)\s*(?P<auth_user>\S*)\s*\[(?P<date>.*?)\]'
                      r'\s*\"(?P<request>.*)\"\s*(?P<status>\d*)\s*(?P<bytes>\d*)$', line.strip())
    if parsed is None:  # or min([len(value) for value in parsed.groupdict().itervalues()]) == 0:
        raise HTTPFormatError('incorrect HTTP format in line: {}'.format(line))
    parsed_dict = parsed.groupdict()
    try:
        parsed_dict['status'], parsed_dict['bytes'] = int(parsed_dict['status']), int(parsed_dict['bytes'])

        # the date is transformed in a datetime.datetime object
        date = parsed_dict['date']
        # the used of a delta is necessary because %z doesn't work in python<3.2...
        delta = datetime.timedelta(hours=int(date[-5:]) / 100)
        parsed_dict['date'] = datetime.datetime.strptime(date[:-6], '%d/%b/%Y:%X') - delta
    except:
        raise HTTPFormatError('incorrect HTTP format in line: {}'.format(line))

    return parsed_dict


def get_section(request):
    """Return the section name from a GET request, or None if not a proper GET request"""
    section = re.match(r'^GET\s*(/[^/ ]*)', request.strip())
    if section is not None:
        return section.group(1)
    return None


if __name__ == '__main__':
    pass
    # print(read_log('../data/log_test'))
    # print(parse_line('127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326'))
    # print(get_section("GET /section123/image.png HTTP/1.1"))

    # might be useful to know the encoding
    # ====================================
    # import locale
    # print(locale.getpreferredencoding())

    # date correction : %z doesn't work in python<3.2
    # ===============================================
    # date = '10/Oct/2000:13:55:36 -0700'
    # delta = datetime.timedelta(hours=int(date[-5:]) / 100)
    # dt = datetime.datetime.strptime(date[:-6], '%d/%b/%Y:%X') - delta
    # print(dt)

    rth = ReaderThread('../data/wtest')
    rth.daemon = False
    rth.start()
    time.sleep(0.2)
    #rth.should_run = False
