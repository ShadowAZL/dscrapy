import requests
from six.moves.urllib.parse import urljoin
from scrapy.utils.python import to_native_str


def get_commands():
    return {
        'help': cmd_help,
        'stop': cmd_stop,
        'list-available': cmd_list_available,
        'list-running': cmd_list_running,
        'list-resources': cmd_list_resources,
}


def cmd_help(host, *args):
    """help - list available commands"""
    print("Available commands:")
    for _, func in sorted(get_commands().items()):
        print("  ", func.__doc__)


def cmd_stop(host, *args):
    """stop <spider> - stop a running spider"""
    try:
        print(client_post(host, 'crawler/engine', 'close_spider', args[0]))
    except requests.exceptions.ConnectionError:
        print('stop %s succeed!' % args[0])


def cmd_list_running(host, *args):
    """list-running - list running spiders"""
    res = client_get(host, 'crawler/engine/open_spiders')
    for x in res:
        print(x)


def cmd_list_available(host, *args):
    """list-available - list name of available spiders"""
    res = client_post(host, 'crawler/spiders', 'list')
    if res['status'] == 'ok':
        for x in res['result']:
            print(x)
    else:
        print(res)


def cmd_list_resources(host, *args):
    """list-resources - list available web service resources"""
    for x in client_get(host, '')['resources']:
        print(x)


def get_url(host, path):
    return urljoin(host, path)


def client_post(host, path, method, *args, **kwargs):
    url = get_url(host, path)
    data = {'method': method, 'params': args or kwargs}
    return requests.post(url, json=data).json()


def client_get(host, path, *args, **kwargs):
    url = get_url(host, path)
    return requests.get(url).json()


def client_post_all(hosts, path, method, *args, **kwargs):
    ret = {}
    for h in hosts:
        h = to_native_str(h)
        ret[h] = client_post(h, path, method, *args, **kwargs)
    return ret


def client_get_all(hosts, path, *args, **kwargs):
    ret = {}
    for h in hosts:
        h = to_native_str(h)
        ret[h] = client_get(h, path, *args, **kwargs)
    return ret