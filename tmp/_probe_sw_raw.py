"""直接调用 SW API 并打印原始字段（绕过 AKShare 列名 bug）。

AKShare index_component_sw 对 801170+ 报 KeyError，因为 API 返回的字段名不同。
此脚本直接调用 API 并动态映射字段名。
"""
import requests
import json
import time
import urllib3
urllib3.disable_warnings()

URL = "https://www.swsresearch.com/institute_sw/api/index_publish/details/component_stocks/"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
    "Referer": "https://www.swsresearch.com/",
    "Accept": "application/json, text/plain, */*",
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

def fetch_raw(code):
    """直接调用 SW API，返回原始 results 列表。"""
    params = {"swindexcode": code, "page": "1", "page_size": "10000"}
    r = requests.get(URL, params=params, headers=HEADERS, verify=False, timeout=30)
    if r.status_code != 200:
        return None, f"HTTP {r.status_code}"
    try:
        data = r.json()
    except Exception as e:
        return None, f"JSON parse error: {e}, text[:200]={r.text[:200]}"
    results = data.get("data", {}).get("results", [])
    return results, None

# 测试成功 vs 失败
for code, name in [("801010", "农林牧渔"), ("801150", "医药生物"), ("801170", "交通运输"), ("801780", "银行")]:
    print(f"\n=== {code} {name} ===")
    results, err = fetch_raw(code)
    if err:
        print(f"  ERROR: {err}")
        # 重试一次（可能限流）
        time.sleep(2)
        results, err = fetch_raw(code)
        if err:
            print(f"  RETRY ERROR: {err}")
            continue
    print(f"  results count: {len(results)}")
    if results:
        print(f"  fields: {list(results[0].keys())}")
        print(f"  first: {results[0]}")
    time.sleep(1)
