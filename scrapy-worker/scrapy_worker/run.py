# -*- coding: utf-8 -*-

import sys
import os

from scrapy.cmdline import execute

# this script is for debug running
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
execute(['scrapy', 'crawl', 'qidian'])
