#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)
import reader
import pytest
import datetime

# TODO test for the parser

# def test_read():
#     res = [u'#simple test file for log reading\n',
#            u" # encoding should be tested (here it's utf8)\n",
#            u' #encoding test \xe9\xe0@\xf9\n',
#            u'# remotehost remotelogname authuser [date] "request" status bytes\n',
#            u'127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326']
#     assert reader.read('../data/log_test') == res


def test_read_log():
    res = ['127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] "GET /apache_pb.gif HTTP/1.0" 200 2326',
        'x.x.x.90 - - [13/Sep/2006:07:01:53 -0700] "PROPFIND /svn/[xxxx]/Extranet/branches/SOW-101 HTTP/1.1" 401 587']
    assert reader.read_log('../data/log_test')[:2] == res
    with pytest.raises(IOError):
        reader.read_log('i am not a good log_file path')

#
# def test_extract_request():
#     assert reader.extract_request('127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700]'
#                                   '"GET /apache_pb.gif HTTP/1.0" 200 2326') ==\
#                                   '"GET /apache_pb.gif HTTP/1.0"'
#     assert reader.extract_request('127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700]'
#                                   '"i am a "request" with "quotes" !" 200 2326') ==\
#                                   '"i am a "request" with "quotes" !"'
#     with pytest.raises(reader.HTTPFormatError):
#         reader.extract_request('127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700] \'I am not a good request!\' 200 2326')
#
#
# def test_extract_date():
#     assert reader.extract_date('127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700]'
#                                '"GET /apache_pb.gif HTTP/1.0" 200 2326') ==\
#                                '[10/Oct/2000:13:55:36 -0700]'
#     assert reader.extract_date('127.0.0.1 - frank [i am a date !]'
#                                '"i am a request with [brackets] !" 200 2326') ==\
#                                '[i am a date !]'
#     with pytest.raises(reader.HTTPFormatError):
#         reader.extract_date('127.0.0.1 - frank "I am not a good request: no date!" 200 2326')


def test_parse_line():
    assert reader.parse_line('127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700]'
                             '"GET /apache_pb.gif HTTP/1.0" 200 2326') ==\
                             {u'status': 200, u'bytes': 2326, u'remote_log_name': u'-',
                              u'remote_host': u'127.0.0.1', u'date': datetime.datetime(2000, 10, 10, 20, 55, 36),
                              u'auth_user': u'frank', u'request': u'"GET /apache_pb.gif HTTP/1.0"'}

    assert reader.parse_line('12.13.14.90 - - [13/Sep/2006:07:00:53 -0700]'
                             '"PROPFIND /svn/[xxxx]/Extranet/branches/SOW-101 HTTP/1.1" 401 587') ==\
                             {u'status': 401, u'bytes': 587, u'remote_log_name': u'-',
                              u'remote_host': u'12.13.14.90', u'date':  datetime.datetime(2006, 9, 13, 14, 0, 53),
                              u'auth_user': u'-',
                              u'request': u'"PROPFIND /svn/[xxxx]/Extranet/branches/SOW-101 HTTP/1.1"'}

    with pytest.raises(reader.HTTPFormatError):
        reader.parse_line('127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700]'
                          '"I am not a good request: no int byte!" 200 a_string')
    with pytest.raises(reader.HTTPFormatError):
        reader.parse_line('127.0.0.1 - frank [10/Oct/2000:13:55:36 -0700]'
                          '"I am not a good request: not complete!"')
