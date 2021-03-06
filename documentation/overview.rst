.. _overview:

Overview
========

What is this program?
---------------------

The goal of HTTP-log is to monitor an actively writen HTTP access log, typically on a LAMP server. The following bloc is
an example of HTTP access log lines
::

    123.12.45.78 - - [22/Dec/2015:03:31:01 +0000] "OPTIONS /page2/blog1/ HTTP/1.1" 200 170
    123.12.45.78 - - [22/Dec/2015:03:31:01 +0000] "TRACE /page2/index.html HTTP/1.1" 200 293
    123.12.45.78 - - [22/Dec/2015:03:31:01 +0000] "GET /blog3/picture.png HTTP/1.1" 200 417
    123.12.45.78 - - [22/Dec/2015:03:31:01 +0000] "GET /page1/page4/picture.png HTTP/1.1" 200 778
    123.12.45.78 - - [22/Dec/2015:03:31:01 +0000] "TRACE /archive4/index.html HTTP/1.1" 200 965

You can find a description of what I had to do here: :ref:`subject`.

This is a typical output:
::

   ================================================================================
                      Welcome! HTTP-log Displayer is now running
       LogSimulator is started - LogReader is started - Statistician is started
   ================================================================================
   16:35:47 - Most visited section in the past 10s is '/page1' with 837 hits.
           Total hits: 9700,
           Total sent bytes: 4835489, i.e. 4.611 MB.
   16:35:57 - Most visited section in the past 10s is '/page2' with 870 hits.
           Total hits: 10000,
           Total sent bytes: 4992571, i.e. 4.761 MB.
                      ///////////////// ALERT \\\\\\\\\\\\\\\\\
             High traffic detected: 12/22/15 16:36:02: outflow 0.957MB/s
   16:36:07 - Most visited section in the past 10s is '/page2' with 1717 hits.
           Total hits: 20000,
           Total sent bytes: 9949869, i.e. 9.489 MB.
                      \\\\\\\\\\\\\\\ ALERT OVER ///////////////
                  End of alert: 12/22/15 16:36:07: outflow 0.213MB/s
   Terminating the program, waiting for the threads to end...
   Program correctly ended!


101 User Manual
---------------

You can use the ``httplog`` command in a terminal opened in the ``source`` folder.
Type ``httplog -h`` to see the help.

* **If you do have** a HTTP access file being writen on your server, type ``httplog path`` (where ``path`` is its
  relative path to httplog or absolute path) to start to monitor it.

* **If you don't have** a HTTP access file being writen right now, type ``httplog path -s`` to start a simulation.
  ``path`` should be the path to a *simulation config file*, you can find two of them in the ``data`` folder:
  ``sim_config`` and ``short_config``. ``sim_config`` gently explains you what it contains.

Arguments
^^^^^^^^^

The ``path`` argument is mandatory.
Use ``-l DEBUG`` to set the log level to ``DEBUG``, other levels are ``INFO``, ``WARNING``, ``ERROR`` and ``CRITICAL``.

Use ``-s`` to indicate that you run a simulation, if you do.

See the ``--help`` for more information.

The alerts
^^^^^^^^^^

The alert monitoring system uses moving averages, and raises an alert in a short moving average is above
a long one, with a certain threshold coefficient. That implies that if the traffic is not increasing or
decreasing *brutally*, no alert (or end-alert) will be raised.

.. note:: The alert system is based on the real outflow (in bytes), not the number of requests received.

.. note:: You can change the alert monitoring parameters in the :mod:`httplog` (for a command line execution) and
   :mod:`playground`.

   Change the line ``AlertParam(short_median=12, long_median=120, threshold=1.5, time_resolution=10)``.
   The unit base of ``short_median`` and ``long_median`` is ``time_resolution``, that means that
   ``long_median=2`` with ``time_resolution=10`` will calculate an outflow average on the last ``2 * 10 = 20`` seconds.
   An alert will be raised if ``short_outflow_average > long_outflow_average * threshold``.



What are all those folders for?
-------------------------------

There should be several folders in your ``HTTP-log`` folder. Let's have a quick look:

* ``source``: obviously where the source code is. Go there to play with the program.
* ``data``: used to store some useful test or configuration files.
* ``log``: the place where you will find the files generated by the program.
* ``documentation`` is where you are now, it contains all the documentation web and config files (for sphinx).

I want to change your code
--------------------------

I recommend you to create a virtual environment with python 2.7 so that your own python installation doesn't conflict
with the program requirements. First install ``virtualenv``, then create your virtual environment, activate it, and finally
install the dependencies stored in ``data/requierements.txt``.
::

    pip install virtualenv
    virtualenv python27 -p /usr/bin/python2.7
    source python27/bin/activate  # or simply 'python27\Scripts\activate' if you are on Windows
    pip install -r data/requirements.txt

We now have the same dev environment. You can use ``playground.py`` if you want to launch the program from your IDE,
without command line arguments. Each module has a ``if __main__ == '__main__':`` that allows you to start and play with them.

And now what?
-------------

You could read my page about :ref:`architecture` to understand it!

