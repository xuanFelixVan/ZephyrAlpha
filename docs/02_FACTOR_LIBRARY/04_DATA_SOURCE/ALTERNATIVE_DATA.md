# 另类数据 - 新闻舆情

> NLP处理、情感分析、事件研究
>
> **版本**: v2.1
> **更新日期**: 2026-03-30
> **方案**: 混合方案 (AkShare + iFind + Tushare + 模力方舟LLM)

---

## 1. 新闻数据获取方案

### 1.1 分层获取架构

| 层级 | 数据源 | 用途 | 稳定性 | 成本 | 频率限制 |
|------|--------|------|--------|------|---------|
| **Layer 1** | AkShare (免费) | 主力新闻源 | ⭐⭐⭐ | 免费 | <30次/分 |
| **Layer 2** | Tushare Pro | 付费补充 | ⭐⭐⭐⭐⭐ | 积分制 | 500次/分 |
| **Layer 3** | iFind API | 备用 | ⭐⭐⭐⭐ | 订阅 | 视订阅级别 |
| **Layer 4** | 政府网站RSS | 政策面 | ⭐⭐⭐⭐⭐ | 免费 | 无限制 |

### 1.2 推荐配置

```python
# 新闻数据源配置
NEWS_SOURCES = {
    'primary': 'akshare',           # AkShare主力
    'backup': 'ifind',             # iFind备用
    'paid': 'tushare_pro',        # Tushare付费版
    'policy': 'gov_rss'           # 政府RSS
}

# AkShare安全频率配置
AKSHARE_CONFIG = {
    'news_delay': 2,        # 新闻接口间隔2秒
    'max_per_minute': 30,   # 每分钟不超过30次
    'retry_times': 3,       # 重试次数
    'retry_delay': 5         # 重试间隔5秒
}
```

### 1.3 各平台限制说明

| 平台 | 频率限制 | 稳定性 | 风险 |
|------|---------|--------|------|
| AkShare | <30次/分 | ⭐⭐⭐ | 可能被封IP |
| Tushare Pro | 500次/分 | ⭐⭐⭐⭐⭐ | 付费但稳定 |
| iFind | 视订阅级别 | ⭐⭐⭐⭐ | 需权限 |
| 政府RSS | 无限制 | ⭐⭐⭐⭐⭐ | 合规安全 |

### 1.4 政府网站RSS源（零风险）

```python
# 政府公开RSS订阅源
GOV_RSS_SOURCES = {
    'people_daily': 'http://www.people.com.cn/rss/',           # 人民网
    'chinanews': 'http://www.chinanews.com/rss/',             # 中国新闻网
    'stats_gov': 'https://www.stats.gov.cn/sj/zxfb/rss.xml', # 国家统计局
}

# 使用示例
import feedparser

def fetch_gov_news():
    """获取政府网站新闻（零风险）"""
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
    """安全获取新闻（带限频）"""
    time.sleep(delay)  # 控制请求频率
    try:
        df = ak.stock_news_em(symbol=symbol)
        return df
    except Exception as e:
        print(f"获取失败: {e}")
        time.sleep(5)  # 失败后等待
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

### 2.2 模型选择 (已测试 - 2026-03-30)

| 任务 | 推荐模型 | 部署方式 | 上下文 | 状态 |
|------|----------|----------|--------|------|
| 情感分析 | **GLM-4.7-Flash** | API (模力方舟) | 200K | ✅ 已测试 |
| 深度思考 | **Qwen3-4B** | API (模力方舟) | 32K | ✅ 已测试 |
| 推理分析 | **DeepSeek-R1-Distill-Qwen-14B** | API (模力方舟) | 32K | ✅ 已测试 |
| 数学证明 | **DeepSeek-Prover-V2-7B** | API (模力方舟) | - | ✅ 已测试 |
| 事件分类 | **Qwen3-4B** | API (模力方舟) | 32K | ✅ 可用 |
| 实体识别 | **GLM-4.7-Flash** | API (模力方舟) | 200K | ✅ 可用 |

### 2.3 API模型配置

```python
# 模力方舟 API 配置 (免费)
MOAI_CONFIG = {
    'api_base': 'https://ai.gitee.com/api/v1/chat/completions',
    'api_key': 'XA8UNQKJTRBEXHXJICM7KBOJHP6NRVN6UINHIZF8',  # 已测试可用
    'models': {
        'glm_4_flash': {
            'name': 'GLM-4.7-Flash',
            'context': 200000,
            'use_case': '情感分析、实体识别、大量文本处理'
        },
        'qwen3_4b': {
            'name': 'Qwen3-4B',
            'context': 32000,
            'use_case': '深度思考、事件分类'
        },
        'deepseek_r1': {
            'name': 'DeepSeek-R1-Distill-Qwen-14B',
            'context': 32000,
            'use_case': '推理分析、复杂问题'
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
    {"role": "user", "content": "分析这条新闻的情感: 茅台Q4净利润增长15%"}
])

# 深度思考
result = chat_with_moai("Qwen3-4B", [
    {"role": "user", "content": "分析当前市场状态"}
])
```

---

## 3. 另类数据类型

| 类型 | 数据内容 | 更新频率 | 处理方式 |
|------|---------|---------|---------|
| 新闻数据 | 财经新闻、公告、研报 | 实时 | NLP + 情感分析 |
| 舆情数据 | 雪球、股吧、微博讨论 | 15分钟 | 情感分析 + 风险识别 |
| 搜索数据 | 百度搜索指数、Google Trends | 日频 | 搜索热度 |
| 社交媒体 | 财经大V、机构评论 | 实时 | 实体识别 + 关系抽取 |

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
    """新闻处理器"""

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

        返回：
            -1（极度负面）到 1（极度正面）
        """
        # 使用情感分析模型
        score = self.sentiment_model.predict(text)
        return score

    def extract_entities(self, text: str) -> List[str]:
        """提取命名实体（股票代码、公司名称）"""
        entities = self.ner_model.extract(text)

        # 提取股票代码
        stock_codes = re.findall(r'\d{6}', text)

        # 提取公司简称
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
        'pattern': r'(\d+)派(\d+)|(\d+)送(\d+)',
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
    '监管函': {
        'keywords': ['监管函', '问询函', '警示函', '处罚'],
        'pattern': r'(监管|问询|警示).*函',
        'sentiment_impact': 'negative'
    },
    '减持': {
        'keywords': ['减持', '卖出', '转让'],
        'pattern': r'(股东|高管|实际控制人).*(减持|卖出)',
        'sentiment_impact': 'negative'
    }
}

class EventClassifier:
    """事件分类器"""

    def classify_event(self, news: NewsItem) -> str:
        """识别事件类型"""
        text = news.title + ' ' + news.content

        for event_type, config in EVENT_PATTERNS.items():
            if re.search(config['pattern'], text):
                return event_type

        return 'general'  # 默认普通新闻
```

---

## 4. 舆情风险识别

```python
class RiskSentimentDetector:
    """舆情风险检测"""

    def __init__(self):
        self.risk_keywords = {
            '黑天鹅': ['造假', '欺诈', '违规', '调查', '处罚'],
            '经营风险': ['亏损', '债务', '违约', '诉讼'],
            '市场风险': ['暴跌', '闪崩', '踩踏', '清仓']
        }

    def detect_risk(self, news_items: List[NewsItem]) -> Dict[str, float]:
        """检测舆情风险

        返回：
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

        # 归一化
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

        参数：
            symbol: 股票代码
            event_date: 事件日期
            window: 事件窗口 (-5, 5) 表示事件前5天到后5天
            market_symbol: 市场基准

        返回：
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

        参数：
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

        # 按事件类型汇总
        summary = df.groupby('event_type').agg({
            'car': ['mean', 'std', 'count'],
            't_stat': 'mean'
        }).round(4)

        # 过滤样本数过少的类型
        summary = summary[summary[('car', 'count')] >= min_samples]

        return summary

    def _t_test(self, series: pd.Series) -> float:
        """简单t检验"""
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

        计算过去N天新闻情感加权平均
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

        计算各类事件的累计情感得分
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

        综合负面新闻数量和强度
        """
        news = self.get_news(symbol, days=5)

        risk_score = 0.0
        for n in news:
            if n.sentiment is not None and n.sentiment < -0.3:
                risk_score += abs(n.sentiment)

        return min(risk_score, 1.0)  # 归一化到0-1
```

---

## 6.5 舆情数据表结构设计 (v2.0) - 2026-03-29 确定

> 基于专业机构实践 + 个人投资者"1人+AI"模式

### 6.5.1 ClickHouse 舆情事实表

```sql
-- ============================================================
-- 新闻事实表 (宽表设计，适合ClickHouse列式存储)
-- 版本: v2.0 确定
-- ============================================================
CREATE TABLE quant_system.news_sentiment (
    -- 主键和维度
    news_id           String,           -- 新闻唯一ID
    stock_code        String,           -- 关联股票代码 (如: 000001.SZ)
    trade_date        Date,             -- 交易日期

    -- 新闻原始信息
    headline          String,           -- 新闻标题
    summary           String,           -- AI生成摘要 (永久保留)
    content           String,           -- 原文 (近2年,之后删除)
    source            String,           -- 来源 (东方财富/新浪等)
    source_type       Enum8('official'=1, 'media'=2, 'social'=3, 'research'=4),
    url               String,           -- 原文链接
    publish_time      DateTime,         -- 发布时间
    crawl_time        DateTime,         -- 采集时间

    -- 情感多维度分析 (v2.0新增)
    sentiment_score   Float32,          -- 情感得分 (-1 ~ +1)
    valence           Float32,          -- 效价: 愉快程度 (-1 ~ +1)
    arousal           Float32,          -- 唤醒度: 激动程度 (0 ~ 1)
    dominance         Float32,          -- 支配度: 控制程度 (0 ~ 1)
    sentiment_confidence Float32,       -- 置信度 (0 ~ 1)

    -- 事件分类 (混合模式: 预定义+AI扩展)
    event_type        String,           -- 预定义核心类型
    event_type_ext    String,           -- AI扩展动态类型
    event_level       Enum8('normal'=0, 'warning'=1, 'important'=2, 'major'=3),
    event_keywords    Array(String),    -- 事件关键词

    -- 实体识别
    entities          Array(String),    -- 识别的实体 (股票/公司/人)
    mentioned_stocks  Array(String),    -- 提及的股票列表
    mentioned_amount  Float32,          -- 提及金额 (如: 10亿)

    -- ESG标签 (v2.0新增)
    esg_category      Enum8('E'=1, 'S'=2, 'G'=3, 'none'=0),
    esg_score         Float32,         -- ESG相关度 (0 ~ 1)

    -- 质量控制
    tags              Array(String),    -- 标签: ['新能源', '政策', '龙头']
    is_reliable       UInt8,           -- 是否可靠 (1=可靠)
    relevance_score   Float32,         -- 与关联股票相关性 (0 ~ 1)
    novelty_score     Float32,         -- 新闻新颖度 (0=旧闻, 1=独家)

    -- 审计字段
    processed_time    DateTime,        -- 处理完成时间
    model_version     String           -- 使用的模型版本

) ENGINE = MergeTree()
PARTITION BY toYYYYMM(trade_date)
ORDER BY (trade_date, stock_code, news_id)
TTL publish_time + INTERVAL 2 YEAR;  -- 2年后删除原文，只保留summary
```

### 6.5.2 新闻-股票关联表

```sql
-- 新闻-股票关联表 (多对多关系)
CREATE TABLE quant_system.news_stock_relation (
    news_id           String,
    stock_code        String,
    relation_type     Enum8('mentioned'=1, 'related'=2, 'impacted'=3),
    mention_count     UInt16,          -- 提及次数
    mention_position  String,          -- 首次提及位置 (title/content/both)
    sentiment_toward_stock Float32,    -- 对该股票的情感

    PRIMARY KEY (news_id, stock_code)
) ENGINE = MergeTree();
```

### 6.5.3 预定义事件类型表

```sql
-- 事件类型维度表 (预定义核心类型)
CREATE TABLE quant_system.dim_event_type (
    event_type     String,
    event_name     String,
    event_level    Enum8('normal'=0, 'warning'=1, 'important'=2, 'major'=3),
    market_reaction String,            -- 历史平均市场反应
    avg_sentiment  Float32,            -- 该类型事件平均情感

    PRIMARY KEY event_type
) ENGINE = MergeTree();

-- 预定义事件类型 (v2.0)
INSERT INTO dim_event_type VALUES
('earnings_pre',      '业绩预增',      'important', 'positive',  0.4),
('earnings_warn',     '业绩预警',      'important', 'negative', -0.5),
('earnings_miss',     '业绩不及预期',  'important', 'negative', -0.4),
('merger_acqui',      '并购重组',      'major',     'positive',  0.3),
('blockchain',        '区块链',        'major',     'positive',  0.2),
('regulation',        '监管函',         'warning',   'negative', -0.4),
('policy_benefit',    '政策利好',       'important', 'positive',  0.5),
('product_launch',    '新产品发布',     'normal',    'positive',  0.2),
('management_change', '高管变动',       'important', 'neutral',   0.0),
('share_reduce',      '股东减持',       'warning',   'negative', -0.3),
('share_increase',    '股东增持',       'important', 'positive',  0.3),
('split_report',     '分红送转',        'normal',    'positive',  0.2),
('new_listing',      '新股上市',        'normal',    'positive',  0.3),
('delisting_risk',   '退市风险',        'major',     'negative', -0.6),
('black_swan',       '黑天鹅事件',       'major',     'negative', -0.7),
('industry_upgrade',  '行业升级',        'important', 'positive',  0.3),
('macroeconomy',     '宏观经济',         'important', 'neutral',   0.0);
```

### 6.5.4 情感多维度专业指标说明

| 指标 | 范围 | 专业机构用途 | 示例 |
|------|------|-------------|------|
| **sentiment_score** | -1 ~ +1 | 基础情感因子 | 简单直接 |
| **valence** | -1 ~ +1 | 效价(愉快程度) | "央行降准" valence=+0.7 |
| **arousal** | 0 ~ 1 | 唤醒度(激动程度) | 突发新闻 arousal=0.9 |
| **dominance** | 0 ~ 1 | 支配度(控制程度) | 官方发布 dominance=0.9 |
| **sentiment_confidence** | 0 ~ 1 | 模型置信度 | 过滤低质量分析 |

### 6.5.5 存储策略

| 数据类型 | 保留期限 | 存储策略 |
|---------|---------|---------|
| headline, summary | **永久** | 核心数据资产 |
| content (原文) | **2年** | TTL自动删除，节省80%空间 |
| 情感得分/实体/事件 | **永久** | 结构化高效存储 |
| ESG标签 | **永久** | 随新闻保留 |

### 6.5.6 数据量估算

| 表 | 日增量 | 年增量 | 压缩后 |
|---|--------|--------|--------|
| news_sentiment | ~5万条 | ~1500万条 | ~10GB/年 |
| news_stock_relation | ~15万条 | ~4500万条 | ~5GB/年 |
| dim_event_type | 静态 | ~20条 | 可忽略 |

---

## 6. 新闻数据获取方案 (v2.0) - 2026-03-29 确定

> 采用"混合双打"模式，充分利用免费资源

### 6.0.1 新闻数据源汇总

| 数据源 | 免费额度 | 专业度 | A股支持 | 个股代码 | API状态 |
|--------|---------|--------|---------|---------|---------|
| **Alpha Vantage** | 25次/天 | ⭐⭐⭐⭐⭐ | ✅ | ❌ 不支持 | ✅ 已测试 |
| **Finnhub** | 60次/分钟 | ⭐⭐⭐⭐ | ✅ | ❌ 不支持 | ✅ 已测试 |
| **Marketaux** | 100次/天 | ⭐⭐⭐⭐ | ✅ | ❌ 不支持 | ✅ 已测试 |
| **AkShare** | 无限制 | ⭐⭐⭐ | ✅ | ✅ 支持 | ⚠️ 不稳定 |
| **iFinD** | 需账号 | ⭐⭐⭐⭐⭐ | ✅ | ✅ 支持 | ⚠️ 无权限 |
| **Tushare** | 付费 | ⭐⭐⭐⭐ | ✅ | ✅ 支持 | 待购买 |

**详细测试结果见 6.0.9 节**

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
**限制**: ⚠️ 仅支持美股，A股格式(600519.SH)返回Invalid ticker format
**适用**: 美股新闻情感分析、与A股关联度低

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

**优势**: 每分钟60次请求，实时性强，覆盖全球新闻
**限制**: ⚠️ 主要覆盖美股，A股公司新闻数据有限
**适用**: 美股实时监控

### 6.0.4 Marketaux (⭐推荐 - 全球市场+情感分析)

```python
import requests

api_token = '1IDURCqFtIglEtB0f9ZPKEMfl9YF7onH7BQUyIrt'
url = 'https://api.marketaux.com/v1/news/all'

# 1. 获取全球金融新闻
params = {
    'api_token': api_token,
    'limit': 50
}

# 2. 按国家过滤 (中国)
params = {
    'api_token': api_token,
    'countries': 'cn',  # 中国
    'limit': 50
}

# 3. 按情感筛选
params = {
    'api_token': api_token,
    'sentiment_gte': 0.5,  # 高情感得分
    'limit': 50
}

# 4. 关键词搜索
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
- ✅ 支持全球80+市场，包括中国 ✅
- ✅ 自带情感分析 (sentiment_score: -1 ~ +1)
- ✅ 100次/天免费额度
- ✅ 可按国家/交易所/情感筛选

**测试结果**:
```
✅ countries=cn: 返回3条中国相关新闻
✅ exchanges=SSE: 支持上海证券交易所
✅ sentiment_gte=0.5: 可筛选高情感新闻
✅ 关键词"China stock market": 有结果
```

**适用**: A股+港股新闻情感分析

### 6.0.6 A股新闻来源 (国内平台)

```python
import akshare as ak

# 央视新闻 (较稳定)
df = ak.news_cctv()

# 个股新闻 (东方财富)
df = ak.stock_news_em(symbol="000001")

# 市场主要新闻
df = ak.stock_news_main_cx()
```

**优势**: A股新闻全覆盖，来源包括东方财富/新浪/同花顺等
**限制**: 接口不稳定，可能失效
**适用**: A股舆情分析

### 6.0.7 混合使用策略

```python
# A股新闻 (主力)
# - Marketaux: 全球市场+情感分析 (100次/天) ⭐推荐
# - AkShare: 东方财富、同花顺等 (免费)
# - iFinD: 同花顺官方 (需开通权限)
# - Tushare: 财联社等 (付费)

# 美股新闻 + 情感分析 (辅助)
# - Alpha Vantage: 自带情感评分 (25次/天)
# - Finnhub: 实时新闻 (60次/分钟)

def get_china_news_with_sentiment():
    """获取A股新闻+情感 - 使用Marketaux"""
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
1. **A股舆情**: Marketaux (主力) + AkShare (备用)
2. **美股情感**: Alpha Vantage (自带情感分析)
3. **实时监控**: Finnhub (高频)

### 6.0.8 全球市场覆盖对比

| 市场 | Alpha Vantage | Finnhub | Marketaux | AkShare | iFinD |
|------|--------------|---------|-----------|---------|-------|
| A股个股 | ❌ | ❌ | ❌ | ✅ | ✅ |
| A股宏观 | ❌ | ❌ | ✅ | ✅ | ✅ |
| 港股 | ❌ | ⚠️ | ✅ | ✅ | ✅ |
| 美股 | ✅ | ✅ | ✅ | ❌ | ❌ |

**结论**:
- A股个股新闻: AkShare/iFinD/Tushare
- A股宏观+情感: Marketaux
- 美股+情感: Alpha Vantage
- 实时监控: Finnhub

---

### 6.0.9 新闻API详细测试结果 (2026-03-30)

#### 测试平台汇总

| 平台 | 测试接口数 | 成功数 | 可用量 |
|------|-----------|--------|--------|
| AkShare | 7 | 2 | news_cctv, futures_news_shmet |
| iFinD | 4 | 1 | 登录成功 |
| Alpha Vantage | 1 | 1 | NEWS_SENTIMENT |
| Finnhub | 1 | 1 | news |
| Marketaux | 1 | 1 | news/all |

#### AkShare测试结果 (2026-03-30)

| 接口 | 状态 | 数据量 | 说明 |
|------|------|--------|------|
| stock_news_em | ❌ 失败 | 0 | 东方财富API返回解析错误 |
| news_cctv | ✅ 成功 | 12 | 央视新闻正常 |
| futures_news_shmet | ✅ 成功 | 10 | 期货新闻正常 |
| news_economic_baidu | ⚠️ 成功 | 0 | 空数据 |
| news_trade_notify_suspend_baidu | ⚠️ 成功 | 0 | 空数据 |
| news_trade_notify_dividend_baidu | ⚠️ 成功 | 0 | 空数据 |
| news_report_time_baidu | ⚠️ 成功 | 0 | 空数据 |

**结论**: AkShare部分接口不稳定，但央视新闻和期货新闻可用。

#### iFinD测试结果

| 接口 | 状态 | errorcode | 说明 |
|------|------|-----------|------|
| 登录 | ✅ 成功 | 0 | 账号登录正常 |
| THS_iwencai | ❌ 无数据 | -4001 | 新闻无权限 |
| THS_ReportQuery | ❌ 参数错误 | -4210 | 参数格式错误 |
| THS_BD | ❌ 参数错误 | -209 | 指标参数无效 |

**结论**: iFinD新闻接口需要开通权限，当前账号无可用新闻数据。

#### Alpha Vantage测试结果

| 接口 | 状态 | 说明 |
|------|------|------|
| NEWS_SENTIMENT | ✅ 成功 | 美股自带情感分析 |

#### Finnhub测试结果

| 接口 | 状态 | 说明 |
|------|------|------|
| news | ✅ 成功 | 美股实时新闻 |

#### Marketaux测试结果

| 测试项 | 状态 | 说明 |
|--------|------|------|
| 全球新闻 | ✅ 成功 | 3条 |
| countries=cn | ✅ 成功 | 中国相关新闻 |
| exchanges=SSE | ⚠️ 有数据 | 但非A股公司 |
| A股代码查询 | ❌ 无数据 | 600519等返回空 |

**结论**: Marketaux不支持按A股代码查询，只能获取宏观中国新闻。

---

## 7. 舆情系统验证方案

### 6.1 验证挑战

```
舆情分析 vs 价格走势：鸡生蛋问题
┌─────────────────────────────────────────────────────────────┐
│                                                             │
│  我们想用舆情预测股价                                        │
│           ↓                                                 │
│  但股价本身反映舆情                                         │
│           ↓                                                 │
│  如何知道AI情感分析是否正确？                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 6.2 验证方案

| 方案 | 说明 | 实施难度 |
|------|------|----------|
| **事后验证法** | 对比历史新闻情感与次日股价涨跌 | ⭐ 简单 |
| **标注数据集** | 人工标注100条新闻，对比AI准确率 | ⭐ 中等 |
| **因子IC验证** | 计算舆情因子与收益相关性 | ⭐⭐⭐ 科学 |

### 6.3 IC验证 (最科学)

```
IC (Information Coefficient) = corr(舆情分数, 次日收益)

判断标准:
├── |IC| > 0.03  → 因子有效
├── |IC| > 0.05  → 因子较强
└── |IC| < 0.02  → 因子无效，需优化
```

### 6.4 反馈闭环

```
AI分析 ──→ 回测验证 ──→ IC结果 ──→ 优化模型 ──→ 持续监控
              │
              └──→ 定期输出验证报告
```

---

## 7. 数据存储方案

### 7.1 实际数据量估算

```
┌─────────────────────────────────────────────────────────────┐
│                   数据量详细估算                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  1. 分钟K线数据 (重点!)                                    │
│     5000只 × 240分钟/天 × 250天 × 10年                    │
│     = 30亿条记录  ≈ 50-100 GB                             │
│                                                             │
│  2. 因子数据                                              │
│     5700因子 × 5000只 × 2500天 ≈ 10-50 GB                │
│                                                             │
│  3. 舆情/新闻数据                                         │
│     ~1亿条新闻 × 2KB ≈ 200 GB                             │
│                                                             │
│  ════════════════════════════════════════════════════       │
│  总计: 100-400 GB ⚠️                                      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.2 存储选型对比

| 方案 | 处理能力 | 优点 | 缺点 |
|------|----------|------|------|
| PostgreSQL | < 50GB | 简单 | 分区复杂 |
| TimescaleDB | < 100GB | 自动分区 | 勉强 |
| **ClickHouse** | **100GB+** | 列式存储、压缩强 | 需单独部署 |
| **分层存储** | **TB级** | 冷热分离 | 需管理 |

### 7.3 最终存储方案 (v2.0) - 2026-03-29 确定

> **基于专业量化机构实践 + 个人投资者硬件配置 (RTX 3090 + 64GB RAM + 1.2TB SSD)**

```
┌─────────────────────────────────────────────────────────────┐
│          Layer 1: 热数据 (Redis - SSD)                      │
├─────────────────────────────────────────────────────────────┤
│  存储介质: Redis (高性能内存数据库)                         │
│                                                             │
│  数据范围:                                                  │
│  ├── 1分钟K线: 最近60交易日 (~30GB)                       │
│  ├── 实时因子: 当日计算结果                                │
│  └── 最新行情: tick级盘口                                  │
│                                                             │
│  用途: 实盘交易、当日策略执行                               │
│  保留策略: 60个交易日后1分钟数据降采样为5分钟            │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│          Layer 2: 温数据 (ClickHouse)                     │
├─────────────────────────────────────────────────────────────┤
│  存储介质: ClickHouse (列式存储)                           │
│                                                             │
│  数据范围:                                                  │
│  ├── 5/15/30/60分钟K线: 近1年 (~20GB)                  │
│  ├── 日K线: 近5年 (~10GB)                                │
│  ├── 财务数据: 近5年 (~5GB)                              │
│  └── 舆情结构化数据: 近2年 (~10GB)                       │
│                                                             │
│  用途: 中期回测、策略验证、因子计算                        │
└─────────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────┐
│          Layer 3: 冷数据 (ClickHouse压缩)                  │
├─────────────────────────────────────────────────────────────┤
│  存储介质: ClickHouse (高压缩率)                          │
│                                                             │
│  数据范围:                                                  │
│  ├── 日K线: 10年+历史 (~30GB)                            │
│  ├── 降采样5分钟: 3年前数据 (~15GB)                     │
│  └── 舆情归档: 2年前历史 (~20GB)                         │
│                                                             │
│  用途: 长期回测、全市场扫描、历史验证                      │
└─────────────────────────────────────────────────────────────┘

总计压缩后存储: ~110GB
```

### 7.4 存储选型对比

| 方案 | 处理能力 | 优点 | 缺点 |
|------|----------|------|------|
| PostgreSQL | < 50GB | 简单 | 分区复杂 |
| TimescaleDB | < 100GB | 自动分区 | 勉强 |
| **ClickHouse** | **100GB+** | 列式存储、压缩强 | 需单独部署 |
| **分层存储** | **TB级** | 冷热分离 | 需管理 |

### 7.5 ClickHouse + Redis 配置

```python
# ClickHouse 配置
CLICKHOUSE_CONFIG = {
    'host': 'localhost',
    'database': 'quant_system',
    'port': 9000,
    'tables': {
        # K线数据 (按频率分层)
        'kline_1min': '1分钟K线 (热数据, 60交易日)',
        'kline_5min': '5分钟K线 (温数据, 近1年)',
        'kline_15min': '15分钟K线 (温数据, 近1年)',
        'kline_30min': '30分钟K线 (温数据, 近1年)',
        'kline_60min': '60分钟K线 (温数据, 近1年)',
        'kline_daily': '日K线 (温数据5年/冷数据10年+)',
        # 财务数据
        'financial_data': '财务报表数据',
        # 舆情数据
        'news_sentiment': '舆情结构化数据 (情感/实体/事件)',
        # 因子数据
        'factors_alpha': 'Alpha因子'
    }
}

# Redis 热数据缓存
REDIS_CONFIG = {
    'host': 'localhost',
    'port': 6379,
    'ttl': 86400,  # 1天
    'hot_data': [
        'recent_60day_1min_kline',  # 最近60交易日1分钟K线
        'realtime_factors',          # 当日实时因子
        'latest_quotes'             # 最新行情
    ]
}
```

### 7.6 分层存储架构图

```
┌─────────────────────────────────────────────────────────────┐
│                   分层存储架构                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌─────────────────────────────────────────────────────┐ │
│  │          Layer 1: 热数据 (Redis/SSD)               │ │
│  │                                                     │ │
│  │  最近60交易日:                                      │ │
│  │  ├── 1分钟K线 (原始最细粒度)                      │ │
│  │  ├── 实时因子                                       │ │
│  │  └── Tick数据 (可选)                               │ │
│  │                                                     │ │
│  │  大小: ~30 GB                                       │ │
│  │  用途: 实盘交易、当日策略                          │ │
│  │  淘汰策略: 60日后降采样为5分钟                    │ │
│  └─────────────────────────────────────────────────────┘ │
│                           ↓                                 │
│  ┌─────────────────────────────────────────────────────┐ │
│  │          Layer 2: 温数据 (ClickHouse)              │ │
│  │                                                     │ │
│  │  近1-5年:                                           │ │
│  │  ├── 5/15/30/60分钟K线                            │ │
│  │  ├── 日K线 (近5年)                                 │ │
│  │  ├── 财务数据                                       │ │
│  │  └── 舆情结构化 (近2年)                            │ │
│  │                                                     │ │
│  │  大小: ~45 GB                                       │ │
│  │  用途: 中期回测、策略验证                          │ │
│  └─────────────────────────────────────────────────────┘ │
│                           ↓                                 │
│  ┌─────────────────────────────────────────────────────┐ │
│  │          Layer 3: 冷数据 (ClickHouse压缩)          │ │
│  │                                                     │ │
│  │  5-10年+:                                          │ │
│  │  ├── 日K线 (10年+)                                 │ │
│  │  ├── 降采样5分钟 (归档)                            │ │
│  │  └── 舆情历史归档                                  │ │
│  │                                                     │ │
│  │  大小: ~65 GB                                       │ │
│  │  用途: 长期回测、全市场扫描                        │ │
│  └─────────────────────────────────────────────────────┘ │
│                                                             │
│  ═══════════════════════════════════════════════════════   │
│  总计压缩存储: ~110 GB ✓ 适合1.2TB SSD                   │
│  ═══════════════════════════════════════════════════════   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.7 专业机构存储策略参考

> 参考: 量化数据中台最佳实践

| 数据类型 | 保留策略 | 压缩比 | 说明 |
|---------|---------|--------|------|
| 1分钟K线 | **保留60交易日**，之后降采样 | ~70%空间节省 | 覆盖策略参数优化需求 |
| 5/15/30/60分钟 | **全部保留** 1年 | 列式压缩 ~40% | 机构研究证明5分钟足够99%策略 |
| 日K线 | **永久保留** | 列式压缩 ~60% | 核心历史数据 |
| 财务数据 | **永久保留** | 列式压缩 ~50% | 估值因子必需 |
| 舆情结构化 | **永久保留结构化**，文本可删 | ~80%空间节省 | 情感得分/实体/事件 |
| 舆情向量 | **可选**，如需语义检索加ChromaDB | - | 后续扩展 |

### 7.8 短期 vs 长期回测方案

```
┌─────────────────────────────────────────────────────────────┐
│                   分层回测架构                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ═══════════════════════════════════════════════════════   │
│  短期回测 (近1年) - 高精度                                 │
│  ═══════════════════════════════════════════════════════   │
│  数据: Redis 热数据                                       │
│  精度: 分钟级                                              │
│  用途: 策略开发、参数优化                                  │
│                                                             │
│  ═══════════════════════════════════════════════════════   │
│  中期回测 (1-5年) - 标准精度                              │
│  ═══════════════════════════════════════════════════════   │
│  数据: ClickHouse 温数据                                  │
│  精度: 日线级                                              │
│  用途: 策略验证、稳健性检验                               │
│                                                             │
│  ═══════════════════════════════════════════════════════   │
│  长期回测 (5-10年) - 抽样精度                             │
│  ═══════════════════════════════════════════════════════   │
│  数据: ClickHouse 冷数据                                  │
│  精度: 日线级                                              │
│  用途: 全市场扫描、长期趋势验证                           │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 7.6 回测工作流

```
1. 新策略开发
   └── 短期回测 (近1年，分钟级) → 快速验证

2. 策略优化
   └── 中期回测 (3-5年，日线级) → 参数调优

3. 策略验证
   └── 长期回测 (全量历史) → 稳健性检验

4. 实盘部署
   └── 实时数据 → 盘中监控
```

### 7.10 ClickHouse 性能保证

```
查询速度:
├── 100GB数据查询: < 3秒
├── 全A股10年日K: < 1秒
├── 单只股票5年分钟K: < 0.5秒
└── 并行查询: 自动利用多核

压缩能力:
├── 列式存储，压缩比 10:1 ~ 20:1
├── 100GB原始数据 → 5-10GB存储
└── 磁盘占用小，查询更快
```

---

## 8. 另类因子体系（免费数据源）

> **版本**: v1.0
> **更新日期**: 2026-03-30
> **数据源分工**: iFinD（主，5900因子）+ 另类因子（免费API补充）

### 8.1 因子分类体系

| 类别 | 数据源 | 更新频率 | 说明 |
|------|--------|----------|------|
| **iFinD因子** | iFinD | 分钟/日 | 5900+量化因子（付费订阅） |
| **另类因子** | 免费API | 日频 | 天气/搜索/资金流等 |
| **舆情因子** | AkShare等 | 实时 | 新闻情感/事件驱动 |

### 8.2 免费另类因子获取渠道

#### 8.2.1 资金流因子（⭐推荐 - 免费且稳定）

| 因子 | 获取方式 | 免费额度 | 实现难度 |
|------|----------|----------|----------|
| 北向资金 | 东方财富 | 无限制 | ⭐ |
| 融资融券 | 东方财富 | 无限制 | ⭐ |
| 龙虎榜 | 上交所/深交所 | 无限制 | ⭐ |
| 大宗交易 | 东方财富 | 无限制 | ⭐ |

```python
import akshare as ak

# 北向资金（沪深港通）
df = ak.stock_board_em()  # 概念板块资金流
df = ak.stock_individual_em()  # 个股资金流

# 融资融券
df = ak.stock_margin_detail_sz()  # 深圳融资融券
df = ak.stock_margin_detail_sh()  # 上海融资融券

# 龙虎榜
df = ak.stock_lhb_detail_em()  # 龙虎榜明细
```

#### 8.2.2 天气/气候因子（⭐推荐 - 免费API）

| 因子 | 免费API | 日额度 | 适用场景 |
|------|---------|--------|----------|
| 温度/天气 | 心知天气 | 400次/天 | 消费/农业股票 |
| 空气质量AQI | PM25.in | 1000次/天 | 环保/医药 |
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

# PM25.in（免费，无需注册）
def get_aqi(city="beijing"):
    """获取AQI数据"""
    url = f"https://api.waqi.info/feed/{city}/"
    params = {"token": "your_token"}  # 免费注册获取
    response = requests.get(url, params=params)
    return response.json()
```

#### 8.2.3 搜索指数因子（⭐推荐 - 百度/Google）

| 因子 | API | 免费额度 | 说明 |
|------|-----|----------|------|
| 百度搜索指数 | AkShare | 无限制 | 关键词搜索热度 |
| 百度资讯指数 | AkShare | 无限制 | 新闻关注度 |
| 百度需求图谱 | AkShare | 无限制 | 用户意图 |

```python
import akshare as ak

# 百度搜索指数（关键词）
df = ak.baidu_search_index(keyword="茅台", start_date="20230101", end_date="20230331")

# 百度资讯指数
df = ak.baidu_info_index(keyword="新能源汽车", start_date="20230101", end_date="20230331")
```

#### 8.2.4 社交媒体因子（免费）

| 因子 | API | 免费额度 | 说明 |
|------|-----|----------|------|
| 微博讨论 | 微博API | 部分免费 | 社交情绪 |
| 雪球评论 | 雪球 | 需要爬虫 | 投资者情绪 |
| 东方财富股吧 | AkShare | 免费 | 散户情绪 |

```python
import akshare as ak

# 东方财富股吧帖子
df = ak.stock_guba_sina()  # 股吧帖子列表

# 东方财富个股评论
df = ak.stock_comment_sina()  # 个股评论情绪
```

#### 8.2.5 宏观经济因子（⭐官方免费）

| 因子 | 数据源 | 获取方式 | 更新频率 |
|------|--------|----------|----------|
| GDP | 国家统计局 | 公开数据 | 季度 |
| CPI/PPI | 国家统计局 | 公开数据 | 月度 |
| 央行利率 | 中国人民银行 | 公开数据 | 不定期 |
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

#### 8.2.6 政策事件因子（⭐免费）

| 因子 | 获取方式 | 更新频率 |
|------|----------|----------|
| 政策公告 | 政府网站RSS | 实时 |
| 监管函 | 东方财富 | 日更 |
| 研报发布 | 东方财富 | 日更 |

```python
import akshare as ak
import feedparser

# 监管函
df = ak.stock_regulatory_notice_em()

# 研报
df = ak.stock_research_report_em()

# 政府RSS
def fetch_gov_rss():
    """获取政府网站政策"""
    feeds = {
        '国务院': 'http://www.gov.cn/xxgk/gmxbmmrdf/servlexml/xxgkml.xml',
        '证监会': 'http://www.csrc.gov.cn/csrc/cxxw/rss.xml',
    }
    for name, url in feeds.items():
        feed = feedparser.parse(url)
        print(f"{name}: {len(feed.entries)} 条")
```

### 8.3 免费另类因子汇总表

| 优先级 | 因子类别 | 具体因子 | 免费程度 | 实现难度 |
|--------|----------|----------|----------|----------|
| 🔴 高 | 资金流 | 北向/融资融券/龙虎榜 | ⭐⭐⭐⭐⭐ | ⭐ |
| 🔴 高 | 交易行为 | 大宗/杠杆资金 | ⭐⭐⭐⭐⭐ | ⭐ |
| 🟡 中 | 搜索指数 | 百度搜索/资讯指数 | ⭐⭐⭐⭐ | ⭐ |
| 🟡 中 | 天气AQI | 温度/空气质量 | ⭐⭐⭐⭐ | ⭐⭐ |
| 🟢 低 | 社交媒体 | 微博/股吧情绪 | ⭐⭐⭐ | ⭐⭐ |
| 🟢 低 | 宏观经济 | GDP/CPI/利率 | ⭐⭐⭐⭐⭐ | ⭐ |

### 8.4 数据更新频率策略

| 场景 | 更新频率 | 数据类型 |
|------|----------|----------|
| **实盘交易** | 分钟级 | iFinD行情数据 |
| **盘前准备** | 日级 | 北向资金/融资融券 |
| **另类因子** | 日级 | 天气/搜索指数 |
| **舆情因子** | 实时 | 新闻/公告 |

### 8.5 快速实现路径

```python
# Phase 1: 资金流因子（1天）
fund_flow = {
    'north_flow': ak.stock_em_hsgt_north_net_flow_in(),  # 北向资金
    'margin': ak.stock_margin_detail_sz(),  # 融资融券
    'lhb': ak.stock_lhb_detail_em(),  # 龙虎榜
}

# Phase 2: 搜索因子（1天）
search_index = {
    'baidu_search': ak.baidu_search_index(keyword="茅台"),
}

# Phase 3: 天气因子（2天）
weather = {
    'temperature': get_weather(city="shanghai"),
    'aqi': get_aqi(city="beijing"),
}
```

---

## 9. 数据源配置

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
