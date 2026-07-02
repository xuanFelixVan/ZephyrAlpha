# -*- coding: utf-8 -*-
"""需Key新闻源实测脚本（5个源，用户已注册）
1. NewsAPI.org   - Key: 5f54c041aa2a4781a66f8cc6194e1272
2. Tiingo        - Key: 67daaf30a656486e0108a94c98267fe7ccbdb5f1
3. Finnhub       - Key: d74lr19r01qg1eo5vib0d74lr19r01qg1eo5vibg
4. Newsdata.io   - Key: pub_b0314d331fa44f30a649189362c9d5e7
5. Alpha Vantage - Key: 1RASLEIEKE35Q9KB
"""
import requests
import time
import warnings
warnings.filterwarnings("ignore")

# ============ API Keys (用户注册) ============
NEWSAPI_KEY    = "5f54c041aa2a4781a66f8cc6194e1272"
TIINGO_KEY     = "67daaf30a656486e0108a94c98267fe7ccbdb5f1"
FINNHUB_KEY    = "d74lr19r01qg1eo5vib0d74lr19r01qg1eo5vibg"
NEWSDATA_KEY   = "pub_b0314d331fa44f30a649189362c9d5e7"
ALPHAVANT_KEY  = "1RASLEIEKE35Q9KB"

def _ok(name, n, sample=""):
    print(f"  ✅ {name}: {n}条{(' | 样本=' + sample[:100]) if sample else ''}")
    return True

def _fail(name, err):
    print(f"  ❌ {name}: {err}")
    return False

# ============ 1. NewsAPI.org ============
def test_newsapi():
    print("\n=== 1. NewsAPI.org (全球新闻, 100请求/天) ===")
    results = []
    # 测试1: 全球财经新闻搜索
    try:
        url = f"https://newsapi.org/v2/everything?q=stock market&apiKey={NEWSAPI_KEY}&pageSize=5&language=en"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            n = data.get("totalResults", 0)
            articles = data.get("articles", [])
            sample = articles[0].get("title", "") if articles else ""
            _ok("NewsAPI-everything(全球财经)", n, sample)
            results.append(True)
        else:
            results.append(_fail("NewsAPI-everything", f"HTTP {r.status_code}: {r.text[:100]}"))
    except Exception as e:
        results.append(_fail("NewsAPI-everything", str(e)[:120]))
    time.sleep(1)
    # 测试2: 头条新闻
    try:
        url = f"https://newsapi.org/v2/top-headlines?category=business&apiKey={NEWSAPI_KEY}&pageSize=5&country=us"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            n = data.get("totalResults", 0)
            articles = data.get("articles", [])
            sample = articles[0].get("title", "") if articles else ""
            _ok("NewsAPI-top-headlines(商业头条)", n, sample)
            results.append(True)
        else:
            results.append(_fail("NewsAPI-top-headlines", f"HTTP {r.status_code}: {r.text[:100]}"))
    except Exception as e:
        results.append(_fail("NewsAPI-top-headlines", str(e)[:120]))
    return any(results)

# ============ 2. Tiingo ============
def test_tiingo():
    print("\n=== 2. Tiingo (70M+文章20年历史) ===")
    results = []
    # 测试1: Tiingo News API
    try:
        url = f"https://api.tiingo.com/tiingo/news?apiKey={TIINGO_KEY}&limit=5"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            articles = r.json()
            n = len(articles)
            sample = articles[0].get("title", "") if articles else ""
            _ok("Tiingo-News(财经新闻)", n, sample)
            results.append(True)
        else:
            results.append(_fail("Tiingo-News", f"HTTP {r.status_code}: {r.text[:100]}"))
    except Exception as e:
        results.append(_fail("Tiingo-News", str(e)[:120]))
    time.sleep(1)
    # 测试2: Tiingo 日K线（验证Key是否支持行情数据）
    try:
        url = f"https://api.tiingo.com/tiingo/daily/AAPL/prices?apiKey={TIINGO_KEY}&startDate=2025-06-01&endDate=2025-07-01"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            n = len(data)
            sample = str(data[0])[:100] if data else ""
            _ok("Tiingo-Daily(AAPL日K线)", n, sample)
            results.append(True)
        else:
            results.append(_fail("Tiingo-Daily", f"HTTP {r.status_code}: {r.text[:100]}"))
    except Exception as e:
        results.append(_fail("Tiingo-Daily", str(e)[:120]))
    return any(results)

# ============ 3. Finnhub ============
def test_finnhub():
    print("\n=== 3. Finnhub (公司级新闻+股票关联) ===")
    results = []
    # 测试1: 公司新闻
    try:
        url = f"https://finnhub.io/api/v1/company-news?symbol=AAPL&from=2025-06-01&to=2025-07-01&token={FINNHUB_KEY}"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            articles = r.json()
            n = len(articles)
            sample = articles[0].get("headline", "") if articles else ""
            _ok("Finnhub-company-news(AAPL)", n, sample)
            results.append(True)
        else:
            results.append(_fail("Finnhub-company-news", f"HTTP {r.status_code}: {r.text[:100]}"))
    except Exception as e:
        results.append(_fail("Finnhub-company-news", str(e)[:120]))
    time.sleep(1)
    # 测试2: 市场新闻
    try:
        url = f"https://finnhub.io/api/v1/news?category=general&token={FINNHUB_KEY}"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            articles = r.json()
            n = len(articles)
            sample = articles[0].get("headline", "") if articles else ""
            _ok("Finnhub-market-news(市场新闻)", n, sample)
            results.append(True)
        else:
            results.append(_fail("Finnhub-market-news", f"HTTP {r.status_code}: {r.text[:100]}"))
    except Exception as e:
        results.append(_fail("Finnhub-market-news", str(e)[:120]))
    time.sleep(1)
    # 测试3: 公司基本面（验证Key是否支持行情数据）
    try:
        url = f"https://finnhub.io/api/v1/quote?symbol=AAPL&token={FINNHUB_KEY}"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            price = data.get("c", 0)  # current price
            _ok("Finnhub-quote(AAPL实时报价)", 1, f"price={price}")
            results.append(price > 0)
        else:
            results.append(_fail("Finnhub-quote", f"HTTP {r.status_code}: {r.text[:100]}"))
    except Exception as e:
        results.append(_fail("Finnhub-quote", str(e)[:120]))
    return any(results)

# ============ 4. Newsdata.io ============
def test_newsdata():
    print("\n=== 4. Newsdata.io (200请求/天) ===")
    results = []
    # 测试1: 财经新闻
    try:
        url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_KEY}&category=business&language=en&size=5"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            articles = data.get("results", [])
            n = len(articles)
            sample = articles[0].get("title", "") if articles else ""
            _ok("Newsdata-business(财经新闻)", n, sample)
            results.append(n > 0)
        else:
            results.append(_fail("Newsdata-business", f"HTTP {r.status_code}: {r.text[:100]}"))
    except Exception as e:
        results.append(_fail("Newsdata-business", str(e)[:120]))
    time.sleep(1)
    # 测试2: 股市新闻
    try:
        url = f"https://newsdata.io/api/1/news?apikey={NEWSDATA_KEY}&q=stock market&language=en&size=5"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            articles = data.get("results", [])
            n = len(articles)
            sample = articles[0].get("title", "") if articles else ""
            _ok("Newsdata-stock(股市新闻)", n, sample)
            results.append(n > 0)
        else:
            results.append(_fail("Newsdata-stock", f"HTTP {r.status_code}: {r.text[:100]}"))
    except Exception as e:
        results.append(_fail("Newsdata-stock", str(e)[:120]))
    return any(results)

# ============ 5. Alpha Vantage ============
def test_alpha_vantage():
    print("\n=== 5. Alpha Vantage (新闻+情感分析, 5次/min) ===")
    results = []
    # 测试1: News & Sentiment
    try:
        url = f"https://www.alphavantage.co/query?function=NEWS_SENTIMENT&tickers=AAPL&apikey={ALPHAVANT_KEY}&limit=5"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            feed = data.get("feed", [])
            n = len(feed)
            sample = feed[0].get("title", "") if feed else ""
            _ok("AlphaVantage-NEWS_SENTIMENT(AAPL)", n, sample)
            results.append(n > 0)
        else:
            results.append(_fail("AlphaVantage-NEWS_SENTIMENT", f"HTTP {r.status_code}: {r.text[:100]}"))
    except Exception as e:
        results.append(_fail("AlphaVantage-NEWS_SENTIMENT", str(e)[:120]))
    time.sleep(13)  # 5次/min = 12秒间隔
    # 测试2: 日K线 TIME_SERIES_DAILY（验证Key是否支持行情数据）
    try:
        url = f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol=AAPL&apikey={ALPHAVANT_KEY}&outputsize=compact"
        r = requests.get(url, timeout=15)
        if r.status_code == 200:
            data = r.json()
            ts = data.get("Time Series (Daily)", {})
            n = len(ts)
            sample = list(ts.keys())[0] if ts else ""
            _ok("AlphaVantage-TIME_SERIES_DAILY(AAPL)", n, f"latest={sample}")
            results.append(n > 0)
        else:
            results.append(_fail("AlphaVantage-TIME_SERIES_DAILY", f"HTTP {r.status_code}: {r.text[:100]}"))
    except Exception as e:
        results.append(_fail("AlphaVantage-TIME_SERIES_DAILY", str(e)[:120]))
    return any(results)

if __name__ == "__main__":
    print("=" * 70)
    print("需Key新闻源实测 (5个源, 用户已注册)")
    print("=" * 70)
    r1 = test_newsapi()
    r2 = test_tiingo()
    r3 = test_finnhub()
    r4 = test_newsdata()
    r5 = test_alpha_vantage()
    print("\n" + "=" * 70)
    print(f"总结: NewsAPI={'✅' if r1 else '❌'} | Tiingo={'✅' if r2 else '❌'} | "
          f"Finnhub={'✅' if r3 else '❌'} | Newsdata={'✅' if r4 else '❌'} | "
          f"AlphaVantage={'✅' if r5 else '❌'}")
