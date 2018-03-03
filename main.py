# -*- coding: utf-8 -*-
from scrapy.cmdline import execute

import sys
import os
#当前文件的文件夹目录
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
print(os.path.dirname(os.path.abspath(__file__)))


execute(['scrapy', 'crawl', 'jobbole'])