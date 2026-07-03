# -*- coding: utf-8 -*-
# [BLUEPRINT] N/A | tmp/test_free_sources/show_news_format.py | §data-source-verification
# [MODULE] tmp.test_free_sources.show_news_format
# [DOMAIN] D_DATA
# [DEPENDENCIES] zephyr.shared.security.secrets; requests
# [CONSUMERS]
# [STARTUP] manual
# [MATURITY] prototype
# [INVARIANTS] 一次性数据源验证脚本——新闻 API 验证
# [MODIFY-GUARD]
# [STABILITY] evolving
# [SAFETY] L
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] exit 0=验证完成
# [TESTS]
# [TTL] task_bound

"""打印各新闻源的实际返回数据格式（完整字段）"""
import sys
import requests
import re
import json
import time
import warnings
from pathlib import Path
warnings.filterwarnings("ignore")

# 通过 SSoT secret loader 读取 API key（.env 由 zephyr/__init__.py 自动加载）
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from zephyr.shared.security.secrets import get_secret_or_default

HEADERS = {"User-Agent": "Mozilla/5.0", "Accept": "application/json, */*",
           "Accept-Language": "zh-CN,zh;q=0.9"}

def show_format(name, data, max_depth=2, max_items=1):
    """美观打印数据结构"""
    print(f"\n{'='*70}")
    print(f"【{name}】数据格式")
    print(f"{'='*70}")
    if isinstance(data, list):
        print(f"类型: list, 共{len(data)}条")
        for i, item in enumerate(data[:max_items]):
            print(f"\n--- 第{i+1}条 ---")
            print(json.dumps(item, ensure_ascii=False, indent=2, default=str)[:1500])
    elif isinstance(data, dict):
        print(f"类型: dict, 顶层字段={list(data.keys())}")
        print(json.dumps(data, ensure_ascii=False, indent=2, default=str)[:2000])
    else:
        print(f"类型: {type(data)}")
        print(str(data)[:1500])

# 1. 东方财富快讯
print("\n" + "#"*70)
print("# 1. 东方财富快讯")
print("#"*70)
try:
    url = "https://newsapi.eastmoney.com/kuaixun/v1/getlist_102_ajaxResult_50_1_.html"
    r = requests.get(url, headers={**HEADERS, "Referer": "https://kuaixun.eastmoney.com/"}, timeout=10)
    match = re.search(r'var\s+ajaxResult\s*=\s*(\{.*\})', r.text, re.DOTALL)
    if match:
        data = json.loads(match.group(1))
        articles = data.get("LivesList", data.get("Data", []))
        if not articles:
            for k, v in data.items():
                if isinstance(v, list) and len(v) > 0:
                    articles = v
                    break
        show_format("东方财富快讯", articles, max_items=2)
except Exception as e:
    print(f"❌ {e}")

time.sleep(1)

# 2. 同花顺快讯
print("\n" + "#"*70)
print("# 2. 同花顺快讯")
print("#"*70)
try:
    url = "https://news.10jqka.com.cn/tapp/news/push/stock/?page=1&tag=&track=website&pagesize=3"
    r = requests.get(url, headers={**HEADERS, "Referer": "https://news.10jqka.com.cn/"}, timeout=10)
    data = r.json()
    articles = data.get("data", {}).get("list", [])
    show_format("同花顺快讯", articles, max_items=2)
except Exception as e:
    print(f"❌ {e}")

time.sleep(1)

# 3. 华尔街见闻
print("\n" + "#"*70)
print("# 3. 华尔街见闻")
print("#"*70)
try:
    url = "https://api-one-wscn.awtmt.com/apiv1/content/lives?channel=global-channel&client=pc&limit=3"
    r = requests.get(url, headers={**HEADERS, "Referer": "https://wallstreetcn.com/live"}, timeout=10)
    data = r.json()
    items = data.get("data", {}).get("items", [])
    show_format("华尔街见闻", items, max_items=2)
except Exception as e:
    print(f"❌ {e}")

time.sleep(1)

# 4. 金十数据
print("\n" + "#"*70)
print("# 4. 金十数据")
print("#"*70)
try:
    r = requests.get("https://www.jin10.com/", headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    script_match = re.search(r'(?:https:)?//www\.jin10\.com/new/js/index\.[^"\'\ ]+\.js', r.text)
    script_url = script_match.group(0)
    if script_url.startswith("//"): script_url = "https:" + script_url
    r2 = requests.get(script_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
    app_id = re.search(r'"x-app-id":"([^"]+)"', r2.text).group(1)
    url = "https://flash-api.jin10.com/get_flash_list?channel=-8200&limit=3"
    r3 = requests.get(url, headers={"User-Agent": "Mozilla/5.0", "x-app-id": app_id,
                                    "x-version": "1.0.0", "Referer": "https://www.jin10.com/"}, timeout=10)
    data = r3.json()
    articles = data.get("data", [])
    show_format("金十数据", articles, max_items=2)
except Exception as e:
    print(f"❌ {e}")

time.sleep(1)

# 5. NewsAPI.org (需Key)
print("\n" + "#"*70)
print("# 5. NewsAPI.org (需Key)")
print("#"*70)
try:
    NEWSAPI_KEY = get_secret_or_default("NEWSAPI_KEY")
    url = f"https://newsapi.org/v2/everything?q=apple stock&apiKey={NEWSAPI_KEY}&pageSize=2&language=en"
    r = requests.get(url, timeout=15)
    data = r.json()
    articles = data.get("articles", [])
    show_format("NewsAPI.org", articles, max_items=2)
except Exception as e:
    print(f"❌ {e}")

time.sleep(2)

# 6. Alpha Vantage (需Key, 含情感分析)
print("\n" + "#"*70)
print("# 6. Alpha Vantage NEWS_SENTIMENT (需Key, 含情感分析)")
print("#"*70)
try:
    ALPHAVANT_KEY = get_secret_or_default("ALPHAVANTAGE_API_KEY")
    url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey={ALPHAVANT_KEY}&limit=2"
    r = requests.get(url, timeout=15)
    data = r.json()
    feed = data.get("feed", [])
    show_format("Alpha Vantage (含情感分析)", feed, max_items=2)
except Exception as e:
    print(f"❌ {e}")

time.sleep(13)

# 7. Finnhub (需Key)
print("\n" + "#"*70)
print("# 7. Finnhub 市场新闻 (需Key)")
print("#"*70)
try:
    FINNHUB_KEY = get_secret_or_default("FINNHUB_API_KEY")
    url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_KEY}"
    r = requests.get(url, timeout=15)
    articles = r.json()
    show_format("Finnhub", articles, max_items=2)
except Exception as e:
    print(f"❌ {e}")

time.sleep(1)

# 8. AKShare 东财个股新闻
print("\n" + "#"*70)
print("# 8. AKShare 东财个股新闻")
print("#"*70)
try:
    import akshare as ak
    df = ak.stock_news_em(symbol="600000")
    print(f"\n类型: DataFrame, 共{len(df)}行, 列={list(df.columns)}")
    print(f"\n--- 第1条(转dict) ---")
    print(json.dumps(df.iloc[0].to_dict(), ensure_ascii=False, indent=2, default=str)[:1500])
except Exception as e:
    print(f"❌ {e}")

print("\n" + "="*70)
print("格式展示完毕")
