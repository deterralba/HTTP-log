#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)

from threading import Thread, Lock
from operator import itemgetter

from Queue import Queue, Empty
import datetime
import re
import time

import log_writer


class HTTPFormatError(Exception):
    """Raised when the HTTP access log line is not recognized"""
    pass


class Statistics:
    def __init__(self):
        self.lock = Lock()
        self.section = {}
        self.number_of_hits = 0
        self.total_broadband = 0

    def upadate_stat(self, HTTP_dict):
        with self.lock:
            # print(HTTP_dict)
            # print(get_section(HTTP_dict['request']))

            last_section = get_section(HTTP_dict['request'])
            # print(last_section)
            if last_section is not None:  # TODO an error should be raised
                if last_section in self.section:
                    self.section[last_section] += 1
                else:
                    self.section[last_section] = 1

            self.total_broadband += HTTP_dict['bytes']

    def get_last_stats(self):
        with self.lock:
            max_section, max_hit  = max(self.section.iteritems(), key=itemgetter(1))
            return max_section, max_hit

    def reset_stat(self):
        with self.lock:
            self.number_of_hits = 0
            self.section.clear()
            self.total_broadband = 0


class Monitor(Thread):
    """ """

    def __init__(self, input_queue, sleeping_time=0.1):
        Thread.__init__(self)

        self.input_queue = input_queue

        self.stat = Statistics()
        self.should_run = True
        self.sleeping_time = sleeping_time

    def run(self):
        """ """
        last_display_time = time.time()
        while self.should_run:
            # print(self.input_queue.qsize())

            # while self.input_queue.qsize() > 0:
            if time.time() - last_display_time > 1:
                self.display()
                self.stat.reset_stat()
                last_display_time = time.time()
            try:
                log_line = self.input_queue.get(block=True, timeout=0.1)
            except Empty:
                continue
            HTTP_dict = parse_line(log_line)
            self.stat.upadate_stat(HTTP_dict)


            # print('queue empty', self.input_queue.qsize())
            # print(self.stat.section)
            if self.input_queue.qsize() == 0:
                time.sleep(self.sleeping_time)

        # print(self.stat.get_last_stats())

        max_l = []
        l = list(self.stat.section.iteritems())
        # print(l)
        # max_l.append(max(l, key=itemgetter(1)))
        # print(max_l)
        # del l[l.index(max_l[0])]
        # print(l)
        # l = sorted(self.stat.section.iteritems(), key=itemgetter(1), reverse=True)
        # print(l[:3])

    def display(self):
        stat = self.stat.get_last_stats()
        print('='*60)
        print('Most visited section:', stat[0], 'with', stat[1], 'hits.')
        print('='*60)


class QueueWriter(Thread):
    """ """

    def __init__(self, output_queue, pace10=1, factor=3):
        Thread.__init__(self)

        self.output_queue = output_queue
        self.pace10 = pace10
        self.factor = factor

        self.should_run = True

    def run(self):
        """ """
        total_count = 0
        random_log_line = log_writer.random_log_line_maker('HTTP_slow', factor=self.factor)
        while self.should_run:
            line_count_second10 = 0
            start_time_second10 = time.time()
            while self.should_run and line_count_second10 < self.pace10 and time.time() - start_time_second10 < 0.1:
                self.output_queue.put(random_log_line(date=datetime.datetime.utcnow().strftime('[%d/%b/%Y:%X +0000]')))
                line_count_second10 += 1
                # print(line_count_second10)

            delta = time.time() - start_time_second10
            if delta < 0.1 and line_count_second10 == self.pace10:  # check that line !!
                # print('waiting for :', 0.1 - delta)
                time.sleep(0.1 - delta)
            else:
                print('putting operations are too slow, reduce pace10, '
                      'lines putted this 10th of second:', line_count_second10)
            total_count += line_count_second10
        # print('qsize', self.output_queue.qsize())
        # print('total count', total_count)


def parse_line(line):
    """Parse a HTTP w3c formatted line and return a dictionary with the following keys:
    ``'remote_host', 'remote_log_name', 'auth_user', 'date', 'request', 'status', 'bytes'``

    Notes
    -----

    * ``date`` is converted in a datetime object, UTC-time
    * ``status`` and ``bytes`` are converted to ``int``

    Raises
    ------
    HTTPFormatError
    """
    # 127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326

    parsed = re.match(r'^(?P<remote_host>\S*)\s*(?P<remote_log_name>\S*)\s*(?P<auth_user>\S*)\s*\[(?P<date>.*?)\]'
                      r'\s*\"(?P<request>.*)\"\s*(?P<status>\d*)\s*(?P<bytes>\d*)$', line.strip())
    if parsed is None:
        raise HTTPFormatError('incorrect HTTP format in line: {}'.format(line))
    HTTP_dict = parsed.groupdict()
    try:
        HTTP_dict['status'], HTTP_dict['bytes'] = int(HTTP_dict['status']), int(HTTP_dict['bytes'])

        # the date is transformed in a datetime.datetime object
        date = HTTP_dict['date']
        # the used of a delta is necessary to get real utc time because '%z' doesn't work in python<3.2!
        delta = datetime.timedelta(hours=int(date[-5:]) / 100)
        HTTP_dict['date'] = datetime.datetime.strptime(date[:-6], '%d/%b/%Y:%X') - delta
    except:
        raise HTTPFormatError('incorrect HTTP format in line: {}'.format(line))

    return HTTP_dict


def get_section(request):
    """Return the section name from a GET request, or None if not a proper GET request"""
    section = re.match(r'^\S*\s*(/[^/ ]*)', request.strip())
    if section is not None:
        return section.group(1)
    return None


if __name__ == '__main__':

    def simulate_putter_and_getter(with_getter=True):
        q = Queue()
        pace10 = 30  # ie pace = 10*pace10

        putter = QueueWriter(q, pace10=pace10)  # pace10=1000 -> 10,000 put/sec
        putter.start()

        if with_getter:
            m = Monitor(q)
            m.start()

        time.sleep(10)
        putter.should_run = False

        if with_getter:
            m.should_run = False

    simulate_putter_and_getter(with_getter=True)


