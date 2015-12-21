#!/usr/bin/env python
# coding: utf8

from __future__ import (unicode_literals, absolute_import, division, print_function)

import time

if __name__ == '__main__':

    # The output ../log folder is created
    import os
    import sys
    try:
        os.mkdir('../log')
    except OSError as e:
        if not os.path.isdir('../log'):
            print("Impossible to create the '../log' directory. Can try to create it yourself?\nProgram ended.")

    import display as d
    import reader
    import statistician
    import atexit

    alert_param = statistician.AlertParam(short_median=1, long_median=6, threshold=3, time_resolution=3)
    display_period = 3
    sim_config_path = '../data/sim_config'
    log_level = d.LogLevel.DEBUG

    try:
        import log_writer
        shakespeare = log_writer.LogSimulator(sim_config_path)

        simulation_param = shakespeare.get_parameters()
        log_path = simulation_param['log_path']

        snoopy = reader.LogReader(log_path)
        kolmogorov = statistician.Statistician(input_queue=snoopy.output_queue, alert_param=alert_param)
        picasso = d.Displayer(statistician=kolmogorov, display_period=display_period, console_print_program_log=True,
                              log_level=log_level)

        picasso.registered_object = [shakespeare, snoopy, kolmogorov]

        shakespeare.daemon = True
        snoopy.daemon = True
        kolmogorov.daemon = True
        picasso.daemon = True

        shakespeare.start()
        while not shakespeare.started_first_writing():
            pass
        snoopy.start()
        kolmogorov.start()
        picasso.start()

        def close_program():
            print("Terminating the program, waiting for the threads to end...")
            shakespeare.should_run = False
            try:
                shakespeare.log_w.should_run = False
            except:
                pass
            snoopy.should_run = False
            kolmogorov.should_run = False
            picasso.should_run = False

            shakespeare.join(1)
            snoopy.join(1)
            kolmogorov.join(1)
            picasso.join(1)
            print("Program correctly ended!")
            return 0
        atexit.register(close_program)

        while shakespeare.is_alive():
            shakespeare.join(0.01)

        time.sleep(1.5)
        # raise KeyboardInterrupt

        shakespeare.should_run = False
        snoopy.should_run = False
        kolmogorov.should_run = False
        picasso.should_run = False

    except KeyboardInterrupt:
        print("Keyboard interruption detected:", end=' ')
        sys.exit(0)
