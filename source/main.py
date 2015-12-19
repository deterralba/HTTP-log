#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)

import time

import display
import reader
import monitor



if __name__ == '__main__':
    log_path = '../data/wtest'

    import log_writer
    lw = log_writer.LogSimulator('../data/sim_config')
    shakespeare = reader.LogReader(log_path)
    snoopy = monitor.Monitor(input_queue=shakespeare.output_queue)
    # picasso = display.Displayer(monitor=snoopy)
    #TODO use the displayer !!

    lw.start()
    time.sleep(0.1)

    shakespeare.start()
    time.sleep(0.1)
    snoopy.start()
    time.sleep(15)

    shakespeare.should_run = False
    snoopy.should_run = False
    shakespeare.should_run = False




    # pace10 = 30  # ie pace = 10*pace10
    #
    # putter = QueueWriter(q, pace10=pace10)  # pace10=1000 -> 10,000 put/sec
    # putter.start()
    #
    # if with_getter:
    #     m = Monitor(q)
    #     m.start()
    #
    # time.sleep(10)
    # putter.should_run = False
    #
    # if with_getter:
    #     m.should_run = False




    # try:
    #     th1 = display.DisplayThread()
    #     th1.start()
    #     while True:
    #         display.time.sleep(1)
    #         print("lol")
    #         r = raw_input()
    #         if r == '1':
    #             break
    # except (KeyboardInterrupt, SystemExit):
    #     print('goodbye !')

