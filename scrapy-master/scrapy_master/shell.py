from scrapy.utils import console

from scrapy_master import scrapyd_utils
from scrapy_master import client
from scrapy_master import settings

console.start_python_console(namespace={'scrapyd_utils': scrapyd_utils,
                                        'client': client,
                                        'settings': settings,
                                        }, shells=['ipython'])

