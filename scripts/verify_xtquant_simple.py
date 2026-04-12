# -*- coding: utf-8 -*-
import sys
import io
if sys.platform == "win32":
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

"""
Simple test script to verify xtquant imports in Python 3.12
Avoid Unicode characters to prevent encoding issues
"""

import sys
import os

print("=" * 80)
print("QMT Python 3.12 Environment Verification")
print("=" * 80)
print()

# 1. Check Python version
print("1. Python Version")
print("-" * 80)
print(f"Version: {sys.version}")
print(f"Executable: {sys.executable}")
print(f"Architecture: {'64-bit' if sys.maxsize > 2**32 else '32-bit'}")

version_ok = sys.version_info.major == 3 and sys.version_info.minor == 12
print(f"Python 3.12: {'OK' if version_ok else 'FAIL'}")

# 2. Test xtquant import
print()
print("2. xtquant Module")
print("-" * 80)
try:
    import xtquant
    print("xtquant import: OK")
    if hasattr(xtquant, '__version__'):
        print(f"Version: {xtquant.__version__}")
except ImportError as e:
    print(f"xtquant import: FAIL - {e}")
    sys.exit(1)

# 3. Test xtdata import
print()
print("3. xtdata Module")
print("-" * 80)
try:
    from xtquant import xtdata
    print("xtdata import: OK")
except ImportError as e:
    print(f"xtdata import: FAIL - {e}")

# 4. Test xttrader imports (critical for QMT)
print()
print("4. xttrader Module (Critical for QMT Connection)")
print("-" * 80)
xttrader_ok = False
xtaccount_ok = False

try:
    from xtquant.xttrader import XtQuantTrader
    print("XtQuantTrader import: OK")
    xttrader_ok = True
except ImportError as e:
    print(f"XtQuantTrader import: FAIL - {e}")

try:
    from xtquant.xttrader import XtAccount
    print("XtAccount import: OK")
    print("*** This was the critical failure point with Python 3.13 ***")
    xtaccount_ok = True
except ImportError as e:
    print(f"XtAccount import: FAIL - {e}")
    print("*** This is the critical issue that prevents QMT connection ***")

# 5. Summary
print()
print("=" * 80)
print("VERIFICATION SUMMARY")
print("=" * 80)

checks = [
    ("Python 3.12", version_ok),
    ("xtquant module", "xtquant" in sys.modules),
    ("XtQuantTrader class", xttrader_ok),
    ("XtAccount class", xtaccount_ok),
]

all_ok = all(ok for _, ok in checks)

print("\nCheck Results:")
for name, ok in checks:
    status = "PASS" if ok else "FAIL"
    print(f"  {name:20} [{status}]")

print()
if all_ok:
    print("SUCCESS: All checks passed! Python 3.12 environment is ready for QMT.")
    print()
    print("Next steps:")
    print("  1. Start QMT client")
    print("  2. Login with 'Minimal Mode' or 'Independent Trading' checked")
    print("  3. Run test script: python scripts/test_qmt_connection_v4.py")
else:
    print("WARNING: Some checks failed. QMT connection may not work.")
    if not xtaccount_ok:
        print("\nCritical issue: XtAccount import failed.")
        print("This means the xtquant library may not be fully compatible.")
        print("Try reinstalling xtquant: pip install --force-reinstall xtquant")
    
print()
