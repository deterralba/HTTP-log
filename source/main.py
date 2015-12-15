#!/usr/bin/env python
# -*- coding: utf-8 -*-

from __future__ import (unicode_literals, absolute_import, division, print_function)

import display
import reader


if __name__ == '__main__':
    try:
        th1 = display.DisplayThread()
        th1.start()
        while True:
            display.time.sleep(1)
            print("lol")
            r = raw_input()
            if r == '1':
                break
    except (KeyboardInterrupt, SystemExit):
        print('goodbye !')

