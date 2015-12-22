.. _module_description:

The different modules
=====================

The core
--------

* :mod:`httplog` is the "main thread module", called when you type ```httplog path`` in the terminal. It parses the arguments,
  creates the children threads and manages them.

* :mod:`reader` contains the :obj:`reader.LogReader` thread that continuously reads the log file.

* :mod:`statistician` contains the :obj:`statistician.Statistician` thread that calculates the stats with a
  :obj:`statistician.Statistics` object.

* :mod:`display` contains the :obj:`display.Displayer` thread that displays stats and alerts on the console or on log files.
  :obj:`display.Displayer` contains a thread-safe logging and printing system through which every printing command go.

The simulation module
---------------------

* :mod:`log_writer` contains :obj:`log_writer.LogSimulator` and :obj:`log_writer.LogWriter` two threads used to generate
  actively written HTTP access logs from simulation config files.

The other modules
-----------------

* The test modules: they start with ``test_`` and are used by ``py.test`` to test the source code.
  They need to be completed!

* The :mod:`misc` modules, a.k.a. miscellaneous module, used as a storage facility. You can ignore it.

Links
-----


..  toctree::
    :maxdepth: 2

    pages/modules