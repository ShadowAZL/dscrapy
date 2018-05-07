from flask import Flask, jsonify, request
from six.moves.urllib_parse import urlparse
from scrapy_master import settings
from scrapy_master.utils import RedisAgent
from scrapy_master.zoo_watcher import ZooWatcher
from scrapy_master import client
from scrapy_master import scrapyd_utils
app = Flask(__name__)
app.config.from_object(settings)
config = app.config

zw = ZooWatcher(config['ZOOKEEPER_PATH'], hosts=config['ZOOKEEPER_HOSTS'])

redis_cli = RedisAgent(config)
redis_cli.send_start_urls()


@app.route('/allstats.json')
def allstats():
    return jsonify(redis_cli.get_all_stats())


@app.route('/stats.json')
def stats():
    name = request.args['stats_name']
    return jsonify(redis_cli.get_stats(name))


@app.route('/crawlspeed.json')
def crawlspeed():
    return jsonify(redis_cli.get_crawl_speed())


@app.route('/spiderlist.json')
def spiderlist():
    return jsonify(zw.children.values())


@app.route('/control.json')
def control():
    if request.method == 'GET':
        hosts = request.args['hosts'].split(',')
        path = request.args['path']
        return jsonify(client.client_get_all(hosts, path))
    else:
        hosts = request.form['hosts'].split(',')
        path = request.form['path']
        method = request.form['method']
        return jsonify(client.client_post_all(hosts, path))



