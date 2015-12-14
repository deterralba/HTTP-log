#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)
import reader


def test_read():
    res = [u'#simple test file for log reading\n',
           u" # encoding should be tested (here it's utf8)\n",
           u' #encoding test \xe9\xe0@\xf9\n',
           u'# remotehost remotelogname authuser [date] "request" status bytes\n',
           u'127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326']
    assert reader.read('../data/log_test') == res


def test_read_log():
    res = [u'127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326']
    assert reader.read_log('../data/log_test') == res
