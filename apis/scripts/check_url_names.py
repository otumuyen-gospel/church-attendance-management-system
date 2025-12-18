import os, sys

# Ensure project root (folder containing manage.py) is on sys.path
proj_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if proj_root not in sys.path:
    sys.path.insert(0, proj_root)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apis.settings')

import django
from django.urls import get_resolver

django.setup()

resolver = get_resolver()

print('Inspecting top-level url patterns:')
for p in resolver.url_patterns:
    try:
        name = p.name
        cb = getattr(p, 'callback', None)
        qual = getattr(cb, '__qualname__', None)
        print(repr(p.pattern), 'callback=', cb, 'qualname=', qual, 'name_type=', type(name), 'name_repr=', repr(name))
    except Exception as e:
        print('ERROR inspecting pattern', p, e)

# Also walk nested resolvers
from django.urls.resolvers import URLResolver

def walk(resolver):
    for p in resolver.url_patterns:
        if isinstance(p, URLResolver):
            walk(p)
        else:
            try:
                name = p.name
                cb = getattr(p, 'callback', None)
                qual = getattr(cb, '__qualname__', None)
                print('  nested:', repr(p.pattern), 'callback=', cb, 'qualname=', qual, 'name_type=', type(name), 'name_repr=', repr(name))
            except Exception as e:
                print('  ERROR nested inspecting pattern', p, e)

walk(resolver)
