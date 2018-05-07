import traceback
import logging
from scrapy.utils.serialize import ScrapyJSONDecoder


logger = logging.getLogger(__name__)


def server_call(target, json_request, json_decoder=None):
    if json_decoder is None:
        json_decoder = ScrapyJSONDecoder()

    try:
        req = json_decoder.decode(json_request)
        logger.info(str(req))
    except Exception as e:
        return control_error('Parse error', traceback.format_exc())

    try:
        methname = req['method']
    except KeyError:
        return control_error('Invalid Request')

    try:
        method = getattr(target, methname)
    except AttributeError:
        return control_error('Method not found')

    params = req.get('params', [])
    a, kw = ([], params) if isinstance(params, dict) else (params, {})
    kw = dict([(str(k), v) for k, v in kw.items()]) # convert kw keys to str


    try:
        return control_result(method(*a, **kw))
    except Exception as e:
        return control_error(str(e), traceback.format_exc())


def control_error(message, data=None):
    return {
        'status': 'error',
        'error': {
            'message': message,
            'data': data,
        },
    }


def control_result(result):
    return {
        'status': 'ok',
        'result': result,
    }
