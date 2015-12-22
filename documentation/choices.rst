.. _choices:

My choices and what could be improved
=====================================

    *"Python is love, python is life."*
    -- Dalai Lama

Python
------

Python has several advantages:

* It allows you to write quickly and easily *not-so-slow* and clean program
* It is already installed on every Linux server (and OSX, but is this relevant?)
* It is reliable
* I know it

I could have used faster languages like C++ or Go. It would also have been interesting if I had do use several external
libraries the program but I manage to use only the standard library, hence the installation is really dead-simple.
Libraries like ``py.test`` are used for the development but are not necessary for the deployment.

Python 2.7
^^^^^^^^^^

   *"I used python 2.7, because it's fun to learn deprecated technologies"*

Ok, python 2.7 is not really *deprecated*, bugs are still corrected and it is still a great tool.
Python 2.7 is used in professional environments, and it used to be more widely adopted than python 3, that is why I used it.

If you have an old Linux VM somewhere, you should still be able to use httplog on, it thanks to 2.7.

Libraries and OS features
^^^^^^^^^^^^^^^^^^^^^^^^^

No external library is necessary to use the program. You got my point : simpler installation, higher compatibility,
less user tears.

I did not used any Unix-only features, even if it could have been more elegant to do so (who said polling?).
Windows users, you are welcome: httplog will run for you too.

Implementation choices
----------------------

Several threads
^^^^^^^^^^^^^^^

Summary of :ref:`architecture` page, *several threads* means

* faster
* better
* stronger
* more complicated code
* subtle problems with delicate solutions

For instance:

* When a critical error is raised in a child thread and the program must be exited (ex: incorrect log path given, hence no input),
  I used ``thread.interrupt_main`` to stop the main program, because the raised exception is not sent to the parent thread.
  Then the parent thread automatically asks the others threads to end, thanks to the ``atexit`` mechanism.
  The children threads check between to tasks if their attribute ``should_run`` is still ``True``,
  if it is not, they close the opened files and gently exit. This allows you to simply stop them with ``should_run = False``
  and a little patience.
  Yes, it is more complicated than a single thread process, but it works.

* When you use and communicate data between threads, thread-safe systems are needed. You don't want a variable that can be
  overridden by another thread while you use it! That is why the ``LogReader`` send the read lines to the ``Statistician``
  using a ``Queue``, and why the ``Statistician`` use a ``Lock`` when accessing his ``stats`` (to send them to the
  ``Displayer`` or to update them)

Reading the log
^^^^^^^^^^^^^^^

The reader thread uses a temporal loop to read the log file: it goes to the EOF using ``log.readline()``, then waits for
a certain time (defined by :attr:`reader.sleeping_time`) and starts again. Simple, cross-platform solution. No polling,
no signal, just ``import io``.


.. note:: When the log is going to fast i.e. they are to many HTTP access lines written each second and the reader cannot follow the pace,
   there is a mechanism that makes the reader aware of it (it checks the last time it has been in EOF). :obj:`reader.LogReader` send
   a ``WARNING`` to the :obj:`display.Displayer` when it happens.

   This mechanism can be implemented for the :obj:`Statistician.statistician`.
   It is already implemented for the :obj:`log_writer.LogWriter`: it sends a ``WARNING`` to the displayer when not enough lines are written.

Parsing the lines:
^^^^^^^^^^^^^^^^^^

To parse the read lines, a regex is used. °The input is a raw string, the output is a dictionary with the keys
``remotehost, remotelogname, authuser, date, request, status, bytes``.

``Status`` and ``bytes`` are converted to ``int``.
If needed, the date can be transformed in a ``datetime`` object (this is rather slow, hence disabled by default).
Exceptions are raised and handled when an incorrect line is read, and a ``WARNING`` is send to the displayer.

.. note:: Commented and empty lines are ignored.

.. warning:: Only valid W3C HTTP access lines can be read:
   ::

        # remotehost remotelogname authuser [date] "request" status bytes
        127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326

Parsing the lines: optimisation
...............................

Who should parse the line: the Statistician or the LogReader? To answer that question, I implemented the two alternatives and
took the faster one, the one the optimally divide the work between the threads. The LogReader is now parsing the lines.

Simple alerts
^^^^^^^^^^^^^

The alert monitoring system is working, but their parameters are not necessarily properly fitted for your use.

Possible improvements
---------------------

Optimisation
^^^^^^^^^^^^

It is always possible to optimise the program, or to rewrite it in GO or C++. Note that most of the loop conditions are
already optimised: they were tested and chosen to maximise the speed of the program.

Function are defined before the loops to avoid ``if else`` statements (ex: ``timeout_check`` in :meth:`log_writer.LogWriter.run`),
lists are generated once for all (ex: in the :func:`log_writer.uniform_random_local_URL_maker`) etc.

Better stats and alerts
^^^^^^^^^^^^^^^^^^^^^^^

Alerts are not perfects, more efficient detection mechanisms could be written. Several types of alerts could be raised,
for instance we may want to distinguish "outflow alerts" (scale: sent bytes per second) from "requests alerts" (scale: number of requests
per second).

Printed stats are not incredibly thrilling either.

You might want to overwrite :meth:`statistician.Statistics.emergency`, :meth:`statistician.Statistics.update_long_term`,
and the corresponding methods in :obj:`display.Displayer`.

Displayer and UI/UX
^^^^^^^^^^^^^^^^^^^

The actual UX is quite simple : a command line to start, a keyboard interruption to end it, a few log files written and that's it.

``Curses`` could be used to create a real interface (and break the windows compatibility...). The thread could be forked
and it could become a background daemon (like httpd).

A user interface could be written with Qt or Tkinter (not so useful on a console, but you could code a remote displayer,
or ... a monitoring web interface, start a startup, settle down in NYC etc.).

Unit Tests
^^^^^^^^^^

The code coverage of my test is a sensible subject, I should write unit tests instead of ``if __name__ == '__main__'`` tests.

Clean the code
^^^^^^^^^^^^^^

Not every bloc of code is beautiful... for instance the ``global displayer`` in :mod:`display` is working and
without obvious side effect but it is more a trick than an elegant solution. The problem was "how redirect all the 'print'
to a special object method without having to explicitly give the object reference to everyone?".
If you want to talk about it, tell me!

A singleton pattern might be more appropriate.

Service optimisation
^^^^^^^^^^^^^^^^^^^^

You have data. This is nice, let's use it!

You could analyse your log file to detect which web page
generate the most outgoing traffic, and try to minimise its impact. You could try to detect strange behaviors,
there are several interesting uses that one could think of for your logs.

Bug fix
^^^^^^^

There are no known bug, tell me if you find one!

What's next?
------------

Read :ref:`module_description` description to see were is what,
then take a look at :mod:`playground` to change the default parameters of the simulation.

For me, if think I will work on ``Curses``, it looks fun. Data analysis is also fun.
