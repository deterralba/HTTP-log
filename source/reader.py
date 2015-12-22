#!/usr/bin/env python
# coding: utf8

from __future__ import (unicode_literals, absolute_import, division, print_function)

from threading import Thread
from Queue import Queue

import display as d

import io
import re
import sys

import datetime
import time


class HTTPFormatError(Exception):
    """Raised when the HTTP access log line is not recognized"""
    pass


class LogReader(Thread):
    """
    This thread object is read the log file, and by default parses its lines. Then it sends them in a queue that is
    read by the Statistician.

    Attributes
    ----------
    log_path: string
    sleeping_time: float
    parse: bool
    total_nb_of_line_read: int
    should_run: bool
        If False, the thread will shortly end stop its operation. Used to cleanly end the program.
    output_queue: Queue
    name: string
    """

    def __init__(self, log_path, sleeping_time=0.1, parse=True):
        Thread.__init__(self)

        self.log_path = log_path
        self.sleeping_time = sleeping_time
        self.parse = parse

        self.total_nb_of_line_read = 0
        self.should_run = True
        self.output_queue = Queue()
        self.name = 'log reader thread'

    def run(self):
        """
        Opens the input log file at ``log_path``, goes to the EOF, then try to read new lines. If new lines are detected,
        sends them to the ``output_queue`` for the ``Statistician`` (parsed or not parsed depending of the parameter).

        When EOF, waits for ``sleeping_time`` and starts again.

        Warnings
        --------
        Code should be more commented here!
        """
        try:
            log_file = io.open(self.log_path, 'rt')
        except IOError:
            d.displayer.log(self, d.LogLevel.CRITICAL, "wrong path for the input log '{}'".format(self.log_path))
            from thread import interrupt_main
            interrupt_main()
            sys.exit()

        log_file.seek(0, io.SEEK_END)
        d.displayer.log(self, d.LogLevel.DEBUG, "At EOF, ready for reading")

        # print sys 2
        last_printed_time = time.time()
        since_last_printed = 0

        last_EOF = 0
        last_EOF_time = time.time()
        EOF_reached_printed = True  # because we start at EOF
        fist_reading_loop = True

        while self.should_run:
            EOF = False
            while not EOF:

                line = log_file.readline()
                if not line:
                    # print("EOF in line", i + 1)
                    EOF = True
                    # sys1 EOF info
                    last_EOF = 0
                    last_EOF_time = time.time()
                else:
                    self.total_nb_of_line_read += 1
                    EOF_reached_printed = False

                    # sys1 EOF info
                    last_EOF += 1
                    if last_EOF % 5000 == 0:
                        if time.time() - last_EOF_time > 1:
                            d.displayer.log(self, d.LogLevel.WARNING,
                                            'last EOF {} lines ago, {:.02f}s ago'
                                            ''.format(last_EOF, time.time() - last_EOF_time))

                    # sys2 EOF info
                    since_last_printed += 1
                    if since_last_printed % 100 == 0:
                        delta = time.time() - last_printed_time
                        if delta > 1:
                            d.displayer.log(self, d.LogLevel.DEBUG,
                                            '{}   lines parsed last {}s'.format(since_last_printed, delta))

                            last_printed_time = time.time()
                            since_last_printed = 0

                    line = line.strip()
                    if not line.startswith('#') and len(line) > 0:
                        if self.parse:
                            try:
                                self.output_queue.put(parse_line(line))
                            except HTTPFormatError as e:
                                d.displayer.log(self, d.LogLevel.ERROR, e.message)
                        else:
                            self.output_queue.put(line)

                            # print('read:', line)

            if not EOF_reached_printed:
                d.displayer.log(self, d.LogLevel.INFO, 'Log EOF reached after {} lines'
                                                       ''.format(self.total_nb_of_line_read))
                EOF_reached_printed = True
            # print(time.time() - t)
            # print('qsize', self.output_queue.qsize())

            if not fist_reading_loop:
                # d.displayer.log(self, d.LogLevel.DEBUG, 'Sleep for {}s'.format(self.sleeping_time))
                time.sleep(self.sleeping_time)

            fist_reading_loop = False

        log_file.close()

    def state(self):
        """
        Returns
        -------
        string
            Describes the present thread state

        """
        return 'total nb of read line: {}' \
               ''.format(self.total_nb_of_line_read)


def parse_line(line, parse_date=False):
    """Parse a HTTP w3c formatted line and return a dictionary with the following keys:
    ``'remote_host', 'remote_log_name', 'auth_user', 'date', 'request', 'status', 'bytes'``

    Note
    ----

    * ``status`` and ``bytes`` are converted to ``int``
    * ``date`` can be converted in a datetime object, UTC-time, but by default the conversion is disable (it is slow)

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

        if parse_date:
            # the date is transformed in a datetime.datetime object
            date = HTTP_dict['date']
            # the used of a delta is necessary to get real utc time because '%z' doesn't work in python<3.2!
            delta = datetime.timedelta(hours=int(date[-5:]) / 100)
            HTTP_dict['date'] = datetime.datetime.strptime(date[:-6], '%d/%b/%Y:%X') - delta
    except:
        raise HTTPFormatError('incorrect HTTP format in line: {}'.format(line))

    return HTTP_dict


def get_section(request):
    """
    Return the section name from a HTTP request, or None if not a proper HTTP request

    Examples
    --------

    * ``GET /test/index/ HTTP``   =>   ``/test``
    * ``GET /te.st/index/ HTTP``   =>   ``/te.st``
    * ``GET /test/index.html HTTP``   =>   ``/test``
    * ``GET /test HTTP``   =>   ``/testv
    * ``GET /test.html HTTP``   =>   ``/``
    * ``GET / HTTP``   =>   ``/``

    """
    # section = re.match(r'^\S+\s+(/[^/ ]*)', request.strip())
    section = re.match(r'^\S+\s+(/[^ /]*)', request.strip())
    if section is not None:
        if '.' in section.group(1) and request.count('/') == 1:
            return '/'
        return section.group(1)
    return None


if __name__ == '__main__':
    f
    # ===== HTTP access log line parser =====
    print(parse_line('127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326'))
    print(get_section("GET /section123/image.png HTTP/1.1"))

    # ===== get_section() tests =====
    string_="GET /test/index/ HTTP"; print(string_, "  =>  ", get_section(string_))
    string_="GET /te.st/index/ HTTP"; print(string_, "  =>  ", get_section(string_))
    string_="GET /test/index.html HTTP"; print(string_, "  =>  ", get_section(string_))
    string_="GET /test HTTP"; print(string_, "  =>  ", get_section(string_))
    string_="GET /test.html HTTP"; print(string_, "  =>  ", get_section(string_))
    string_="GET / HTTP"; print(string_, "  =>  ", get_section(string_))


    # might be useful to know the encoding
    # ====================================
    import locale
    print('encoding', locale.getpreferredencoding())


    # date correction process : %z doesn't work in python<3.2
    # =======================================================
    date = '10/Oct/2000:13:55:36 -0700'
    delta = datetime.timedelta(hours=int(date[-5:]) / 100)
    dt = datetime.datetime.strptime(date[:-6], '%d/%b/%Y:%X') - delta
    print('date: ', dt)

    # test the LogReader
    # ==================
    picasso = d.Displayer(debug=True)
    time.sleep(0.1)
    rth = LogReader('../log/simulated_log')
    rth.start()
    time.sleep(1)
    rth.should_run = False
