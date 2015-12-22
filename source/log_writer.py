#!/usr/bin/env python
# coding: utf8

from __future__ import (unicode_literals, absolute_import, division, print_function)

from threading import Thread
from random import randint

import display as d

import datetime
import time

import io
import os
import sys


class LogSimulatorConfigFileError(Exception):
    """Raised when the path or the format of the config file is incorrect"""
    pass


class LogSimulator(Thread):
    """
    Simulates a real actively writen HTTP access log: writes lines in a given log file
    at given speeds during given times. All theses parameters are read in a given config file.

    Note
    ----
    See ``data/sim_config`` to understand how a config file should be written.

    Attributes
    ----------
    config_path: string
        The path to the config file where the parameters and the command for the simulation are stored.

    log_w: LogWriter
        A reference to the present LogWriter


    """

    def __init__(self, config_path):
        Thread.__init__(self)
        self.config_path = config_path

        self.total_nb_of_lines_previously_written = 0
        self.log_w = None
        self.name = 'log simulator thread'
        self.param_dict = None
        self.should_run = True

    def get_parameters(self):
        """
        Reads the config file and extracts the parameters i.e. the lines with '='.
        Sets ``LogSimulator.param_dict``.

        Returns
        -------
        dictionary
            A dictionary with the parameters as key

        """
        # the list of the parameters that can be recognized in the config file
        acceptable_parameters = ['line_type', 'log_path', 'erase_first']

        try:
            config_file = io.open(self.config_path)
        except (IOError, ValueError):
            print("LogSimulator: CRITICAL: Impossible to open '{}', is the given path correct ?".format(self.config_path))
            from thread import interrupt_main
            interrupt_main()
            sys.exit()

        # this is the dict used to store the arguments of LogWriter()
        # 'erase_first': the first loop must create a clean the log_file (ie erase and recreate it)
        self.param_dict = {'erase_first': True, 'log_path': '../log/simulated_log', 'line_type': 'HTTP_fast'}

        # the config file is read a first time to obtain the arguments and store them in param_dict
        for line in config_file:
            if not line.strip().startswith('#') and len(line.strip()) > 0:  # comment or empty line
                # a line with '=' should be a parameter line, defining an acceptable_parameters (see the list)
                if "=" in line:
                    key, value = (word.strip() for word in line.split('='))
                    if key in acceptable_parameters:
                        self.param_dict[key] = value
                    else:
                        print("Error while reading the config file at line '{}', unrecognised parameter '{}'"
                              "".format(line, key))
                        from thread import interrupt_main
                        interrupt_main()
                        sys.exit()

        config_file.close()
        # print(self.param_dict)
        return self.param_dict

    def run(self):
        """
        Reads the config file given, and executes the commands read with the read parameters.
        """

        if self.param_dict is None:
            self.get_parameters()

        try:
            config_file = io.open(self.config_path)
        except (IOError, ValueError):
            print("LogSimulator: CRITICAL: Impossible to open '{}', is the given path correct ?".format(self.config_path))
            from thread import interrupt_main
            interrupt_main()
            sys.exit()

        # the config file is read a first time to obtain the arguments and store them in param_dict
        for line in config_file:
            if self.should_run and not line.strip().startswith('#') and len(line.strip()) > 0:
                # a line without '=' should be a command line 'pace, timeout', calling a LogWriter
                if "=" not in line:
                    try:
                        self.param_dict['pace'], self.param_dict['timeout'] = [int(i) for i in line.split(',')]
                    except ValueError:
                        d.displayer.log(self, d.LogLevel.ERROR,
                                        "Error while reading the config file at line '{}'".format(line))
                        continue

                    # print(param_dict)
                    self.param_dict['is_simulated'] = self
                    self.log_w = LogWriter(**self.param_dict)
                    self.log_w.start()
                    while self.log_w.is_alive():
                        self.log_w.join(0.01)

                    # log_file shouldn't be erased again after the first loop
                    if self.param_dict['erase_first']:  # only True in the first loop
                        self.param_dict['erase_first'] = False

            if not self.should_run:
                break

        config_file.close()

    def state(self):
        """
        Returns
        -------
        string
            Describes the present thread state

        """
        total_number = self.total_nb_of_lines_previously_written
        if self.log_w.is_alive():
            total_number += self.log_w.nb_of_line_written
        return 'Total number of line written: {}'.format(total_number)

    def started_first_writing(self):
        """
        Returns
        -------
        bool
            True if the LogWriter has started to write, else False

        """
        if self.log_w is not None:
            return self.log_w.started_writing
        else:
            return False


class LogWriter(Thread):
    """Writes a given type of lines in the file given by the log_path at a given speed during a given time.

    Warnings
    --------
    The time is the priority, hence of the I/O cannot follow the writing speed asked, the program will not write as many
    lines as asked, but it will end in time. A WARNING log message will be send.


    Attributes
    ----------
    log_path: string
        The path to the log file, may already exist and will be erased or may not exist and will be create
        (see :attr:`erase_first`)

    line_type: string
        The type of line that that should be writen in the log, can be:

            * ``'line'``: ``lineX`` will be writen, where ``X`` is the number of the line writen (fastest)
            * ``'HTTP_fast'``: an HTTP access line will be writen,
              but only the HTTP request and the bytes will be random (slower)
            * ``'HTTP_slow'``: an HTTP access line will be writen, everything will be random (slowest)

    pace: int
        The number of line that should be writen every second. If the IO stream cannot follow the pace, a log message is
        send to the Displayer.

    timeout: int
        The number of seconds meanwhile the log should be writen, never stop if ``timeout == -1``,
        minimum timeout is 1.

    erase_first: bool
        If True, the log_path is erased before being writen (log file is opened in ``'at'`` mode).

    should_run: bool
        Used to get out of the writing ``while`` loop when the user want to stop the program.

    is_simulated: LogSimulator or None
        A reference to the LogSimulator if this is a simulation, or None. Used to update LogSimulator.total_number...

    nb_of_line_written: int
        The number of line written by the LogWriter. Only update every 100 lines !

    started_writing: bool
        Becomes True after the first flush() ie after a first line has been written.
        NB: Could be deduced from nb_of_line_written...


    """

    def __init__(self, log_path, line_type='HTTP_slow', pace=3000, timeout=-1, erase_first=True, is_simulated=False):
        Thread.__init__(self)

        self.log_path = log_path
        self.line_type = line_type
        self.pace = pace
        self.timeout = timeout
        self.erase_first = erase_first
        self.is_simulated = is_simulated

        self.nb_of_line_written = 0
        self.should_run = True
        self.name = 'log writer thread'
        self.started_writing = False

    def run(self):
        """
        Open the output log file and writes log lines in it ``n = pace`` every second, as long as execution time < timeout

        Called when the thread is started.
        """
        line_count = 0
        start_time = time.time()

        if self.erase_first:
            try:
                os.remove(self.log_path)
                d.displayer.log(self, d.LogLevel.DEBUG, 'Input log file found and erased')
            except OSError:
                d.displayer.log(self, d.LogLevel.DEBUG, 'Input log file file not found, will be created')

        try:
            log_file = io.open(self.log_path, 'at')
        except IOError:
            d.displayer.log(self, d.LogLevel.CRITICAL, "impossible to write on '{}'".format(self.log_path))
            from thread import interrupt_main
            interrupt_main()
            sys.exit()

        # the function that will generate the lines is bound once for all (optimisation)
        random_line = random_log_line_maker(self.line_type)

        # the expression used in the first while is defined once for all (optimisation)
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

            # this is executed at most once every second
            while self.should_run and line_count_second < self.pace and time.time() - start_time_second < 1:
                log_file.write(random_line(date=date, line_count=line_count) + '\n')
                line_count += 1
                line_count_second += 1
                if line_count % 100 == 0:
                    # the date update and the flush() processes are not updated every line, it slows down the process
                    # the are launch every 100 lines
                    log_file.flush()
                    self.started_writing = True
                    self.nb_of_line_written = line_count
                    date = datetime.datetime.utcnow().strftime('[%d/%b/%Y:%X +0000]')

                # time.sleep(1.0/self.pace) : this could have been a solution for the writing but sleep is not precise enough...

            log_file.flush()  # line_count % 100 != 0, they are still 'unflush' log lines
            self.nb_of_line_written = line_count
            d.displayer.log(self, d.LogLevel.INFO, '{} lines written so far'.format(self.nb_of_line_written))

            delta = time.time() - start_time_second
            # print('delta :', delta)
            if delta < 1 and line_count_second == self.pace:
                # print('waiting for :', 1 - delta)
                time.sleep(1 - delta)  # this could be changed : slows the exit process. See the Displayer method
            else:
                d.displayer.log(self, d.LogLevel.INFO,
                                'Writing operations are too slow, change line_type or reduce pace, '
                                'lines writen this second: {}'.format(line_count_second))

        d.displayer.log(self, d.LogLevel.DEBUG,
                        'End writting after {} lines in {:.4f}s'.format(line_count, time.time() - start_time))

        # the total number of lines written is updated in the LogSimulator, if this is a simulation (not pretty)
        if self.is_simulated:
            self.is_simulated.total_nb_of_lines_previously_written += self.nb_of_line_written

        log_file.close()
        time.sleep(0.005)  # little pause to avoid IOError when reopening the file just after closing it (on Windows)


def generate_all_URL_possible(factor=2, max_depth=2):
    """
    Generates a list of all the possible local URL with the given parameters

    Note
    ----

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
    * ``/archive2/archive0/archive2/archive2/picture.png``    <- max_depth = 4, with URL_end

    """
    section = ['page', 'blog', 'archive']
    URL_beggining = [word + str(i) for word in section for i in xrange(1, factor+1)]  # add an integer at the end of the section
    URL_end = ['picture.png', 'index.html']  # 'form.php', 'script.js', 'style.css',

    if max_depth >= 1:
        l = ['/' + sect + '/' for sect in URL_beggining]
        for i in xrange(1, max_depth):
            l.extend([base + sect + '/' for base in l for sect in URL_beggining])
    l.append('/')

    l.extend([word + end for word in l for end in URL_end])
    # print(l)
    return l


def uniform_random_local_URL_maker(factor=2, max_depth=2):
    """
    Returns a ``uniform_random_local_URL`` function that returns equi-probable local URL,
    this is useful (I assure you) to avoid getting always the same most hit section in a simulation.


    Note
    ----

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
    * ``/archive2/archive0/archive2/archive2/picture.png``    <- max_depth = 4, with URL_end

    """
    l = generate_all_URL_possible(factor, max_depth)
    length_l = len(l)
    # print(length_l)

    def uniform_random_local_URL():
        return l[randint(0, length_l-1)]
    return uniform_random_local_URL


def random_HTTP_request(URL):
    """
    Args
    ----
    URL: string
        The URL that will be written in the HTTP request


    Returns
    -------
    string
        A random W3C valid HTTP request


    Examples
    --------

    * ``"HEAD /index.html HTTP/1.1"``
    * ``"GET /page0/ HTTP/1.1"``
    * ``"DELETE /archive0/blog1/ HTTP/1.1"``

    """
    method = ['HEAD', 'GET', 'OPTIONS', 'TRACE', 'POST', 'PUT', 'DELETE', 'PATCH', 'CONNECT'][randint(0, 8)]
    return '"{} {} {}"'.format(method, URL, 'HTTP/1.1')


def random_log_line_maker(line_type, **kwargs):
    """
    Returns
    -------
    function:
        The right log line writer function


    Args
    ----
    line_type: string
        The type of line that should be generated, can be

        * ``line``: the string returned will be ``lineX\\n`` where X is ``line_count`` given in keyword argument
        * ``HTTP_fast``: the string returned will be a static HTTP access log line with random HTTP request
                         and a accurate date, and random bytes
        * ``HTTP_slow``: the string returned will be a fully random HTTP access line


    Keyword Args
    ------------
    factor: int
        Parameters used in the uniform_random_local_URL_maker() function

    max_depth: int
        Parameters used in the uniform_random_local_URL_maker() function
    """
    if line_type == 'HTTP_fast':
        request_param = {'factor': 4, 'max_depth': 2}
        request_param.update(kwargs)
        random_URL = uniform_random_local_URL_maker(**request_param)

        def fast_rand(date=0, line_count=0):
            remote_host = '123.12.45.78'
            remote_log_name = '-'
            auth_user = '-'
            request = random_HTTP_request(random_URL())
            status = '200'
            bytes_ = str(randint(0, 1e3))
            return " ".join([remote_host, remote_log_name, auth_user, date, request, status, bytes_])

        return fast_rand

    elif line_type == 'HTTP_slow':
        request_param = {'factor': 4, 'max_depth': 4}
        request_param.update(kwargs)
        random_URL = uniform_random_local_URL_maker(**request_param)

        def slow_rand(date=0, line_count=0):
            remote_host = ".".join([str(randint(0, 255)) for i in xrange(4)])
            remote_log_name = '-'
            auth_user = '-'
            request = random_HTTP_request(random_URL())
            status = str(100 * randint(1, 5) + randint(0, 5))
            bytes_ = str(randint(0, 1e4))
            return " ".join([remote_host, remote_log_name, auth_user, date, request, status, bytes_])

        return slow_rand

    elif line_type == 'line':

        def line_rand(date=0, line_count=0):
            return 'line' + str(line_count)  # PEP8 says 'do not assign lambda expressions'...
            # faster than ''.join(['line', str(line_count)])

        return line_rand

    else:
        raise ValueError('line_type={} is an incorrect parameter'.format(line_type))


if __name__ == '__main__':

    def benchmark_LogWriter(pace_list=(5000, 10000, 25000),
                            line_type_list=('line', 'HTTP_fast', 'HTTP_slow'),
                            timeout=1):
        """Benchmark a LogWriter, useful to know the maximum writing speed"""
        log_path = '../log/simulated_log'
        pace_line_type = [(pace, line_type) for pace in pace_list for line_type in line_type_list]
        for pace, line_type in pace_line_type:
            print("="*30)
            print("Benchmark of LogWriter with\n\tPace: {}, Line Type: {}".format(pace, line_type))
            lw = LogWriter(log_path, line_type=line_type, timeout=timeout, pace=pace)
            lw.start()
            lw.join()

    # benchmark_LogWriter(pace_list=[1e9])


    def simulate_writer_and_reader(with_reader=True, reader_parse=False):
        """Simulate a LogWriter and a LogReader, useful to know the maximum writing and reading speeds"""
        import reader
        import display as d
        log_path = '../log/simulated_log'
        config_path = '../data/short_sim'

        print('Simulation started')

        picasso = d.Displayer(debug=True)  # needed for d.displayer.log()
        ls = LogSimulator(config_path)

        ls.start()
        time.sleep(0.01)  # pause to let the LogWriter write
        if with_reader:
            rd = reader.LogReader(log_path, parse=reader_parse)
            rd.start()

        ls.join()
        time.sleep(1)
        if with_reader:
            rd.should_run = False
        print('Simulation ended.')

    simulate_writer_and_reader(with_reader=True, reader_parse=True)


    # ===== Performance tests =====
    import timeit
    print(timeit.timeit("''.join(['line', str(1234)])", number=1000))
    print(timeit.timeit("'line' + str(1234)", number=1000))

    # ===== HTTP access log line generation =====
    local_URL = uniform_random_local_URL_maker()
    [print(local_URL()) for i in xrange(5)]
    [print(random_HTTP_request(local_URL())) for i in xrange(5)]
    [print(random_log_line_maker(i)(date=str(datetime.datetime.utcnow().strftime('[%d/%b/%Y:%X +0000]')),
                                    line_count=j))
        for i in ['line', 'HTTP_fast', 'HTTP_slow']
        for j in xrange(5)]

    # ===== URL maker test tests =====
    print('Total number of URLs', len(generate_all_URL_possible(factor=2, max_depth=2)))
    uniform_random_local_URL = uniform_random_local_URL_maker(factor=1, max_depth=1)
    [print(uniform_random_local_URL()) for i in xrange(50)]

