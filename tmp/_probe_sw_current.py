"""用 sw_index_first_info() 获取当前有效的申万一级行业代码并测试。"""
import os
os.environ["NO_PROXY"] = "*"
os.environ["HTTP_PROXY"] = ""
os.environ["HTTPS_PROXY"] = ""

import akshare as ak
import time

# 获取当前 31 个一级行业
df = ak.sw_index_first_info()
print(f"当前一级行业数: {len(df)}")
print(f"列名: {list(df.columns)}")
print(df[["行业代码", "行业名称", "成份个数"]].to_string())

# 测试每个代码
codes = df["行业代码"].tolist()
names = df["行业名称"].tolist()
counts = df["成份个数"].tolist()

print(f"\n=== 测试 index_component_sw (带 .SI 后缀) ===")
for code, name, expected_count in zip(codes, names, counts):
    try:
        df_comp = ak.index_component_sw(symbol=code)
        actual = len(df_comp)
        status = "✅" if actual > 0 else "❌"
        print(f"  {status} {code} {name}: {actual} 行 (期望 {expected_count})")
    except Exception as e:
        print(f"  ❌ {code} {name}: {type(e).__name__}: {str(e)[:80]}")
    time.sleep(0.5)
