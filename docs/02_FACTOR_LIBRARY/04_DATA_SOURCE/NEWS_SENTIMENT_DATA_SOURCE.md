---
module_id: DATA_NEWS_SENTIMENT_001
version: 2.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-06
owner: 首席文档架构师
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管理
compliance_level: 研究标准
parent_document: ../INDEX.md
implementation_status: 进行中
responsibility: 新闻情感数据源与文本分析
---
---

# 另类数据 - 新闻舆情

> **核心职责**: 新闻情感数据源接入和情感分析，涉及新闻舆情 另类数据
> **职责边界**: 
> - ✅ 本文档负责：新闻情感数据源接入和情感分析
> - ❌ 本文档不负责：其他模块内容


## 文档职责说明

**本文档职责**: 新闻舆情数据源技术规格
- 定义新闻舆情数据获取方案
- 说明NLP处理和情感分析方法
- 提供多数据源整合策略

**相关文档引用**:
| 文档 | 路径 | 关系 | 说明 |
|------|------|------|------|
| 数据源适配器 | [DATA_SOURCE_ADAPTERS.md](./DATA_SOURCE_ADAPTERS.md) | 上层架构 | 数据源统一适配器 |
| 数据源索引 | [INDEX.md](./INDEX.md) | 上级索引 | 数据源模块总索引 |

**职责边界**:
- ✅ 本文档负责: 新闻舆情数据获取和处理方案
- ❌ 本文档不负责: 情感因子计算（由因子库负责）

> NLP处理、情感分析、事件研究
>
> **版本**: v2.1
> **更新日期**: 2026-03-30
> **方案**: 混合方案 (AkShare + iFind + Tushare + 模力方舟LLM)

---

## 1. 新闻数据获取方案

### 1.1 分层获取架构

| 层级 | 数据�?| 用�?| 稳定�?| 成本 | 频率限制 |
|------|--------|------|--------|------|---------|
| **层级1** | AkShare (免费) | 主力新闻�?| ⭐⭐�?| 免费 | <30�?�?|
| **层级2** | Tushare Pro | 付费补充 | ⭐⭐⭐⭐�?| 积分�?| 500�?�?|
| **层级3** | iFind API | 备用 | ⭐⭐⭐⭐ | 订阅 | 视订阅级�?|
| **层级4** | 政府网站RSS | 政策�?| ⭐⭐⭐⭐�?| 免费 | 无限�?|

### 1.2 推荐配置

```python
# 新闻数据源配�?
NEWS_SOURCES = {
    'primary': 'akshare',           # AkShare主力
    'backup': 'ifind',             # iFind备用
    'paid': 'tushare_pro',        # Tushare付费�?
    'policy': 'gov_rss'           # 政府RSS
}

# AkShare安全频率配置
AKSHARE_CONFIG = {
    'news_delay': 2,        # 新闻接口间隔2�?
    'max_per_minute': 30,   # 每分钟不超过30�?
    'retry_times': 3,       # 重试次数
    'retry_delay': 5         # 重试间隔5�?
}
```

### 1.3 各平台限制说�?

| 平台 | 频率限制 | 稳定�?| 风险 |
|------|---------|--------|------|
| AkShare | <30�?�?| ⭐⭐�?| 可能被封IP |
| Tushare Pro | 500�?�?| ⭐⭐⭐⭐�?| 付费但稳�?|
| iFind | 视订阅级�?| ⭐⭐⭐⭐ | 需权限 |
| 政府RSS | 无限�?| ⭐⭐⭐⭐�?| 合规安全 |

### 1.4 政府网站RSS源（零风险）

```python
# 政府公开RSS订阅�?
GOV_RSS_SOURCES = {
    'people_daily': 'http://www.people.com.cn/rss/',           # 人民�?
    'chinanews': 'http://www.chinanews.com/rss/',             # 中国新闻�?
    'stats_gov': 'https://www.stats.gov.cn/sj/zxfb/rss.xml', # 国家统计局
}

# 使用示例
import feedparser

def fetch_gov_news():
    """获取政府网站新闻（零风险�?""
    rss_url = 'http://www.people.com.cn/rss/finance.xml'
    feed = feedparser.parse(rss_url)
    for entry in feed.entries[:10]:
        print(entry.title, entry.published)
```

### 1.5 稳定使用建议

```python
import time
import akshare as ak

def safe_news_fetch(symbol="000001", delay=2):
    """安全获取新闻（带限频�?""
    time.sleep(delay)  # 控制请求频率
    try:
        df = ak.stock_news_em(symbol=symbol)
        return df
    except Exception as e:
        print(f"获取失败: {e}")
        time.sleep(5)  # 失败后等�?
        return None
```

---

## 2. 本地LLM处理方案

### 2.1 硬件支持

| 硬件 | 配置 | 能力 |
|------|------|------|
| GPU | RTX 3090 24GB | 可跑7B模型 |
| RAM | 64GB | 足够并行处理 |
| 存储 | 1.2TB | 新闻数据够用 |

### 2.2 模型选择 (已测�?- 2026-03-30)

| 任务 | 推荐模型 | 部署方式 | 上下�?| 状�?|
|------|----------|----------|--------|------|
| 情感分析 | **GLM-4.7-Flash** | API (模力方舟) | 200K | �?已测�?|
| 深度思�?| **Qwen3-4B** | API (模力方舟) | 32K | �?已测�?|
| 推理分析 | **DeepSeek-R1-Distill-Qwen-14B** | API (模力方舟) | 32K | �?已测�?|
| 数学证明 | **DeepSeek-Prover-V2-7B** | API (模力方舟) | - | �?已测�?|
| 事件分类 | **Qwen3-4B** | API (模力方舟) | 32K | �?可用 |
| 实体识别 | **GLM-4.7-Flash** | API (模力方舟) | 200K | �?可用 |

### 2.3 API模型配置

```python
# 模力方舟 API 配置 (免费)
MOAI_CONFIG = {
    'api_base': 'https://ai.gitee.com/api/v1/chat/completions',
    'api_key': 'XA8UNQKJTRBEXHXJICM7KBOJHP6NRVN6UINHIZF8',  # 已测试可�?
    'models': {
        'glm_4_flash': {
            'name': 'GLM-4.7-Flash',
            'context': 200000,
            'use_case': '情感分析、实体识别、大量文本处�?
        },
        'qwen3_4b': {
            'name': 'Qwen3-4B',
            'context': 32000,
            'use_case': '深度思考、事件分�?
        },
        'deepseek_r1': {
            'name': 'DeepSeek-R1-Distill-Qwen-14B',
            'context': 32000,
            'use_case': '推理分析、复杂问�?
        },
        'deepseek_prover': {
            'name': 'DeepSeek-Prover-V2-7B',
            'use_case': '数学定理证明'
        }
    }
}

# 本地LLM配置 (预留)
LOCAL_LLM_CONFIG = {
    'event_classifier': {
        'model': 'Qwen/Qwen2.5-7B-Instruct',
        'device': 'cuda',            # RTX 3090
        'max_memory': {0: '14GB'}
    },
    'entity_extractor': {
        'model': 'THUDM/ChatGLM3-6B',
        'device': 'cuda',           # RTX 3090
        'max_memory': {0: '12GB'}
    }
}
```

### 2.4 使用示例

```python
import requests

def chat_with_moai(model: str, messages: list, max_tokens: int = 1000):
    """模力方舟API调用示例"""
    api_key = "XA8UNQKJTRBEXHXJICM7KBOJHP6NRVN6UINHIZF8"
    url = "https://ai.gitee.com/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens
    }
    response = requests.post(url, headers=headers, json=data, timeout=30)
    return response.json()['choices'][0]['message']['content']

# 情感分析
result = chat_with_moai("GLM-4.7-Flash", [
    {"role": "user", "content": "分析这条新闻的情�? 茅台Q4净利润增长15%"}
])

# 深度思�?
result = chat_with_moai("Qwen3-4B", [
    {"role": "user", "content": "分析当前市场状�?}
])
```

---

## 3. 另类数据类型

| 类型 | 数据内容 | 更新频率 | 处理方式 |
|------|---------|---------|---------|
| 新闻数据 | 财经新闻、公告、研�?| 实时 | NLP + 情感分析 |
| 舆情数据 | 雪球、股吧、微博讨�?| 15分钟 | 情感分析 + 风险识别 |
| 搜索数据 | 百度搜索指数、Google Trends | 日频 | 搜索热度 |
| 社交媒体 | 财经大V、机构评�?| 实时 | 实体识别 + 关系抽取 |

---

## 4. 新闻数据处理

```python
import re
from typing import List, Dict
from dataclasses import dataclass
from datetime import datetime

@dataclass
class NewsItem:
    """新闻条目"""
    news_id: str
    title: str
    content: str
    publish_time: datetime
    source: str
    url: str
    sentiment: float = None  # -1 to 1
    entities: List[str] = None
    event_type: str = None

class NewsProcessor:
    """新闻处理�?""

    def __init__(self):
        self.sentiment_model = None  # 加载情感分析模型
        self.ner_model = None        # 命名实体识别模型

    def process_news(self, raw_news: dict) -> NewsItem:
        """处理单条新闻"""
        news = NewsItem(
            news_id=raw_news['id'],
            title=raw_news['title'],
            content=raw_news['content'],
            publish_time=raw_news['publish_time'],
            source=raw_news['source'],
            url=raw_news.get('url', '')
        )

        # 情感分析
        news.sentiment = self.analyze_sentiment(news.title + ' ' + news.content)

        # 实体识别
        news.entities = self.extract_entities(news.content)

        # 事件类型识别
        news.event_type = self.classify_event(news)

        return news

    def analyze_sentiment(self, text: str) -> float:
        """情感分析

        返回�?
            -1（极度负面）�?1（极度正面）
        """
        # 使用情感分析模型
        score = self.sentiment_model.predict(text)
        return score

    def extract_entities(self, text: str) -> List[str]:
        """提取命名实体（股票代码、公司名称）"""
        entities = self.ner_model.extract(text)

        # 提取股票代码
        stock_codes = re.findall(r'\d{6}', text)

        # 提取公司简�?
        companies = [e for e in entities if e.type == 'ORG']

        return list(set(stock_codes + companies))
```

---

## 3. 事件类型识别

```python
EVENT_PATTERNS = {
    '财报发布': {
        'keywords': ['财报', '业绩', '净利润', '营收', '每股收益'],
        'pattern': r'(财报|业绩|利润).*(发布|公告|显示)',
        'sentiment_impact': 'positive'  # 通常利好
    },
    '分红送转': {
        'keywords': ['分红', '送股', '转增', '派息'],
        'pattern': r'(\d+)�?\d+)|(\d+)�?\d+)',
        'sentiment_impact': 'positive'
    },
    '并购重组': {
        'keywords': ['并购', '重组', '收购', '定增'],
        'pattern': r'(并购|重组|收购).*(完成|通过|公告)',
        'sentiment_impact': 'uncertain'
    },
    '政策利好': {
        'keywords': ['政策', '支持', '鼓励', '补贴', '规划'],
        'pattern': r'(支持|鼓励|补贴|政策).*(行业|产业|公司)',
        'sentiment_impact': 'positive'
    },
    '监管�?: {
        'keywords': ['监管�?, '问询�?, '警示�?, '处罚'],
        'pattern': r'(监管|问询|警示).*�?,
        'sentiment_impact': 'negative'
    },
    '减持': {
        'keywords': ['减持', '卖出', '转让'],
        'pattern': r'(股东|高管|实际控制�?.*(减持|卖出)',
        'sentiment_impact': 'negative'
    }
}

class EventClassifier:
    """事件分类�?""

    def classify_event(self, news: NewsItem) -> str:
        """识别事件类型"""
        text = news.title + ' ' + news.content

        for event_type, config in EVENT_PATTERNS.items():
            if re.search(config['pattern'], text):
                return event_type

        return 'general'  # 默认普通新�?
```

---

## 4. 舆情风险识别

```python
class RiskSentimentDetector:
    """舆情风险检�?""

    def __init__(self):
        self.risk_keywords = {
            '黑天�?: ['造假', '欺诈', '违规', '调查', '处罚'],
            '经营风险': ['亏损', '债务', '违约', '诉讼'],
            '市场风险': ['暴跌', '闪崩', '踩踏', '清仓']
        }

    def detect_risk(self, news_items: List[NewsItem]) -> Dict[str, float]:
        """检测舆情风�?

        返回�?
            风险评分 {risk_type: score}
        """
        risk_scores = {risk_type: 0.0 for risk_type in self.risk_keywords}

        for news in news_items:
            if news.sentiment is not None and news.sentiment < -0.5:
                # 高度负面新闻
                text = news.title + ' ' + news.content
                for risk_type, keywords in self.risk_keywords.items():
                    if any(kw in text for kw in keywords):
                        risk_scores[risk_type] += abs(news.sentiment)

        # 归一�?
        total = sum(risk_scores.values())
        if total > 0:
            risk_scores = {k: v/total for k, v in risk_scores.items()}

        return risk_scores

    def generate_alert(self, risk_scores: Dict[str, float], threshold: float = 0.3):
        """生成风险告警"""
        alerts = []
        for risk_type, score in risk_scores.items():
            if score > threshold:
                alerts.append({
                    'type': 'risk_sentiment',
                    'risk_type': risk_type,
                    'score': score,
                    'message': f'舆情{risk_type}风险上升 ({score:.1%})'
                })
        return alerts
```

---

## 5. 事件研究分析

```python
class EventStudy:
    """事件研究分析"""

    def __init__(self, price_loader):
        self.price_loader = price_loader

    def calculate_cumulative_return(
        self,
        symbol: str,
        event_date: datetime,
        window: tuple = (-5, 5),
        market_symbol: str = '000300.SH'
    ) -> dict:
        """计算累计超额收益 (CAR)

        参数�?
            symbol: 股票代码
            event_date: 事件日期
            window: 事件窗口 (-5, 5) 表示事件�?天到�?�?
            market_symbol: 市场基准

        返回�?
            CAR分析结果
        """
        # 获取窗口期收益率
        returns = self.price_loader.get_returns(
            symbol, event_date + timedelta(days=window[0]),
            event_date + timedelta(days=window[1])
        )
        market_returns = self.price_loader.get_returns(
            market_symbol, event_date + timedelta(days=window[0]),
            event_date + timedelta(days=window[1])
        )

        # 计算超额收益
        excess_returns = returns - market_returns

        # 计算累计超额收益
        car = excess_returns.cumsum()

        # 计算CAR
        car_window = car.loc[event_date:event_date + timedelta(days=window[1])]

        return {
            'symbol': symbol,
            'event_date': event_date,
            'car': car_window.iloc[-1],
            'car_series': car_window,
            'avg_excess_return': excess_returns.mean(),
            't_stat': self._t_test(car_window)
        }

    def run_event_study(
        self,
        events: List[dict],
        min_samples: int = 10
    ) -> pd.DataFrame:
        """批量事件研究

        参数�?
            events: 事件列表 [{symbol, event_date, event_type}]
            min_samples: 最少样本数
        """
        results = []

        for event in events:
            try:
                result = self.calculate_cumulative_return(
                    event['symbol'],
                    event['event_date']
                )
                result['event_type'] = event['event_type']
                results.append(result)
            except Exception as e:
                continue

        df = pd.DataFrame(results)

        # 按事件类型汇�?
        summary = df.groupby('event_type').agg({
            'car': ['mean', 'std', 'count'],
            't_stat': 'mean'
        }).round(4)

        # 过滤样本数过少的类型
        summary = summary[summary[('car', 'count')] >= min_samples]

        return summary

    def _t_test(self, series: pd.Series) -> float:
        """简单t检�?""
        from scipy import stats
        n = len(series)
        mean = series.mean()
        std = series.std()
        return mean / (std / (n ** 0.5)) if std > 0 else 0
```

---

## 6. 新闻因子构建

```python
class NewsFactorBuilder:
    """新闻因子构建"""

    def build_sentiment_factor(self, symbol: str, window: int = 5) -> float:
        """情感因子

        计算过去N天新闻情感加权平�?
        """
        news = self.get_news(symbol, days=window)

        if not news:
            return 0.0

        # 时间加权
        weights = [1 / (i + 1) for i in range(len(news))]
        sentiments = [n.sentiment for n in news if n.sentiment is not None]

        if not sentiments:
            return 0.0

        return sum(w * s for w, s in zip(weights, sentiments))

    def build_event_sentiment_factor(self, symbol: str) -> dict:
        """事件情感因子

        计算各类事件的累计情感得�?
        """
        news = self.get_news(symbol, days=30)

        event_sentiment = {}
        for event_type in EVENT_PATTERNS.keys():
            type_news = [n for n in news if n.event_type == event_type]
            if type_news:
                event_sentiment[event_type] = sum(n.sentiment for n in type_news)
            else:
                event_sentiment[event_type] = 0.0

        return event_sentiment

    def build_risk_sentiment_factor(self, symbol: str) -> float:
        """风险舆情因子

        综合负面新闻数量和强�?
        """
        news = self.get_news(symbol, days=5)

        risk_score = 0.0
        for n in news:
            if n.sentiment is not None and n.sentiment < -0.3:
                risk_score += abs(n.sentiment)

        return min(risk_score, 1.0)  # 归一化到0-1
```

---

## 6.5 舆情数据表结构设�?(v2.0) - 2026-03-29 确定

> 基于专业机构实践 + 个人投资�?1�?AI"模式

### 6.5.1 ClickHouse 舆情事实�?

```sql
-- ============================================================
-- 新闻事实�?(宽表设计，适合ClickHouse列式存储)
-- 版本: v2.0 确定
-- ============================================================
CREATE TABLE quant_system.news_sentiment (
    -- 主键和维�?
    news_id           String,           -- 新闻唯一ID
    stock_code        String,           -- 关联股票代码 (�? 000001.SZ)
    trade_date        Date,             -- 交易日期

    -- 新闻原始信息
    headline          String,           -- 新闻标题
    summary           String,           -- AI生成摘要 (永久保留)
    content           String,           -- 原文 (�?�?之后删除)
    source            String,           -- 来源 (东方财富/新浪�?
    source_type       Enum8('official'=1, 'media'=2, 'social'=3, 'research'=4),
    url               String,           -- 原文链接
    publish_time      DateTime,         -- 发布时间
    crawl_time        DateTime,         -- 采集时间

    -- 情感多维度分�?(v2.0新增)
    sentiment_score   Float32,          -- 情感得分 (-1 ~ +1)
    valence           Float32,          -- 效价: 愉快程度 (-1 ~ +1)
    arousal           Float32,          -- 唤醒�? 激动程�?(0 ~ 1)
    dominance         Float32,          -- 支配�? 控制程度 (0 ~ 1)
    sentiment_confidence Float32,       -- 置信�?(0 ~ 1)

    -- 事件分类 (混合模式: 预定�?AI扩展)
    event_type        String,           -- 预定义核心类�?
    event_type_ext    String,           -- AI扩展动态类�?
    event_level       Enum8('normal'=0, 'warning'=1, 'important'=2, 'major'=3),
    event_keywords    Array(String),    -- 事件关键�?

    -- 实体识别
    entities          Array(String),    -- 识别的实�?(股票/公司/�?
    mentioned_stocks  Array(String),    -- 提及的股票列�?
    mentioned_amount  Float32,          -- 提及金额 (�? 10�?

    -- ESG标签 (v2.0新增)
    esg_category      Enum8('E'=1, 'S'=2, 'G'=3, 'none'=0),
    esg_score         Float32,         -- ESG相关�?(0 ~ 1)

    -- 质量控制
    tags              Array(String),    -- 标签: ['新能�?, '政策', '龙头']
    is_reliable       UInt8,           -- 是否可靠 (1=可靠)
    relevance_score   Float32,         -- 与关联股票相关�?(0 ~ 1)
    novelty_score     Float32,         -- 新闻新颖�?(0=旧闻, 1=独家)

    -- 审计字段
    processed_time    DateTime,        -- 处理完成时间
    model_version     String           -- 使用的模型版�?

) ENGINE = MergeTree()
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, stock_code, news_id)
TTL publish_time + INTERVAL 2 YEAR;  -- 2年后删除原文，只保留summary
```

### 6.5.2 新闻-股票关联�?

```sql
-- 新闻-股票关联�?(多对多关�?
CREATE TABLE quant_system.news_stock_relation (
    news_id           String,
    stock_code        String,
    relation_type     Enum8('mentioned'=1, 'related'=2, 'impacted'=3),
    mention_count     UInt16,          -- 提及次数
    mention_position  String,          -- 首次提及位置 (title/content/both)
    sentiment_toward_stock Float32,    -- 对该股票的情�?

    PRIMARY KEY (news_id, stock_code)
) ENGINE = MergeTree();
```

### 6.5.3 预定义事件类型表

```sql
-- 事件类型维度�?(预定义核心类�?
CREATE TABLE quant_system.dim_event_type (
    event_type     String,
    event_name     String,
    event_level    Enum8('normal'=0, 'warning'=1, 'important'=2, 'major'=3),
    market_reaction String,            -- 历史平均市场反应
    avg_sentiment  Float32,            -- 该类型事件平均情�?

    PRIMARY KEY event_type
) ENGINE = MergeTree();

-- 预定义事件类�?(v2.0)
INSERT INTO dim_event_type VALUES
('earnings_pre',      '业绩预增',      'important', 'positive',  0.4),
('earnings_warn',     '业绩预警',      'important', 'negative', -0.5),
('earnings_miss',     '业绩不及预期',  'important', 'negative', -0.4),
('merger_acqui',      '并购重组',      'major',     'positive',  0.3),
('blockchain',        '区块�?,        'major',     'positive',  0.2),
('regulation',        '监管�?,         'warning',   'negative', -0.4),
('policy_benefit',    '政策利好',       'important', 'positive',  0.5),
('product_launch',    '新产品发�?,     'normal',    'positive',  0.2),
('management_change', '高管变动',       'important', 'neutral',   0.0),
('share_reduce',      '股东减持',       'warning',   'negative', -0.3),
('share_increase',    '股东增持',       'important', 'positive',  0.3),
('split_report',     '分红送转',        'normal',    'positive',  0.2),
('new_listing',      '新股上市',        'normal',    'positive',  0.3),
('delisting_risk',   '退市风�?,        'major',     'negative', -0.6),
('black_swan',       '黑天鹅事�?,       'major',     'negative', -0.7),
('industry_upgrade',  '行业升级',        'important', 'positive',  0.3),
('macroeconomy',     '宏观经济',         'important', 'neutral',   0.0);
```

### 6.5.4 情感多维度专业指标说�?

| 指标 | 范围 | 专业机构用�?| 示例 |
|------|------|-------------|------|
| **sentiment_score** | -1 ~ +1 | 基础情感因子 | 简单直�?|
| **valence** | -1 ~ +1 | 效价(愉快程度) | "央行降准" valence=+0.7 |
| **arousal** | 0 ~ 1 | 唤醒�?激动程�? | 突发新闻 arousal=0.9 |
| **dominance** | 0 ~ 1 | 支配�?控制程度) | 官方发布 dominance=0.9 |
| **sentiment_confidence** | 0 ~ 1 | 模型置信�?| 过滤低质量分�?|

### 6.5.5 存储策略

| 数据类型 | 保留期限 | 存储策略 |
|---------|---------|---------|
| headline, summary | **永久** | 核心数据资产 |
| content (原文) | **2�?* | TTL自动删除，节�?0%空间 |
| 情感得分/实体/事件 | **永久** | 结构化高效存�?|
| ESG标签 | **永久** | 随新闻保�?|

### 6.5.6 数据量估�?

| �?| 日增�?| 年增�?| 压缩�?|
|---|--------|--------|--------|
| news_sentiment | ~5万条 | ~1500万条 | ~10GB/�?|
| news_stock_relation | ~15万条 | ~4500万条 | ~5GB/�?|
| dim_event_type | 静�?| ~20�?| 可忽�?|

---

## 6. 新闻数据获取方案 (v2.0) - 2026-03-29 确定

> 采用"混合双打"模式，充分利用免费资�?

### 6.0.1 新闻数据源汇�?

| 数据�?| 免费额度 | 专业�?| A股支�?| 个股代码 | API状�?|
|--------|---------|--------|---------|---------|---------|
| **Alpha Vantage** | 25�?�?| ⭐⭐⭐⭐�?| �?| �?不支�?| �?已测�?|
| **Finnhub** | 60�?分钟 | ⭐⭐⭐⭐ | �?| �?不支�?| �?已测�?|
| **Marketaux** | 100�?�?| ⭐⭐⭐⭐ | �?| �?不支�?| �?已测�?|
| **AkShare** | 无限�?| ⭐⭐�?| �?| �?支持 | ⚠️ 不稳�?|
| **iFinD** | 需账号 | ⭐⭐⭐⭐�?| �?| �?支持 | ⚠️ 无权�?|
| **Tushare** | 付费 | ⭐⭐⭐⭐ | �?| �?支持 | 待购�?|

**详细测试结果�?6.0.9 �?*

### 6.0.2 Alpha Vantage (美股专用 - 自带情感分析)

```python
import requests

api_key = 'Q4V376TF4JKPFRCI'
url = 'https://www.alphavantage.co/query'
params = {
    'function': 'NEWS_SENTIMENT',
    'tickers': 'AAPL',  # 美股格式
    'apikey': api_key,
    'limit': 50
}
response = requests.get(url, params=params)
data = response.json()

# 返回字段:
# - overall_sentiment_score: 总体情感得分 (-1 ~ +1)
# - overall_sentiment_label: "Bullish", "Bearish", "Neutral"
# - topics: [{topic, relevance_score}]
# - ticker_sentiment: [{ticker, sentiment_score, relevance_score}]
```

**优势**: 直接返回情感得分，无需自己训练NLP模型
**限制**: ⚠️ 仅支持美股，A股格�?600519.SH)返回Invalid ticker format
**适用**: 美股新闻情感分析、与A股关联度�?

### 6.0.3 Finnhub (美股专用 - 实时性强)

```python
import requests

api_key = 'd74lr19r01qg1eo5vib0d74lr19r01qg1eo5vibg'
url = 'https://finnhub.io/api/v1/news'
params = {
    'category': 'general',  # general/business/technology/etc
    'token': api_key
}
response = requests.get(url, params=params)
data = response.json()

# 返回字段:
# - headline: 新闻标题
# - summary: 新闻摘要
# - source: 来源 (Reuters/CNBC etc)
# - category: 类别
```

**优势**: 每分�?0次请求，实时性强，覆盖全球新�?
**限制**: ⚠️ 主要覆盖美股，A股公司新闻数据有�?
**适用**: 美股实时监控

### 6.0.4 Marketaux (⭐推�?- 全球市场+情感分析)

```python
import requests

api_token = '1IDURCqFtIglEtB0f9ZPKEMfl9YF7onH7BQUyIrt'
url = 'https://api.marketaux.com/v1/news/all'

# 1. 获取全球金融新闻
params = {
    'api_token': api_token,
    'limit': 50
}

# 2. 按国家过�?(中国)
params = {
    'api_token': api_token,
    'countries': 'cn',  # 中国
    'limit': 50
}

# 3. 按情感筛�?
params = {
    'api_token': api_token,
    'sentiment_gte': 0.5,  # 高情感得�?
    'limit': 50
}

# 4. 关键词搜�?
params = {
    'api_token': api_token,
    'search': 'China stock market',
    'limit': 50
}

response = requests.get(url, params=params)
data = response.json()

# 返回字段:
# - title: 新闻标题
# - description: 新闻描述
# - source: 来源
# - published_at: 发布时间
# - entities: [{name, sentiment_score, country, exchange}]
```

**优势**:
- �?支持全球80+市场，包括中�?�?
- �?自带情感分析 (sentiment_score: -1 ~ +1)
- �?100�?天免费额�?
- �?可按国家/交易所/情感筛�?

**测试结果**:
```
�?countries=cn: 返回3条中国相关新�?
�?exchanges=SSE: 支持上海证券交易所
�?sentiment_gte=0.5: 可筛选高情感新闻
�?关键�?China stock market": 有结�?
```

**适用**: A�?港股新闻情感分析

### 6.0.6 A股新闻来�?(国内平台)

```python
import akshare as ak

# 央视新闻 (较稳�?
df = ak.news_cctv()

# 个股新闻 (东方财富)
df = ak.stock_news_em(symbol="000001")

# 市场主要新闻
df = ak.stock_news_main_cx()
```

**优势**: A股新闻全覆盖，来源包括东方财�?新浪/同花顺等
**限制**: 接口不稳定，可能失效
**适用**: A股舆情分�?

### 6.0.7 混合使用策略

```python
# A股新�?(主力)
# - Marketaux: 全球市场+情感分析 (100�?�? ⭐推�?
# - AkShare: 东方财富、同花顺�?(免费)
# - iFinD: 同花顺官�?(需开通权�?
# - Tushare: 财联社等 (付费)

# 美股新闻 + 情感分析 (辅助)
# - Alpha Vantage: 自带情感评分 (25�?�?
# - Finnhub: 实时新闻 (60�?分钟)

def get_china_news_with_sentiment():
    """获取A股新�?情感 - 使用Marketaux"""
    import requests
    api_token = '1IDURCqFtIglEtB0f9ZPKEMfl9YF7onH7BQUyIrt'
    url = 'https://api.marketaux.com/v1/news/all'
    params = {
        'api_token': api_token,
        'countries': 'cn',
        'limit': 50
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data  # 自带情感得分

def get_us_sentiment(ticker):
    """获取美股情感 - 使用Alpha Vantage"""
    import requests
    api_key = 'Q4V376TF4JKPFRCI'
    ...
```

**推荐策略**:
1. **A股舆�?*: Marketaux (主力) + AkShare (备用)
2. **美股情感**: Alpha Vantage (自带情感分析)
3. **实时监控**: Finnhub (高频)

### 6.0.8 全球市场覆盖对比

| 市场 | Alpha Vantage | Finnhub | Marketaux | AkShare | iFinD |
|------|--------------|---------|-----------|---------|-------|
| A股个�?| �?| �?| �?| �?| �?|
| A股宏�?| �?| �?| �?| �?| �?|
| 港股 | �?| ⚠️ | �?| �?| �?|
| 美股 | �?| �?| �?| �?| �?|

**结论**:
- A股个股新�? AkShare/iFinD/Tushare
- A股宏�?情感: Marketaux
- 美股+情感: Alpha Vantage
- 实时监控: Finnhub

---

### 6.0.9 新闻API详细测试结果 (2026-03-30)

#### 测试平台汇�?

| 平台 | 测试接口�?| 成功�?| 可用�?|
|------|-----------|--------|--------|
| AkShare | 7 | 2 | news_cctv, futures_news_shmet |
| iFinD | 4 | 1 | 登录成功 |
| Alpha Vantage | 1 | 1 | NEWS_SENTIMENT |
| Finnhub | 1 | 1 | news |
| Marketaux | 1 | 1 | news/all |

#### AkShare测试结果 (2026-03-30)

| 接口 | 状�?| 数据�?| 说明 |
|------|------|--------|------|
| stock_news_em | �?失败 | 0 | 东方财富API返回解析错误 |
| news_cctv | �?成功 | 12 | 央视新闻正常 |
| futures_news_shmet | �?成功 | 10 | 期货新闻正常 |
| news_economic_baidu | ⚠️ 成功 | 0 | 空数�?|
| news_trade_notify_suspend_baidu | ⚠️ 成功 | 0 | 空数�?|
| news_trade_notify_dividend_baidu | ⚠️ 成功 | 0 | 空数�?|
| news_report_time_baidu | ⚠️ 成功 | 0 | 空数�?|

**结论**: AkShare部分接口不稳定，但央视新闻和期货新闻可用�?

#### iFinD测试结果

| 接口 | 状�?| errorcode | 说明 |
|------|------|-----------|------|
| 登录 | �?成功 | 0 | 账号登录正常 |
| THS_iwencai | �?无数�?| -4001 | 新闻无权�?|
| THS_ReportQuery | �?参数错误 | -4210 | 参数格式错误 |
| THS_BD | �?参数错误 | -209 | 指标参数无效 |

**结论**: iFinD新闻接口需要开通权限，当前账号无可用新闻数据�?

#### Alpha Vantage测试结果

| 接口 | 状�?| 说明 |
|------|------|------|
| NEWS_SENTIMENT | �?成功 | 美股自带情感分析 |

#### Finnhub测试结果

| 接口 | 状�?| 说明 |
|------|------|------|
| news | �?成功 | 美股实时新闻 |

#### Marketaux测试结果

| 测试�?| 状�?| 说明 |
|--------|------|------|
| 全球新闻 | �?成功 | 3�?|
| countries=cn | �?成功 | 中国相关新闻 |
| exchanges=SSE | ⚠️ 有数�?| 但非A股公�?|
| A股代码查�?| �?无数�?| 600519等返回空 |

**结论**: Marketaux不支持按A股代码查询，只能获取宏观中国新闻�?

---

## 7. 舆情系统验证方案

### 6.1 验证挑战

```
舆情分析 vs 价格走势：鸡生蛋问题
┌─────────────────────────────────────────────────────────────�?
�?                                                            �?
�? 我们想用舆情预测股价                                        �?
�?          �?                                                �?
�? 但股价本身反映舆�?                                        �?
�?          �?                                                �?
�? 如何知道AI情感分析是否正确�?                               �?
�?                                                            �?
└─────────────────────────────────────────────────────────────�?
```

### 6.2 验证方案

| 方案 | 说明 | 实施难度 |
|------|------|----------|
| **事后验证�?* | 对比历史新闻情感与次日股价涨�?| �?简�?|
| **标注数据�?* | 人工标注100条新闻，对比AI准确�?| �?中等 |
| **因子IC验证** | 计算舆情因子与收益相关�?| ⭐⭐�?科学 |

### 6.3 IC验证 (最科学)

```
IC (Information Coefficient) = corr(舆情分数, 次日收益)

判断标准:
├── |IC| > 0.03  �?因子有效
├── |IC| > 0.05  �?因子较强
└── |IC| < 0.02  �?因子无效，需优化
```

### 6.4 反馈闭环

```
AI分析 ──�?回测验证 ──�?IC结果 ──�?优化模型 ──�?持续监控
              �?
              └──�?定期输出验证报告
```

---

## 7. 数据存储方案

### 7.1 实际数据量估�?

```
┌─────────────────────────────────────────────────────────────�?
�?                  数据量详细估�?                            �?
├─────────────────────────────────────────────────────────────�?
�?                                                            �?
�? 1. 分钟K线数�?(重点!)                                    �?
�?    5000�?× 240分钟/�?× 250�?× 10�?                   �?
�?    = 30亿条记录  �?50-100 GB                             �?
�?                                                            �?
�? 2. 因子数据                                              �?
�?    5700因子 × 5000�?× 2500�?�?10-50 GB                �?
�?                                                            �?
�? 3. 舆情/新闻数据                                         �?
�?    ~1亿条新闻 × 2KB �?200 GB                             �?
�?                                                            �?
�? ════════════════════════════════════════════════════       �?
�? 总计: 100-400 GB ⚠️                                      �?
�?                                                            �?
└─────────────────────────────────────────────────────────────�?
```

### 7.2 存储选型对比

| 方案 | 处理能力 | 优点 | 缺点 |
|------|----------|------|------|
| PostgreSQL | < 50GB | 简�?| 分区复杂 |
| TimescaleDB | < 100GB | 自动分区 | 勉强 |
| **ClickHouse** | **100GB+** | 列式存储、压缩强 | 需单独部署 |
| **分层存储** | **TB�?* | 冷热分离 | 需管理 |

### 7.3 最终存储方案(v2.0) - 2026-03-29 确定

> **术语说明**: 本节中的"Layer 1/2/3"指的是数据存储层级（热数据、温数据、冷数据），而非系统架构层级。这是数据工程领域的标准术语，用于描述数据生命周期管理中的不同存储阶段。

> **基于专业量化机构实践 + 个人投资者硬件配置(RTX 3090 + 64GB RAM + 1.2TB SSD)**

```
┌─────────────────────────────────────────────────────────────�?
�?         Layer 1: 热数�?(Redis - SSD)                      �?
├─────────────────────────────────────────────────────────────�?
�? 存储介质: Redis (高性能内存数据�?                         �?
�?                                                            �?
�? 数据范围:                                                  �?
�? ├── 1分钟K�? 最�?0交易�?(~30GB)                       �?
�? ├── 实时因子: 当日计算结果                                �?
�? └── 最新行�? tick级盘�?                                 �?
�?                                                            �?
�? 用�? 实盘交易、当日策略执�?                              �?
�? 保留策略: 60个交易日�?分钟数据降采样为5分钟            �?
└─────────────────────────────────────────────────────────────�?
                            �?
┌─────────────────────────────────────────────────────────────�?
�?         Layer 2: 温数�?(ClickHouse)                     �?
├─────────────────────────────────────────────────────────────�?
�? 存储介质: ClickHouse (列式存储)                           �?
�?                                                            �?
�? 数据范围:                                                  �?
�? ├── 5/15/30/60分钟K�? �?�?(~20GB)                  �?
�? ├── 日K�? �?�?(~10GB)                                �?
�? ├── 财务数据: �?�?(~5GB)                              �?
�? └── 舆情结构化数�? �?�?(~10GB)                       �?
�?                                                            �?
�? 用�? 中期回测、策略验证、因子计�?                       �?
└─────────────────────────────────────────────────────────────�?
                            �?
┌─────────────────────────────────────────────────────────────�?
�?         Layer 3: 冷数�?(ClickHouse压缩)                  �?
├─────────────────────────────────────────────────────────────�?
�? 存储介质: ClickHouse (高压缩率)                          �?
�?                                                            �?
�? 数据范围:                                                  �?
�? ├── 日K�? 10�?历史 (~30GB)                            �?
�? ├── 降采�?分钟: 3年前数据 (~15GB)                     �?
�? └── 舆情归档: 2年前历史 (~20GB)                         �?
�?                                                            �?
�? 用�? 长期回测、全市场扫描、历史验�?                     �?
└─────────────────────────────────────────────────────────────�?

总计压缩后存�? ~110GB
```

### 7.4 存储选型对比

| 方案 | 处理能力 | 优点 | 缺点 |
|------|----------|------|------|
| PostgreSQL | < 50GB | 简�?| 分区复杂 |
| TimescaleDB | < 100GB | 自动分区 | 勉强 |
| **ClickHouse** | **100GB+** | 列式存储、压缩强 | 需单独部署 |
| **分层存储** | **TB�?* | 冷热分离 | 需管理 |

### 7.5 ClickHouse + Redis 配置

```python
# ClickHouse 配置
CLICKHOUSE_CONFIG = {
    'host': 'localhost',
    'database': 'quant_system',
    'port': 9000,
    'tables': {
        # K线数�?(按频率分�?
        'kline_1min': '1分钟K�?(热数�? 60交易�?',
        'kline_5min': '5分钟K�?(温数�? �?�?',
        'kline_15min': '15分钟K�?(温数�? �?�?',
        'kline_30min': '30分钟K�?(温数�? �?�?',
        'kline_60min': '60分钟K�?(温数�? �?�?',
        'kline_daily': '日K�?(温数�?�?冷数�?0�?)',
        # 财务数据
        'financial_data': '财务报表数据',
        # 舆情数据
        'news_sentiment': '舆情结构化数�?(情感/实体/事件)',
        # 因子数据
        'factors_alpha': 'Alpha因子'
    }
}

# Redis 热数据缓�?
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'ttl': 86400,  # 1�?
    'hot_data': [
        'recent_60day_1min_kline',  # 最�?0交易�?分钟K�?
        'realtime_factors',          # 当日实时因子
        'latest_quotes'             # 最新行�?
    ]
}
```

### 7.6 分层存储架构�?

```
┌─────────────────────────────────────────────────────────────�?
�?                  分层存储架构                             �?
├─────────────────────────────────────────────────────────────�?
�?                                                            �?
�? ┌─────────────────────────────────────────────────────�?�?
�? �?         Layer 1: 热数�?(Redis/SSD)               �?�?
�? �?                                                    �?�?
�? �? 最�?0交易�?                                      �?�?
�? �? ├── 1分钟K�?(原始最细粒�?                      �?�?
�? �? ├── 实时因子                                       �?�?
�? �? └── Tick数据 (可�?                               �?�?
�? �?                                                    �?�?
�? �? 大小: ~30 GB                                       �?�?
�? �? 用�? 实盘交易、当日策�?                         �?�?
�? �? 淘汰策略: 60日后降采样为5分钟                    �?�?
�? └─────────────────────────────────────────────────────�?�?
�?                          �?                                �?
�? ┌─────────────────────────────────────────────────────�?�?
�? �?         Layer 2: 温数�?(ClickHouse)              �?�?
�? �?                                                    �?�?
�? �? �?-5�?                                           �?�?
�? �? ├── 5/15/30/60分钟K�?                           �?�?
�? �? ├── 日K�?(�?�?                                 �?�?
�? �? ├── 财务数据                                       �?�?
�? �? └── 舆情结构�?(�?�?                            �?�?
�? �?                                                    �?�?
�? �? 大小: ~45 GB                                       �?�?
�? �? 用�? 中期回测、策略验�?                         �?�?
�? └─────────────────────────────────────────────────────�?�?
�?                          �?                                �?
�? ┌─────────────────────────────────────────────────────�?�?
�? �?         Layer 3: 冷数�?(ClickHouse压缩)          �?�?
�? �?                                                    �?�?
�? �? 5-10�?:                                          �?�?
�? �? ├── 日K�?(10�?)                                 �?�?
�? �? ├── 降采�?分钟 (归档)                            �?�?
�? �? └── 舆情历史归档                                  �?�?
�? �?                                                    �?�?
�? �? 大小: ~65 GB                                       �?�?
�? �? 用�? 长期回测、全市场扫描                        �?�?
�? └─────────────────────────────────────────────────────�?�?
�?                                                            �?
�? ══════════════════════════════════════════════════════�?  �?
�? 总计压缩存储: ~110 GB �?适合1.2TB SSD                   �?
�? ══════════════════════════════════════════════════════�?  �?
�?                                                            �?
└─────────────────────────────────────────────────────────────�?
```

### 7.7 专业机构存储策略参�?

> 参�? 量化数据中台最佳实�?

| 数据类型 | 保留策略 | 压缩�?| 说明 |
|---------|---------|--------|------|
| 1分钟K�?| **保留60交易�?*，之后降采样 | ~70%空间节省 | 覆盖策略参数优化需�?|
| 5/15/30/60分钟 | **全部保留** 1�?| 列式压缩 ~40% | 机构研究证明5分钟足够99%策略 |
| 日K�?| **永久保留** | 列式压缩 ~60% | 核心历史数据 |
| 财务数据 | **永久保留** | 列式压缩 ~50% | 估值因子必需 |
| 舆情结构�?| **永久保留结构�?*，文本可�?| ~80%空间节省 | 情感得分/实体/事件 |
| 舆情向量 | **可�?*，如需语义检索加ChromaDB | - | 后续扩展 |

### 7.8 短期 vs 长期回测方案

```
┌─────────────────────────────────────────────────────────────�?
�?                  分层回测架构                             �?
├─────────────────────────────────────────────────────────────�?
�?                                                            �?
�? ══════════════════════════════════════════════════════�?  �?
�? 短期回测 (�?�? - 高精�?                                �?
�? ══════════════════════════════════════════════════════�?  �?
�? 数据: Redis 热数�?                                      �?
�? 精度: 分钟�?                                             �?
�? 用�? 策略开发、参数优�?                                 �?
�?                                                            �?
�? ══════════════════════════════════════════════════════�?  �?
�? 中期回测 (1-5�? - 标准精度                              �?
�? ══════════════════════════════════════════════════════�?  �?
�? 数据: ClickHouse 温数�?                                 �?
�? 精度: 日线�?                                             �?
�? 用�? 策略验证、稳健性检�?                              �?
�?                                                            �?
�? ══════════════════════════════════════════════════════�?  �?
�? 长期回测 (5-10�? - 抽样精度                             �?
�? ══════════════════════════════════════════════════════�?  �?
�? 数据: ClickHouse 冷数�?                                 �?
�? 精度: 日线�?                                             �?
�? 用�? 全市场扫描、长期趋势验�?                          �?
�?                                                            �?
└─────────────────────────────────────────────────────────────�?
```

### 7.6 回测工作�?

```
1. 新策略开�?
   └── 短期回测 (�?年，分钟�? �?快速验�?

2. 策略优化
   └── 中期回测 (3-5年，日线�? �?参数调优

3. 策略验证
   └── 长期回测 (全量历史) �?稳健性检�?

4. 实盘部署
   └── 实时数据 �?盘中监控
```

### 7.10 ClickHouse 性能保证

```
查询速度:
├── 100GB数据查询: < 3�?
├── 全A�?0年日K: < 1�?
├── 单只股票5年分钟K: < 0.5�?
└── 并行查询: 自动利用多核

压缩能力:
├── 列式存储，压缩比 10:1 ~ 20:1
├── 100GB原始数据 �?5-10GB存储
└── 磁盘占用小，查询更快
```

---

## 8. 另类因子体系（免费数据源�?

> **版本**: v1.0
> **更新日期**: 2026-03-30
> **数据源分�?*: iFinD（主�?900因子�? 另类因子（免费API补充�?

### 8.1 因子分类体系

| 类别 | 数据�?| 更新频率 | 说明 |
|------|--------|----------|------|
| **iFinD因子** | iFinD | 分钟/�?| 5900+量化因子（付费订阅） |
| **另类因子** | 免费API | 日频 | 天气/搜索/资金流等 |
| **舆情因子** | AkShare�?| 实时 | 新闻情感/事件驱动 |

### 8.2 免费另类因子获取渠道

#### 8.2.1 资金流因子（⭐推�?- 免费且稳定）

| 因子 | 获取方式 | 免费额度 | 实现难度 |
|------|----------|----------|----------|
| 北向资金 | 东方财富 | 无限�?| �?|
| 融资融券 | 东方财富 | 无限�?| �?|
| 龙虎�?| 上交所/深交所 | 无限�?| �?|
| 大宗交易 | 东方财富 | 无限�?| �?|

```python
import akshare as ak

# 北向资金（沪深港通）
df = ak.stock_board_em()  # 概念板块资金�?
df = ak.stock_individual_em()  # 个股资金�?

# 融资融券
df = ak.stock_margin_detail_sz()  # 深圳融资融券
df = ak.stock_margin_detail_sh()  # 上海融资融券

# 龙虎�?
df = ak.stock_lhb_detail_em()  # 龙虎榜明�?
```

#### 8.2.2 天气/气候因子（⭐推�?- 免费API�?

| 因子 | 免费API | 日额�?| 适用场景 |
|------|---------|--------|----------|
| 温度/天气 | 心知天气 | 400�?�?| 消费/农业股票 |
| 空气质量AQI | PM25.in | 1000�?�?| 环保/医药 |
| 台风/极端天气 | 国家气象局 | 公开数据 | 农业/保险 |

```python
# 心知天气API（免费注册）
import requests

def get_weather(city="beijing"):
    """获取城市天气数据"""
    api_key = "your_api_key"  # 免费注册获取
    url = f"https://api.seniverse.com/v3/weather/daily.json"
    params = {
        "key": api_key,
        "location": city,
        "language": "zh-Hans",
        "unit": "c"
    }
    response = requests.get(url, params=params)
    return response.json()

# PM25.in（免费，无需注册�?
def get_aqi(city="beijing"):
    """获取AQI数据"""
    url = f"https://api.waqi.info/feed/{city}/"
    params = {"token": "your_token"}  # 免费注册获取
    response = requests.get(url, params=params)
    return response.json()
```

#### 8.2.3 搜索指数因子（⭐推荐 - 百度/Google�?

| 因子 | API | 免费额度 | 说明 |
|------|-----|----------|------|
| 百度搜索指数 | AkShare | 无限�?| 关键词搜索热�?|
| 百度资讯指数 | AkShare | 无限�?| 新闻关注�?|
| 百度需求图�?| AkShare | 无限�?| 用户意图 |

```python
import akshare as ak

# 百度搜索指数（关键词�?
df = ak.baidu_search_index(keyword="茅台", start_date="20230101", end_date="20230331")

# 百度资讯指数
df = ak.baidu_info_index(keyword="新能源汽�?, start_date="20230101", end_date="20230331")
```

#### 8.2.4 社交媒体因子（免费）

| 因子 | API | 免费额度 | 说明 |
|------|-----|----------|------|
| 微博讨论 | 微博API | 部分免费 | 社交情绪 |
| 雪球评论 | 雪球 | 需要爬�?| 投资者情�?|
| 东方财富股吧 | AkShare | 免费 | 散户情绪 |

```python
import akshare as ak

# 东方财富股吧帖子
df = ak.stock_guba_sina()  # 股吧帖子列表

# 东方财富个股评论
df = ak.stock_comment_sina()  # 个股评论情绪
```

#### 8.2.5 宏观经济因子（⭐官方免费�?

| 因子 | 数据�?| 获取方式 | 更新频率 |
|------|--------|----------|----------|
| GDP | 国家统计局 | 公开数据 | 季度 |
| CPI/PPI | 国家统计局 | 公开数据 | 月度 |
| 央行利率 | 中国人民银行 | 公开数据 | 不定�?|
| 社融数据 | 央行 | 公开数据 | 月度 |

```python
import akshare as ak

# CPI数据
df = ak.macro_china_cpi()

# 社融数据
df = ak.macro_china_shrzgm()

# 央行公开市场操作
df = ak.macro_china_central_bank()
```

#### 8.2.6 政策事件因子（⭐免费�?

| 因子 | 获取方式 | 更新频率 |
|------|----------|----------|
| 政策公告 | 政府网站RSS | 实时 |
| 监管�?| 东方财富 | 日更 |
| 研报发布 | 东方财富 | 日更 |

```python
import akshare as ak
import feedparser

# 监管�?
df = ak.stock_regulatory_notice_em()

# 研报
df = ak.stock_research_report_em()

# 政府RSS
def fetch_gov_rss():
    """获取政府网站政策"""
    feeds = {
        '国务�?: 'http://www.gov.cn/xxgk/gmxbmmrdf/servlexml/xxgkml.xml',
        '证监�?: 'http://www.csrc.gov.cn/csrc/cxxw/rss.xml',
    }
    for name, url in feeds.items():
        feed = feedparser.parse(url)
        print(f"{name}: {len(feed.entries)} �?)
```

### 8.3 免费另类因子汇总表

| 优先�?| 因子类别 | 具体因子 | 免费程度 | 实现难度 |
|--------|----------|----------|----------|----------|
| 🔴 �?| 资金�?| 北向/融资融券/龙虎�?| ⭐⭐⭐⭐�?| �?|
| 🔴 �?| 交易行为 | 大宗/杠杆资金 | ⭐⭐⭐⭐�?| �?|
| 🟡 �?| 搜索指数 | 百度搜索/资讯指数 | ⭐⭐⭐⭐ | �?|
| 🟡 �?| 天气AQI | 温度/空气质量 | ⭐⭐⭐⭐ | ⭐⭐ |
| 🟢 �?| 社交媒体 | 微博/股吧情绪 | ⭐⭐�?| ⭐⭐ |
| 🟢 �?| 宏观经济 | GDP/CPI/利率 | ⭐⭐⭐⭐�?| �?|

### 8.4 因子更新频率矩阵（专业机构标准）

#### 8.4.1 按频率分类的因子体系

| 频率级别 | 更新频率 | 因子类别 | 代表因子 |
|----------|----------|----------|----------|
| **高频** | tick/分钟 | 行情因子 | 价格/成交�?波动�?订单�?|
| **日频** | 日更(盘后) | 资金�?技�?| 北向/融资融券/换手�?RSI/MACD |
| **周频** | 周更 | 部分另类 | 搜索指数(周级) |
| **低频** | 季更/月更 | 基本�?宏观 | ROE/PE/GDP/CPI |

#### 8.4.2 详细因子更新频率�?

| 因子类别 | 具体因子 | 更新频率 | 计算来源 | 数据�?|
|----------|----------|----------|----------|--------|
| **行情�?* | 实时价格 | tick | 实时行情 | iFinD |
| | 成交�?成交�?| tick | 实时行情 | iFinD |
| | 波动�?HV) | 分钟 | 分钟数据计算 | iFinD |
| | K�?1/5/15/60分钟) | 分钟 | K线合�?| iFinD |
| **资金�?* | 北向资金 | **日更(盘后)** | 沪深港�?| 东方财富 |
| | 融资融券 | **日更(盘后)** | 交易所 | 东方财富 |
| | 龙虎�?| **日更(盘后)** | 交易所 | 上交所/深交所 |
| | 大宗交易 | **日更(盘后)** | 交易所 | 东方财富 |
| **技术类** | RSI/MACD | 分钟 | K线计�?| iFinD |
| | 均线(MA) | 分钟 | K线计�?| iFinD |
| | 布林�?| 分钟 | K线计�?| iFinD |
| **基本�?* | PE/PB/PS | **日更** | 行情+财务 | iFinD |
| | ROE/毛利�?| **季更** | 财报 | iFinD |
| | 资产负债率 | **季更** | 财报 | iFinD |
| | 营收/利润 | **季更** | 财报 | iFinD |
| **另类-搜索** | 百度搜索指数 | **日更** | 百度API | AkShare |
| | 百度资讯指数 | **日更** | 百度API | AkShare |
| **另类-天气** | 温度/天气 | **日更** | 气象API | 心知天气 |
| | AQI空气质量 | **日更** | 环保API | PM25.in |
| **另类-宏观** | GDP | **季更** | 国家统计局 | 公开数据 |
| | CPI/PPI | **月更** | 国家统计局 | 公开数据 |
| | 央行利率 | **不定�?* | 央行 | 公开数据 |
| **舆情** | 新闻情感 | **实时** | NLP分析 | AkShare |
| | 监管�?| **日更** | 东方财富 | AkShare |
| | 公告事件 | **实时** | 交易所 | iFinD |
| | 研报发布 | **日更** | 东方财富 | AkShare |

#### 8.4.3 专业机构每日更新流程

```
┌─────────────────────────────────────────────────────────────�?
�?              专业机构数据更新流程 (A�?                       �?
├─────────────────────────────────────────────────────────────�?
�?                                                            �?
�? ══════════════════════════════════════════════════════�?  �?
�? 盘前 (08:30-09:00)                                       �?
�? ══════════════════════════════════════════════════════�?  �?
�? ├── 隔夜新闻/舆情更新                                     �?
�? ├── 前一日资金流数据(北向/融资融券)                       �?
�? ├── 盘前公告/监管�?                                     �?
�? └── 当日应关注的财报发布                                  �?
�?                                                            �?
�? ══════════════════════════════════════════════════════�?  �?
�? 盘中 (09:30-11:30 / 13:00-15:00)                        �?
�? ══════════════════════════════════════════════════════�?  �?
�? ├── 实时行情 tick�?�?存储Redis                           �?
�? ├── 分钟K线更�?�?1/5/15/60分钟                          �?
�? ├── 实时舆情监控 �?新闻/公告事件                          �?
�? └── 策略信号生成 �?根据分钟因子                           �?
�?                                                            �?
�? ══════════════════════════════════════════════════════�?  �?
�? 盘后 (15:00-18:00)                                       �?
�? ══════════════════════════════════════════════════════�?  �?
�? ├── 日K线生�?�?存储ClickHouse                           �?
�? ├── 日频因子计算 �?换手�?波动�?资金�?                  �?
�? ├── 龙虎榜数据更�?                                       �?
�? └── 北向资金数据更新                                      �?
�?                                                            �?
�? ══════════════════════════════════════════════════════�?  �?
�? 晚间 (18:00-22:00)                                       �?
�? ══════════════════════════════════════════════════════�?  �?
�? ├── 公告/财报数据下载                                     �?
�? ├── 基本面因子日更新(PE/PB�?                             �?
�? ├── 另类因子(日频)更新 �?百度指数/天气                    �?
�? └── 舆情日度汇�?                                        �?
�?                                                            �?
�? ══════════════════════════════════════════════════════�?  �?
�? 周末 (可�?                                               �?
�? ══════════════════════════════════════════════════════�?  �?
�? ├── 月度宏观数据更新 �?CPI/GDP                            �?
�? ├── 季频基本面因子更�?�?ROE/营收�?                       �?
�? └── 因子 IC 回测验证                                      �?
�?                                                            �?
└─────────────────────────────────────────────────────────────�?
```

#### 8.4.4 你的5900因子的频率分�?

| 因子频率 | 占比估计 | iFinD示例 | 实现方式 |
|----------|----------|-----------|----------|
| **分钟�?* | ~20% | 技术指标、趋势类 | iFinD实时 |
| **日频** | ~50% | 大部分量化因�?| iFinD日更 |
| **周频** | ~10% | 部分另类因子 | AkShare |
| **季频** | ~20% | 基本面、财务类 | iFinD财报 |

### 8.5 快速实现路�?

```python
# Phase 1: 资金流因子（1天）
fund_flow = {
    'north_flow': ak.stock_em_hsgt_north_net_flow_in(),  # 北向资金
    'margin': ak.stock_margin_detail_sz(),  # 融资融券
    'lhb': ak.stock_lhb_detail_em(),  # 龙虎�?
}

# Phase 2: 搜索因子�?天）
search_index = {
    'baidu_search': ak.baidu_search_index(keyword="茅台"),
}

# Phase 3: 天气因子�?天）
weather = {
    'temperature': get_weather(city="shanghai"),
    'aqi': get_aqi(city="beijing"),
}
```

### 8.6 专业机构5900因子处理策略

> **数据�?*: iFinD（租用计算资源）
> **本地存储**: 仅存储K线、舆情、资金流等本地计算的数据
> **因子处理**: iFinD服务器预计算，本地按需调用

#### 8.6.1 因子分类策略

| 因子类型 | 数量估算 | 计算策略 | 存储位置 |
|----------|----------|----------|----------|
| **日频因子** | ~3000�?| iFinD预计�?| 本地可选存�?|
| **分钟因子** | ~1000�?| iFinD实时计算 | Redis缓存 |
| **基础因子** | ~2000�?| iFinD历史计算 | 本地存储K线后计算 |

#### 8.6.2 专业机构因子处理流程

```
┌─────────────────────────────────────────────────────────────────────�?
�?             专业机构5900因子处理流程 (iFinD模式)                      �?
├─────────────────────────────────────────────────────────────────────�?
�?                                                                    �?
�? ══════════════════════════════════════════════════════════════�?  �?
�? 第一�? 因子元数据管�?                                          ══�?
�? ══════════════════════════════════════════════════════════════�?  �?
�?                                                                    �?
�? ┌─────────────────────────────────────────────────────────────�?  �?
�? �? 因子目录 (Factor Catalog) - iFinD提供:                       �?  �?
�? �? ├── THS_DP: 总市�?                                    �?  �?
�? �? ├── THS_DAYCHANGE: 日涨�?                              �?  �?
�? �? ├── THS_MA: 移动平均�?                                 �?  �?
�? �? ├── THS_RSI: 相对强弱指数                                �?  �?
�? �? └── ... (5900个因�?                                    �?  �?
�? └─────────────────────────────────────────────────────────────�?  �?
�?                             �?                                     �?
�? ══════════════════════════════════════════════════════════════�?  �?
�? 第二�? 因子分类                                               ══�?
�? ══════════════════════════════════════════════════════════════�?  �?
�?                                                                    �?
�? ┌─────────────────────────────────────────────────────────────�?  �?
�? �? 从iFinD下载因子列表 �?人工/自动分类:                       �?  �?
�? �?                                                             �?  �?
�? �? ├── 日频因子: 估�?财务/动量�?�?盘后批量获取           �?  �?
�? �? ├── 分钟因子: 技术指标类 �?盘中实时调用                   �?  �?
�? �? └── 基础因子: 价格�?�?存储K线后按需计算               �?  �?
�? └─────────────────────────────────────────────────────────────�?  �?
�?                             �?                                     �?
�? ══════════════════════════════════════════════════════════════�?  �?
�? 第三�? 调用方式                                               ══�?
�? ══════════════════════════════════════════════════════════════�?  �?
�?                                                                    �?
�? ┌─────────────────────────────────────────────────────────────�?  �?
�? �? 盘后18:00 (日频因子):                                      �?  �?
�? �? ├── 连接iFinD批量接口                                     �?  �?
�? �? ├── 获取今日所有日频因子�?                                �?  �?
�? �? └── 本地存储到ClickHouse (可�?                           �?  �?
�? �?                                                             �?  �?
�? �? 盘中 (分钟因子):                                           �?  �?
�? �? ├── 实时调用iFinD接口                                     �?  �?
�? �? └── 存Redis缓存 (TTL=5分钟)                              �?  �?
�? �?                                                             �?  �?
�? �? 回测/研究�?                                                �?  �?
�? �? ├── 检查本地存储是否有该因�?                             �?  �?
�? �? ├── �?�?直接读取 (�?                                    �?  �?
�? �? └── �?�?调用iFinD计算 (准确)                            �?  �?
�? └─────────────────────────────────────────────────────────────�?  �?
�?                                                                    �?
└─────────────────────────────────────────────────────────────────────�?
```

#### 8.6.3 本地存储 vs iFinD计算对比

| 场景 | 本地存储 | iFinD实时计算 | 推荐 |
|------|----------|---------------|------|
| **实盘交易** | ⭐⭐�?(�? | ⭐⭐ (有延�? | 本地存储热门因子 |
| **回测研究** | ⭐⭐�?(�? | ⭐⭐�?(准确) | iFinD计算 |
| **冷门因子** | �?(占用空间) | ⭐⭐�?(按需) | iFinD计算 |

#### 8.6.4 5900因子使用建议

```python
# 策略: 常用因子本地存，冷门因子按需�?
FACTOR_STRATEGY = {
    # 高频使用的因�?�?本地预计算存�?
    'local_storage': [
        'THS_DP',       # 总市�?
        'THS_TURNING',  # 换手�?
        'THS_MA5',      # 5日均�?
        'THS_VOLUME',   # 成交�?
    ],

    # 中频因子 �?盘中实时获取
    'realtime_fetch': [
        'THS_RSI',      # RSI
        'THS_MACD',     # MACD
        'THS_BOLL',     # 布林�?
    ],

    # 冷门因子 �?回测时调�?
    'on_demand': [
        'THS_XXXX',     # iFinD分类中的其他因子
    ]
}
```

---

## 9. 实时数据 vs 历史数据处理流程

> **版本**: v1.0
> **更新日期**: 2026-03-30
> **专业机构标准**: 实时与历史数据分开处理，通过统一接口访问

### 9.1 核心区别

| 维度 | 实时数据 | 历史数据 |
|------|----------|----------|
| **用�?* | 实盘交易决策 | 回测/研究 |
| **处理模式** | 流式处理(push) | 批处�?pull) |
| **延迟要求** | <100ms | 无要�?|
| **数据顺序** | 必须有序 | 可重�?|
| **存储** | Redis/内存 | ClickHouse |
| **计算** | 增量计算 | 全量计算 |

### 9.2 专业机构数据处理架构

```
┌─────────────────────────────────────────────────────────────────────�?
�?                   专业机构数据处理架构                                 �?
├─────────────────────────────────────────────────────────────────────�?
�?                                                                    �?
�? ══════════════════════════════════════════════════════════════�?  �?
�? 实时数据�?(Real-time)                                           ══�?
�? ══════════════════════════════════════════════════════════════�?  �?
�?                                                                    �?
�? ┌─────────�?   ┌─────────�?   ┌─────────�?   ┌─────────�?       �?
�? �?数据�? │───▶│ 消息队列 │───▶│ 实时计算 │───▶│ 策略执行 �?       �?
�? �?iFinD  �?   �?Kafka   �?   �?因子/信号�?   �?订单生成�?       �?
�? �?QMT    �?   �?/Redis  �?   �?<100ms  �?   �?<500ms  �?       �?
�? └─────────�?   └─────────�?   └─────────�?   └─────────�?       �?
�?                                                                    �?
�? ══════════════════════════════════════════════════════════════�?  �?
�? 历史数据�?(Historical)                                           ══�?
�? ══════════════════════════════════════════════════════════════�?  �?
�?                                                                    �?
�? ┌─────────�?   ┌─────────�?   ┌─────────�?   ┌─────────�?       �?
�? �?数据�? │───▶│ 批量采集 │───▶│ 数据仓库 │───▶│ 回测引擎 �?       �?
�? �?iFinD  �?   �?�?�?  �?   │ClickHouse�?   �?全量计算�?       �?
�? �?AkShare�?   �?定时任务 �?   �? 历史数据 �?   �? 因子验证�?       �?
�? └─────────�?   └─────────�?   └─────────�?   └─────────�?       �?
�?                                                                    �?
└─────────────────────────────────────────────────────────────────────�?
```

### 9.3 实时数据处理流程

```
┌─────────────────────────────────────────────────────────────────────�?
�?                   实时数据处理流程 (实盘)                            �?
├─────────────────────────────────────────────────────────────────────�?
�?                                                                    �?
�? Step 1: 数据订阅 (0-10ms)                                         �?
�? ┌─────────────────────────────────────────────────────────────�?  �?
�? �?iFinD/QMT 实时行情 �?WebSocket/TCP �?本地缓存               �?  �?
�? �?                                                             �?  �?
�? �?数据类型:                                                     �?  �?
�? �?├── tick级逐笔成交                                          �?  �?
�? �?├── 盘口五档报价                                            �?  �?
�? �?└── 分钟K线合�?                                            �?  �?
�? └─────────────────────────────────────────────────────────────�?  �?
�?                             �?                                     �?
�? Step 2: 消息队列 (10-50ms)                                        �?
�? ┌─────────────────────────────────────────────────────────────�?  �?
�? �?Redis Pub/Sub �?Kafka �?异步分发到各计算节点               �?  �?
�? �?                                                             �?  �?
�? �?用�?                                                        �?  �?
�? �?├── 分发给多个策略实�?                                      �?  �?
�? �?└── 临时缓存(防止丢包)                                       �?  �?
�? └─────────────────────────────────────────────────────────────�?  �?
�?                             �?                                     �?
�? Step 3: 实时计算 (50-100ms)                                        �?
�? ┌─────────────────────────────────────────────────────────────�?  �?
�? �?计算节点:                                                     �?  �?
�? �?├── 实时因子计算 (技术指�?资金�?                          �?  �?
�? �?├── 信号生成 (买入/卖出/持有)                               �?  �?
�? �?└── 风控检�?(仓位/回撤/止损)                               �?  �?
�? └─────────────────────────────────────────────────────────────�?  �?
�?                             �?                                     �?
�? Step 4: 策略执行 (100-500ms)                                       �?
�? ┌─────────────────────────────────────────────────────────────�?  �?
�? �?订单生成 �?风控审核 �?券商API下单 �?成交回报                 �?  �?
�? └─────────────────────────────────────────────────────────────�?  �?
�?                                                                    �?
└─────────────────────────────────────────────────────────────────────�?
```

### 9.4 历史数据处理流程

```
┌─────────────────────────────────────────────────────────────────────�?
�?                   历史数据处理流程 (回测/研究)                       �?
├─────────────────────────────────────────────────────────────────────�?
�?                                                                    �?
�? Step 1: 数据采集 (定时任务)                                         �?
�? ┌─────────────────────────────────────────────────────────────�?  �?
�? �?定时任务 (盘后18:00-22:00):                                  �?  �?
�? �?├── iFinD日K线数据下�?                                     �?  �?
�? �?├── AkShare资金流数�?                                      �?  �?
�? �?├── 财务数据更新                                            �?  �?
�? �?└── 另类因子数据                                            �?  �?
�? └─────────────────────────────────────────────────────────────�?  �?
�?                             �?                                     �?
�? Step 2: 数据清洗 (ETL)                                             �?
�? ┌─────────────────────────────────────────────────────────────�?  �?
�? �?数据质量检�?                                               �?  �?
�? �?├── 缺失值处�?(前向填充/插�?                              �?  �?
�? �?├── 异常值检�?(3σ原则/IQR)                                 �?  �?
�? �?├── 停牌处理 (剔除/保留)                                    �?  �?
�? �?└── 复权处理 (前复�?后复�?                               �?  �?
�? └─────────────────────────────────────────────────────────────�?  �?
�?                             �?                                     �?
�? Step 3: 数据入库 (ClickHouse)                                      �?
�? ┌─────────────────────────────────────────────────────────────�?  �?
�? �?数据分层存储:                                               �?  �?
�? �?├── 热数�? Redis (�?0�?分钟K�?                         �?  �?
�? �?├── 温数�? ClickHouse (�?�?分钟K�?                    �?  �?
�? �?└── 冷数�? ClickHouse压缩 (1�?历史)                      �?  �?
�? └─────────────────────────────────────────────────────────────�?  �?
�?                             �?                                     �?
�? Step 4: 因子计算 (批处�?                                           �?
�? ┌─────────────────────────────────────────────────────────────�?  �?
�? �?因子计算:                                                   �?  �?
�? �?├── 日频因子: 全量计算 (日更)                              �?  �?
�? �?├── 分钟因子: 增量计算 (分钟�?                            �?  �?
�? �?└── 基本面因�? 财报后计�?(季更)                          �?  �?
�? └─────────────────────────────────────────────────────────────�?  �?
�?                             �?                                     �?
�? Step 5: 回测验证                                                   �?
�? ┌─────────────────────────────────────────────────────────────�?  �?
�? �?回测引擎:                                                   �?  �?
�? �?├── 短期回测: 1分钟数据 (�?�?                            �?  �?
�? �?├── 中期回测: 5分钟数据 (1-3�?                            �?  �?
�? �?└── 长期回测: 日K数据 (5-10�?                            �?  �?
�? └─────────────────────────────────────────────────────────────�?  �?
�?                                                                    �?
└─────────────────────────────────────────────────────────────────────�?
```

### 9.5 实时 vs 历史对比矩阵

| 环节 | 实时处理 | 历史处理 |
|------|----------|----------|
| **数据获取** | WebSocket推�?| 定时任务拉取 |
| **计算模式** | 增量/流式 | 全量/批处�?|
| **延迟要求** | <100ms | 分钟级可接受 |
| **计算范围** | 当前tick/分钟 | 全历史区�?|
| **存储介质** | Redis/内存 | ClickHouse |
| **用�?* | 实盘下单 | 回测研究 |
| **代码路径** | `src/modules/...` | `src/modules/backtest/...` |

### 9.6 统一数据访问接口

```python
class DataService:
    """统一数据访问接口 - 专业机构标准

    同一接口自动选择实时或历史数据源
    """

    def get_price(self, symbol: str, start: datetime, end: datetime,
                  freq: str = "1d") -> pd.DataFrame:
        """获取价格数据

        参数:
            symbol: 股票代码
            start: 开始时�?
            end: 结束时间
            freq: 频率 (tick/1m/5m/1d)

        返回:
            DataFrame
        """
        # 判断是实时请求还是历史请�?
        if self._is_realtime_request(end, freq):
            return self._get_realtime_data(symbol, start, end, freq)
        else:
            return self._get_historical_data(symbol, start, end, freq)

    def _is_realtime_request(self, end: datetime, freq: str) -> bool:
        """判断是否为实时请�?""
        now = datetime.now()
        # 交易时间�?+ 请求频率为分钟级 = 实时请求
        is_trading_hours = is_trading_time(now)
        is_minute_freq = freq in ["tick", "1m", "5m", "15m", "60m"]
        return is_trading_hours and is_minute_freq

    def _get_realtime_data(self, symbol, start, end, freq):
        """实时数据获取 (Redis)"""
        # 从Redis获取实时数据
        return self.redis_client.get(f"price:{symbol}:{freq}")

    def _get_historical_data(self, symbol, start, end, freq):
        """历史数据获取 (ClickHouse)"""
        # 从ClickHouse获取历史数据
        return self.clickhouse.query(f"""
            SELECT * FROM kline_{freq}
            WHERE symbol = '{symbol}'
            AND trade_time BETWEEN '{start}' AND '{end}'
        """)

    def get_factor(self, symbol: str, factor_name: str,
                   freq: str = "1d") -> pd.DataFrame:
        """获取因子数据

        实时因子: 增量计算
        历史因子: 批处理计�?
        """
        if self._is_realtime_factor(factor_name):
            return self._calculate_realtime_factor(symbol, factor_name)
        else:
            return self._get_historical_factor(symbol, factor_name)
```

### 9.7 你的系统实现建议

| 模块 | 实时处理 | 历史处理 |
|------|----------|----------|
| **数据�?* | iFinD实时行情 | iFinD历史 + AkShare |
| **传输** | WebSocket/回调 | 定时任务 |
| **缓存** | Redis | ClickHouse |
| **计算** | 增量因子 | 全量因子 |
| **存储** | 热数�?60�? | �?冷数�?1�?) |
| **代码路径** | `ZephyrAlpha/src/modules/` | `ZephyrAlpha/src/modules/factors/` |

---

## 10. 数据源配�?

```yaml
alternative_data_sources:
  news:
    - name: "东方财富"
      url: "https://www.eastmoney.com"
      api: "akshare"
      update_frequency: "30min"

    - name: "新浪财经"
      url: "https://finance.sina.com.cn"
      api: "akshare"
      update_frequency: "30min"

  sentiment:
    - name: "baidu-senta"
      type: "sentiment_analysis"
      accuracy: "95%"

    - name: "snowNLP"
      type: "sentiment_analysis"
      accuracy: "85%"

  search:
    - name: "百度指数"
      api: "akshare"
      update_frequency: "daily"
```

---

**版本**: 2.0 | **更新**: 2026-03-29

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
