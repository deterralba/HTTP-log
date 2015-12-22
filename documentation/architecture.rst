.. _architecture:

The software architecture
=========================

Introduction: a simple solution
-------------------------------

To implement what is asked in the :ref:`subject`, you really need to do only 3 main tasks:

1. Read continuously the HTTP log file
2. Keep some statistics on what you read
3. Print your stats and alerts in the console

So you could write a program that 1. read a line of the log, 2. Parse it, keep a counter for each hit section,
check if an alert is starting or ending, and finally 3. Print an alert or the stats if it is time.

Then you start again. And again, and again:

+------------+
| Thread 1   |
+============+
| Task 1     |
+------------+
| Task 2     |
+------------+
| Task 3     |
+------------+
| Task 1     |
+------------+
| Task 2     |
+------------+
| Task 3     |
+------------+
| Task 1     |
+------------+
| etc...     |
+------------+

Why a multi-threads structure
-----------------------------

While you are doing your statistics, you are not reading the log, nor printing them.
If you need advanced stats, printing, or even parsing, you may be interested to do something like this :

+------------+------------+-----------+
| Thread 1   | Thread 2   | Thread 3  |
+============+============+===========+
| Task  1    | Task 2     | Task 3    |
+------------+------------+-----------+
| Task  1    | Task 2     | Task 3    |
+------------+------------+-----------+
| etc...     | etc...     | etc...    |
+------------+------------+-----------+

If you want to write a program that will be able to do more advance things in the future,
if you want to use more than one core of your high end 32-cores processor,
if you think that maybe one day you will deal with several types of input or output, or several type of clients that will
each ask for different statistics...

What you need is a multi-threads program! It is a bit more complicated, but it is much more challenging and interesting also.


The threads awaken
------------------

Did I say they were 3 main tasks in the program ? Because there are 4 threads in my program ;)

1. A :obj:`reader.Reader`, that reads the input log file,
2. A :obj:`statistician.Statistician`, that calculates the statistics,
3. A :obj:`displayer.Displayer`, that displays the stats and the alert, or write them in output logs,
4. The ``main thread`` (usually in :mod:`httplog`) that manages the others.

If you use the simulation mode of the program, two others kind of threads are created:

5. :obj:`log_writer.LogWriter`: that writes in the log file the log lines at the speed you want during the time you want,
6. :obj:`log_writer.LogSimulator`: that reads the simulation configuration file and manages
   the succession of :obj:`log_writer.LogWriter` it needs.


The different roles of the threads should be clearer now, do not hesitate to contact me through github if you have any suggestion!

Now let's see how I chose to implement all theses tasks and threads: :ref:`choices`
