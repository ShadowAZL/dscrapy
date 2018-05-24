import six
import logging
from scrapy.exceptions import NotConfigured
from scrapy.exporters import BaseItemExporter
from pymongo import MongoClient
from twisted.internet import threads
import datetime


class MongoDBPipeline(BaseItemExporter):
    """ MongoDB pipeline class """
    # Default options
    config = {
        'uri': 'mongodb://localhost:27017',
        'database': '%(spider)s',
        'collection': 'items',
        'append_timestamp': True
    }

    def __init__(self, **kwargs):
        """ Constructor """
        super(MongoDBPipeline, self).__init__(**kwargs)
        self.logger = logging.getLogger(__name__)

    @classmethod
    def from_settings(cls, settings):
        if not settings.getbool('MONGODB_ENABLED'):
            raise NotConfigured
        return cls()

    def open_spider(self, spider):
        # Configure the connection
        self.config['database'] = self.config['database'] % {'spider': spider.name}
        self.configure(spider.settings)

        # Connecting to a stand alone MongoDB
        connection = MongoClient(
            self.config['uri'])
        self.logger.info('MongoDb Connect %s', self.config['uri'])

        # Set up the database
        self.database = connection[self.config['database']]
        self.collections = self.database[self.config['collection']]

        self.logger.info('Connected to MongoDB %s, using %s', self.config['uri'], self.config['database'])

    def configure(self, settings):
        """ Configure the MongoDB connection """
        # Set all regular options
        options = [
            ('uri', 'MONGODB_URI'),
            ('database', 'MONGODB_DATABASE'),
            ('collection', 'MONGODB_COLLECTION')
        ]

        for key, setting in options:
            if settings[setting]:
                self.config[key] = settings[setting]

    def process_item(self, item, spider):
        """ Process the item and add it to MongoDB
        """
        return threads.deferToThread(self._process_item, item, spider)

    def _process_item(self, item, spider):
        item = dict(self._get_serialized_fields(item))

        item = dict((k, v) for k, v in six.iteritems(item) if v)

        if self.config['append_timestamp']:
            item['scrapy-mongodb'] = {'ts': datetime.datetime.utcnow()}

        self.collections.insert_one(item)
