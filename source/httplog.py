#!/usr/bin/env python
# coding: utf8

from __future__ import (unicode_literals, absolute_import, division, print_function)

import time
import sys

"""
This is the main module, that should be called from a terminal with args. See the :ref:`overview` or type
``httplog --help`` for more information.
"""


if __name__ == '__main__':

    def run(log_simulator=None):
        """ Starts the core threads:

        * snoopy the :ojb:`reader.LogReader`,
        * kolmogorov the :ojb:`statistician.Statistician`,
        * and picasso the :ojb:`display.Displayer`.

        It is called in both real case and simulation.

        Args
        ----
        log_simulator: LogSimulator or None
            Reference to the LogSimulator if this is a simulation, else None. Used to define ``is_simulation``.

        """
        import atexit

        is_simulation = False
        if log_simulator:
            is_simulation = True

        snoopy = reader.LogReader(log_path)
        kolmogorov = statistician.Statistician(input_queue=snoopy.output_queue, alert_param=alert_param)
        picasso = d.Displayer(statistician=kolmogorov, log_level=log_level)

        thread_list = [snoopy, kolmogorov, picasso]

        if is_simulation:
            thread_list = [log_simulator] + thread_list
        picasso.registered_object = thread_list[:-1]  # the displayer is not registered by the displayer

        # the thread are demonised to ensure that they stop when the program is exited
        # we define a close_program() function to avoid brutal ends of the children. Let's not be barbaric.
        for th in thread_list:
            th.daemon = True

        def close_program():
            """Will be called when the main thread exits, gently asks the children threads to stop (with a timeout)"""
            print("Terminating the program, waiting for the threads to end...")
            if is_simulation:
                try:
                    log_simulator.log_w.should_run = False
                except:
                    pass
            for th in thread_list:
                th.should_run = False

            try:
                for th in thread_list:
                    th.join(1)
            except:
                pass

            correctly_ended = True
            for th in thread_list:
                if th.is_alive():
                    print("Program will end brutally, {} is not over".format(th.name))
                    correctly_ended = False

            print("Program {} ended!".format('correctly'*correctly_ended + 'brutally'*(not correctly_ended)))
        atexit.register(close_program)

        # the threads are started
        if is_simulation:
            log_simulator.start()
            while not log_simulator.started_first_writing():
                pass
            del thread_list[0]
        for th in thread_list:
            th.start()

    # The output ../log folder is created if necessary
    import os
    try:
        os.mkdir('../log')
    except OSError as e:
        if not os.path.isdir('../log'):
            print("Impossible to create the '../log' directory. Can try to create it yourself?\nProgram ended.")

    # the arguments are parsed and tested
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

    # initial configuration of the program, this is where you want to change the AlertParam. See the doc overview.
    try:
        if args.simulation:
            print('HTTP_log will now start a simulation with the config file {}'.format(args.path))

            sim_config_path = args.path
            # Here you can change the AlertParam for a simulation
            alert_param = statistician.AlertParam(short_median=1, long_median=3, threshold=1.5, time_resolution=5)

            import log_writer
            shakespeare = log_writer.LogSimulator(sim_config_path)
            simulation_param = shakespeare.get_parameters()
            log_path = simulation_param['log_path']

            run(log_simulator=shakespeare)

            # We wait that shakespeare ends
            while shakespeare.is_alive():
                shakespeare.join(0.01)

            sys.exit(0)

        else:
            # Here you can change the AlertParam for real cases
            # (short_median=12, long_median=120, threshold=1.5, time_resolution=10) is for 2min and  20min moving averages
            alert_param = statistician.AlertParam(short_median=12, long_median=120, threshold=1.5, time_resolution=10)

            log_path = args.path

            run()

            # we wait for a KeyboardInterrupt
            while True:
                time.sleep(0.2)
    except KeyboardInterrupt:
        sys.exit(0)


def READ_THE_SOURCE_CODE_FOR_THE_DOC_PLZ():
    pass
    """
    This is an ugly hack because sphinx ignores ``__name__ == '__main__':``

    If you read this, just ignore this function.
    """
