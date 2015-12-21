#!/usr/bin/env python
# coding: utf8

from __future__ import (unicode_literals, absolute_import, division, print_function)

import time
import sys

if __name__ == '__main__':

    def run(log_simulator=None):
        import atexit
        is_simulation = False
        if log_simulator:
            is_simulation = True
        # print(is_simulation)
        snoopy = reader.LogReader(log_path)
        kolmogorov = statistician.Statistician(input_queue=snoopy.output_queue, alert_param=alert_param)
        picasso = d.Displayer(statistician=kolmogorov, log_level=log_level)

        thread_list = [snoopy, kolmogorov, picasso]
        picasso.registered_object = thread_list[:-1]  # the displayer is not registered by the displayer
        if is_simulation:
            picasso.registered_object = [log_simulator] + picasso.registered_object

        if is_simulation:
            log_simulator.daemon = True
        for th in thread_list:
            th.daemon = True

        def close_program():
            print("Terminating the program, waiting for the threads to end...")
            if is_simulation:
                try:
                    log_simulator.log_w.should_run = False
                except:
                    pass
                log_simulator.should_run = False
            for th in thread_list:
                th.should_run = False

            try:
                if is_simulation:
                    log_simulator.join(1)
                for th in thread_list:
                    th.join(1)
            except:
                pass
            time.sleep(1)

            correctly_ended= True
            for th in thread_list:
                if th.is_alive():
                    print("Program will end brutally, {} is not over".format(th.name))
                    correctly_ended = False

            print("Program {} ended!".format('correctly'*correctly_ended + 'brutally'*(not correctly_ended)))
        atexit.register(close_program)

        if is_simulation:
            # this is the LogSimulator
            log_simulator.start()
            while not log_simulator.started_first_writing():
                pass
        for th in thread_list:
            th.start()

        return thread_list


    # The output ../log folder is created
    import os
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
    # print(args)

    import display as d
    import reader
    import statistician

    try:
        log_level = [k for k, v in d.LogLevel.level_name.iteritems() if v == args.log_level][0]
    except IndexError:
        print('Wrong verbosity value, program ended.')
        sys.exit(1)

    try:
        if args.simulation:
            print('HTTP_log will now start a simulation with the config file {}'.format(args.path))

            sim_config_path = args.path
            alert_param = statistician.AlertParam(short_median=1, long_median=3, threshold=1.5, time_resolution=5)

            import log_writer
            shakespeare = log_writer.LogSimulator(sim_config_path)
            simulation_param = shakespeare.get_parameters()
            log_path = simulation_param['log_path']
            print(log_path)

            run(log_simulator=shakespeare)

            while shakespeare.is_alive():
                shakespeare.join(0.01)

            sys.exit()

        else:
            alert_param = statistician.AlertParam(short_median=12, long_median=120, threshold=1.5, time_resolution=10)

            log_path = args.path

            run()

            while True:
                time.sleep(0.2)
    except KeyboardInterrupt:
        sys.exit(0)
