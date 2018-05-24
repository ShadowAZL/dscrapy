"""A pickle wrapper module with protocol=-1 by default."""

import msgpack as pickle


def loads(s):
    return pickle.loads(s, raw=False)


def dumps(obj):
    return pickle.dumps(obj)
