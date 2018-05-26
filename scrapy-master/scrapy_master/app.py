from flask import Flask, jsonify, request, render_template
from six.moves.urllib_parse import urlparse
from scrapy.utils.python import to_native_str
from scrapyd.utils import native_stringify_dict
from scrapy_master import settings
from scrapy_master.utils import RedisAgent, schedule, cancel
from scrapy_master.zoo_watcher import ZooWatcher
from scrapy_master import client
from scrapy_master.logstats import LogStats
from datetime import datetime
import uuid
app = Flask(__name__)
app.config.from_object(settings)
config = app.config
start_time = datetime.now()

zw = ZooWatcher(config['ZOOKEEPER_PATH'], hosts=config['ZOOKEEPER_HOSTS'])

redis_cli = RedisAgent(config)
redis_cli.send_start_urls()

logstats = LogStats(app.config)
logstats.start()


jobid = uuid.uuid4()
if config['SCRAPYD_ENABLED']:
    schedule(config['SCRAPYD_MASTER'], project=config['PROJECT_NAME'], spider=config['SPIDER_NAME'], jobid=jobid)


@app.route('/stop')
def stop():
    cancel(config['SCRAPYD_MASTER'], project=config['PROJECT_NAME'], job=jobid)
    return 'Stop OK!'


@app.route('/allstats')
def allstats():
    return jsonify(native_stringify_dict(redis_cli.get_all_stats(), keys_only=False))


@app.route('/stats')
def stats():
    name = request.args['stats_name']
    return jsonify(to_native_str(redis_cli.get_stats(name)))


@app.route('/status')
def job_status():
    return render_template('job.html')


@app.route('/api/status/list', methods=['POST'])
def spider_list():
    spiders = [to_native_str(s) for s in zw.children.values()]
    return jsonify(spiders)


@app.route('/api/status/stats', methods=['POST'])
def spider_stats():
    raw_stats = native_stringify_dict(redis_cli.get_all_stats(), keys_only=False)
    stats = {'start_time': start_time, 'dupefilter/filtered': raw_stats.get('dupefilter/filtered', 0),
             'item_scraped_count': raw_stats.get('item_scraped_count', 0), 'response_received_count': raw_stats.get('response_received_count', 0),
             'Page Crawled Speed': "%s pages/min" % logstats.prate, 'Item Scraped Speed': "%s items/min" % logstats.irate,
             'Avg Page Crawled Speed': "%.2f pages/min" % logstats.avg_prate, 'Avg Item Scraped Speed': "%.2f items/min" % logstats.avg_irate,
             }
    return jsonify(stats)


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