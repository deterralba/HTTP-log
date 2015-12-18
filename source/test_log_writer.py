#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)
import log_writer
import re


def test_random_local_URL():
    assert check_local_URL('/') is True
    assert check_local_URL('/test') is True
    assert check_local_URL('/test/test.php') is True

    assert check_local_URL('') is False
    assert check_local_URL('/ /') is False

    for i in xrange(10):
        assert check_local_URL(log_writer.random_local_URL(factor=4, max_depth=4)) is True


def check_local_URL(URL):
    """Return True is URL starts with '/' and doesn't contain any whitespace character"""
    return URL.startswith('/') and re.search(r'\s', URL) is None

