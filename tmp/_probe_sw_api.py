"""直接调用 SW API 探查 801170 返回字段差异。"""
import requests
import json
import urllib3
urllib3.disable_warnings()

url = "https://www.swsresearch.com/institute_sw/api/index_publish/details/component_stocks/"
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/114.0.0.0 Safari/537.36"
}

# 对比成功 vs 失败的行业
for code, name in [("801010", "农林牧渔"), ("801170", "医药生物"), ("801730", "通信")]:
    print(f"\n=== {code} {name} ===")
    params = {"swindexcode": code, "page": "1", "page_size": "10000"}
    r = requests.get(url, params=params, headers=headers, verify=False, timeout=30)
    data = r.json()
    results = data.get("data", {}).get("results", [])
    print(f"  results count: {len(results)}")
    if results:
        # 打印第一条的所有字段
        first = results[0]
        print(f"  fields: {list(first.keys())}")
        print(f"  first record: {first}")
    else:
        # 打印完整响应看结构
        print(f"  full response: {json.dumps(data, ensure_ascii=False, indent=2)[:500]}")
