# -*- coding: utf-8 -*-
"""Tiingo 重测 — 用正确的认证方式(Header token 或 URL token=)"""
import sys
import requests
import time
from pathlib import Path

# 通过 SSoT secret loader 读取 API key（.env 由 zephyr/__init__.py 自动加载）
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from zephyr.shared.security.secrets import get_secret_or_default

TIINGO_KEY = get_secret_or_default("TIINGO_API_KEY")

print("=== Tiingo 重测（3种认证方式）===")

# 方式1: URL token= 参数
print("\n[方式1] URL token= 参数:")
try:
    url = f"https://api.tiingo.com/tiingo/news?token={TIINGO_KEY}&limit=5"
    r = requests.get(url, timeout=15)
    print(f"  HTTP {r.status_code}: {r.text[:150]}")
    if r.status_code == 200:
        articles = r.json()
        print(f"  ✅ Tiingo-News: {len(articles)}条 | 样本={articles[0].get('title','')[:80]}")
except Exception as e:
    print(f"  ❌ {e}")

time.sleep(2)

# 方式2: Header Authorization: Token
print("\n[方式2] Header Authorization: Token:")
try:
    url = "https://api.tiingo.com/tiingo/news?limit=5"
    headers = {"Authorization": f"Token {TIINGO_KEY}"}
    r = requests.get(url, headers=headers, timeout=15)
    print(f"  HTTP {r.status_code}: {r.text[:150]}")
    if r.status_code == 200:
        articles = r.json()
        print(f"  ✅ Tiingo-News: {len(articles)}条 | 样本={articles[0].get('title','')[:80]}")
except Exception as e:
    print(f"  ❌ {e}")

time.sleep(2)

# 方式3: Header + 日K线测试
print("\n[方式3] Header + 日K线(AAPL):")
try:
    url = "https://api.tiingo.com/tiingo/daily/AAPL/prices?startDate=2025-06-01&endDate=2025-07-01"
    headers = {"Authorization": f"Token {TIINGO_KEY}"}
    r = requests.get(url, headers=headers, timeout=15)
    print(f"  HTTP {r.status_code}: {r.text[:150]}")
    if r.status_code == 200:
        data = r.json()
        print(f"  ✅ Tiingo-Daily: {len(data)}行 | 样本={str(data[0])[:100]}")
except Exception as e:
    print(f"  ❌ {e}")

time.sleep(2)

# 方式4: 检查账户状态
print("\n[方式4] 检查Tiingo账户订阅状态:")
try:
    url = "https://api.tiingo.com/api/test/"
    headers = {"Authorization": f"Token {TIINGO_KEY}"}
    r = requests.get(url, headers=headers, timeout=15)
    print(f"  HTTP {r.status_code}: {r.text[:200]}")
except Exception as e:
    print(f"  ❌ {e}")
