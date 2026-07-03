"""探查 THS 行业成分股接口（替代 index_component_sw 的 801170+ 失败问题）。"""
import sys
sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
import os
os.environ["NO_PROXY"] = "*"
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

import akshare as ak

# 1. 获取 THS 行业列表
print("=== stock_board_industry_name_ths ===")
try:
    df = ak.stock_board_industry_name_ths()
    print(f"shape: {df.shape}, columns: {list(df.columns)}")
    print(df.head(10))
    industry_names = df["name"].tolist() if "name" in df.columns else df.iloc[:, 0].tolist()
    print(f"\n行业数: {len(industry_names)}")
    print(f"前10个: {industry_names[:10]}")
except Exception as e:
    print(f"ERROR: {e}")
    industry_names = []

# 2. 测试获取成分股（用第一个行业）
if industry_names:
    test_name = industry_names[0]
    print(f"\n=== stock_board_industry_cons_ths(symbol='{test_name}') ===")
    try:
        df = ak.stock_board_industry_cons_ths(symbol=test_name)
        print(f"shape: {df.shape}, columns: {list(df.columns)}")
        print(df.head(3))
    except Exception as e:
        print(f"ERROR: {e}")

# 3. 测试几个大行业
for name in ["医药生物", "银行", "计算机", "电子"]:
    print(f"\n=== stock_board_industry_cons_ths(symbol='{name}') ===")
    try:
        df = ak.stock_board_industry_cons_ths(symbol=name)
        print(f"shape: {df.shape}, columns: {list(df.columns)}")
        if len(df) > 0:
            print(f"first: {dict(df.iloc[0])}")
    except Exception as e:
        print(f"ERROR: {e}")
