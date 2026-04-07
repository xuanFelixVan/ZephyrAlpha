---
module_id: ALTERNATIVE_DATA_INTEGRATION_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: å®æ½å¢é
standard_type: ä¸ä¸éåæºæèå¾
applicable_scope: Layer 1 æ°æ®æºå±
compliance_level: ä¸ä¸æ å
responsibility:
  - å¦ç±»æ°æ®éæ
  - æ°æ®æºæ¥å?
  - æ°æ®æ åå?
  - æ°æ®è´¨éæ§å¶
layer: Layer 5 (策略执行层)
---


## 核心定位

负责另类数据集成的设计与实现，整合多源另类数据，提供数据清洗、标准化和特征提取功能，支持因子挖掘和策略增强。

# ALTERNATIVE DATA INTEGRATION BLUEPRINT

> **æ ¸å¿èè´£**: Alternative Data Integrationèå¾è®¾è®¡
> **èè´£è¾¹ç**: 
> - â?æ¬ææ¡£è´è´£ï¼Alternative Data Integrationèå¾è®¾è®¡ç¸å³åå®¹
> - â?æ¬ææ¡£ä¸è´è´£ï¼å¶ä»æ¨¡ååå®?

ï»? å¦ç±»æ°æ®æºéæé¡¹ç®è?

> **æ ¸å¿å®ä½**: å¦ç±»æ°æ®æºéæé¡¹ç®è?çæ ¸å¿åè½å®ç?

> **é¡¹ç®ç¼å·**: ALT-DATA-2026-001
> **é¡¹ç®åç§°**: å¦ç±»æ°æ®æºéæä¸å å­ææç³»ç»
> **é¡¹ç®å¨æ**: 8å¨ï¼2026-04-02 ?2026-05-28?> **é¡¹ç®ä¼å?*: P0çº§ï¼é»æ­æ§ï¼
> **é¡¹ç®ç®æ **: æ©å±æ°æ®å¹¿åº¦ï¼æåå å­ç ç©¶æ·±åº¦ï¼æå»ºå¦ç±»æ°æ®å å­


## æ ¸å¿å®ä½

**åä¸èè´£**: å¦ç±»æ°æ®æºéæä¸å å­æå»ºï¼åæ¬æ°é»æ°æ®ãç¤¾äº¤åªä½æ°æ®ãåæå¸é¢ææ°æ®çééãå¤çåå å­çæ

### èè´£è¾¹ç

**â?æ ¸å¿èè´£**:

- å¦ç±»æ°æ®æºæ¥å¥ï¼æ°é»ãç¤¾äº¤åªä½ãåæå¸é¢æï¼?
- æ°æ®ééä¸æ¸æ´ï¼APIæ¥å£ãç¬è«ãå®æ¶æµï¼?
- NLPå¤çä¸å å­æå»ºï¼ææåæãäºä»¶æåãå®ä½è¯å«ï¼
- å å­ç®¡çä¸éªè¯ï¼å­å¨ãICéªè¯ãçæ§ï¼

**â?éèè´£èå?*:
- ä¼ ç»å¸åºæ°æ®éé
- æ°æ®è´¨éçæ§
- æ°æ®å­å¨åºç¡è®¾æ½

## ä¸ãé¡¹ç®æ¶æè®¾?
### 1.1 æ´ä½æ¶æ

```
ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ??                   å¦ç±»æ°æ®æºéææ¶?                                ?ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ??                                                                    ?? æ°æ®æºå± (Data Sources)                                            ?? âââ æ°é»æ°æ®? è´¢èç¤¾APIãæ°æµªè´¢ç»APIãä¸æ¹è´¢å¯API                ?? âââ ç¤¾äº¤åªä½æ°æ®? å¾®åAPIãéªçç½ç¬è«ãä¸æ¹è´¢å¯è¡?             ?? âââ åæå¸é¢ææ°æ®æº: ä¸æ¹è´¢å¯åæå¸é¢æãåè±é¡ºç æ¥               ??                                                                    ?? æ°æ®éé?(Data Collection)                                       ?? âââ APIæ¥å£éé? ç»ä¸APIè°ç¨æ¥å£                                 ?? âââ ç¬è«å¼æ: Scrapy + Selenium                                   ?? âââ å®æ¶æ°æ®? WebSocket + Kafka                                 ?? âââ æ°æ®è°åº¦? Apache Airflow                                    ??                                                                    ?? æ°æ®å¤ç?(Data Processing)                                       ?? âââ æ°æ®æ¸æ´: å»éãå»åªãæ ¼å¼æ åå                               ?? âââ NLPå¤ç: GLM-4-Flashï¼ææåæãäºä»¶æåï¼                     ?? âââ å®ä½è¯å«: è¡ç¥¨ä»£ç ãå¬å¸åç§°ãäººç©è¯?                        ?? âââ å³ç³»æ½å: æ°é»-è¡ç¥¨å³èãäº?å½±ååæ                         ??                                                                    ?? å å­æå»º?(Factor Construction)                                   ?? âââ æ°é»å å­: ææå å­ãäºä»¶é©±å¨å å­ãç­åº¦å ?                    ?? âââ æç»ªå å­: å¸åºæç»ªãæ¿åæç»ªãä¸ªè¡æ?                        ?? âââ é¢æå å­: åæå¸é¢æå·®å¼ãä¸è´é¢æå?                        ?? âââ å³æ³¨åº¦å ? ç¤¾äº¤åªä½ç­åº¦ãæç´¢ææ°ãè®¨è®ºé                     ??                                                                    ?? å å­ç®¡ç?(Factor Management)                                     ?? âââ å å­å­å¨: SQLite + åéæ°æ®?                                 ?? âââ ICéªè¯: å å­æææ§æ£?                                        ?? âââ å å­çæ§: å®æ¶å å­è·è¸ª                                         ?? âââ å å­æ³¨å: èªå¨åå å­æ³¨åæµ?                                  ??                                                                    ?ââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââââ?```

### 1.2 ææ¯æ éæ©

| ææ¯é¢?| ææ¯éå | éæ©çç± |
|---------|---------|---------|
| **æ°æ®éé** | Scrapy + Selenium + Requests | æçç¨³å®ï¼æ¯æå¨æé¡µ?|
| **NLPå¤ç** | GLM-4-Flash | ææ¬ä½ï¼0.1?ç¾ä¸tokensï¼ï¼éåº¦?|
| **å®ä½è¯å«** | GLM-4-Flash + æ­£åè¡¨è¾¾?| åç¡®çé«ï¼ææ¬ä½ |
| **æ°æ®å­å¨** | SQLite + ChromaDB | è½»éçº§ï¼éåä¸ªäººä½¿ç¨ |
| **ä»»å¡è°åº¦** | Apache Airflow | æççå·¥ä½æµå¼æ |
| **å®æ¶æµå¤?* | Kafkaï¼å¯éï¼ | æ¯æå®æ¶æ°æ®?|
| **æ°æ®ç¼å­** | Redis | æåæ¥è¯¢æ§è½ |

---

## äºãæ°æ®æºè¯¦ç»è®¾è®¡

### 2.1 æ°é»æ°æ®?
#### 2.1.1 è´¢èç¤¾API

**æ°æ®åå®¹**:
- å®æ¶è´¢ç»æ°é»?Ã24å°æ¶?- å¿«è®¯ãå¬åãç ?- è¡ä¸æ°é»ãå¬å¸æ°?
**ææ¯æ¹?*:
```python
class CailianNewsDataSource:
    """è´¢èç¤¾æ°é»æ°æ®æº"""
    
    def __init__(self, config):
        self.api_url = "https://www.cls.cn/api/sw"
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Referer': 'https://www.cls.cn/'
        }
        
    def get_realtime_news(self, limit=100):
        """è·åå®æ¶æ°é»"""
        params = {
            'app': 'CailianpressWeb',
            'os': 'web',
            'sv': '8.4.6',
            'sign': self._generate_sign(),
            'rn': limit
        }
        response = requests.get(self.api_url, headers=self.headers, params=params)
        return self._parse_news(response.json())
    
    def get_stock_news(self, stock_code, start_date, end_date):
        """è·åä¸ªè¡ç¸å³æ°é»"""
        # éè¿å³é®è¯æç´¢ç¸å³æ°?        pass
```

**æ°æ®å­æ®µ**:
| å­æ®µ?| ç±»å | è¯´æ |
|--------|------|------|
| news_id | string | æ°é»å¯ä¸ID |
| title | string | æ°é»æ é¢ |
| content | text | æ°é»æ­£æ |
| publish_time | datetime | åå¸æ¶é´ |
| source | string | æ°æ®æ¥æº |
| stock_codes | array | ç¸å³è¡ç¥¨ä»£ç  |
| sentiment | float | ææå¾å?1??|
| event_type | string | äºä»¶ç±»å |

**ææ¬**: åè´¹ï¼æé¢çéå¶?
---

#### 2.1.2 æ°æµªè´¢ç»API

**æ°æ®åå®¹**:
- è´¢ç»æ°é»ãå¬?- è¡ä¸èµè®¯ãå¸åºå?
**ææ¯æ¹?*:
```python
class SinaFinanceDataSource:
    """æ°æµªè´¢ç»æ°æ®?""
    
    def __init__(self, config):
        self.api_url = "https://feed.mix.sina.com.cn/api/roll/get"
        
    def get_news(self, page=1, page_size=50):
        """è·åæ°é»åè¡¨"""
        params = {
            'pageid': '153',
            'lid': '2509',
            'k': '',
            'num': page_size,
            'page': page
        }
        response = requests.get(self.api_url, params=params)
        return self._parse_response(response.json())
```

**ææ¬**: åè´¹

---

#### 2.1.3 ä¸æ¹è´¢å¯API

**æ°æ®åå®¹**:
- è´¢ç»æ°é»ãå¬?- ç æ¥ãèµ?
**ææ¯æ¹?*:
```python
class EastMoneyDataSource:
    """ä¸æ¹è´¢å¯æ°æ®?""
    
    def __init__(self, config):
        self.api_url = "https://np-listapi.eastmoney.com/comm/web/getFastNewsList"
        
    def get_news(self, page_index=1, page_size=50):
        """è·åæ°é»åè¡¨"""
        params = {
            'client': 'web',
            'biz': 'web_724',
            'fastColumn': '102',
            'sortEnd': '',
            'pageSize': page_size,
            'pageIndex': page_index
        }
        response = requests.get(self.api_url, params=params)
        return self._parse_response(response.json())
```

**ææ¬**: åè´¹

---

### 2.2 ç¤¾äº¤åªä½æ°æ®?
#### 2.2.1 å¾®åAPI

**æ°æ®åå®¹**:
- è´¢ç»å¤§Vè§ç¹
- è¡ç¥¨è®¨è®ºãæ?- ç­é¨è¯é¢

**ææ¯æ¹?*:
```python
class WeiboDataSource:
    """å¾®åæ°æ®?""
    
    def __init__(self, config):
        self.api_url = "https://m.weibo.cn/api/container/getIndex"
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Cookie': config.get('weibo_cookie')
        }
        
    def search_stock_posts(self, stock_name, page=1):
        """æç´¢è¡ç¥¨ç¸å³å¾®å"""
        params = {
            'containerid': f'100103type=1&q={stock_name}',
            'page_type': 'searchall',
            'page': page
        }
        response = requests.get(self.api_url, headers=self.headers, params=params)
        return self._parse_posts(response.json())
    
    def get_hot_topics(self):
        """è·åç­é¨è¯é¢"""
        params = {
            'containerid': '106003type=25&t=3&disable_hot=1&filter_type=realtime'
        }
        response = requests.get(self.api_url, headers=self.headers, params=params)
        return self._parse_topics(response.json())
```

**æ°æ®å­æ®µ**:
| å­æ®µ?| ç±»å | è¯´æ |
|--------|------|------|
| post_id | string | å¾®åID |
| user_id | string | ç¨æ·ID |
| user_name | string | ç¨æ·?|
| content | text | å¾®ååå®¹ |
| publish_time | datetime | åå¸æ¶é´ |
| likes | int | ç¹èµ?|
| comments | int | è¯è®º?|
| reposts | int | è½¬å?|
| sentiment | float | ææå¾å |

**ææ¬**: åè´¹ï¼éè¦ç»å½cookie?
---

#### 2.2.2 éªçç½ç¬?
**æ°æ®åå®¹**:
- è¡ç¥¨è®¨è®ºãè§?- æèµèæ?- ç­é¨è¡ç¥¨

**ææ¯æ¹?*:
```python
class XueqiuDataSource:
    """éªçæ°æ®?""
    
    def __init__(self, config):
        self.base_url = "https://xueqiu.com"
        self.headers = {
            'User-Agent': 'Mozilla/5.0',
            'Cookie': config.get('xueqiu_cookie')
        }
        
    def get_stock_posts(self, stock_code, page=1):
        """è·åè¡ç¥¨ç¸å³è®¨è®º"""
        url = f"{self.base_url}/query/v1/symbol/search/status.json"
        params = {
            'symbol': stock_code,
            'count': 20,
            'page': page
        }
        response = requests.get(url, headers=self.headers, params=params)
        return self._parse_posts(response.json())
    
    def get_hot_stocks(self):
        """è·åç­é¨è¡ç¥¨"""
        url = f"{self.base_url}/stock/pick_and_drop_list.json"
        response = requests.get(url, headers=self.headers)
        return self._parse_hot_stocks(response.json())
```

**ææ¬**: åè´¹ï¼éè¦ç»å½cookie?
---

#### 2.2.3 ä¸æ¹è´¢å¯è¡å§

**æ°æ®åå®¹**:
- è¡ç¥¨è®¨è®ºãè§?- æ£æ·æç»ª

**ææ¯æ¹?*:
```python
class GubaDataSource:
    """ä¸æ¹è´¢å¯è¡å§æ°æ®?""
    
    def __init__(self, config):
        self.base_url = "https://guba.eastmoney.com"
        
    def get_stock_posts(self, stock_code, page=1):
        """è·åè¡ç¥¨å§å¸?""
        url = f"{self.base_url}/list,{stock_code}.html"
        params = {
            'pageindex': page
        }
        response = requests.get(url, params=params)
        return self._parse_posts(response.text)
```

**ææ¬**: åè´¹

---

### 2.3 åæå¸é¢ææ°æ®æº

#### 2.3.1 ä¸æ¹è´¢å¯åæå¸é¢?
**æ°æ®åå®¹**:
- åæå¸è¯?- ç®æ ä»·é¢?- çå©é¢æµ

**ææ¯æ¹?*:
```python
class AnalystExpectationDataSource:
    """åæå¸é¢ææ°æ®æº"""
    
    def __init__(self, config):
        self.api_url = "https://data.eastmoney.com/dataapi/limit_up"
        
    def get_analyst_rating(self, stock_code):
        """è·ååæå¸è¯?""
        url = f"https://data.eastmoney.com/report/info/{stock_code}.html"
        response = requests.get(url)
        return self._parse_rating(response.text)
    
    def get_consensus_forecast(self, stock_code):
        """è·åä¸è´é¢?""
        params = {
            'code': stock_code,
            'rtype': 'EPS'
        }
        response = requests.get(self.api_url, params=params)
        return self._parse_forecast(response.json())
```

**æ°æ®å­æ®µ**:
| å­æ®µ?| ç±»å | è¯´æ |
|--------|------|------|
| stock_code | string | è¡ç¥¨ä»£ç  |
| analyst_name | string | åæå¸å§?|
| institution | string | æºæåç§° |
| rating | string | è¯çº§ï¼ä¹°?å¢æ/ä¸?åæ/ååº?|
| target_price | float | ç®æ ?|
| eps_forecast | float | EPSé¢æµ |
| report_date | date | æ¥åæ¥æ |

**ææ¬**: åè´¹

---

## ä¸ãNLPå¤çæµç¨

### 3.1 ææåæ

**ææ¯æ¹?*: GLM-4-Flash

```python
class SentimentAnalyzer:
    """ææåæ?""
    
    def __init__(self):
        self.model = "glm-4-flash"
        self.api_key = config.get('zhipu_api_key')
        
    def analyze_sentiment(self, text):
        """åæææ¬ææ"""
        prompt = f"""
        è¯·åæä»¥ä¸è´¢ç»æ°é»çææå¾åï¼è¿?1?ä¹é´çææå¾åï¼
        -1è¡¨ç¤ºæåº¦è´é¢?è¡¨ç¤ºä¸­æ§ï¼1è¡¨ç¤ºæåº¦æ­£é¢
        
        æ°é»åå®¹ï¼{text}
        
        è¯·åªè¿åææå¾åæ°å¼ï¼ä¸è¦å¶ä»è§£é?        """
        
        response = self._call_api(prompt)
        sentiment_score = float(response.strip())
        return sentiment_score
    
    def batch_analyze(self, texts):
        """æ¹éææåæ"""
        results = []
        for text in texts:
            sentiment = self.analyze_sentiment(text)
            results.append(sentiment)
        return results
```

**ææ¬**: 0.1?ç¾ä¸tokens

---

### 3.2 äºä»¶æå

**ææ¯æ¹?*: GLM-4-Flash

```python
class EventExtractor:
    """äºä»¶æå?""
    
    def __init__(self):
        self.model = "glm-4-flash"
        self.event_types = [
            'ä¸ç»©å¬å', 'å¹¶è´­éç»', 'è¡æåå¨', 'é«ç®¡åå¨',
            'äº§ååå¸', 'æ¿ç­å½±å', 'è¡ä¸å?, 'å¸åºäºä»¶'
        ]
        
    def extract_events(self, text):
        """æåæ°é»äºä»¶"""
        prompt = f"""
        è¯·ä»ä»¥ä¸è´¢ç»æ°é»ä¸­æåå³é®äºä»¶ä¿¡æ¯ï¼
        
        æ°é»åå®¹ï¼{text}
        
        è¯·è¿åJSONæ ¼å¼?        {{
            "event_type": "äºä»¶ç±»å",
            "event_summary": "äºä»¶æè¦",
            "related_stocks": ["ç¸å³è¡ç¥¨ä»£ç "],
            "impact_level": "å½±åç­çº§ï¼é«/?ä½ï¼",
            "sentiment": "ææå¾åï¼æ­£?è´é¢/ä¸­æ§ï¼"
        }}
        """
        
        response = self._call_api(prompt)
        event_info = json.loads(response)
        return event_info
```

---

### 3.3 å®ä½è¯å«

**ææ¯æ¹?*: GLM-4-Flash + æ­£åè¡¨è¾¾?
```python
class EntityRecognizer:
    """å®ä½è¯å«?""
    
    def __init__(self):
        self.stock_pattern = r'(SH\d{6}|SZ\d{6}|\d{6}\.(SH|SZ))'
        
    def extract_stocks(self, text):
        """æåè¡ç¥¨ä»£ç """
        # 1. æ­£åå¹éè¡ç¥¨ä»£ç 
        stock_codes = re.findall(self.stock_pattern, text)
        
        # 2. GLM-4è¯å«å¬å¸åç§°
        prompt = f"""
        è¯·ä»ä»¥ä¸ææ¬ä¸­è¯å«æææå°çä¸å¸å¬å¸åç§°ï¼è¿åè¡ç¥¨ä»£ç åè¡¨ï¼
        
        ææ¬ï¼{text}
        
        è¯·åªè¿åè¡ç¥¨ä»£ç åè¡¨ï¼æ ¼å¼ï¼["ä»£ç 1", "ä»£ç 2"]
        """
        
        response = self._call_api(prompt)
        stock_names = json.loads(response)
        
        return list(set(stock_codes + stock_names))
```

---

## åãå å­æå»ºæ¹?
### 4.1 æ°é»å å­

#### å å­1: æ°é»ææå å­

**å å­å®ä¹**: åºäºæ°é»ææåææå»ºçå ?
**è®¡ç®æ¹æ³**:
```python
def calculate_news_sentiment_factor(stock_code, date, window=7):
    """
    è®¡ç®æ°é»ææå å­
    
    Args:
        stock_code: è¡ç¥¨ä»£ç 
        date: è®¡ç®æ¥æ
        window: æ¶é´çªå£ï¼å¤©?    
    Returns:
        å å­å¼ï¼-1??    """
    # 1. è·åè¿å»windowå¤©çç¸å³æ°é»
    news_list = get_stock_news(stock_code, date-window, date)
    
    # 2. è®¡ç®æ¯æ¡æ°é»çææå¾?    sentiments = [analyze_sentiment(news['content']) for news in news_list]
    
    # 3. å æå¹³åï¼è¿ææ°é»æéæ´é«ï¼
    weights = np.exp(np.linspace(-1, 0, len(sentiments)))
    weights = weights / weights.sum()
    
    factor_value = np.average(sentiments, weights=weights)
    
    return factor_value
```

**å å­ç¹å¾**:
- å å­ç±»å: æç»ªå å­
- æ´æ°é¢ç: æ¥é¢
- æ°æ®çªå£: 7?- ICé¢æ: 0.03-0.05

---

#### å å­2: äºä»¶é©±å¨å å­

**å å­å®ä¹**: åºäºéå¤§äºä»¶çå½±åæå»ºçå å­

**è®¡ç®æ¹æ³**:
```python
def calculate_event_driven_factor(stock_code, date):
    """
    è®¡ç®äºä»¶é©±å¨å å­
    
    Args:
        stock_code: è¡ç¥¨ä»£ç 
        date: è®¡ç®æ¥æ
    
    Returns:
        å å­å¼ï¼äºä»¶å½±åå¾å?    """
    # 1. è·åè¿æéå¤§äºä»¶
    events = get_recent_events(stock_code, date, days=30)
    
    # 2. è®¡ç®äºä»¶å½±åå¾å
    impact_scores = []
    for event in events:
        # æ ¹æ®äºä»¶ç±»ååå½±åç­çº§è®¡ç®å¾?        base_score = EVENT_IMPACT_MAP[event['event_type']]
        level_multiplier = {'?: 1.0, '?: 0.6, '?: 0.3}[event['impact_level']]
        sentiment_multiplier = {'æ­£é¢': 1.0, 'è´é¢': -1.0, 'ä¸?: 0.0}[event['sentiment']]
        
        score = base_score * level_multiplier * sentiment_multiplier
        impact_scores.append(score)
    
    # 3. å æå¹³åï¼è¿æäºä»¶æéæ´é«ï¼
    factor_value = np.mean(impact_scores) if impact_scores else 0
    
    return factor_value
```

**å å­ç¹å¾**:
- å å­ç±»å: äºä»¶å å­
- æ´æ°é¢ç: æ¥é¢
- æ°æ®çªå£: 30?- ICé¢æ: 0.04-0.06

---

#### å å­3: æ°é»ç­åº¦å å­

**å å­å®ä¹**: åºäºæ°é»æ°éåå³æ³¨åº¦æå»ºçå ?
**è®¡ç®æ¹æ³**:
```python
def calculate_news_heat_factor(stock_code, date, window=7):
    """
    è®¡ç®æ°é»ç­åº¦å å­
    
    Args:
        stock_code: è¡ç¥¨ä»£ç 
        date: è®¡ç®æ¥æ
        window: æ¶é´çªå£ï¼å¤©?    
    Returns:
        å å­å¼ï¼ç­åº¦å¾å?    """
    # 1. è·åè¿å»windowå¤©çæ°é»æ°é
    news_count = count_stock_news(stock_code, date-window, date)
    
    # 2. è®¡ç®å¨å¸åºå¹³åæ°é»æ°?    market_avg = get_market_avg_news_count(date-window, date)
    
    # 3. è®¡ç®ç¸å¯¹ç­åº¦
    heat_score = (news_count - market_avg) / market_avg
    
    # 4. æ ååå°0-1
    factor_value = 1 / (1 + np.exp(-heat_score))
    
    return factor_value
```

**å å­ç¹å¾**:
- å å­ç±»å: å³æ³¨åº¦å ?- æ´æ°é¢ç: æ¥é¢
- æ°æ®çªå£: 7?- ICé¢æ: 0.02-0.04

---

### 4.2 æç»ªå å­

#### å å­4: å¸åºæç»ªå å­

**å å­å®ä¹**: åºäºç¤¾äº¤åªä½æç»ªæå»ºçå¸åºæ´ä½æç»ªå ?
**è®¡ç®æ¹æ³**:
```python
def calculate_market_sentiment_factor(date):
    """
    è®¡ç®å¸åºæç»ªå å­
    
    Args:
        date: è®¡ç®æ¥æ
    
    Returns:
        å å­å¼ï¼å¸åºæç»ªå¾å?    """
    # 1. è·åå¾®åãéªçãè¡å§çç­é¨è®¨è®º
    posts = get_hot_posts(date)
    
    # 2. è®¡ç®æç»ªå¾å
    sentiments = [analyze_sentiment(post['content']) for post in posts]
    
    # 3. å æå¹³åï¼æäºå¨éå æï¼
    weights = [post['likes'] + post['comments'] + post['reposts'] for post in posts]
    weights = np.array(weights) / sum(weights)
    
    factor_value = np.average(sentiments, weights=weights)
    
    return factor_value
```

**å å­ç¹å¾**:
- å å­ç±»å: æç»ªå å­
- æ´æ°é¢ç: æ¥é¢
- éç¨èå´: å¨å¸?- ICé¢æ: 0.03-0.05

---

#### å å­5: ä¸ªè¡æç»ªå å­

**å å­å®ä¹**: åºäºç¤¾äº¤åªä½è®¨è®ºæå»ºçä¸ªè¡æç»ªå ?
**è®¡ç®æ¹æ³**:
```python
def calculate_stock_sentiment_factor(stock_code, date, window=7):
    """
    è®¡ç®ä¸ªè¡æç»ªå å­
    
    Args:
        stock_code: è¡ç¥¨ä»£ç 
        date: è®¡ç®æ¥æ
        window: æ¶é´çªå£ï¼å¤©?    
    Returns:
        å å­å¼ï¼ä¸ªè¡æç»ªå¾å?    """
    # 1. è·åç¤¾äº¤åªä½è®¨è®º
    posts = get_stock_posts(stock_code, date-window, date)
    
    # 2. è®¡ç®æç»ªå¾å
    sentiments = [analyze_sentiment(post['content']) for post in posts]
    
    # 3. è®¡ç®è®¨è®ºç­åº¦
    engagement = sum([post['likes'] + post['comments'] + post['reposts'] for post in posts])
    
    # 4. ç»¼åæç»ªåç­?    avg_sentiment = np.mean(sentiments)
    heat_score = np.log1p(engagement)
    
    factor_value = avg_sentiment * (1 + 0.1 * heat_score)
    
    return factor_value
```

**å å­ç¹å¾**:
- å å­ç±»å: æç»ªå å­
- æ´æ°é¢ç: æ¥é¢
- æ°æ®çªå£: 7?- ICé¢æ: 0.03-0.05

---

### 4.3 é¢æå å­

#### å å­6: åæå¸é¢æå·®å¼å ?
**å å­å®ä¹**: åºäºåæå¸é¢æä¸å®éå¼å·®å¼æå»ºçå å­

**è®¡ç®æ¹æ³**:
```python
def calculate_expectation_gap_factor(stock_code, date):
    """
    è®¡ç®åæå¸é¢æå·®å¼å ?    
    Args:
        stock_code: è¡ç¥¨ä»£ç 
        date: è®¡ç®æ¥æ
    
    Returns:
        å å­å¼ï¼é¢æå·®å¼å¾å?    """
    # 1. è·ååæå¸ä¸è´é¢?    consensus = get_consensus_forecast(stock_code, date)
    
    # 2. è·åå®é?    actual = get_actual_eps(stock_code, date)
    
    # 3. è®¡ç®é¢æå·®å¼
    if consensus and actual:
        gap = (actual - consensus) / abs(consensus)
        factor_value = gap
    else:
        factor_value = 0
    
    return factor_value
```

**å å­ç¹å¾**:
- å å­ç±»å: é¢æå å­
- æ´æ°é¢ç: å­£åº¦
- ICé¢æ: 0.05-0.08

---

#### å å­7: åæå¸è¯çº§ååå ?
**å å­å®ä¹**: åºäºåæå¸è¯çº§ååæå»ºçå å­

**è®¡ç®æ¹æ³**:
```python
def calculate_rating_change_factor(stock_code, date, window=30):
    """
    è®¡ç®åæå¸è¯çº§ååå ?    
    Args:
        stock_code: è¡ç¥¨ä»£ç 
        date: è®¡ç®æ¥æ
        window: æ¶é´çªå£ï¼å¤©?    
    Returns:
        å å­å¼ï¼è¯çº§ååå¾å?    """
    # 1. è·åè¿å»windowå¤©çè¯çº§åå
    ratings = get_rating_history(stock_code, date-window, date)
    
    # 2. è®¡ç®è¯çº§åå
    if len(ratings) >= 2:
        rating_map = {'ä¹°å¥': 2, 'å¢æ': 1, 'ä¸?: 0, 'åæ': -1, 'ååº': -2}
        latest_rating = rating_map.get(ratings[-1]['rating'], 0)
        previous_rating = rating_map.get(ratings[0]['rating'], 0)
        
        factor_value = latest_rating - previous_rating
    else:
        factor_value = 0
    
    return factor_value
```

**å å­ç¹å¾**:
- å å­ç±»å: é¢æå å­
- æ´æ°é¢ç: æ¥é¢
- æ°æ®çªå£: 30?- ICé¢æ: 0.03-0.05

---

### 4.4 å³æ³¨åº¦å ?
#### å å­8: ç¤¾äº¤åªä½ç­åº¦å å­

**å å­å®ä¹**: åºäºç¤¾äº¤åªä½è®¨è®ºéæå»ºçå³æ³¨åº¦å ?
**è®¡ç®æ¹æ³**:
```python
def calculate_social_heat_factor(stock_code, date, window=7):
    """
    è®¡ç®ç¤¾äº¤åªä½ç­åº¦å å­
    
    Args:
        stock_code: è¡ç¥¨ä»£ç 
        date: è®¡ç®æ¥æ
        window: æ¶é´çªå£ï¼å¤©?    
    Returns:
        å å­å¼ï¼ç­åº¦å¾å?    """
    # 1. è·åç¤¾äº¤åªä½è®¨è®º?    posts = get_stock_posts(stock_code, date-window, date)
    
    # 2. è®¡ç®æ»äºå¨é
    total_engagement = sum([
        post['likes'] + post['comments'] + post['reposts']
        for post in posts
    ])
    
    # 3. è®¡ç®è®¨è®º?    post_count = len(posts)
    
    # 4. ç»¼åç­åº¦å¾å
    heat_score = np.log1p(total_engagement) + 0.5 * np.log1p(post_count)
    
    # 5. æ å?    factor_value = heat_score / 10  # ç®åæ åå
    
    return factor_value
```

**å å­ç¹å¾**:
- å å­ç±»å: å³æ³¨åº¦å ?- æ´æ°é¢ç: æ¥é¢
- æ°æ®çªå£: 7?- ICé¢æ: 0.02-0.04

---

## äºãæ°æ®å­å¨è®¾?
### 5.1 æ°æ®åºè®¾?
#### æ°é»æ°æ®?
```sql
CREATE TABLE news_data (
    news_id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT,
    publish_time TIMESTAMP NOT NULL,
    source TEXT NOT NULL,
    url TEXT,
    stock_codes TEXT,  -- JSON array
    sentiment REAL,
    event_type TEXT,
    event_summary TEXT,
    impact_level TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_news_publish_time ON news_data(publish_time);
CREATE INDEX idx_news_source ON news_data(source);
CREATE INDEX idx_news_sentiment ON news_data(sentiment);
```

#### ç¤¾äº¤åªä½æ°æ®?
```sql
CREATE TABLE social_posts (
    post_id TEXT PRIMARY KEY,
    platform TEXT NOT NULL,  -- weibo, xueqiu, guba
    user_id TEXT,
    user_name TEXT,
    content TEXT NOT NULL,
    publish_time TIMESTAMP NOT NULL,
    likes INTEGER DEFAULT 0,
    comments INTEGER DEFAULT 0,
    reposts INTEGER DEFAULT 0,
    stock_codes TEXT,  -- JSON array
    sentiment REAL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_posts_platform ON social_posts(platform);
CREATE INDEX idx_posts_publish_time ON social_posts(publish_time);
CREATE INDEX idx_posts_sentiment ON social_posts(sentiment);
```

#### åæå¸é¢ææ°æ®è¡¨

```sql
CREATE TABLE analyst_expectations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    stock_code TEXT NOT NULL,
    analyst_name TEXT,
    institution TEXT,
    rating TEXT,
    target_price REAL,
    eps_forecast REAL,
    report_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_analyst_stock ON analyst_expectations(stock_code);
CREATE INDEX idx_analyst_date ON analyst_expectations(report_date);
```

#### å å­æ°æ®?
```sql
CREATE TABLE alternative_factors (
    factor_id TEXT PRIMARY KEY,
    factor_name TEXT NOT NULL,
    factor_type TEXT NOT NULL,
    stock_code TEXT NOT NULL,
    date DATE NOT NULL,
    factor_value REAL NOT NULL,
    data_source TEXT,
    calculation_method TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(factor_name, stock_code, date)
);

CREATE INDEX idx_factor_type ON alternative_factors(factor_type);
CREATE INDEX idx_factor_date ON alternative_factors(date);
CREATE INDEX idx_factor_stock ON alternative_factors(stock_code);
```

---

### 5.2 åéæ°æ®åºè®¾?
**ç?*: å­å¨æ°é»åç¤¾äº¤åªä½åå®¹çåéè¡¨ç¤ºï¼æ¯æè¯­ä¹æ?
```python
from chromadb import Client
from chromadb.config import Settings

class VectorStore:
    """åéå­å¨"""
    
    def __init__(self):
        self.client = Client(Settings(
            chroma_db_impl="duckdb+parquet",
            persist_directory="./data/vector_db"
        ))
        
        # åå»ºcollection
        self.news_collection = self.client.get_or_create_collection("news_vectors")
        self.posts_collection = self.client.get_or_create_collection("posts_vectors")
        
    def add_news(self, news_id, content, metadata):
        """æ·»å æ°é»åé"""
        # çæembedding
        embedding = self._generate_embedding(content)
        
        # å­å¨åé
        self.news_collection.add(
            ids=[news_id],
            embeddings=[embedding],
            metadatas=[metadata],
            documents=[content]
        )
        
    def search_similar_news(self, query, n_results=10):
        """æç´¢ç¸ä¼¼æ°é»"""
        query_embedding = self._generate_embedding(query)
        
        results = self.news_collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        return results
```

---

## å­ãé¡¹ç®å®æ½è®¡?
### 6.1 æ¶é´è§å

| é¶æ®µ | æ¶é´ | ä»»å¡ | äº¤ä»?|
|------|------|------|--------|
| **Phase 1: æ°æ®æºæ¥?* | Week 1-3 | æ¥å¥æ°é»ãç¤¾äº¤åªä½ãåæå¸é¢ææ°æ®?| æ°æ®ééæ¨¡åãæ°æ®åºè¡¨ç»?|
| **Phase 2: NLPå¤ç** | Week 4-5 | å¼åææåæãäºä»¶æåãå®ä½è¯å«æ¨¡?| NLPå¤çæ¨¡åãAPIéæ |
| **Phase 3: å å­æå»º** | Week 6-7 | æå»º8ä¸ªå¦ç±»æ°æ®å ?| å å­è®¡ç®æ¨¡åãå å­æ°?|
| **Phase 4: æµè¯éªè¯** | Week 8 | ICéªè¯ãåæµéªè¯ãç³»ç»æµ?| æµè¯æ¥åãéªæ¶æ?|

---

### 6.2 éç¨?
| éç¨?| æ¶é´ | éªæ¶æ å |
|--------|------|---------|
| **M1: æ°æ®æºæ¥å¥å®?* | Week 3 | è³å°3ä¸ªæ°æ®æºæ¥å¥ï¼æ°æ®è´¨?95% |
| **M2: NLPå¤çå®æ** | Week 5 | ææåæåç¡®?80%ï¼äºä»¶æåå®?|
| **M3: å å­æå»ºå®æ** | Week 7 | è³å°8ä¸ªå å­ï¼ICå?0.03 |
| **M4: é¡¹ç®éªæ¶** | Week 8 | æææµè¯éè¿ï¼ææ¡£å®?|

---

## ä¸ãèµæºå?
### 7.1 äººåèµæº

| è§è² | èè´£ | å·¥ä½?|
|------|------|--------|
| **é¡¹ç®è´è´£?* | æ´ä½åè°ãè¿åº¦ç®¡?| 20% |
| **æ°æ®å·¥ç¨?* | æ°æ®æºæ¥å¥ãæ°æ®é?| 60% |
| **NLPå·¥ç¨?* | ææåæãäºä»¶æ?| 40% |
| **å å­ç ç©¶?* | å å­æå»ºãICéªè¯ | 40% |
| **æµè¯å·¥ç¨?* | ç³»ç»æµè¯ãè´¨éä¿?| 20% |

**æ»å·¥ä½é**: ?80äººæ¶

---

### 7.2 ææ¯èµ?
| èµæºç±»å | è§æ ¼ | ææ¬ |
|---------|------|------|
| **è®¡ç®èµæº** | æ¬å°å¼åæº??6G?| 0?|
| **å­å¨èµæº** | æ¬å°SSD 500GB | 0?|
| **APIè°ç¨** | GLM-4-Flash | ?00??|
| **æ°æ®?* | å¬å¼API | 0?|

**æ»æ?*: ?00??
---

## å«ãé£é©ç®¡?
### 8.1 ææ¯é£?
| é£é© | å½±å | æ¦ç | ç¼è§£æªæ½ |
|------|------|------|---------|
| **APIé¢çéå¶** | ?| ?| å®ç°è¯·æ±éåãå¤è´¦å·è½®æ¢ |
| **æ°æ®è´¨éä¸ç¨³?* | ?| ?| æ°æ®æ¸æ´ãå¼å¸¸æ£?|
| **NLPåç¡®çä¸?* | ?| ?| æ¨¡åä¼åãäººå·¥æ æ³¨éª?|
| **ç³»ç»æ§è½ç¶é¢** | ?| ?| å¼æ­¥å¤çãç¼å­ä¼?|

---

### 8.2 é¡¹ç®é£é©

| é£é© | å½±å | æ¦ç | ç¼è§£æªæ½ |
|------|------|------|---------|
| **è¿åº¦å»¶æ** | ?| ?| é¢çç¼å²æ¶é´ãå¹¶è¡å¼?|
| **èµæºä¸è¶³** | ?| ?| ä¼åçº§ç®¡çãèµæºå¤?|
| **éæ±å?* | ?| ?| éæ±å»ç»ãåæ´æ§?|

---

## ä¹ãéªæ¶æ ?
### 9.1 åè½éªæ¶

| åè½ | éªæ¶æ å | æµè¯æ¹æ³ |
|------|---------|---------|
| **æ°æ®éé** | æ°æ®å®æ´?95% | æ°æ®è´¨éæ£?|
| **NLPå¤ç** | ææåæåç¡®?80% | äººå·¥æ æ³¨éªè¯ |
| **å å­è®¡ç®** | å å­æ°é??| åè½æµè¯ |
| **ICéªè¯** | ICå?0.03 | ç»è®¡æ£?|

---

### 9.2 æ§è½éªæ¶

| ææ  | ç®æ ?| æµè¯æ¹æ³ |
|------|--------|---------|
| **æ°æ®ééå»¶è¿** | <5åé | æ§è½æµè¯ |
| **å å­è®¡ç®å»¶è¿** | <10?| æ§è½æµè¯ |
| **ç³»ç»å¯ç¨?* | >99% | çæ§ç»è®¡ |

---

## åãé¡¹ç®æ?
### 10.1 å·²çææ?
1. **é¡¹ç®èå¾**: æ¬æ?2. **ææ¯è§æ ¼ä¹¦**: å¾å¶?3. **å®æ½è®¡å**: å¾å¶?4. **æµè¯è®¡å**: å¾å¶?
---

**èå¾çæ¬**: v1.0  
**åå»ºæ¥æ**: 2026-04-02  
**ç?*: ?å·²å®?

## åæ´åå²

| çæ¬ | æ¥æ | åæ´åå®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-02 | åå§çæ¬åå»º | é¦å¸­æ¶æå¸?|

---

**èå¾çæ¬**: v1.0.1 | **åå»ºæ¥æ**: 2026-04-02 | **ç¶æ?*: Active
---


---

## ð ç¸å³ææ¡£

### ä¸æ¸¸ä¾èµ

| ææ¡£åç§° | module_id | ä¾èµç±»å | è¯´æ |
|---------|-----------|---------|------|
| [DATA SOURCE MANAGEMENT BLUEPRINT](./DATA_SOURCE_MANAGEMENT_BLUEPRINT.md) | DATA_SOURCE_MANAGEMENT_001 | å¼ºä¾èµ?| æä¾æ°æ®æºè¿æ¥åéç½® |

### ä¸æ¸¸ä¾èµ

| ææ¡£åç§° | module_id | ä¾èµç±»å | è¯´æ |
|---------|-----------|---------|------|
| [DATA QUALITY MONITORING BLUEPRINT](./DATA_QUALITY_MONITORING_BLUEPRINT.md) | DATA_QUALITY_MONITORING_001 | å¼ºä¾èµ?| æ¥æ¶å¦ç±»æ°æ®è¿è¡è´¨éæ£æ?|
| [DATA CATALOG BLUEPRINT](./DATA_CATALOG_BLUEPRINT.md) | DATA_CATALOG_001 | ä¸­ä¾èµ?| æ³¨åå¦ç±»æ°æ®èµäº§ |

### ææ¯ä¾èµ?

| ææ¯ç»ä»?| çæ¬ | ç¨é?| ææ¡£ |
|---------|------|------|------|
| **Scrapy** | 2.11+ | æ°æ®éé | [å®æ¹ææ¡£](https://scrapy.org/) |
| **Selenium** | 4.15+ | å¨æé¡µé¢æå?| [å®æ¹ææ¡£](https://www.selenium.dev/) |
| **GLM-4-Flash** | latest | NLPå¤ç | [å®æ¹ææ¡£](https://open.bigmodel.cn/) |
| **Apache Airflow** | 2.7+ | ä»»å¡è°åº¦ | [å®æ¹ææ¡£](https://airflow.apache.org/) |

### å¼ç¨å³ç³»å?

```mermaid
graph LR
    U0["DATA SOURCE MAN"] --> B
    B["ALTERNATIVE DAT"]
    B --> D0["DATA QUALITY MO"]
    B --> D1["DATA CATALOG BL"]
    
    style B fill:#ff6b6b
    style U0 fill:#4ecdc4
    style D0 fill:#45b7d1
```

## 1. ææ¡£æ²»ç

### 1.1 System_Manifest.mdç´¢å¼

```markdown
#### Layer 6: ç»åä¼åå±?
##### 6.001. Alternative Data Integration
- **æ¨¡åID**: ALTERNATIVE_DATA_INTEGRATION_001
- **èå¾ææ¡£**: ALTERNATIVE_DATA_INTEGRATION_BLUEPRINT.md
- **ææ¯è§æ ¼ä¹¦**: å¾åå»?
- **èè´£**: Layer 2 Alphaå å­å±?- å¦ç±»æ°æ®æºéæ?
- **ç¶æ?*: Active
```

### 1.2 æ¨¡åèè´£è¾¹ç

| æ¨¡å | èè´£ | è¾¹ç |
|------|------|------|
| **Alternative Data Integration** | Layer 2 Alphaå å­å±?- å¦ç±»æ°æ®æºéæ?| **æ ¸å¿æ¨¡å** |

### 1.3 çæ¬ç®¡ç

| çæ¬ | æ¥æ | åæ´åå®¹ | åæ´äº?|
|------|------|----------|--------|
| v1.0.0 | 2026-04-02 | åå§çæ¬åå»º | é¦å¸­èå¾æ¶æå¸?|

---

**èå¾çæ¬**: v1.0.0 | **åå»ºæ¥æ**: 2026-04-02 | **ç¶æ?*: Active
