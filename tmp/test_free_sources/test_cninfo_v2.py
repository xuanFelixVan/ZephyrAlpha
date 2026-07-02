# -*- coding: utf-8 -*-
"""巨潮资讯网公告API测试(修正参数: 600000是上交所sse不是szse)
巨潮是证监会指定信息披露平台,有完整公告历史
"""
import requests
import json
import time
import warnings
warnings.filterwarnings("ignore")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "zh-CN,zh;q=0.9",
    "Content-Type": "application/x-www-form-urlencoded",
    "Referer": "http://www.cninfo.com.cn/new/commonUrl?url=disclosure/list/notice",
    "Origin": "http://www.cninfo.com.cn",
}

def test_cninfo(stock_code, org_id, column, name):
    """测试巨潮公告API"""
    print(f"\n--- {name}({stock_code}, column={column}) ---")
    url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
    data = {
        "stock": f"{stock_code},{org_id}",
        "tabName": "fulltext",
        "pageSize": 10,
        "pageNum": 1,
        "column": column,
        "category": "",
        "plate": "",
        "seDate": "2026-06-01~2026-07-03",
        "searchkey": "",
        "secid": "",
        "sortName": "",
        "sortType": "",
        "isHLtitle": "true",
    }
    try:
        r = requests.post(url, data=data, headers=HEADERS, timeout=15)
        if r.status_code == 200:
            resp = r.json()
            articles = resp.get("announcements", [])
            n = len(articles)
            print(f"✅ {name}: {n}条")
            if n > 0:
                first = articles[0]
                print(f"   样本: title={first.get('announcementTitle','')[:50]}")
                print(f"         type={first.get('announcementType','')}")
                print(f"         time={first.get('announcementTime','')}")
                print(f"         secCode={first.get('secCode','')}")
                print(f"   完整字段: {list(first.keys())}")
                print(f"\n   第1条完整JSON:")
                print(f"   {json.dumps(first, ensure_ascii=False, indent=2, default=str)[:1000]}")
            return n > 0
        else:
            print(f"❌ {name}: HTTP {r.status_code}: {r.text[:80]}")
            return False
    except Exception as e:
        print(f"❌ {name}: {str(e)[:100]}")
        return False

# 测试多个股票(上交所sse/深交所szse)
print("="*70)
print("巨潮资讯网公告API测试 (证监会指定信息披露平台)")
print("="*70)

# 600000浦发银行 - 上交所SSE
r1 = test_cninfo("600000", "gsshz0000001", "sse", "浦发银行(上交所)")
time.sleep(1)

# 000001平安银行 - 深交所SZSE
r2 = test_cninfo("000001", "gssz0000001", "szse", "平安银行(深交所)")
time.sleep(1)

# 300750宁德时代 - 深交所创业板
r3 = test_cninfo("300750", "9900028528", "szse", "宁德时代(创业板)")

# 全市场最新公告(不指定股票)
print("\n--- 全市场最新公告(不指定股票) ---")
url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
data = {
    "tabName": "fulltext",
    "pageSize": 10,
    "pageNum": 1,
    "column": "sse",  # 上交所
    "category": "",
    "plate": "",
    "seDate": "2026-07-01~2026-07-03",
    "searchkey": "",
    "secid": "",
    "sortName": "",
    "sortType": "",
    "isHLtitle": "true",
}
try:
    r = requests.post(url, data=data, headers=HEADERS, timeout=15)
    if r.status_code == 200:
        resp = r.json()
        articles = resp.get("announcements", [])
        n = len(articles)
        print(f"✅ 全市场最新公告(上交所): {n}条")
        if n > 0:
            for i, a in enumerate(articles[:3]):
                print(f"   {i+1}. [{a.get('secCode','')}] {a.get('announcementTitle','')[:50]}")
    else:
        print(f"❌ 全市场: HTTP {r.status_code}")
except Exception as e:
    print(f"❌ 全市场: {e}")

print(f"\n{'='*70}")
print(f"总结: 浦发={('✅' if r1 else '❌')} | 平安={('✅' if r2 else '❌')} | 宁德={('✅' if r3 else '❌')}")
