#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)

import time

from display import LogLevel, Displayer

import display as d
import reader
import statistician


if __name__ == '__main__':
    reader_is_parsing = True
    log_path = '../data/wtest'
    picasso = d.Displayer(display_period=1, debug=True)
    picasso.log_level = d.LogLevel.INFO

    import log_writer
    shakespeare = log_writer.LogSimulator('../data/sim_config')
    snoopy = reader.LogReader(log_path, parse=reader_is_parsing)
    kolmogorov = statistician.Statistician(input_queue=snoopy.output_queue, parse=not reader_is_parsing)
    picasso.statistician = kolmogorov
    picasso.registered_object = [shakespeare, snoopy, kolmogorov]
    picasso.log_level = d.LogLevel.DEBUG

    shakespeare.start()
    time.sleep(0.01)
    snoopy.start()
    time.sleep(0.01)
    kolmogorov.start()
    picasso.start()

    shakespeare.join()
    time.sleep(0.5)

    shakespeare.should_run = False
    snoopy.should_run = False
    kolmogorov.should_run = False
    picasso.should_run = False


    # pace10 = 30  # ie pace = 10*pace10
    #
    # putter = QueueWriter(q, pace10=pace10)  # pace10=1000 -> 10,000 put/sec
    # putter.start()
    #
    # if with_getter:
    #     m = Statistician(q)
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

