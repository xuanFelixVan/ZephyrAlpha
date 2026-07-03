"""测试 i问财获取申万行业分类。"""
import sys
import os
sys.path.insert(0, r"d:\ZephyrAlpha\tmp")
from _ds_common import load_env, iwencai_to_df
from iFinDPy import THS_iFinDLogin, THS_iwencai

load_env()
r = THS_iFinDLogin(os.environ["IFIND_USERNAME"], os.environ["IFIND_PASSWORD"])
print(f"login: {r}")

# 测试不同的查询语句
queries = [
    "申万一级行业",
    "申万行业分类",
    "所属申万一级行业",
    "全部A股 申万一级行业",
]

for q in queries:
    print(f"\n=== 查询: {q} ===")
    try:
        result = THS_iwencai(q, "stock")
        df = iwencai_to_df(result)
        print(f"  shape: {df.shape}")
        if len(df) > 0:
            print(f"  columns: {list(df.columns)}")
            print(df.head(3).to_string())
    except Exception as e:
        print(f"  ERROR: {e}")
