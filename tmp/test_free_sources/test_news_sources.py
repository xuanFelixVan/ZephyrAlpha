# -*- coding: utf-8 -*-
"""免费新闻数据源实测脚本（免费无Key类）
1. FinNews (GitHub RSS聚合, pip install finnews)
2. 财经RSS直连 (feedparser, 财联社/东财/新浪/雪球)
3. Inshorts非官方API (requests)
4. AKShare新闻 (对照, 须断开VPN)
"""
import sys
import time
import warnings
warnings.filterwarnings("ignore")

def _ok(name, n, sample=""):
    print(f"  ✅ {name}: {n}条{(' | 样本=' + sample[:80]) if sample else ''}")
    return True

def _fail(name, err):
    print(f"  ❌ {name}: {err}")
    return False

# ============ 1. FinNews (RSS聚合库) ============
def test_finnews():
    print("\n=== 1. FinNews (GitHub scaratozzolo/FinNews, RSS聚合) ===")
    try:
        from finnews.stats import Stats
        from finnews.news import News
        # Stats: 央行/财政部等
        stats = Stats()
        stats.acquire()
        n_stats = len(stats.news)
        sample_stats = stats.news[0][:80] if stats.news else ""
        _ok("FinNews-Stats(央行/财政部)", n_stats, sample_stats)
        r1 = n_stats > 0
    except Exception as e:
        r1 = _fail("FinNews-Stats", str(e)[:120])

    try:
        from finnews.news import News
        news = News()
        news.acquire()
        n_news = len(news.news)
        sample_news = news.news[0][:80] if news.news else ""
        _ok("FinNews-News(财经新闻)", n_news, sample_news)
        r2 = n_news > 0
    except Exception as e:
        r2 = _fail("FinNews-News", str(e)[:120])
    return r1 or r2

# ============ 2. 财经RSS直连 (feedparser) ============
def test_rss_direct():
    print("\n=== 2. 财经RSS直连 (feedparser, 免费) ===")
    import feedparser
    # 国内财经RSS
    cn_feeds = [
        ("财联社-电报", "https://rsshub.app/cls/telegraph"),
        ("东方财富-要闻", "https://rsshub.app/eastmoney/report"),
        ("新浪财经", "https://rsshub.app/finance/sina"),
    ]
    # 国外财经RSS
    ws_feeds = [
        ("Reuters-World", "https://feeds.reuters.com/reuters/worldNews"),
        ("Reuters-Business", "https://feeds.reuters.com/reuters/businessNews"),
        ("Yahoo-Finance", "https://finance.yahoo.com/news/rssindex"),
        ("WSJ-Markets", "https://feeds.wsjonline.com/rss/RSSMarketsMain.xml"),
        ("CNBC-TopNews", "https://www.cnbc.com/id/100003114/device/rss/rss.html"),
        ("Bloomberg-Markets", "https://rsshub.app/bloomberg/markets"),
    ]
    results = []
    for name, url in cn_feeds + ws_feeds:
        try:
            feed = feedparser.parse(url)
            n = len(feed.entries)
            if n > 0:
                sample = feed.entries[0].get("title", "")[:80]
                _ok(name, n, sample)
                results.append(True)
            else:
                results.append(_fail(name, "0条(可能RSSHub需自建或被墙)"))
        except Exception as e:
            results.append(_fail(name, str(e)[:100]))
        time.sleep(0.5)
    return any(results)

# ============ 3. Inshorts非官方API ============
def test_inshorts():
    print("\n=== 3. Inshorts非官方API (免费无Key) ===")
    import requests
    # Inshorts: 印度新闻聚合, 有business分类
    cats = ["business", "world", "technology"]
    results = []
    for cat in cats:
        try:
            url = f"https://inshortsapi.vercel.app/news?category={cat}"
            r = requests.get(url, timeout=10)
            if r.status_code == 200:
                data = r.json()
                n = data.get("count", 0) or len(data.get("data", []))
                articles = data.get("data", [])
                sample = articles[0].get("title", "")[:80] if articles else ""
                _ok(f"Inshorts-{cat}", n, sample)
                results.append(n > 0)
            else:
                results.append(_fail(f"Inshorts-{cat}", f"HTTP {r.status_code}"))
        except Exception as e:
            results.append(_fail(f"Inshorts-{cat}", str(e)[:100]))
        time.sleep(1)
    return any(results)

# ============ 4. AKShare新闻 (对照) ============
def test_akshare_news():
    print("\n=== 4. AKShare新闻 (对照, 须断开VPN) ===")
    results = []
    try:
        import akshare as ak
        df = ak.stock_news_em(symbol="600000")
        n = len(df)
        sample = df.iloc[0].to_dict() if n > 0 else {}
        _ok("AKShare-stock_news_em(东财个股新闻)", n, str(sample)[:80])
        results.append(n > 0)
    except Exception as e:
        results.append(_fail("AKShare-stock_news_em", str(e)[:100]))
    time.sleep(1)
    try:
        import akshare as ak
        df = ak.stock_research_report_em(symbol="600000")
        n = len(df)
        _ok("AKShare-stock_research_report_em(东财研报)", n)
        results.append(n > 0)
    except Exception as e:
        results.append(_fail("AKShare-stock_research_report_em", str(e)[:100]))
    return any(results)

# ============ 5. GDELT (国外免费新闻数据库, 无Key) ============
def test_gdelt():
    print("\n=== 5. GDELT (全球事件数据库, 免费无Key) ===")
    try:
        import requests
        # GDELT DOC 2.0 API, 免费无Key
        url = "https://api.gdeltproject.org/api/v2/doc/doc?query=apple stock&mode=artlist&maxrecords=5&format=json"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            articles = data.get("articles", [])
            n = len(articles)
            sample = articles[0].get("title", "")[:80] if articles else ""
            _ok("GDELT-DOC2.0(全球新闻搜索)", n, sample)
            return n > 0
        else:
            return _fail("GDELT-DOC2.0", f"HTTP {r.status_code}")
    except Exception as e:
        return _fail("GDELT-DOC2.0", str(e)[:120])

if __name__ == "__main__":
    print("=" * 70)
    print("免费新闻数据源实测 (免费无Key类)")
    print("=" * 70)
    r1 = test_finnews()
    r2 = test_rss_direct()
    r3 = test_inshorts()
    r4 = test_akshare_news()
    r5 = test_gdelt()
    print("\n" + "=" * 70)
    print(f"总结: FinNews={'✅' if r1 else '❌'} | RSS直连={'✅' if r2 else '❌'} | "
          f"Inshorts={'✅' if r3 else '❌'} | AKShare新闻={'✅' if r4 else '❌'} | "
          f"GDELT={'✅' if r5 else '❌'}")
