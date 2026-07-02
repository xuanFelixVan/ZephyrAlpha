# -*- coding: utf-8 -*-
"""国内财经新闻数据源实测v2（用china-finance-rss项目的正确API URL）
发现的新源: 华尔街见闻 / 金十数据
正确URL: 财联社/v1/roll/get_roll_list | 东财newsapi/kuaixun | 同花顺/tapp/news/push/stock
"""
import requests
import time
import json
import re
import warnings
warnings.filterwarnings("ignore")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
    "Accept": "application/json, text/html, */*",
    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
}

def _ok(name, n, sample=""):
    print(f"  ✅ {name}: {n}条{(' | 样本=' + sample[:100]) if sample else ''}")
    return True

def _fail(name, err):
    print(f"  ❌ {name}: {err}")
    return False

# ============ 1. 东方财富快讯 (正确URL) ============
def test_eastmoney_v2():
    print("\n=== 1. 东方财富快讯 (newsapi.eastmoney.com) ===")
    try:
        url = "https://newsapi.eastmoney.com/kuaixun/v1/getlist_102_ajaxResult_50_1_.html"
        headers = {**HEADERS, "Referer": "https://kuaixun.eastmoney.com/"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            text = r.text
            # 东财返回的是jsonP格式: var ajaxResult={...}
            match = re.search(r'var\s+ajaxResult\s*=\s*(\{.*\})', text, re.DOTALL)
            if match:
                data = json.loads(match.group(1))
                articles = data.get("LivesList", data.get("Data", []))
                if not articles:
                    # 尝试其他字段
                    for k, v in data.items():
                        if isinstance(v, list) and len(v) > 0:
                            articles = v
                            break
                n = len(articles)
                sample = articles[0].get("title", "") or articles[0].get("digest", "")[:80] if articles else ""
                _ok("东财-7x24快讯", n, sample)
                return n > 0
            else:
                # 可能是纯JSON
                try:
                    data = r.json()
                    articles = data.get("LivesList", data.get("Data", []))
                    n = len(articles)
                    _ok("东财-7x24快讯(JSON)", n)
                    return n > 0
                except:
                    return _fail("东财-7x24快讯", f"解析失败, text={text[:100]}")
        else:
            return _fail("东财-7x24快讯", f"HTTP {r.status_code}")
    except Exception as e:
        return _fail("东财-7x24快讯", str(e)[:100])

# ============ 2. 同花顺快讯 (正确URL) ============
def test_ths_v2():
    print("\n=== 2. 同花顺快讯 (news.10jqka.com.cn/tapp) ===")
    try:
        url = "https://news.10jqka.com.cn/tapp/news/push/stock/?page=1&tag=&track=website&pagesize=20"
        headers = {**HEADERS, "Referer": "https://news.10jqka.com.cn/"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            articles = data.get("data", {}).get("list", [])
            n = len(articles)
            sample = articles[0].get("title", "") if articles else ""
            _ok("同花顺-快讯推送", n, sample)
            return n > 0
        else:
            return _fail("同花顺-快讯推送", f"HTTP {r.status_code}")
    except Exception as e:
        return _fail("同花顺-快讯推送", str(e)[:100])

# ============ 3. 华尔街见闻 (新发现) ============
def test_wallstreetcn():
    print("\n=== 3. 华尔街见闻 (api-one-wscn.awtmt.com, 免费) ===")
    try:
        url = "https://api-one-wscn.awtmt.com/apiv1/content/lives?channel=global-channel&client=pc&limit=20"
        headers = {**HEADERS, "Referer": "https://wallstreetcn.com/live"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            items = data.get("data", {}).get("items", [])
            n = len(items)
            # 华尔街见闻有中文和英文内容
            sample = items[0].get("title", "") or items[0].get("content_text", "")[:80] if items else ""
            _ok("华尔街见闻-全球直播", n, sample)
            return n > 0
        else:
            return _fail("华尔街见闻-全球直播", f"HTTP {r.status_code}")
    except Exception as e:
        return _fail("华尔街见闻-全球直播", str(e)[:100])

# ============ 4. 金十数据 (新发现, 需提取x-app-id) ============
def test_jin10():
    print("\n=== 4. 金十数据 (flash-api.jin10.com, 免费) ===")
    try:
        # 步骤1: 从首页提取x-app-id
        base_headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.jin10.com/"}
        r = requests.get("https://www.jin10.com/", headers=base_headers, timeout=10)
        # 提取JS bundle URL
        match = re.search(r'(?:https:)?//www\.jin10\.com/new/js/index\.[^"\'\ ]+\.js', r.text)
        if not match:
            match = re.search(r'/new/js/index\.[^"\'\ ]+\.js', r.text)
        if not match:
            return _fail("金十数据", "无法找到前端bundle URL")
        script_url = match.group(0)
        if script_url.startswith("//"):
            script_url = "https:" + script_url
        elif script_url.startswith("/"):
            script_url = "https://www.jin10.com" + script_url
        # 步骤2: 从bundle提取x-app-id
        r2 = requests.get(script_url, headers=base_headers, timeout=10)
        id_match = re.search(r'"x-app-id":"([^"]+)"', r2.text)
        if not id_match:
            return _fail("金十数据", "无法提取x-app-id")
        app_id = id_match.group(1)
        # 步骤3: 调用flash API
        url = "https://flash-api.jin10.com/get_flash_list?channel=-8200&limit=20"
        headers = {
            "User-Agent": "Mozilla/5.0",
            "Accept": "application/json,text/plain,*/*",
            "Referer": "https://www.jin10.com/",
            "Origin": "https://www.jin10.com",
            "x-app-id": app_id,
            "x-version": "1.0.0",
        }
        r3 = requests.get(url, headers=headers, timeout=10)
        if r3.status_code == 200:
            data = r3.json()
            articles = data.get("data", [])
            n = len(articles)
            sample = articles[0].get("data", {}).get("content", "")[:80] if articles else ""
            _ok("金十数据-快讯", n, sample)
            return n > 0
        else:
            return _fail("金十数据-快讯", f"HTTP {r3.status_code}")
    except Exception as e:
        return _fail("金十数据", str(e)[:120])

# ============ 5. 财联社 (正确URL, 需签名) ============
def test_cls_v2():
    print("\n=== 5. 财联社 (www.cls.cn/v1/roll/get_roll_list, 需签名) ===")
    try:
        import hashlib
        # 财联社签名算法（从china-finance-rss源码提取）
        params = {"app": "CailianpressWeb", "os": "web", "sv": "7.7.5"}
        # 简化签名（可能不完整，先试试无签名直接请求）
        url = "https://www.cls.cn/v1/roll/get_roll_list?app=CailianpressWeb&os=web&sv=7.7.5"
        headers = {"User-Agent": "Mozilla/5.0", "Referer": "https://www.cls.cn/telegraph"}
        r = requests.get(url, headers=headers, timeout=10)
        if r.status_code == 200:
            data = r.json()
            articles = data.get("data", {}).get("roll_data", [])
            n = len(articles)
            sample = articles[0].get("brief", "") or articles[0].get("content", "")[:80] if articles else ""
            _ok("财联社-电报列表(v1)", n, sample)
            return n > 0
        else:
            return _fail("财联社-电报列表(v1)", f"HTTP {r.status_code}: {r.text[:80]}")
    except Exception as e:
        return _fail("财联社-电报列表(v1)", str(e)[:120])

# ============ 6. 巨潮资讯网(公告API) ============
def test_cninfo_api():
    print("\n=== 6. 巨潮资讯网公告API (www.cninfo.com.cn) ===")
    try:
        url = "http://www.cninfo.com.cn/new/hisAnnouncement/query"
        data = {
            "stock": "600000,gsshz0000001",
            "tabName": "fulltext",
            "pageSize": 10,
            "pageNum": 1,
            "column": "szse",
            "category": "",
            "plate": "",
            "seDate": "",
        }
        headers = {**HEADERS, "Referer": "http://www.cninfo.com.cn/"}
        r = requests.post(url, data=data, headers=headers, timeout=10)
        if r.status_code == 200:
            resp = r.json()
            articles = resp.get("announcements", [])
            n = len(articles)
            sample = articles[0].get("announcementTitle", "") if articles else ""
            _ok("巨潮资讯-公告API(600000)", n, sample)
            return n > 0
        else:
            return _fail("巨潮资讯-公告API", f"HTTP {r.status_code}")
    except Exception as e:
        return _fail("巨潮资讯-公告API", str(e)[:100])

if __name__ == "__main__":
    print("=" * 70)
    print("国内财经新闻数据源实测v2 (正确API URL)")
    print("=" * 70)
    r1 = test_eastmoney_v2()
    time.sleep(1)
    r2 = test_ths_v2()
    time.sleep(1)
    r3 = test_wallstreetcn()
    time.sleep(1)
    r4 = test_jin10()
    time.sleep(1)
    r5 = test_cls_v2()
    time.sleep(1)
    r6 = test_cninfo_api()
    print("\n" + "=" * 70)
    print(f"总结: 东财={'✅' if r1 else '❌'} | 同花顺={'✅' if r2 else '❌'} | "
          f"华尔街见闻={'✅' if r3 else '❌'} | 金十={'✅' if r4 else '❌'} | "
          f"财联社={'✅' if r5 else '❌'} | 巨潮={'✅' if r6 else '❌'}")
