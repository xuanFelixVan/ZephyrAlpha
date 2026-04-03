"""
Inspect XtQuantTrader methods to understand API
"""

import inspect
from xtquant import xttrader

print("XtQuantTrader class inspection")
print("=" * 80)

XtQuantTrader = xttrader.XtQuantTrader

print("1. Class info:")
print(f"   Module: {XtQuantTrader.__module__}")
print(f"   Name: {XtQuantTrader.__name__}")
print()

print("2. Methods:")
methods = []
for name in dir(XtQuantTrader):
    if not name.startswith('_'):
        attr = getattr(XtQuantTrader, name)
        if callable(attr):
            methods.append(name)

for method in sorted(methods):
    print(f"   - {method}")
print()

print("3. Subscribe method details:")
if hasattr(XtQuantTrader, 'subscribe'):
    subscribe_method = getattr(XtQuantTrader, 'subscribe')
    try:
        sig = inspect.signature(subscribe_method)
        print(f"   Signature: {sig}")
    except:
        print("   Cannot get signature")
    
    # Check docstring
    doc = subscribe_method.__doc__
    if doc:
        print(f"   Docstring (first line): {doc.strip().split(chr(10))[0]}")
else:
    print("   No subscribe method found")

print()
print("4. Other important methods:")
important_methods = ['connect', 'run', 'stop', 'subscribe', 'query_stock_asset']
for method in important_methods:
    if hasattr(XtQuantTrader, method):
        attr = getattr(XtQuantTrader, method)
        if callable(attr):
            try:
                sig = inspect.signature(attr)
                print(f"   {method}: {sig}")
            except:
                print(f"   {method}: (signature unavailable)")
    else:
        print(f"   {method}: NOT FOUND")

print()
print("5. Check for account-related parameters:")
# Try to find any method that mentions account
for method in methods:
    attr = getattr(XtQuantTrader, method)
    if attr.__doc__ and 'account' in attr.__doc__.lower():
        print(f"   Method '{method}' mentions account in docstring")