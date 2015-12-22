#!/usr/bin/env python
# coding: utf8

"""
This is a storage for now useless pieces of code that used to be, or could be useful one day.
"""

from __future__ import (unicode_literals, absolute_import, division, print_function)

from Queue import Queue
from threading import Thread

import time
import io


class InputThread(Thread):
    """ An always waiting for input tread, printing what it gets."""
    def __init__(self):
        Thread.__init__(self)

    def run(self):
        while True:
            i = raw_input()
            print(i)


class Monitor(Thread):
    """A thread used to demonstrate how a queue object is working"""
    def __init__(self, input_queue):
        Thread.__init__(self)

        self.should_run = True
        self.input_queue = input_queue
        self.reader = True

    def run(self):
        print(self.name, self.reader)
        if self.reader:
            print(self.input_queue.get())
        else:
            self.input_queue.put(123)


def EOF_reader(path):
    """Read a file until the EOF.

    Warnings
    --------
    This is far too slow because tell() is bugged in python 2.x !
    """
    with io.open(path) as f:
        last_tell = f.tell()
        EOF = False
        i = 0

        while not EOF:
            print('beginning of line ', i + 1, f.tell(), f.readline().strip(), f.tell())
            if last_tell == f.tell():
                print("EOF in line", i + 1)
                EOF = True
            last_tell = f.tell()
            i += 1


def read_log(log_name):
    """A "two liner" that read the log file given. Fun.

    Returns
    -------
    list of strings:
        A list of all the non-empty line that are not starting with '#'

    Note
    ----
    The returned line are ``.strip()``-ed
    """
    with io.open(log_name, 'rt') as log_file:  # encoding can be set with 'utf_8'
        return [line.strip() for line in log_file if not line.strip().startswith('#') and len(line.strip()) > 0]



def random_local_URL(factor=2, max_depth=2):
    """
    Returns
    -------
    string
        A random local URL

    Warning
    -------
    The repartition of the returned URL is not uniform ! ULR with 0-depth (ie '/', with or without file name)
    are returned more often that longer URL.
    Use :func:`uniform_random_local_URL_maker` to get a ``uniform_random_local_URL`` function.

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
    from random import randint
    # print(factor, max_depth)
    section = ['page', 'blog', 'archive']
    URL_begging = [word + str(i) for i in xrange(1, factor+1) for word in
                   section]  # add an integer at the end of the section
    URL_end = ['picture.png', 'index.html', '']  # 'form.php', 'script.js', 'style.css', '']
    return '/' + '/'.join([URL_begging[randint(0, len(URL_begging) - 1)] for i in xrange(randint(0, max_depth))] +
                          [URL_end[randint(0, len(URL_end) - 1)]])  # * (randint(0, 4) >= 1)])


if __name__ == '__main__':

    # The following code uses Monitor()
    q = Queue()
    m1 = Monitor(q)
    m2 = Monitor(q)
    print('q.qsize:', q.qsize())

    m2.start()
    time.sleep(0.01)
    print('q.qsize:', q.qsize())

    m1.reader = False
    m1.start()
    time.sleep(0.01)
    print('q.qsize:', q.qsize())

    time.sleep(1)
    print('q.qsize:', q.qsize())
