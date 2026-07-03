"""拦截 AKShare index_component_sw 捕获 801170 原始列名。

通过 monkey-patch pd.DataFrame.rename 捕获 rename 前的列名。
"""
import os
os.environ["NO_PROXY"] = "*"
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

import pandas as pd

# 保存原始 rename 方法
_orig_rename = pd.DataFrame.rename
_captured = {}

def patched_rename(self, *args, **kwargs):
    # 记录 rename 前的列名和参数
    import traceback
    caller = traceback.extract_stack()[-2]
    if "akshare" in (caller.filename or "") or "sw" in (caller.filename or "").lower():
        _captured["before"] = list(self.columns)
        _captured["rename_args"] = kwargs if kwargs else (args[0] if args else None)
    return _orig_rename(self, *args, **kwargs)

pd.DataFrame.rename = patched_rename

import akshare as ak

# 测试成功的代码
print("=== 801010 (should work) ===")
try:
    df = ak.index_component_sw(symbol="801010")
    print(f"  OK: shape={df.shape}")
    if "before" in _captured:
        print(f"  raw columns: {_captured['before']}")
        print(f"  rename map: {_captured['rename_args']}")
except Exception as e:
    print(f"  ERROR: {e}")
    if "before" in _captured:
        print(f"  raw columns: {_captured['before']}")
        print(f"  rename map: {_captured['rename_args']}")

_captured.clear()

# 测试失败的代码
print("\n=== 801170 (should fail) ===")
try:
    df = ak.index_component_sw(symbol="801170")
    print(f"  OK: shape={df.shape}")
except Exception as e:
    print(f"  ERROR: {type(e).__name__}: {e}")
    if "before" in _captured:
        print(f"  raw columns: {_captured['before']}")
        print(f"  rename map: {_captured['rename_args']}")
    else:
        print(f"  (rename was not called, API may have returned empty results)")
        # 检查是否在 r.json() 之前就失败了
        # 让我们直接拦截 requests.get
