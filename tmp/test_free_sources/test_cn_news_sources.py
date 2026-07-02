# -*- coding: utf-8 -*-
"""国内财经新闻数据源实测（搜索发现的新源）
1. 新浪财经API (feed.mix.sina.com.cn) - 实时+滚动新闻, JSON, 免费
2. 东方财富快讯 (kuaixun.eastmoney.com / np-listapi) - 7x24快讯, JSON, 免费
3. 财联社电报 (cls.cn/nodeapi) - 实时快讯, JSON, 免费
4. 百度股市通 (gushitong.baidu.com) - 股票新闻, 免费
5. 同花顺快讯 (news.10jqka.com.cn) - 7x24快讯, 免费
注意: 须断开VPN测试（国内网站）
"""
import requests
import time
import json
import warnings
warnings.filterwarnings("ignore")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Safari/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def _ok(name, n, sample=""):
    print(f"  ✅ {name}: {n}条{(' | 样本=' + sample[:100]) if sample else ''}")
    return True

def _fail(name, err):
    print(f"  ❌ {name}: {err}")
    return False

# ============ 1. 新浪财经API ============
def test_sina():
    print("\n=== 1. 新浪财经API (免费无Key) ===")
    results = []
    # 1a. 滚动新闻API
    try:
        url = "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=1686&num=10&page=1"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            articles = data.get("data", {}).get("data", [])
            n = len(articles)
            sample = articles[0].get("title", "") if articles else ""
            _ok("新浪-滚动财经(lid=1686)", n, sample)
            results.append(n > 0)
        else:
            results.append(_fail("新浪-滚动财经", f"HTTP {r.status_code}"))
    except Exception as e:
        results.append(_fail("新浪-滚动财经", str(e)[:100]))
    time.sleep(1)
    # 1b. 实时新闻API
    try:
        url = "https://feed.mix.sina.com.cn/api/roll/get?pageid=153&lid=2516&num=10&page=1"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            articles = data.get("data", {}).get("data", [])
            n = len(articles)
            sample = articles[0].get("title", "") if articles else ""
            _ok("新浪-实时财经(lid=2516)", n, sample)
            results.append(n > 0)
        else:
            results.append(_fail("新浪-实时财经", f"HTTP {r.status_code}"))
    except Exception as e:
        results.append(_fail("新浪-实时财经", str(e)[:100]))
    return any(results)

# ============ 2. 东方财富快讯 ============
def test_eastmoney():
    print("\n=== 2. 东方财富快讯API (免费无Key) ===")
    results = []
    # 2a. 7x24快讯
    try:
        url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns?client=web&biz=web_news_col&column=350&order=1&needInteractData=0&page_index=1&page_size=10"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            articles = data.get("data", {}).get("list", [])
            n = len(articles)
            sample = articles[0].get("title", "") if articles else ""
            _ok("东财-7x24快讯(col=350)", n, sample)
            results.append(n > 0)
        else:
            results.append(_fail("东财-7x24快讯", f"HTTP {r.status_code}"))
    except Exception as e:
        results.append(_fail("东财-7x24快讯", str(e)[:100]))
    time.sleep(1)
    # 2b. 财经要闻
    try:
        url = "https://np-listapi.eastmoney.com/comm/web/getNewsByColumns?client=web&biz=web_news_col&column=280&order=1&needInteractData=0&page_index=1&page_size=10"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            articles = data.get("data", {}).get("list", [])
            n = len(articles)
            sample = articles[0].get("title", "") if articles else ""
            _ok("东财-财经要闻(col=280)", n, sample)
            results.append(n > 0)
        else:
            results.append(_fail("东财-财经要闻", f"HTTP {r.status_code}"))
    except Exception as e:
        results.append(_fail("东财-财经要闻", str(e)[:100]))
    return any(results)

# ============ 3. 财联社电报 ============
def test_cls():
    print("\n=== 3. 财联社电报API (免费无Key) ===")
    results = []
    # 3a. 电报列表
    try:
        url = "https://www.cls.cn/nodeapi/updateTelegraphList?app=CailianpressWeb&category=&lastTime=&os=web&sv=7.7.5"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            articles = data.get("data", {}).get("roll_data", [])
            n = len(articles)
            sample = articles[0].get("title", "") or articles[0].get("content", "")[:80] if articles else ""
            _ok("财联社-电报列表", n, sample)
            results.append(n > 0)
        else:
            results.append(_fail("财联社-电报列表", f"HTTP {r.status_code}"))
    except Exception as e:
        results.append(_fail("财联社-电报列表", str(e)[:100]))
    return any(results)

# ============ 4. 百度股市通 ============
def test_baidu():
    print("\n=== 4. 百度股市通 (免费无Key) ===")
    results = []
    # 4a. 股票新闻
    try:
        url = "https://gushitong.baidu.com/opendata?resource_id=5352&query=600000&name=&code=600000&market=ab&group=asyn_rank_news&start=0&size=10"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            data = r.json()
            articles = data.get("Result", [])
            n = len(articles)
            sample = articles[0].get("title", "") or articles[0].get("abstract", "")[:80] if articles else ""
            _ok("百度股市通-个股新闻(600000)", n, sample)
            results.append(n > 0)
        else:
            results.append(_fail("百度股市通-个股新闻", f"HTTP {r.status_code}"))
    except Exception as e:
        results.append(_fail("百度股市通-个股新闻", str(e)[:100]))
    return any(results)

# ============ 5. 同花顺快讯 ============
def test_10jqka():
    print("\n=== 5. 同花顺快讯 (免费无Key) ===")
    results = []
    # 5a. 7x24快讯
    try:
        url = "https://news.10jqka.com.cn/realtimenews.html"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            # 同花顺是HTML页面，检查是否可访问
            n = r.text.count("class=\"list-con\"")
            _ok("同花顺-7x24快讯(HTML)", n, "HTML可访问" if n > 0 else "HTML但未匹配到条目")
            results.append(n > 0 or len(r.text) > 5000)
        else:
            results.append(_fail("同花顺-7x24快讯", f"HTTP {r.status_code}"))
    except Exception as e:
        results.append(_fail("同花顺-7x24快讯", str(e)[:100]))
    time.sleep(1)
    # 5b. 同花顺API
    try:
        url = "https://news.10jqka.com.cn/api/pc/v2/real-news-list?ajax=1&type=info"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            try:
                data = r.json()
                articles = data.get("data", {}).get("list", [])
                n = len(articles)
                sample = articles[0].get("title", "") if articles else ""
                _ok("同花顺-API快讯", n, sample)
                results.append(n > 0)
            except:
                results.append(_fail("同花顺-API快讯", "JSON解析失败"))
        else:
            results.append(_fail("同花顺-API快讯", f"HTTP {r.status_code}"))
    except Exception as e:
        results.append(_fail("同花顺-API快讯", str(e)[:100]))
    return any(results)

# ============ 6. 巨潮资讯网(公告) ============
def test_cninfo():
    print("\n=== 6. 巨潮资讯网(公告, 免费无Key) ===")
    try:
        url = "http://www.cninfo.com.cn/new/disclosure/stock?stockCode=600000&orgId=gsshz0000001"
        r = requests.get(url, headers=HEADERS, timeout=10)
        if r.status_code == 200:
            _ok("巨潮资讯-公告页面(600000)", 1, f"HTML可访问({len(r.text)}字节)")
            return True
        else:
            return _fail("巨潮资讯-公告", f"HTTP {r.status_code}")
    except Exception as e:
        return _fail("巨潮资讯-公告", str(e)[:100])

if __name__ == "__main__":
    print("=" * 70)
    print("国内财经新闻数据源实测 (免费无Key)")
    print("=" * 70)
    r1 = test_sina()
    r2 = test_eastmoney()
    r3 = test_cls()
    r4 = test_baidu()
    r5 = test_10jqka()
    r6 = test_cninfo()
    print("\n" + "=" * 70)
    print(f"总结: 新浪={'✅' if r1 else '❌'} | 东财={'✅' if r2 else '❌'} | "
          f"财联社={'✅' if r3 else '❌'} | 百度={'✅' if r4 else '❌'} | "
          f"同花顺={'✅' if r5 else '❌'} | 巨潮={'✅' if r6 else '❌'}")
