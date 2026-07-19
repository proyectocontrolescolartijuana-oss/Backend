import importlib, inspect

try:
    mod = importlib.import_module('vercel.blob')
    print('module', mod)
    for attr in ['put', 'get', 'delete', 'del', 'head', 'list']:
        if hasattr(mod, attr):
            fn = getattr(mod, attr)
            try:
                print(attr, inspect.signature(fn))
            except ValueError:
                print(attr, 'signature unavailable')
        else:
            print(attr, 'missing')
except Exception as exc:
    print('error', type(exc).__name__, exc)
