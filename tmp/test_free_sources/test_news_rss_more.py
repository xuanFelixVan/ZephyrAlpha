# -*- coding: utf-8 -*-
"""补充测试: 更多国外财经RSS + GDELT深度测试"""
import time
import feedparser
import requests
import warnings
warnings.filterwarnings("ignore")

def test_rss(url, name):
    try:
        feed = feedparser.parse(url)
        n = len(feed.entries)
        if n > 0:
            sample = feed.entries[0].get("title", "")[:80]
            print(f"  ✅ {name}: {n}条 | 样本={sample}")
            return True
        else:
            # 检查bozo (解析错误)
            if feed.bozo:
                print(f"  ❌ {name}: 0条(解析错误: {feed.bozo_exception})")
            else:
                print(f"  ❌ {name}: 0条(可能需VPN或已停用)")
            return False
    except Exception as e:
        print(f"  ❌ {name}: {str(e)[:100]}")
        return False

def test_gdelt_deep():
    """GDELT深度测试: 多主题 + 时间范围 + 中文新闻"""
    print("\n=== GDELT深度测试 (免费无Key, 全球事件数据库) ===")
    queries = [
        ("美股-AAPL", "apple stock market", "english"),
        ("中国股市", "china stock market shanghai", "english"),
        ("中文新闻-美联储", "美联储 利率", "chinese"),
        ("中文新闻-A股", "A股 市场", "chinese"),
        ("通用-通胀", "inflation CPI", "english"),
    ]
    results = []
    for name, query, lang in queries:
        try:
            url = (f"https://api.gdeltproject.org/api/v2/doc/doc?"
                   f"query={query}&mode=artlist&maxrecords=5&format=json"
                   f"&sourcelang={lang}")
            r = requests.get(url, timeout=15)
            if r.status_code == 200:
                data = r.json()
                articles = data.get("articles", [])
                n = len(articles)
                sample = articles[0].get("title", "")[:80] if articles else ""
                print(f"  ✅ GDELT-{name}: {n}条 | 样本={sample}")
                results.append(n > 0)
            else:
                print(f"  ❌ GDELT-{name}: HTTP {r.status_code}")
                results.append(False)
        except Exception as e:
            print(f"  ❌ GDELT-{name}: {str(e)[:100]}")
            results.append(False)
        time.sleep(2)  # GDELT限流
    return sum(results), len(results)

if __name__ == "__main__":
    print("=" * 70)
    print("国外财经RSS补充测试 + GDELT深度测试")
    print("=" * 70)

    # 更多国外财经RSS
    print("\n=== 国外财经RSS补充测试 ===")
    ws_feeds = [
        ("SeekingAlpha-Market", "https://seekingalpha.com/market_currents.xml"),
        ("MarketWatch-Top", "https://feeds.content.dowjones.io/public/rss/mw_topstories"),
        ("Bloomberg-Markets", "https://feeds.bloomberg.com/markets/news.rss"),
        ("FT-Markets", "https://www.ft.com/rss/home"),
        ("Investing-News", "https://www.investing.com/rss/news_1.rss"),
        ("Barrons-Stocks", "https://feeds.barrons.com/rss/rssceurope.xml"),
        ("Nasdaq-News", "https://www.nasdaq.com/feed/rssoutlier?category=Stocks"),
        ("Forbes-Business", "https://www.forbes.com/business/feed/"),
        ("Reuters-Business", "https://www.reutersagency.com/feed/?best-topics=business-finance&post_type=best"),
        ("CNBC-World", "https://www.cnbc.com/id/100727362/device/rss/rss.html"),
    ]
    rss_results = []
    for name, url in ws_feeds:
        rss_results.append(test_rss(url, name))
        time.sleep(0.5)

    # GDELT深度测试
    gdelt_ok, gdelt_total = test_gdelt_deep()

    print("\n" + "=" * 70)
    print(f"RSS补充: {sum(rss_results)}/{len(rss_results)} 通过")
    print(f"GDELT深度: {gdelt_ok}/{gdelt_total} 通过")
    print(f"总总结: RSS直连={sum(rss_results)}个可用 | GDELT={gdelt_ok}/{gdelt_total}可用")
