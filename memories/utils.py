import time
import logging
from functools import wraps

logging.basicConfig(level=logging.INFO,
                    format='[%(asctime)s] [%(levelname)s] %(message)s')


def timehttp(endpoint):
    @wraps(endpoint)
    def timed(self, request, response):
        start = time.time()
        result = endpoint(self, request, response)
        logging.info("{uri} => {status} {response} in {timing:.3f}s"
                     .format(uri=request.uri,
                             status=response.status,
                             response=response.body,
                             timing=time.time() - start))
        return result
    return timed


def timeit(func):
    @wraps(func)
    def timed(*args, **kwargs):
        argument_names = func.func_code.co_varnames[:func.func_code.co_argcount]
        arguments = args[:len(argument_names)]
        defaults = func.func_defaults or ()
        arguments += defaults[len(defaults) - (func.func_code.co_argcount - len(arguments)):]
        params = zip(argument_names, arguments)
        arguments = arguments[len(argument_names):]
        if arguments: params.append(('args', arguments))
        if kwargs: params.append(('kwargs', kwargs))
        call = func.func_name + '(' + ', '.join('%s=%r' % p for p in params) + ')'

        start = time.time()
        result = func(*args, **kwargs)
        logging.info("{call} = {result} [{timing:.3f}s]"
                     .format(call=call,
                             result=unicode(result, 'utf8', errors='ignore').encode('utf8'),
                             timing=time.time() - start))
        return result
    return timed
