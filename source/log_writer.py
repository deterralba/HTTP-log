#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)

from threading import Thread
from random import randint

import datetime
import time

import io
import os


class LogSimulatorConfigFileError(Exception):
    """Raised when the path or the format of the config file is incorrect"""
    pass


class LogSimulator(Thread):
    """Simulates a real actively writen HTTP access log: writes lines in a given log file
    at given speeds during given times. All theses parameters are read in a given config file.

    Attributes
    ----------
    config_path: string
        The path to the config file where the parameters and the command for the simulation are stored.
    """

    def __init__(self, config_path):
        Thread.__init__(self)
        self.config_path = config_path

    def run(self):
        """Reads the config file given, and executes the commands read with the read parameters

        Raises
        ------
        LogSimulatorConfigFileError: when the config file path is incorrect or the command or parameters not recognized
        """
        try:
            config_file = io.open(self.config_path)
        except Exception:
            raise LogSimulatorConfigFileError("Error while opening the config file '{}' for the LogSimulator, "
                                              "is the given path correct ?".format(self.config_path))

        # this is the dict used to store the arguments of LogWriter()
        param_dict = {'erase_first': True}  # the first loop must create a clean the log_file (ie erase and recreate it)

        # the config file is read a first time to obtain the arguments and store them in param_dict
        for line in config_file:
            if not line.strip().startswith('#'):  # commented lines are ignored

                # a line with '=' should be a parameter line, defining either 'log_path' or 'line_type'
                if "=" in line:
                    key, value = (word.strip() for word in line.split('='))
                    if key in ['log_path', 'line_type']:
                        param_dict[key] = value
                    else:
                        raise LogSimulatorConfigFileError(
                            "Error while reading the config file at line '{}'".format(line))

                # a line without '=' should be a command line 'pace, timeout', calling a LogWriter
                else:
                    try:
                        param_dict['pace'], param_dict['timeout'] = [int(i) for i in line.split(',')]
                    except Exception:
                        raise LogSimulatorConfigFileError(
                            "Error while reading the config file at line '{}'".format(line))

                    print(param_dict)
                    log_w = LogWriter(**param_dict)
                    log_w.start()
                    log_w.join()

                    # log_file shouldn't be erased again after the first loop
                    if param_dict['erase_first']:  # only True in the first loop
                        param_dict['erase_first'] = False
        config_file.close()


class LogWriter(Thread):
    """Writes a given type of lines in the file given by the log_path at a given speed during a given time.

    Warnings
    --------
    The number of lines is the priority, hence of the I/O cannot follow the pace, the program will just take more time
    ==========================TODO===================================
    change that behavior and that doc !!
    ==========================TODO===================================


    Attributes
    ----------
    log_path: string
        The path to the log file, may already exist and will be erased or may not exist and will be create
        (see :attr:`erase_first`)

    line_type: string
        The type of line that that should be writen in the log, can be:

            * ``'line'``: ``lineX`` will be writen, where ``X`` is the number of the line writen (fastest)
            * ``'HTTP_fast'``: an HTTP access line will be writen, but only the HTTP request will be random (slower)
            * ``'HTTP_slow'``: an HTTP access line will be writen, everything will be random (slowest)

    pace: int
        The number of line that should be writen every second, can go up to 25 000. If the IO stream cannot follow
        the pace, a message is written in the console.
        ==========================TODO===================================
        change the precedent behavior : do not write msg in the console
        ==========================TODO===================================

    timeout: int
        The number of seconds meanwhile the log should be writen, never stop if ``timeout == -1``, minimum timeout is 1.

    erase_first: bool
        If True, the log_path is erased before being writen (log file is opened in ``'at'`` mode)

    should_run: bool
        Used to get out of the infinite while loop when the user want to stop the program

    """

    def __init__(self, log_path, line_type='HTTP_slow', pace=3000, timeout=-1, erase_first=True):
        Thread.__init__(self)

        self.log_path = log_path
        self.line_type = line_type
        self.pace = pace
        self.timeout = timeout
        self.erase_first = erase_first

        self.should_run = True

    def run(self):
        """
        ==========================TODO===================================
        commment the run fct
        ==========================TODO===================================
        """
        line_count = 0
        start_time = time.time()
        if self.erase_first:
            try:
                os.remove(self.log_path)
                print("Log file found and erased")
            except Exception:
                print("Log file not found, will be created")
        log_file = io.open(self.log_path, 'at')

        # the function that will generate the lines is bound once for all
        random_line = random_log_line_maker(self.line_type)

        # the expression used in the first while is defined once for all
        if self.timeout == -1:
            def timeout_check():
                return True
        else:
            def timeout_check():
                return time.time() - start_time < self.timeout

        while self.should_run and timeout_check():
            line_count_second = 0
            start_time_second = time.time()
            date = datetime.datetime.utcnow().strftime('[%d/%b/%Y:%X +0000]')
            # print('start :', start_time_second)
            while self.should_run and line_count_second < self.pace and time.time() - start_time_second < 1:
                log_file.write(random_line(date=date, line_count=line_count) + '\n')
                line_count += 1
                line_count_second += 1
                if line_count % 1000 == 0:
                    log_file.flush()
                    date = datetime.datetime.utcnow().strftime('[%d/%b/%Y:%X +0000]')
                    # print("reset date at", line_count)
                # print('written line', line_count-1)
                # time.sleep(1.0/self.pace)
            log_file.flush()
            delta = time.time() - start_time_second
            # print('delta :', delta)
            if delta < 1 and line_count_second == self.pace:  # check that line !!
                print('waiting for :', 1 - delta)
                time.sleep(1 - delta)
            else:
                print('writing operations are too slow, change line_type or reduce pace, '
                      'lines writen this second:', line_count_second)
            # print('end :', time.time(), 'line_count :', line_count, '\n==========')

        print('LogWriter end after {} lines in {:.4f}s'.format(line_count, time.time() - start_time))
        log_file.close()
        time.sleep(0.005)  # little pause to avoid IOError when reopening the file just after closing it (on Windows)


def random_local_URL(factor=3, max_depth=4):
    """
    Returns
    -------
    string
        A random local URL

    Notes
    -----
    ``number of section = len(section) * factor``

    ``max_depth`` is the highest number possible of /section/subsection/subsubsection/etc.
    ``/archive2/blog0/archive2/page1/ -> depth = 4``

    Examples
    --------
    * ``/``              <- min_depth without URL_end
    * ``/index.html``    <- min_depth with URL_end
    * ``/page0/``
    * ``/archive0/blog1/``
    * ``/blog0/picture.png``
    * ``/page0/archive1/archive2/index.html``
    * ``/archive2/archive0/archive2/archive2/form.php``    <- max_depth = 4, with URL_end
     """
    # print(factor, max_depth)
    section = ['page', 'blog', 'archive']
    URL_begging = [word + str(i) for i in xrange(factor) for word in
                   section]  # add an integer at the end of the section
    URL_end = ['picture.png', 'index.html', 'form.php']
    return '/' + '/'.join([URL_begging[randint(0, len(URL_begging) - 1)] for i in xrange(randint(0, max_depth))] +
                          [URL_end[randint(0, len(URL_end) - 1)] * (randint(0, 4) >= 1)])


def random_HTTP_request(**kwargs):
    """
    Returns
    -------
    string
        A random HTTP request, the local URL is given by :func:`random_local_URL`

    Examples
    --------
    * ``"HEAD /index.html HTTP/1.1"``
    * ``"GET /page0/ HTTP/1.1"``
    * ``"DELETE /archive0/blog1 HTTP/1.1"``
    """
    method = ['HEAD', 'GET', 'OPTIONS', 'TRACE', 'POST', 'PUT', 'DELETE', 'PATCH', 'CONNECT'][randint(0, 8)]
    return '"{} {} {}"'.format(method, random_local_URL(**kwargs), 'HTTP/1.1')


def random_log_line_maker(line_type, **kwargs):
    """Returns the right line writer function, depending of the parameters

    Argument
    --------
    line_type: string
        The type of line that should be generated, can be

        * ``line``: the string returned will be ``lineX\n`` where X is ``line_count`` given in keyword argument
        * ``HTTP_fast``: the string returned will be a static HTTP access log line with random HTTP request
                         and a accurate date
        * ``HTTP_slow``: the string returned will be a fully random HTTP access line
    """
    if line_type == 'HTTP_fast':
        # print("generating fast")
        request_param = {'factor': 4, 'max_depth': 2}
        request_param.update(kwargs)

        def fast_rand(date=0, line_count=0):
            remote_host = '123.12.45.78'
            remote_log_name = '-'
            auth_user = '-'
            request = random_HTTP_request(**request_param)
            status = '100'
            bytes_ = '1500'
            return " ".join([remote_host, remote_log_name, auth_user, date, request, status, bytes_])

        return fast_rand

    elif line_type == 'HTTP_slow':
        # print("generating slow")
        request_param = {'factor': 4, 'max_depth': 4}
        request_param.update(kwargs)

        def slow_rand(date=0, line_count=0):
            remote_host = ".".join([str(randint(0, 255)) for i in xrange(4)])
            remote_log_name = '-'
            auth_user = '-'
            request = random_HTTP_request(**request_param)
            status = str(100 * randint(1, 5) + randint(0, 5))
            bytes_ = str(randint(0, 10e4))
            return " ".join([remote_host, remote_log_name, auth_user, date, request, status, bytes_])

        return slow_rand

    elif line_type == 'line':
        # print("generating line")

        def line_rand(date=0, line_count=0):
            return 'line' + str(line_count)  # PEP8 says 'do not assign lambda expressions'...
            # faster than ''.join(['line', str(line_count)])

        return line_rand

    else:
        raise ValueError('line_type={} is an incorrect parameter'.format(line_type))


if __name__ == '__main__':

    def benchmark_LogWriter(pace_list=(5000, 10000, 25000), line_type_list=('line', 'HTTP_fast', 'HTTP_slow'), timeout=1):
        log_path = '../data/wtest'
        pace_line_type = [(pace, line_type) for pace in pace_list for line_type in line_type_list]
        for pace, line_type in pace_line_type:
            print("="*30)
            print("Benchmark of LogWriter with\n\tPace: {}, Line Type: {}".format(pace, line_type))
            lw = LogWriter(log_path, line_type=line_type, timeout=timeout, pace=pace)
            lw.start()
            lw.join()

    # benchmark_LogWriter(pace_list=[10e9])


    def simulate_writer_and_reader(with_reader=True):
        import reader
        log_path = '../data/wtest'
        config_path = '../data/sim_config'
        ls = LogSimulator(config_path)
        ls.start()
        time.sleep(0.01)  # pause to let the LogWriter write
        if with_reader:
            rd = reader.LogReader(log_path)
            rd.start()

        ls.join()
        time.sleep(1)
        if with_reader:
            rd.should_run = False

    simulate_writer_and_reader(with_reader=True)


    # ===== Performance tests =====
    # import timeit
    # print(timeit.timeit("''.join(['line', str(1234)])", number=1000))
    # print(timeit.timeit("'line' + str(1234)", number=1000))

    # ===== HTTP access log line generation =====
    # [print(random_local_URL()) for i in xrange(5)]
    # [print(random_HTTP_request()) for i in xrange(5)]
    # [print(random_log_line_maker(i)(date=str(datetime.datetime.utcnow().strftime('[%d/%b/%Y:%X +0000]')), line_count=j))
    #     for i in ['line', 'HTTP_fast', 'HTTP_slow']
    #     for j in xrange(5)]

