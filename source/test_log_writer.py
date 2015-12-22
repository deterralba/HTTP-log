#!/usr/bin/env python
# coding: utf8

from __future__ import (unicode_literals, absolute_import, division, print_function)
import log_writer
import re


"""py.test test file"""


def check_local_URL(URL):
    """Return True is URL starts with '/' and doesn't contain any whitespace character"""
    return URL.startswith('/') and re.search(r'\s', URL) is None

# def test_random_local_URL():
#     assert check_local_URL('/') is True
#     assert check_local_URL('/test') is True
#     assert check_local_URL('/test/test.php') is True
#
#     assert check_local_URL('') is False
#     assert check_local_URL('/ /') is False
#
#     for i in xrange(100):
#         assert check_local_URL(log_writer.random_local_URL(factor=2, max_depth=2)) is True

