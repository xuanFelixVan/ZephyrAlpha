# -*- coding: utf-8 -*-
# [BLUEPRINT] N/A | tmp/test_free_sources/download_news_intl.py | §data-source-verification
# [MODULE] tmp.test_free_sources.download_news_intl
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

"""下载国外新闻数据(RSS + AlphaVantage) → JSONL → 导入ClickHouse
财经RSS: Yahoo/SeekingAlpha/MarketWatch/Bloomberg/FT/Investing/Forbes/CNBC
AlphaVantage: NEWS_SENTIMENT (含情感分析, 5次/min)
"""
import sys
import json
import hashlib
import time
import os
from datetime import datetime
import urllib.request
import urllib.parse
from pathlib import Path

# 通过 SSoT secret loader 读取 API key（.env 由 zephyr/__init__.py 自动加载）
sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "src"))
from zephyr.shared.security.secrets import get_secret_or_default

OUTPUT_JSON = r'd:\ZephyrAlpha\tmp\test_free_sources\news_intl.jsonl'

def make_news_id(source, title, publish_time):
    raw = f"{source}|{title}|{publish_time}"
    return hashlib.md5(raw.encode('utf-8')).hexdigest()

def fetch_url(url, headers=None, timeout=15):
    req = urllib.request.Request(url, headers=headers or {'User-Agent': 'Mozilla/5.0'})
    with urllib.request.urlopen(req, timeout=timeout) as resp:
        return resp.read().decode('utf-8', errors='ignore')

all_news = []

# ============ 1. 财经RSS源 (feedparser) ============
print("[1/2] 财经RSS源...")
try:
    import feedparser
    RSS_FEEDS = [
        ('yahoo_finance', 'https://finance.yahoo.com/news/rssindex'),
        ('marketwatch', 'http://feeds.marketwatch.com/marketwatch/topstories/'),
        ('cnbc', 'https://www.cnbc.com/id/100003114/device/rss/rss.html'),
        ('seeking_alpha', 'https://seekingalpha.com/market_currents.xml'),
        ('investing', 'https://www.investing.com/rss/news_1.rss'),
        ('reuters_business', 'https://feeds.reuters.com/reuters/businessNews'),
    ]
    for source_name, feed_url in RSS_FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            count = 0
            for entry in feed.entries[:20]:
                title = entry.get('title', '')
                content = entry.get('summary', '') or entry.get('description', '')[:500]
                pub_str = entry.get('published', '') or entry.get('updated', '')
                # 解析时间
                try:
                    from email.utils import parsedate_to_datetime
                    dt = parsedate_to_datetime(pub_str).replace(tzinfo=None)
                except:
                    dt = datetime.now()
                all_news.append({
                    'news_id': make_news_id(source_name, title, str(dt)),
                    'publish_time': dt.strftime('%Y-%m-%d %H:%M:%S'),
                    'title': title,
                    'content': content[:500],
                    'summary': '',
                    'source': source_name,
                    'source_url': entry.get('link', ''),
                    'category': '财经',
                    'region': 'Global',
                    'language': 'en',
                    'sentiment_score': 0,
                    'sentiment_label': '',
                    'related_symbols': [],
                    'related_tags': [],
                    'raw_data': json.dumps({k: str(v)[:200] for k, v in entry.items()}, ensure_ascii=False)[:2000],
                    'data_source': source_name,
                })
                count += 1
            print(f"  {source_name}: {count} 条")
        except Exception as e:
            print(f"  {source_name}: 失败 {e}")
except ImportError:
    print("  feedparser未安装, 跳过RSS")

# ============ 2. AlphaVantage NEWS_SENTIMENT ============
print("[2/2] AlphaVantage NEWS_SENTIMENT...")
try:
    API_KEY = get_secret_or_default("ALPHAVANTAGE_API_KEY")
    url = f'https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL,MSFT,GOOGL&apikey={API_KEY}&limit=50'
    data = json.loads(fetch_url(url))
    items = data.get('feed', [])
    for item in items:
        title = item.get('title', '')
        content = item.get('summary', '')[:500]
        pub_str = item.get('time_published', '')
        try:
            dt = datetime.strptime(pub_str, '%Y%m%dT%H%M%S')
        except:
            dt = datetime.now()
        # 情感分析
        sentiment_score = float(item.get('overall_sentiment_score', 0))
        sentiment_label = item.get('overall_sentiment_label', '')
        # 关联股票
        ticker_sentiments = item.get('ticker_sentiment', [])
        symbols = [ts.get('ticker', '') for ts in ticker_sentiments if isinstance(ts, dict)]
        all_news.append({
            'news_id': make_news_id('alphavantage', title, str(dt)),
            'publish_time': dt.strftime('%Y-%m-%d %H:%M:%S'),
            'title': title,
            'content': content,
            'summary': content,
            'source': 'alphavantage',
            'source_url': item.get('url', ''),
            'category': '财经',
            'region': 'US',
            'language': 'en',
            'sentiment_score': sentiment_score,
            'sentiment_label': sentiment_label,
            'related_symbols': symbols,
            'related_tags': [],
            'raw_data': json.dumps(item, ensure_ascii=False)[:2000],
            'data_source': 'alphavantage',
        })
    print(f"  AlphaVantage: {len(items)} 条")
except Exception as e:
    print(f"  AlphaVantage失败: {e}")

# ============ 写JSONL ============
print(f"\n总计: {len(all_news)} 条国外新闻")
with open(OUTPUT_JSON, 'w', encoding='utf-8') as f:
    for news in all_news:
        news['related_symbols'] = news['related_symbols'] if news['related_symbols'] else []
        news['related_tags'] = news['related_tags'] if news['related_tags'] else []
        news['sentiment_score'] = float(news['sentiment_score']) if news['sentiment_score'] else 0.0
        f.write(json.dumps(news, ensure_ascii=False) + '\n')

print(f"JSONL文件: {OUTPUT_JSON}")
print("下载完成!")
