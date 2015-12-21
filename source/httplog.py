#!/usr/bin/env python
# coding: utf8

from __future__ import (unicode_literals, absolute_import, division, print_function)

import time

if __name__ == '__main__':

    # The output ../log folder is created
    import os
    import atexit
    try:
        os.mkdir('../log')
    except OSError as e:
        if not os.path.isdir('../log'):
            print("Impossible to create the '../log' directory. Can try to create it yourself?\nProgram ended.")

    import argparse
    import sys
    parser = argparse.ArgumentParser()
    parser.add_argument('path', help='The path to the log you want to monitor')
    parser.add_argument('-l', "--log_level",
                        help="Set the log level, can be: DEBUG, INFO, WARNING, ERROR, CRITICAL - default is WARNING",
                        default='WARNING')
    parser.add_argument('-s', "--simulation",
                        help="Launch a simulation, the path given should be the simulation config path.",
                        action="store_true", default=False)

    args = parser.parse_args()
    print(args)

    import display as d
    import reader
    import statistician

    try:
        log_level = [k for k, v in d.LogLevel.level_name.iteritems() if v == args.log_level][0]
    except IndexError:
        print('Wrong verbosity value, program ended.')
        sys.exit(1)

    alert_param = statistician.AlertParam(short_median=1, long_median=3, threshold=1.3, time_resolution=3)

    if args.simulation:
        try:
            print('HTTP_log will now start a simulation with the config file {}'.format(args.path))

            sim_config_path = args.path

            import log_writer
            shakespeare = log_writer.LogSimulator(sim_config_path)
            simulation_param = shakespeare.get_parameters()
            log_path = simulation_param['log_path']

            snoopy = reader.LogReader(log_path)
            kolmogorov = statistician.Statistician(input_queue=snoopy.output_queue, alert_param=alert_param)
            picasso = d.Displayer(statistician=kolmogorov, console_print_program_log=True, log_level=args.log_level)

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

            shakespeare.should_run = False
            snoopy.should_run = False
            kolmogorov.should_run = False
            picasso.should_run = False
        except KeyboardInterrupt:
            print("Keyboard interruption detected")
            sys.exit(0)
    else:
        log_level = args.log_level
        log_path = args.path

        snoopy = reader.LogReader(log_path)
        kolmogorov = statistician.Statistician(input_queue=snoopy.output_queue, alert_param=alert_param)
        picasso = d.Displayer(statistician=kolmogorov, console_print_program_log=True, log_level=log_level)

        picasso.registered_object = [snoopy, kolmogorov]

        snoopy.daemon = True
        kolmogorov.daemon = True
        picasso.daemon = True

        snoopy.start()
        kolmogorov.start()
        picasso.start()

        def close_program():
            print("Terminating the program, waiting for the threads to end...")
            snoopy.should_run = False
            kolmogorov.should_run = False
            picasso.should_run = False

            snoopy.join(1)
            kolmogorov.join(1)
            picasso.join(1)
            print("Program correctly ended!")
            return 0
        atexit.register(close_program)

        try:
            while True:
                time.sleep(0.2)
        except KeyboardInterrupt:
            print("Keyboard interruption detected")
            sys.exit(0)

