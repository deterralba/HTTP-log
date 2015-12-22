.. _index:

Welcome to HTTP-log's documentation!
====================================

Forewords
---------

**Dear reader,**

This is the cherish documentation of my ``httplog`` program.
I hope you will like it, I tried to make it as smooth as possible.

Let's go to the point!
----------------------

If you are in a hurry, you just need:

1. to have a python 2.7 installed,
2. to go to the ``source`` folder in your favorite terminal and type ``httplog ../data/sim_config -s``
3. enjoy!

What is happening: the command launches a *simulation* of the program: a log file: log/simulated_log, is actively written
by a special part of the program and read in the meantime read by the monitoring program.
You will see every 10s a summery of the traffic observed, with alerts when it's
going up, and down, and up, and down...

Go to the :ref:`overview` page if want to know how to use the program!

Contents:
---------

You will find here:

* A simple user manual with a quick :ref:`overview`
* A description of :ref:`architecture` and the reasons behind :ref:`choices`
* The *usual* doc describing all the functions etc.

..  toctree::
    :maxdepth: 2

    overview
    architecture
    choices
    pages/modules


Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

