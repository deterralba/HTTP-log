#!/usr/bin/env python
# coding: utf8

from __future__ import (unicode_literals, absolute_import, division, print_function)

from threading import Thread, Lock
from operator import itemgetter

from Queue import Queue, Empty
import datetime
import re
import time

import display as d
import log_writer
import reader


class AlertParam:
    """
    Stores the parameters used in the alert detection process.

    ``short_median`` and ``long_median`` are the size of the windows for the moving averages.

    An alert will be raised if ``short_outflow_average > long_outflow_average * threshold``.

    Warnings
    --------
    The unit base of ``short_median`` and ``long_median`` is ``time_resolution``, that means that
    ``long_median=2`` with ``time_resolution=10`` will calculate an outflow average on the last ``2 * 10 = 20`` seconds.
    """
    def __init__(self, short_median=12, long_median=120, threshold=1.5, time_resolution=10):
        self.short_median = int(short_median)
        self.long_median = int(long_median)
        self.threshold = float(threshold)
        self.time_resolution = time_resolution

        if self.short_median >= self.long_median:
            raise ValueError('short_median must be smaller than long_median')
        if self.threshold <= 1.0:
            raise ValueError('threshold must be bigger than 1')


class Statistics:
    """ Object used by the statistician as its "notebook". This is were the stats are saved.

    It calls the Displayer if an alert should be raised or shut down.
    It is called when the stats should be printed.


    Attributes
    ----------
    section: dictionary
    number_of_hits: int
    total_bytes: int
    total_hits: int

    should_run: bool
        If False, the thread will shortly end stop its operation. Used to cleanly end the program.

    long_term_bytes_buffer: int
    long_term_bytes: list of int
    alert_raised: bool

    Note
    ----
    The use of ``statistics.lock`` makes this object thread-safe.

    Warnings
    --------
    ``number_of_hits``, ``total_bytes`` and ``total_hits`` are used for the printed stats,
    'total' is in fact 'total since the last display'.


    """
    def __init__(self):
        self.lock = Lock()

        # used for the printed stats
        # 'total' is in fact 'total since the last display'
        self.section = {}
        self.total_bytes = 0
        self.total_hits = 0

        # used for the alerts
        self.long_term_bytes_buffer = 0
        self.long_term_bytes = []
        self.alert_raised = False

    def upadate_stat(self, HTTP_dict):
        """Update the stats with the given parse line (ie the HTTP_dict)"""
        with self.lock:
            last_section = reader.get_section(HTTP_dict['request'])
            # print(HTTP_dict['request'], last_section)
            if last_section is not None:
                if last_section in self.section:
                    self.section[last_section] += 1
                else:
                    self.section[last_section] = 1
            else:
                d.displayer.log(self, d.LogLevel, "Wrong HTTP request '{}': section not found"
                                                  "".format(HTTP_dict['request']))

            self.total_bytes += HTTP_dict['bytes']
            self.total_hits += 1
            self.long_term_bytes_buffer += HTTP_dict['bytes']

    def get_last_stats(self):
        """Returns a stats dict, used for the regular stats printing"""
        stats = dict.fromkeys(('max_section', 'max_hit', 'total_bytes', 'total_hits'), 0)

        with self.lock:
            stats['total_bytes'] = self.total_bytes
            stats['total_hits'] = self.total_hits
            try:
                stats['max_section'], stats['max_hit'] = max(self.section.iteritems(), key=itemgetter(1))
                return stats
            except ValueError:
                return stats

    def reset_short_stat(self):
        """Called by the displayer after get_last_stats to reset the 'printing stats'"""
        with self.lock:
            self.section.clear()
            self.total_bytes = 0
            self.total_hits = 0

    def update_long_term(self, alert_param):
        """
        Update the ``long_term_bytes`` list.
        Checks if an alert should be raised (or shut down), and raises it if necessary.

        Called by the Statistician every AlertParam.time_resolution.
        """
        with self.lock:
            self.long_term_bytes.append(self.long_term_bytes_buffer)
            self.long_term_bytes_buffer = 0

        if len(self.long_term_bytes) > alert_param.long_median + alert_param.short_median:
            del self.long_term_bytes[0]

            emergency = self.emergency(alert_param)

            if emergency['alert']:
                del emergency['alert']
                if not self.alert_raised:
                    self.alert_raised = True
                    d.displayer.print_new_alert(**emergency)
            else:
                del emergency['alert']
                if self.alert_raised:
                    self.alert_raised = False
                    d.displayer.print_end_alert(**emergency)

    def emergency(self, alert_param):
        """Returns a dictionary with the alert parameters if there is one. Called by ``update_long_term``"""
        short_term = self.long_term_bytes[-alert_param.short_median:]
        long_term = self.long_term_bytes[:-alert_param.short_median]

        short_term_average = sum(short_term) / alert_param.short_median
        long_term_average = sum(long_term) / alert_param.long_median
        res = {'alert_param': alert_param, 'short_average': short_term_average, 'long_average': long_term_average}
        if short_term_average > long_term_average * alert_param.threshold:
            res['alert'] = True
        else:
            res['alert'] = False
        return res


class Statistician(Thread):
    """
    This thread object is responsible for the statistics maintenance, it has a :obj:`Statistics` object to store them and raise
    the alerts.

    It possesses the alert parameters.

    Read lines are 'thread-safely' received thanks to an ``input_queue``. They should be parsed by default, but this can be changed
    with the ``parse`` parameter.

    Attributes
    ----------
    should_run: bool
        If False, the thread will shortly end stop its operation. Used to cleanly end the program.

    Note
    ----
    Alerts are checked every ``AlertParam.time_resolution``.

    """

    def __init__(self, input_queue, sleeping_time=0.1, parse=False,
                 alert_param=AlertParam()):
        Thread.__init__(self)

        self.input_queue = input_queue
        self.sleeping_time = sleeping_time
        self.parse = parse

        self.alert_param = alert_param

        self.total_nb_of_treated_line = 0
        self.stat = Statistics()
        self.should_run = True
        self.name = 'statistician thread'

        self.last_alert_check = time.time()

    def run(self):
        """ Checks if an alert should be raised, checks the input queue, update the stats if necessary and starts again."""
        while self.should_run:
            # if the alert should be check (ie every alert_param.time_resolution)
            if time.time() - self.last_alert_check > self.alert_param.time_resolution:
                # print(time.time() - self.last_alert_check)
                self.stat.update_long_term(self.alert_param)
                self.last_alert_check = time.time()

            # we wait for an input in the queue, with a timeout to avoid stucking the program
            try:
                log_line = self.input_queue.get(block=True, timeout=0.1)
            except Empty:
                continue

            if self.parse:  # False by default
                try:
                    HTTP_dict = reader.parse_line(log_line)
                except reader.HTTPFormatError as e:
                    d.displayer.log(self, d.LogLevel.ERROR, e.message)
            else:
                HTTP_dict = log_line

            # we update the stats
            self.stat.upadate_stat(HTTP_dict)
            self.total_nb_of_treated_line += 1

            if self.input_queue.qsize() == 0:
                d.displayer.log(self, d.LogLevel.INFO, "Queue emptied after {} lines"
                                                       "".format(self.total_nb_of_treated_line))
                time.sleep(self.sleeping_time)

    def state(self):
        """
        Returns
        -------
        string
            Describes the present thread state

        """
        return 'total nb of treated line: {}, in queue: {}' \
               ''.format(self.total_nb_of_treated_line, self.input_queue.qsize())


class QueueWriter(Thread):
    """
    Used to fill the Statistician queue, to simulate a fast reading and compare the reading speed with or without parsing.

    Note
    ----
    pace10 is the pace for 100ms, ie ``10*pace10`` entries are put in the queue every second.
    """

    def __init__(self, output_queue, parse=True, pace10=1, factor=2):
        Thread.__init__(self)

        self.output_queue = output_queue
        self.pace10 = pace10
        self.factor = factor  # used for the URL generation
        self.parse = parse

        self.should_run = True

    def run(self):
        """ Puts ``n=pace10`` lines every 10th of a second in the ``output_queue`` """
        total_count = 0
        random_log_line = log_writer.random_log_line_maker('HTTP_slow', factor=self.factor)
        while self.should_run:
            line_count_second10 = 0
            start_time_second10 = time.time()
            while self.should_run and line_count_second10 < self.pace10 and time.time() - start_time_second10 < 0.1:

                if self.parse:
                    try:
                        log_line = reader.parse_line(
                                random_log_line(date=datetime.datetime.utcnow().strftime('[%d/%b/%Y:%X +0000]')))
                    except reader.HTTPFormatError as e:
                        d.displayer.log(self, d.LogLevel.ERROR, e.message)
                else:
                    log_line = random_log_line(date=datetime.datetime.utcnow().strftime('[%d/%b/%Y:%X +0000]'))

                self.output_queue.put(log_line)
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


if __name__ == '__main__':

    def simulate_putter_and_getter(with_getter=True):
        """"
        Simulate a statistician connected to a LogReader (that is in fact a QueueWriter) to study the performances
        and optimise the system
        """
        statistician_parse = True

        q = Queue()
        pace10 = 100  # ie pace = 10*pace10

        putter = QueueWriter(q, parse=not statistician_parse, pace10=pace10)  # pace10=1000 -> 10,000 put/sec
        putter.start()

        if with_getter:
            displayer = d.Displayer(debug=True)  # needed for d.displayer.log calls
            m = Statistician(q, parse=statistician_parse)
            m.start()

        time.sleep(3)
        putter.should_run = False

        if with_getter:
            m.should_run = False

    simulate_putter_and_getter(with_getter=True)

