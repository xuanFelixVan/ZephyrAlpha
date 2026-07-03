"""探查 AKShare 申万行业成分股接口的列名差异。"""
import sys
sys.path.insert(0, r"d:\ZephyrAlpha\tmp")

# 断开 VPN（AKShare 铁律）
import os
os.environ["NO_PROXY"] = "*"
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

import akshare as ak

# 测试成功和失败的行业代码
test_codes = [
    ("801010", "农林牧渔"),   # 成功
    ("801160", "公用事业"),   # 成功（最后一个成功）
    ("801170", "医药生物"),   # 失败（第一个失败）
    ("801180", "交通运输"),   # 失败
    ("801230", "综合"),       # 失败
    ("801730", "通信"),       # 失败
]

for code, name in test_codes:
    print(f"\n=== {code} {name} ===")
    try:
        df = ak.index_component_sw(symbol=code)
        print(f"  shape: {df.shape}")
        print(f"  columns: {list(df.columns)}")
        if len(df) > 0:
            print(f"  first row: {dict(df.iloc[0])}")
    except Exception as e:
        print(f"  ERROR: {type(e).__name__}: {e}")
        # 尝试获取原始数据
        try:
            import inspect
            src = inspect.getsource(ak.index_component_sw)
            print(f"  function source (first 500 chars):")
            print(src[:500])
        except Exception:
            pass

# 测试替代接口
print("\n\n=== 替代接口测试 ===")

# 1. stock_industry_category_cninfo (巨潮)
try:
    df = ak.stock_industry_category_cninfo()
    print(f"stock_industry_category_cninfo: shape={df.shape}, columns={list(df.columns)}")
    print(df.head(3))
except Exception as e:
    print(f"stock_industry_category_cninfo ERROR: {e}")

# 2. sw_index_first_info
try:
    df = ak.sw_index_first_info()
    print(f"\nsw_index_first_info: shape={df.shape}, columns={list(df.columns)}")
    print(df.head(5))
except Exception as e:
    print(f"sw_index_first_info ERROR: {e}")

# 3. sw_index_second_info
try:
    df = ak.sw_index_second_info()
    print(f"\nsw_index_second_info: shape={df.shape}, columns={list(df.columns)}")
    print(df.head(5))
except Exception as e:
    print(f"sw_index_second_info ERROR: {e}")
