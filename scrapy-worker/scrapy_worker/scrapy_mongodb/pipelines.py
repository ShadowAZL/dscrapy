import six
import logging
from scrapy.exporters import BaseItemExporter
from pymongo import MongoClient


class MongoDBPipeline(BaseItemExporter):
    """ MongoDB pipeline class """
    # Default options
    config = {
        'uri': 'mongodb://localhost:27017',
        'fsync': False,
        'write_concern': 0,
        'database': '%(spider)s',
        'collection': 'items',
        'separate_collections': False,
        'replica_set': None,
        'unique_key': None,
        'buffer': None,
        'append_timestamp': False,
        'stop_on_duplicate': 0,
    }

    def __init__(self, **kwargs):
        """ Constructor """
        super(MongoDBPipeline, self).__init__(**kwargs)
        self.logger = logging.getLogger(__name__)

    def open_spider(self, spider):
        # Configure the connection
        self.config['database'] = self.config['database'] % {'spider': spider.name}
        self.configure(spider.settings)

        # Connecting to a stand alone MongoDB
        connection = MongoClient(
            self.config['uri'],
            fsync=self.config['fsync'])
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
            ('fsync', 'MONGODB_FSYNC'),
            ('write_concern', 'MONGODB_REPLICA_SET_W'),
            ('database', 'MONGODB_DATABASE'),
            ('collection', 'MONGODB_COLLECTION'),
            ('separate_collections', 'MONGODB_SEPARATE_COLLECTIONS'),
            ('replica_set', 'MONGODB_REPLICA_SET'),
            ('unique_key', 'MONGODB_UNIQUE_KEY'),
            ('buffer', 'MONGODB_BUFFER_DATA'),
            ('append_timestamp', 'MONGODB_ADD_TIMESTAMP'),
            ('stop_on_duplicate', 'MONGODB_STOP_ON_DUPLICATE')
        ]

        for key, setting in options:
            if settings[setting]:
                self.config[key] = settings[setting]

    def process_item(self, item, spider):
        """ Process the item and add it to MongoDB
        :type item: Item object
        :param item: The item to put into MongoDB
        :type spider: BaseSpider object
        :param spider: The spider running the queries
        :returns: Item object
        """
        item = dict(self._get_serialized_fields(item))

        item = dict((k, v) for k, v in six.iteritems(item) if v)

        if self.config['append_timestamp']:
            item['scrapy-mongodb'] = {'ts': datetime.datetime.utcnow()}

        self.collections.insert_one(item)

        return item
