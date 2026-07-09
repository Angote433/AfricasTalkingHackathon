import importlib
import inspect

try:
    m = importlib.import_module('cost_service')
    print('MODULE FILE:', getattr(m, '__file__', None))
    keys = sorted([k for k in m.__dict__.keys()])
    print('DICT KEYS COUNT:', len(keys))
    for k in keys:
        print(repr(k), '->', type(m.__dict__[k]).__name__)
    # show specific functions
    for name in ('validate_line_item_cost','validate_costs','detect_round_number'):
        print(name, 'present?', name in m.__dict__)
        if name in m.__dict__:
            print('  is function?', inspect.isfunction(m.__dict__[name]))
except Exception as e:
    import traceback
    print('IMPORT FAILED')
    traceback.print_exc()
