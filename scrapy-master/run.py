import logging
from scrapy_master.app import app

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO)
    app.run()
