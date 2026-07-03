# -*- coding: utf-8 -*-
# [BLUEPRINT] N/A | tmp/test_free_sources/download_news_key.py | §data-source-verification
# [MODULE] tmp.test_free_sources.download_news_key
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

"""下载需Key新闻源: Finnhub + NewsAPI + Newsdata → JSONL → 导入ClickHouse"""
import sys
import json
import hashlib
import os
from datetime import datetime
import urllib.request
import urllib.parse
from pathlib import Path

# 通过 SSoT secret loader 读取 API key（.env 由 zephyr/__init__.py 自动加载）
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from zephyr.shared.security.secrets import get_secret_or_default

OUTPUT_JSON = r'd:\ZephyrAlpha\tmp\test_free_sources\news_key.jsonl'

def make_news_id(source, title, publish_time):
    raw = f"{source}|{title}|{publish_time}"
    return hashlib.md5(raw.encode('utf-8')).hexdigest()

def fetch_json(url, headers=None, timeout=15):
    req = urllib.request.Request(url, headers=headers or {'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return json.loads(resp.read().decode('utf-8'))

all_news = []

# ============ 1. Finnhub 市场新闻 ============
print("[1/3] Finnhub...")
try:
    API_KEY = get_secret_or_default("FINNHUB_API_KEY")
    url = f'https://finnhub.io/api/v1/news?category=general&token={API_KEY}'
    data = fetch_json(url)
    for item in data[:50]:
        title = item.get('headline', '')
        content = item.get('summary', '')[:500]
        pub_ts = item.get('datetime', 0)
        try:
            dt = datetime.fromtimestamp(int(pub_ts))
        except:
            dt = datetime.now()
        all_news.append({
            'news_id': make_news_id('finnhub', title, str(dt)),
            'publish_time': dt.strftime('%Y-%m-%d %H:%M:%S'),
            'title': title,
            'content': content,
            'summary': content,
            'source': 'finnhub',
            'source_url': item.get('url', ''),
            'category': '财经',
            'region': 'Global',
            'language': 'en',
            'sentiment_score': 0,
            'sentiment_label': '',
            'related_symbols': [item.get('related', '')] if item.get('related') else [],
            'related_tags': [],
            'raw_data': json.dumps(item, ensure_ascii=False)[:2000],
            'data_source': 'finnhub',
        })
    print(f"  Finnhub: {min(len(data), 50)} 条")
except Exception as e:
    print(f"  Finnhub失败: {e}")

# ============ 2. NewsAPI ============
print("[2/3] NewsAPI...")
try:
    API_KEY = get_secret_or_default("NEWSAPI_KEY")
    # everything 端点(搜索财经新闻)
    url = f'https://newsapi.org/v2/everything?q=finance+OR+stock+OR+market&language=en&sortBy=publishedAt&pageSize=50&apiKey={API_KEY}'
    data = fetch_json(url)
    items = data.get('articles', [])
    for item in items:
        title = item.get('title', '')
        content = item.get('description', '') or item.get('content', '')[:500]
        pub_str = item.get('publishedAt', '')
        try:
            dt = datetime.strptime(pub_str, '%Y-%m-%dT%H:%M:%SZ')
        except:
            dt = datetime.now()
        src_name = item.get('source', {}).get('name', 'newsapi')
        all_news.append({
            'news_id': make_news_id('newsapi', title, str(dt)),
            'publish_time': dt.strftime('%Y-%m-%d %H:%M:%S'),
            'title': title,
            'content': content[:500] if content else '',
            'summary': content[:200] if content else '',
            'source': 'newsapi',
            'source_url': item.get('url', ''),
            'category': '财经',
            'region': 'Global',
            'language': 'en',
            'sentiment_score': 0,
            'sentiment_label': '',
            'related_symbols': [],
            'related_tags': [],
            'raw_data': json.dumps(item, ensure_ascii=False)[:2000],
            'data_source': 'newsapi',
        })
    print(f"  NewsAPI: {len(items)} 条")
except Exception as e:
    print(f"  NewsAPI失败: {e}")

# ============ 3. Newsdata.io ============
print("[3/3] Newsdata.io...")
try:
    API_KEY = get_secret_or_default("NEWSDATA_API_KEY")
    url = f'https://newsdata.io/api/1/news?apikey={API_KEY}&category=business&language=en&size=50'
    data = fetch_json(url)
    items = data.get('results', [])
    for item in items:
        title = item.get('title', '')
        content = item.get('description', '') or item.get('content', '')[:500]
        pub_str = item.get('pubDate', '')
        try:
            dt = datetime.strptime(pub_str, '%Y-%m-%d %H:%M:%S')
        except:
            try:
                dt = datetime.fromisoformat(pub_str.replace('Z', ''))
            except:
                dt = datetime.now()
        all_news.append({
            'news_id': make_news_id('newsdata', title, str(dt)),
            'publish_time': dt.strftime('%Y-%m-%d %H:%M:%S'),
            'title': title,
            'content': content[:500] if content else '',
            'summary': content[:200] if content else '',
            'source': 'newsdata',
            'source_url': item.get('link', ''),
            'category': '财经',
            'region': 'Global',
            'language': 'en',
            'sentiment_score': 0,
            'sentiment_label': '',
            'related_symbols': [],
            'related_tags': item.get('keywords', []) if isinstance(item.get('keywords'), list) else [],
            'raw_data': json.dumps(item, ensure_ascii=False)[:2000],
            'data_source': 'newsdata',
        })
    print(f"  Newsdata: {len(items)} 条")
except Exception as e:
    print(f"  Newsdata失败: {e}")

# ============ 写JSONL ============
print(f"\n总计: {len(all_news)} 条")
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    for news in all_news:
        news['related_symbols'] = news['related_symbols'] if news['related_symbols'] else []
        news['related_tags'] = news['related_tags'] if news['related_tags'] else []
        news['sentiment_score'] = float(news['sentiment_score']) if news['sentiment_score'] else 0.0
        f.write(json.dumps(news, ensure_ascii=False) + '\n')

print(f"JSONL文件: {OUTPUT_JSON}")
print("下载完成!")
