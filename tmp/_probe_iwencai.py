"""探查 iFind i问财 THS_iwencai 返回结构。"""
import os
for line in open(r"d:\ZephyrAlpha\.env", encoding="utf-8"):
    line = line.strip()
    if line.startswith("IFIND_USERNAME="): u = line.split("=", 1)[1]
    elif line.startswith("IFIND_PASSWORD="): p = line.split("=", 1)[1]
from iFinDPy import *
r = THS_iFinDLogin(u, p)
print("login:", r)

df = THS_iwencai("2025年6月30日龙虎榜个股", "stock")
print("type:", type(df))
print("repr:", repr(df)[:500])
if hasattr(df, "keys"):
    print("keys:", list(df.keys()))
    for k in list(df.keys())[:8]:
        v = df[k]
        print(f"  key={k!r} type={type(v).__name__} preview={str(v)[:200]}")
elif hasattr(df, "iloc"):
    print("DataFrame columns:", list(df.columns))
    print("shape:", df.shape)
    print(df.head(3))
else:
    print("unknown structure, dir:", [x for x in dir(df) if not x.startswith("_")][:20])
