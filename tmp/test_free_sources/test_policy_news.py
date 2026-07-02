# -*- coding: utf-8 -*-
"""测试: 1)财联社签名修复 2)证监会要闻 3)中国政府网政策 4)央行政策"""
import requests
import re
import json
import hashlib
import time
from urllib.parse import urlencode
import warnings
warnings.filterwarnings("ignore")

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
           "Accept": "text/html,application/json", "Accept-Language": "zh-CN,zh;q=0.9"}

# ============ 1. 财联社签名修复测试 ============
print("="*70)
print("1. 财联社电报 (签名修复, sv=8.7.9)")
print("="*70)

def cls_serialize_sign_value(value, key):
    """财联社签名序列化(从china-finance-rss源码)"""
    if value is None:
        return None
    if isinstance(value, (str, int, float, bool)):
        return f'{key}={value}'
    if isinstance(value, list):
        if not value:
            return f'{key}[]'
        return '&'.join(filter(None, (
            cls_serialize_sign_value(item, f'{key}[{index}]')
            for index, item in enumerate(value)
        )))
    if isinstance(value, dict):
        return '&'.join(filter(None, (
            cls_serialize_sign_value(value[item_key], f'{key}[{item_key}]')
            for item_key in sorted(value, key=lambda item: str(item).upper())
        )))
    return None

def cls_sign_params(params):
    """财联社签名算法: SHA1(serialized) -> MD5(sha1)"""
    serialized = '&'.join(filter(None, (
        cls_serialize_sign_value(params[key], key)
        for key in sorted(params, key=lambda item: str(item).upper())
    )))
    sha1_digest = hashlib.sha1(serialized.encode('utf-8')).hexdigest()
    return hashlib.md5(sha1_digest.encode('utf-8')).hexdigest()

try:
    url = 'https://www.cls.cn/v1/roll/get_roll_list'
    params = {
        'refresh_type': 1,
        'rn': 10,
        'last_time': 0,
        'os': 'web',
        'sv': '8.7.9',
        'app': 'CailianpressWeb',
    }
    params['sign'] = cls_sign_params(params)
    full_url = f'{url}?{urlencode(params)}'
    r = requests.get(full_url, headers={**HEADERS, "Referer": "https://www.cls.cn/telegraph"}, timeout=10)
    if r.status_code == 200:
        data = r.json()
        roll_data = data.get("data", {}).get("roll_data", [])
        n = len(roll_data)
        print(f"✅ 财联社电报(签名修复): {n}条")
        if n > 0:
            first = roll_data[0]
            print(f"   样本: title={first.get('title','')[:60]}")
            print(f"         brief={first.get('brief','')[:80]}")
            print(f"         ctime={first.get('ctime','')}")
            print(f"         极重要={first.get('isImportant','')}")
            print(f"   完整字段: {list(first.keys())}")
            print(f"\n   第1条完整JSON:")
            print(f"   {json.dumps(first, ensure_ascii=False, indent=2)[:800]}")
    else:
        print(f"❌ 财联社: HTTP {r.status_code}: {r.text[:100]}")
except Exception as e:
    print(f"❌ 财联社: {e}")

time.sleep(1)

# ============ 2. 证监会要闻 ============
print("\n" + "="*70)
print("2. 证监会要闻 (csrc.gov.cn)")
print("="*70)
try:
    url = "http://www.csrc.gov.cn/csrc/c100028/index.shtml"
    r = requests.get(url, headers=HEADERS, timeout=10)
    if r.status_code == 200:
        r.encoding = 'utf-8'
        # 提取要闻链接(标题+日期)
        matches = re.findall(r'<a[^>]*href="([^"]+)"[^>]*>([^<]+)</a>[^<]*<span[^>]*>(\d{4}-\d{2}-\d{2})', r.text)
        if not matches:
            # 尝试其他格式
            matches = re.findall(r'href="(/csrc/[^"]+\.shtml)"[^>]*>([^<]{8,})</a>', r.text)
            matches = [(m[0], m[1], '') for m in matches[:10]]
        print(f"✅ 证监会要闻页面可访问, 提取到{len(matches)}条")
        for i, (link, title, date) in enumerate(matches[:5]):
            print(f"   {i+1}. [{date}] {title.strip()[:50]}")
            print(f"      链接: http://www.csrc.gov.cn{link if link.startswith('/') else '/'+link}")
    else:
        print(f"❌ 证监会要闻: HTTP {r.status_code}")
except Exception as e:
    print(f"❌ 证监会要闻: {e}")

time.sleep(1)

# ============ 3. 证监会行政处罚 ============
print("\n" + "="*70)
print("3. 证监会行政处罚 (csrc.gov.cn 政务信息)")
print("="*70)
try:
    url = "http://www.csrc.gov.cn/csrc/c105939/index.shtml"
    r = requests.get(url, headers=HEADERS, timeout=10)
    if r.status_code == 200:
        r.encoding = 'utf-8'
        matches = re.findall(r'href="(/csrc/[^"]+\.shtml)"[^>]*title="([^"]+)"', r.text)
        if not matches:
            matches = re.findall(r'href="(/csrc/[^"]+\.shtml)"[^>]*>([^<]{10,})</a>', r.text)
        print(f"✅ 证监会行政处罚页面可访问, 提取到{len(matches)}条")
        for i, (link, title) in enumerate(matches[:5]):
            print(f"   {i+1}. {title.strip()[:50]}")
            print(f"      http://www.csrc.gov.cn{link}")
    else:
        print(f"❌ 证监会行政处罚: HTTP {r.status_code}")
except Exception as e:
    print(f"❌ 证监会行政处罚: {e}")

time.sleep(1)

# ============ 4. 中国政府网政策 ============
print("\n" + "="*70)
print("4. 中国政府网政策文件 (gov.cn)")
print("="*70)
try:
    url = "https://www.gov.cn/zhengce/"
    r = requests.get(url, headers=HEADERS, timeout=10)
    if r.status_code == 200:
        r.encoding = 'utf-8'
        matches = re.findall(r'href="(/zhengce/[^"]+\.htm)"[^>]*>([^<]{8,})</a>', r.text)
        print(f"✅ 中国政府网政策页面可访问, 提取到{len(matches)}条")
        for i, (link, title) in enumerate(matches[:5]):
            print(f"   {i+1}. {title.strip()[:50]}")
            print(f"      https://www.gov.cn{link}")
    else:
        print(f"❌ 中国政府网: HTTP {r.status_code}")
except Exception as e:
    print(f"❌ 中国政府网: {e}")

time.sleep(1)

# ============ 5. 中国人民银行政策 ============
print("\n" + "="*70)
print("5. 中国人民银行政策 (pbc.gov.cn)")
print("="*70)
try:
    url = "http://www.pbc.gov.cn/zhengcehuobisi/125207/index.html"
    r = requests.get(url, headers=HEADERS, timeout=10)
    if r.status_code == 200:
        r.encoding = 'utf-8'
        matches = re.findall(r'href="(/zhengcehuobisi/[^"]+\.html)"[^>]*>([^<]{8,})</a>', r.text)
        if not matches:
            matches = re.findall(r'href="([^"]+\.html)"[^>]*title="([^"]+)"', r.text)
            matches = [(m[0], m[1]) for m in matches[:10]]
        print(f"✅ 央行政策页面可访问, 提取到{len(matches)}条")
        for i, (link, title) in enumerate(matches[:5]):
            print(f"   {i+1}. {title.strip()[:50]}")
            print(f"      链接: {link if link.startswith('http') else 'http://www.pbc.gov.cn'+link}")
    else:
        print(f"❌ 央行政策: HTTP {r.status_code}")
except Exception as e:
    print(f"❌ 央行政策: {e}")

time.sleep(1)

# ============ 6. AKShare 政策接口 ============
print("\n" + "="*70)
print("6. AKShare 政策相关接口测试")
print("="*70)
try:
    import akshare as ak
    # 测试宏观政策新闻
    print("   测试: news_economic_baidu (百度财经经济新闻)")
    try:
        df = ak.news_economic_baidu(symbol="全部")
        print(f"   ✅ 百度财经经济新闻: {len(df)}条, 列={list(df.columns)}")
        print(f"      样本: {df.iloc[0].to_dict()}")
    except Exception as e:
        print(f"   ❌ 百度财经经济新闻: {str(e)[:80]}")
    time.sleep(1)
    print("\n   测试: news_cctv (央视新闻联播)")
    try:
        df = ak.news_cctv(date="20260702")
        print(f"   ✅ 央视新闻联播: {len(df)}条, 列={list(df.columns)}")
        if len(df) > 0:
            print(f"      样本标题: {df.iloc[0].get('title','')[:60]}")
    except Exception as e:
        print(f"   ❌ 央视新闻联播: {str(e)[:80]}")
    time.sleep(1)
    print("\n   测试: macro_china_policy_minute (中国政策分钟)")
    try:
        df = ak.macro_china_policy_minute()
        print(f"   ✅ 中国政策分钟: {len(df)}条, 列={list(df.columns)}")
        if len(df) > 0:
            print(f"      样本: {df.iloc[0].to_dict()}")
    except Exception as e:
        print(f"   ❌ 中国政策分钟: {str(e)[:80]}")
except ImportError:
    print("   ❌ akshare未安装")
except Exception as e:
    print(f"   ❌ {e}")

print("\n" + "="*70)
print("测试完毕")
