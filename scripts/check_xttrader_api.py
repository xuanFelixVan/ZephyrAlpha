"""
Check xttrader module attributes to understand API
"""

import sys
import inspect

print("Checking xttrader module structure...")
print()

try:
    from xtquant import xttrader
    
    print("1. Module imported successfully")
    print(f"   Module: {xttrader}")
    print()
    
    print("2. All attributes in xttrader module:")
    attrs = dir(xttrader)
    for i, attr in enumerate(attrs, 1):
        if not attr.startswith('_'):
            print(f"   {i:3}. {attr}")
    print()
    
    print("3. Classes in xttrader module:")
    classes = []
    for name in attrs:
        obj = getattr(xttrader, name)
        if inspect.isclass(obj):
            classes.append((name, obj))
    
    if classes:
        for name, cls in classes:
            print(f"   - {name}")
            # Try to get docstring
            doc = cls.__doc__
            if doc:
                doc_lines = doc.strip().split('\n')
                if doc_lines:
                    print(f"     Doc: {doc_lines[0]}")
    else:
        print("   No classes found")
    print()
    
    print("4. Check if XtQuantTrader constructor signature:")
    if hasattr(xttrader, 'XtQuantTrader'):
        XtQuantTrader = xttrader.XtQuantTrader
        try:
            sig = inspect.signature(XtQuantTrader.__init__)
            print(f"   XtQuantTrader.__init__ signature: {sig}")
        except:
            print("   Cannot get signature")
    print()
    
    print("5. Search for 'account' related attributes:")
    account_attrs = [attr for attr in attrs if 'account' in attr.lower() or 'acc' in attr.lower()]
    for attr in account_attrs:
        obj = getattr(xttrader, attr)
        obj_type = type(obj).__name__
        print(f"   - {attr}: {obj_type}")
        
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()