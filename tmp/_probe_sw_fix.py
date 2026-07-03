"""直接调用 SW API（复制 AKShare 源码 + 动态列名处理）。

绕过 AKShare index_component_sw 对 801170+ 的 KeyError bug。
"""
import requests
import json
import time
import pandas as pd
import urllib3
urllib3.disable_warnings()

URL = "https://www.swsresearch.com/institute_sw/api/index_publish/details/component_stocks/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
}

# 申万一级行业代码列表（31个）
SW_FIRST_LEVEL = [
    ("801010", "农林牧渔"), ("801030", "基础化工"), ("801040", "钢铁"),
    ("801050", "有色金属"), ("801080", "电子"), ("801110", "家用电器"),
    ("801120", "食品饮料"), ("801130", "纺织服饰"), ("801140", "轻工制造"),
    ("801150", "医药生物"), ("801160", "公用事业"), ("801170", "交通运输"),
    ("801180", "房地产"), ("801200", "商贸零售"), ("801210", "社会服务"),
    ("801230", "综合"), ("801710", "建筑材料"), ("801720", "建筑装饰"),
    ("801730", "电力设备"), ("801740", "国防军工"), ("801750", "计算机"),
    ("801760", "传媒"), ("801770", "通信"), ("801780", "银行"),
    ("801790", "非银金融"), ("801880", "汽车"), ("801890", "机械设备"),
    ("801950", "煤炭"), ("801960", "石油石化"), ("801970", "环保"),
    ("801980", "美容护理"),
]

# AKShare 的标准列名映射
COL_MAP = {
    "index": "序号",
    "stockcode": "证券代码",
    "stockname": "证券名称",
    "newweight": "最新权重",
    "beginningdate": "计入日期",
}

def fetch_component(code):
    """直接调用 SW API，返回 DataFrame。动态处理列名差异。"""
    params = {"swindexcode": code, "page": "1", "page_size": "10000"}
    r = requests.get(URL, params=params, headers=HEADERS, verify=False, timeout=30)
    data_json = r.json()
    results = data_json.get("data", {}).get("results", [])
    if not results:
        return pd.DataFrame()

    df = pd.DataFrame(results)
    df.reset_index(inplace=True)
    df["index"] = df["index"] + 1

    # 打印原始列名用于调试
    orig_cols = list(df.columns)

    # 动态映射：先尝试标准映射，不匹配的尝试模糊匹配
    rename_map = {}
    for col in df.columns:
        if col in COL_MAP:
            rename_map[col] = COL_MAP[col]
        else:
            # 模糊匹配（不区分大小写）
            col_lower = str(col).lower()
            for orig, target in COL_MAP.items():
                if orig.lower() in col_lower or col_lower in orig.lower():
                    rename_map[col] = target
                    break

    df.rename(columns=rename_map, inplace=True)

    # 检查是否有标准列名
    target_cols = ["序号", "证券代码", "证券名称", "最新权重", "计入日期"]
    missing = [c for c in target_cols if c not in df.columns]
    if missing:
        # 打印原始列名帮助调试
        print(f"  ⚠️ 缺失列 {missing}, 原始列: {orig_cols}")
        # 尝试从原始列名中找（可能大小写不同）
        for orig_col in orig_cols:
            for target in missing:
                orig_lower = str(orig_col).lower().replace("_", "")
                target_key = next((k for k, v in COL_MAP.items() if v == target), "")
                if target_key and target_key.lower().replace("_", "") in orig_lower:
                    df.rename(columns={orig_col: target}, inplace=True)
                    missing = [c for c in target_cols if c not in df.columns]
                    break

    # 只保留存在的目标列
    existing = [c for c in target_cols if c in df.columns]
    df = df[existing]

    if "计入日期" in df.columns:
        df["计入日期"] = pd.to_datetime(df["计入日期"], errors="coerce").dt.date
    if "最新权重" in df.columns:
        df["最新权重"] = pd.to_numeric(df["最新权重"], errors="coerce")
    return df

# 测试
for code, name in [("801010", "农林牧渔"), ("801150", "医药生物"), ("801170", "交通运输"), ("801780", "银行")]:
    print(f"\n=== {code} {name} ===")
    try:
        df = fetch_component(code)
        print(f"  shape: {df.shape}, columns: {list(df.columns)}")
        if len(df) > 0:
            print(f"  first: {dict(df.iloc[0])}")
    except Exception as e:
        print(f"  ERROR: {e}")
    time.sleep(1)
