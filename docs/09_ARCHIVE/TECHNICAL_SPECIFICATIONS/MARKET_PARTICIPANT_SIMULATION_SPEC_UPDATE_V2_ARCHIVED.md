---
module_id: TECH_SPEC_MARKET_PARTICIPANT_SIM_UPDATE_002
version: 2.0.0
status: Active
created_date: 2026-04-03
last_updated: 2026-04-03
owner: 首席技术评审官
standard_type: 专业量化机构技术规格书更新文档
applicable_scope: 市场参与者行为模拟系�?compliance_level: 专业标准
parent_document: ./MARKET_PARTICIPANT_SIMULATION_SPEC.md
implementation_status: 设计阶段
---

# 市场参与者行为模拟系统技术规格书更新文档

> **版本**: v2.0
> **创建日期**: 2026-04-03
> **更新内容**: 术语标准化、资金流向监控接口、智能体参数配置、数据获取模�?> **依据文档**: MARKET_PARTICIPANT_BEHAVIOR_RESEARCH_SUPPLEMENT.md

---

## 📝 一、术语标准化更新

### 1.1 核心术语替换对照�?
根据专业量化机构标准，对技术规格书中的术语进行标准化更新：

| 原术�?| 新术语（专业标准�?| 英文术语 | 替换范围 |
|--------|-------------------|---------|---------|
| 主力 | **机构资金** | Institutional Capital | 全文�?|
| 主力资金 | **机构资金** | Institutional Capital | 全文�?|
| 主力/游资智能�?| **机构/热钱智能�?* | Institutional/Hot Money Agent | 智能体名�?|
| 主力控盘 | **机构控盘** | Institutional Control | 行为描述 |
| 主力行为 | **机构资金行为** | Institutional Capital Behavior | 研究领域 |
| 国家�?| **主权基金** | Sovereign Funds | 学术场景 |
| 游资 | **热钱** | Hot Money | 风险监控场景 |
| 散户 | **零售投资�?* | Retail Investors | 学术场景 |

### 1.2 智能体命名规�?
**更新后的智能体命名体�?*�?
```
一级分类（学术标准）：
├── 机构投资者（Institutional Investors�?�?  ├── 主权基金智能体（Sovereign Fund Agent�?�?  �?  └── 代号：AGENT.SOVEREIGN_FUND.001
�?  ├── 公募基金智能体（Mutual Fund Agent�?�?  �?  └── 代号：AGENT.MUTUAL_FUND.001
�?  ├── 私募基金智能体（Private Equity Agent�?�?  �?  ├── 量化基金智能体（Quantitative Fund Agent�?�?  �?  �?  └── 代号：AGENT.QUANT_FUND.001
�?  �?  └── 主观私募智能体（Discretionary PE Agent�?�?  �?      └── 代号：AGENT.DISCRETIONARY_PE.001
�?  ├── 外资智能体（Foreign Capital Agent�?�?  �?  └── 代号：AGENT.FOREIGN_CAPITAL.001
�?  ├── 保险资金智能体（Insurance Fund Agent�?�?  �?  └── 代号：AGENT.INSURANCE_FUND.001
�?  └── 产业资本智能体（Industrial Capital Agent�?�?      └── 代号：AGENT.INDUSTRIAL_CAPITAL.001
└── 零售投资者（Retail Investors�?    ├── 高净值个人智能体（High Net Worth Agent�?    �?  └── 代号：AGENT.HNW.001
    └── 散户智能体（Retail Investor Agent�?        └── 代号：AGENT.RETAIL.001
```

---

## 📊 二、资金流向监控指标接口设�?
### 2.1 DDX/DDE/BBD数据获取接口

#### 2.1.1 接口定义

**接口名称**：CapitalFlowDataFetcher

**接口ID**：INTERFACE.CAPITAL_FLOW.001

**数据�?*：同花顺iFinD

**更新频率**：实时（盘中）、日度（盘后�?
**接口规范**�?
```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd

@dataclass
class DDXIndicator:
    """DDX指标数据结构
    
    索引: DATA.DDX.001
    定义: 大单动向指标
    公式: DDX = (超大单净买入 + 大单净买入) / 流通盘 × 10000
    """
    stock_code: str
    timestamp: datetime
    ddx_value: float  # DDX�?    ddx_ma5: float  # 5日均�?    ddx_ma10: float  # 10日均�?    ddx_consecutive_days: int  # 连续翻红/翻绿天数
    super_large_net_buy: float  # 超大单净买入（万元）
    large_net_buy: float  # 大单净买入（万元）
    circulation_cap: float  # 流通盘（万元）
    confidence: float  # 数据置信�?    
@dataclass
class DDEIndicator:
    """DDE决策系统数据结构
    
    索引: DATA.DDE.001
    定义: 大单净量、散户数量、大单金�?    """
    stock_code: str
    timestamp: datetime
    large_order_net_ratio: float  # 大单净量（占流通盘比率�?    retail_participation: float  # 散户数量（参与度�?    large_order_amount: float  # 大单金额（万元）
    net_inflow_amount: float  # 净流入金额（万元）
    confidence: float

@dataclass
class BBDIndicator:
    """BBD指标数据结构
    
    索引: DATA.BBD.001
    定义: 特大单买卖差�?    公式: BBD = 特大单流入净量金�?    """
    stock_code: str
    timestamp: datetime
    bbd_value: float  # BBD值（万元�?    super_large_inflow: float  # 特大单流入（万元�?    super_large_outflow: float  # 特大单流出（万元�?    total_amount: float  # 总成交额（万元）
    cannibalization_rate: float  # 通吃�?= BBD / 成交�?× 100
    confidence: float

class CapitalFlowDataFetcher(ABC):
    """资金流向数据获取器抽象基�?    
    索引: INTERFACE.CAPITAL_FLOW.001
    职责: 从iFinD获取DDX、DDE、BBD数据
    数据�? 同花顺iFinD
    """
    
    @abstractmethod
    def fetch_ddx(self, 
                  stock_codes: List[str],
                  start_date: datetime,
                  end_date: datetime) -> Dict[str, List[DDXIndicator]]:
        """获取DDX指标数据
        
        参数:
            stock_codes: 股票代码列表（如 ['600519.SH', '000858.SZ']�?            start_date: 开始日�?            end_date: 结束日期
            
        返回:
            Dict[str, List[DDXIndicator]]: 股票代码 -> DDX指标列表
            
        数据源映�?
            iFinD函数: THS_DDX
            字段映射:
                - ddx_value: DDX
                - super_large_net_buy: 超大单净买入
                - large_net_buy: 大单净买入
        """
        pass
    
    @abstractmethod
    def fetch_dde(self,
                  stock_codes: List[str],
                  start_date: datetime,
                  end_date: datetime) -> Dict[str, List[DDEIndicator]]:
        """获取DDE决策数据
        
        参数:
            stock_codes: 股票代码列表
            start_date: 开始日�?            end_date: 结束日期
            
        返回:
            Dict[str, List[DDEIndicator]]: 股票代码 -> DDE指标列表
            
        数据源映�?
            iFinD函数: THS_DDE
            字段映射:
                - large_order_net_ratio: 大单净�?                - retail_participation: 散户数量
                - large_order_amount: 大单金额
        """
        pass
    
    @abstractmethod
    def fetch_bbd(self,
                  stock_codes: List[str],
                  start_date: datetime,
                  end_date: datetime) -> Dict[str, List[BBDIndicator]]:
        """获取BBD指标数据
        
        参数:
            stock_codes: 股票代码列表
            start_date: 开始日�?            end_date: 结束日期
            
        返回:
            Dict[str, List[BBDIndicator]]: 股票代码 -> BBD指标列表
            
        数据源映�?
            iFinD函数: THS_BBD
            字段映射:
                - bbd_value: BBD�?                - super_large_inflow: 特大单流�?                - super_large_outflow: 特大单流�?        """
        pass
    
    @abstractmethod
    def fetch_realtime_capital_flow(self,
                                    stock_codes: List[str]) -> Dict[str, Dict]:
        """获取实时资金流向数据（盘中）
        
        参数:
            stock_codes: 股票代码列表
            
        返回:
            Dict[str, Dict]: 股票代码 -> 实时资金流向数据
            
        更新频率:
            盘中: 3分钟延迟
            盘后: 日度更新
        """
        pass
```

#### 2.1.2 iFinD实现�?
```python
import THSAPI as ths
from datetime import datetime, timedelta
from typing import List, Dict
import pandas as pd

class IFindCapitalFlowFetcher(CapitalFlowDataFetcher):
    """iFinD资金流向数据获取器实�?    
    索引: IMPLEMENTATION.IFIND_CAPITAL_FLOW.001
    数据�? 同花顺iFinD
    依赖: THSAPI (iFinD Python接口)
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.ifs_client = ths.THSApi()
        
    def fetch_ddx(self,
                  stock_codes: List[str],
                  start_date: datetime,
                  end_date: datetime) -> Dict[str, List[DDXIndicator]]:
        """获取DDX指标数据
        
        iFinD调用示例:
            ths.ED_query(
                'ths_ddx_stock',
                stock_codes,
                'ddx,超大单净买入,大单净买入',
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
        """
        result = {}
        
        for stock_code in stock_codes:
            try:
                df = self.ifs_client.ED_query(
                    'ths_ddx_stock',
                    stock_code,
                    'ddx,超大单净买入,大单净买入,流通市�?,
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
                
                indicators = []
                for _, row in df.iterrows():
                    indicator = DDXIndicator(
                        stock_code=stock_code,
                        timestamp=row['time'],
                        ddx_value=row['ddx'],
                        ddx_ma5=self._calculate_ma(row['ddx'], 5),
                        ddx_ma10=self._calculate_ma(row['ddx'], 10),
                        ddx_consecutive_days=self._calculate_consecutive_days(row['ddx']),
                        super_large_net_buy=row['超大单净买入'],
                        large_net_buy=row['大单净买入'],
                        circulation_cap=row['流通市�?],
                        confidence=0.95
                    )
                    indicators.append(indicator)
                
                result[stock_code] = indicators
                
            except Exception as e:
                print(f"Error fetching DDX for {stock_code}: {e}")
                result[stock_code] = []
        
        return result
    
    def fetch_dde(self,
                  stock_codes: List[str],
                  start_date: datetime,
                  end_date: datetime) -> Dict[str, List[DDEIndicator]]:
        """获取DDE决策数据
        
        iFinD调用示例:
            ths.ED_query(
                'ths_dde_stock',
                stock_codes,
                '大单净�?散户数量,大单金额',
                start_date,
                end_date
            )
        """
        result = {}
        
        for stock_code in stock_codes:
            try:
                df = self.ifs_client.ED_query(
                    'ths_dde_stock',
                    stock_code,
                    '大单净�?散户数量,大单金额,净流入金额',
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
                
                indicators = []
                for _, row in df.iterrows():
                    indicator = DDEIndicator(
                        stock_code=stock_code,
                        timestamp=row['time'],
                        large_order_net_ratio=row['大单净�?],
                        retail_participation=row['散户数量'],
                        large_order_amount=row['大单金额'],
                        net_inflow_amount=row['净流入金额'],
                        confidence=0.95
                    )
                    indicators.append(indicator)
                
                result[stock_code] = indicators
                
            except Exception as e:
                print(f"Error fetching DDE for {stock_code}: {e}")
                result[stock_code] = []
        
        return result
    
    def fetch_bbd(self,
                  stock_codes: List[str],
                  start_date: datetime,
                  end_date: datetime) -> Dict[str, List[BBDIndicator]]:
        """获取BBD指标数据
        
        iFinD调用示例:
            ths.ED_query(
                'ths_bbd_stock',
                stock_codes,
                'BBD,特大单流�?特大单流�?总成交额',
                start_date,
                end_date
            )
        """
        result = {}
        
        for stock_code in stock_codes:
            try:
                df = self.ifs_client.ED_query(
                    'ths_bbd_stock',
                    stock_code,
                    'BBD,特大单流�?特大单流�?总成交额',
                    start_date.strftime('%Y-%m-%d'),
                    end_date.strftime('%Y-%m-%d')
                )
                
                indicators = []
                for _, row in df.iterrows():
                    cannibalization_rate = (row['BBD'] / row['总成交额'] * 100) if row['总成交额'] > 0 else 0
                    
                    indicator = BBDIndicator(
                        stock_code=stock_code,
                        timestamp=row['time'],
                        bbd_value=row['BBD'],
                        super_large_inflow=row['特大单流�?],
                        super_large_outflow=row['特大单流�?],
                        total_amount=row['总成交额'],
                        cannibalization_rate=cannibalization_rate,
                        confidence=0.95
                    )
                    indicators.append(indicator)
                
                result[stock_code] = indicators
                
            except Exception as e:
                print(f"Error fetching BBD for {stock_code}: {e}")
                result[stock_code] = []
        
        return result
    
    def fetch_realtime_capital_flow(self,
                                    stock_codes: List[str]) -> Dict[str, Dict]:
        """获取实时资金流向数据（盘中）
        
        iFinD调用示例:
            ths.HQ_query(stock_codes, '最新价,涨跌�?DDX,DDE,BBD')
        """
        result = {}
        
        try:
            df = self.ifs_client.HQ_query(
                stock_codes,
                '最新价,涨跌�?DDX,DDE,BBD,超大单净流入,大单净流入'
            )
            
            for _, row in df.iterrows():
                stock_code = row['股票代码']
                result[stock_code] = {
                    'price': row['最新价'],
                    'change_pct': row['涨跌�?],
                    'ddx': row['DDX'],
                    'dde': row['DDE'],
                    'bbd': row['BBD'],
                    'super_large_net_inflow': row['超大单净流入'],
                    'large_net_inflow': row['大单净流入'],
                    'timestamp': datetime.now()
                }
                
        except Exception as e:
            print(f"Error fetching realtime capital flow: {e}")
        
        return result
    
    def _calculate_ma(self, values: pd.Series, window: int) -> float:
        """计算移动平均"""
        if len(values) < window:
            return values.mean()
        return values.rolling(window=window).mean().iloc[-1]
    
    def _calculate_consecutive_days(self, ddx_series: pd.Series) -> int:
        """计算DDX连续翻红/翻绿天数"""
        if len(ddx_series) == 0:
            return 0
        
        last_value = ddx_series.iloc[-1]
        count = 0
        
        for value in reversed(ddx_series):
            if (last_value > 0 and value > 0) or (last_value < 0 and value < 0):
                count += 1
            else:
                break
        
        return count
```

### 2.2 龙虎榜数据解析接�?
#### 2.2.1 接口定义

```python
@dataclass
class DragonTigerListItem:
    """龙虎榜数据项
    
    索引: DATA.DRAGON_TIGER.001
    定义: 龙虎榜买卖明�?    """
    stock_code: str
    stock_name: str
    trade_date: datetime
    close_price: float
    change_pct: float
    turnover_rate: float
    reason: str  # 上榜原因
    
    buy_seats: List[Dict]  # 买入席位列表
    sell_seats: List[Dict]  # 卖出席位列表
    
    net_buy_amount: float  # 净买入金额（万元）
    institutional_buy_count: int  # 机构买入席位数量
    institutional_sell_count: int  # 机构卖出席位数量
    
    hot_money_flag: bool  # 是否有知名游�?    institutional_flag: bool  # 是否有机构专用席�?
class DragonTigerDataParser(ABC):
    """龙虎榜数据解析器抽象基类
    
    索引: INTERFACE.DRAGON_TIGER.001
    职责: 解析龙虎榜数据，识别机构席位和游资席�?    数据�? 同花顺iFinD、交易所公开数据
    """
    
    @abstractmethod
    def fetch_dragon_tiger_list(self,
                                start_date: datetime,
                                end_date: datetime,
                                reason_filter: Optional[List[str]] = None) -> List[DragonTigerListItem]:
        """获取龙虎榜列�?        
        参数:
            start_date: 开始日�?            end_date: 结束日期
            reason_filter: 上榜原因过滤（如 ['涨停', '跌停', '换手率异�?]�?            
        返回:
            List[DragonTigerListItem]: 龙虎榜数据列�?            
        数据源映�?
            iFinD函数: THS龙虎�?            字段映射:
                - stock_code: 证券代码
                - trade_date: 交易日期
                - buy_seats: 买入席位
                - sell_seats: 卖出席位
        """
        pass
    
    @abstractmethod
    def identify_institutional_seats(self,
                                    seats: List[Dict]) -> List[Dict]:
        """识别机构专用席位
        
        参数:
            seats: 席位列表
            
        返回:
            List[Dict]: 机构席位列表
            
        识别规则:
            1. 席位名称包含"机构专用"
            2. 席位名称包含"公募"�?社保"�?保险"
            3. 席位代码符合机构席位编码规则
        """
        pass
    
    @abstractmethod
    def identify_hot_money_seats(self,
                                seats: List[Dict]) -> List[Dict]:
        """识别知名游资席位
        
        参数:
            seats: 席位列表
            
        返回:
            List[Dict]: 游资席位列表
            
        识别规则:
            1. 知名游资营业部名单（如：华鑫上海分公司、财通杭州体育场路等�?            2. 历史操作风格匹配
        """
        pass
    
    @abstractmethod
    def analyze_institutional_behavior(self,
                                       item: DragonTigerListItem) -> Dict:
        """分析机构资金行为
        
        参数:
            item: 龙虎榜数据项
            
        返回:
            Dict: 机构行为分析结果
            
        分析维度:
            1. 机构净买入金额
            2. 机构买入/卖出席位数量对比
            3. 机构协同度（多家机构同时买入�?            4. 游资与机构博弈情�?        """
        pass
```

#### 2.2.2 iFinD实现�?
```python
class IFindDragonTigerParser(DragonTigerDataParser):
    """iFinD龙虎榜数据解析器实现
    
    索引: IMPLEMENTATION.IFIND_DRAGON_TIGER.001
    数据�? 同花顺iFinD
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.ifs_client = ths.THSApi()
        
        self.known_hot_money_seats = {
            '华鑫证券有限责任公司上海分公�?: '知名游资',
            '财通证券股份有限公司杭州体育场路证券营业部': '知名游资',
            '国泰君安证券股份有限公司上海分公�?: '知名游资',
            '中国中金财富证券有限公司北京分公�?: '知名游资',
            '华泰证券股份有限公司深圳分公�?: '知名游资',
        }
    
    def fetch_dragon_tiger_list(self,
                                start_date: datetime,
                                end_date: datetime,
                                reason_filter: Optional[List[str]] = None) -> List[DragonTigerListItem]:
        """获取龙虎榜列�?        
        iFinD调用示例:
            ths.ED_query(
                'ths龙虎�?,
                '',
                '证券代码,证券简�?交易日期,收盘�?涨跌�?换手�?上榜原因,买入席位,卖出席位',
                start_date,
                end_date
            )
        """
        items = []
        
        try:
            df = self.ifs_client.ED_query(
                'ths龙虎�?,
                '',
                '证券代码,证券简�?交易日期,收盘�?涨跌�?换手�?上榜原因,买入席位,卖出席位',
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            if reason_filter:
                df = df[df['上榜原因'].isin(reason_filter)]
            
            for _, row in df.iterrows():
                buy_seats = self._parse_seats(row['买入席位'])
                sell_seats = self._parse_seats(row['卖出席位'])
                
                institutional_buy = self.identify_institutional_seats(buy_seats)
                institutional_sell = self.identify_institutional_seats(sell_seats)
                
                hot_money_buy = self.identify_hot_money_seats(buy_seats)
                hot_money_sell = self.identify_hot_money_seats(sell_seats)
                
                net_buy = sum([seat['买入金额'] for seat in buy_seats]) - \
                         sum([seat['卖出金额'] for seat in sell_seats])
                
                item = DragonTigerListItem(
                    stock_code=row['证券代码'],
                    stock_name=row['证券简�?],
                    trade_date=row['交易日期'],
                    close_price=row['收盘�?],
                    change_pct=row['涨跌�?],
                    turnover_rate=row['换手�?],
                    reason=row['上榜原因'],
                    buy_seats=buy_seats,
                    sell_seats=sell_seats,
                    net_buy_amount=net_buy,
                    institutional_buy_count=len(institutional_buy),
                    institutional_sell_count=len(institutional_sell),
                    hot_money_flag=len(hot_money_buy) > 0 or len(hot_money_sell) > 0,
                    institutional_flag=len(institutional_buy) > 0 or len(institutional_sell) > 0
                )
                
                items.append(item)
                
        except Exception as e:
            print(f"Error fetching dragon tiger list: {e}")
        
        return items
    
    def identify_institutional_seats(self, seats: List[Dict]) -> List[Dict]:
        """识别机构专用席位"""
        institutional_seats = []
        
        for seat in seats:
            seat_name = seat.get('营业部名�?, '')
            
            if '机构专用' in seat_name or \
               '公募' in seat_name or \
               '社保' in seat_name or \
               '保险' in seat_name or \
               'QFII' in seat_name:
                institutional_seats.append(seat)
        
        return institutional_seats
    
    def identify_hot_money_seats(self, seats: List[Dict]) -> List[Dict]:
        """识别知名游资席位"""
        hot_money_seats = []
        
        for seat in seats:
            seat_name = seat.get('营业部名�?, '')
            
            if seat_name in self.known_hot_money_seats:
                hot_money_seats.append(seat)
        
        return hot_money_seats
    
    def analyze_institutional_behavior(self, item: DragonTigerListItem) -> Dict:
        """分析机构资金行为"""
        institutional_buy_seats = self.identify_institutional_seats(item.buy_seats)
        institutional_sell_seats = self.identify_institutional_seats(item.sell_seats)
        
        institutional_net_buy = sum([seat['买入金额'] for seat in institutional_buy_seats]) - \
                               sum([seat['卖出金额'] for seat in institutional_sell_seats])
        
        hot_money_buy_seats = self.identify_hot_money_seats(item.buy_seats)
        hot_money_sell_seats = self.identify_hot_money_seats(item.sell_seats)
        
        hot_money_net_buy = sum([seat['买入金额'] for seat in hot_money_buy_seats]) - \
                           sum([seat['卖出金额'] for seat in hot_money_sell_seats])
        
        return {
            'stock_code': item.stock_code,
            'trade_date': item.trade_date,
            'institutional_net_buy': institutional_net_buy,
            'institutional_buy_count': len(institutional_buy_seats),
            'institutional_sell_count': len(institutional_sell_seats),
            'institutional_coordination': len(institutional_buy_seats) >= 3,
            'hot_money_net_buy': hot_money_net_buy,
            'institutional_vs_hot_money': 'institutional' if institutional_net_buy > hot_money_net_buy else 'hot_money',
            'signal_strength': self._calculate_signal_strength(
                institutional_net_buy,
                len(institutional_buy_seats),
                item.net_buy_amount
            )
        }
    
    def _parse_seats(self, seats_str: str) -> List[Dict]:
        """解析席位字符�?""
        seats = []
        
        return seats
    
    def _calculate_signal_strength(self,
                                   institutional_net_buy: float,
                                   institutional_count: int,
                                   total_net_buy: float) -> float:
        """计算信号强度"""
        if total_net_buy == 0:
            return 0.0
        
        ratio = institutional_net_buy / abs(total_net_buy)
        count_bonus = min(institutional_count / 5.0, 1.0)
        
        strength = (ratio * 0.7 + count_bonus * 0.3)
        
        return min(max(strength, 0.0), 1.0)
```

### 2.3 北向资金监控接口

#### 2.3.1 接口定义

```python
@dataclass
class NorthboundCapitalFlow:
    """北向资金流向数据结构
    
    索引: DATA.NORTHBOUND.001
    定义: 北向资金（沪股�?深股通）流向数据
    """
    trade_date: datetime
    shanghai_connect_net_buy: float  # 沪股通净买入（亿元）
    shenzhen_connect_net_buy: float  # 深股通净买入（亿元）
    total_net_buy: float  # 总净买入（亿元）
    
    shanghai_connect_balance: float  # 沪股通余额（亿元�?    shenzhen_connect_balance: float  # 深股通余额（亿元�?    
    top_buy_stocks: List[Dict]  # 买入�?0股票
    top_sell_stocks: List[Dict]  # 卖出�?0股票
    
    sector_allocation: Dict[str, float]  # 行业配置

@dataclass
class NorthboundHolding:
    """北向资金持仓数据结构
    
    索引: DATA.NORTHBOUND_HOLDING.001
    定义: 北向资金持仓明细
    """
    stock_code: str
    stock_name: str
    hold_amount: float  # 持股数量（万股）
    hold_value: float  # 持股市值（万元�?    hold_ratio: float  # 持股占比�?�?    change_amount: float  # 持股变化（万股）
    change_ratio: float  # 持股变化比例�?�?
class NorthboundCapitalMonitor(ABC):
    """北向资金监控器抽象基�?    
    索引: INTERFACE.NORTHBOUND.001
    职责: 监控北向资金流向和持仓变�?    数据�? 同花顺iFinD、港交所公开数据
    """
    
    @abstractmethod
    def fetch_daily_flow(self,
                        start_date: datetime,
                        end_date: datetime) -> List[NorthboundCapitalFlow]:
        """获取北向资金日度流向
        
        参数:
            start_date: 开始日�?            end_date: 结束日期
            
        返回:
            List[NorthboundCapitalFlow]: 日度流向数据列表
            
        数据源映�?
            iFinD函数: THS北向资金
            字段映射:
                - total_net_buy: 北向资金净买入
                - shanghai_connect_net_buy: 沪股通净买入
                - shenzhen_connect_net_buy: 深股通净买入
        """
        pass
    
    @abstractmethod
    def fetch_holdings(self,
                      stock_codes: Optional[List[str]] = None,
                      top_n: int = 100) -> List[NorthboundHolding]:
        """获取北向资金持仓明细
        
        参数:
            stock_codes: 股票代码列表（可选，默认返回全部�?            top_n: 返回前N只股票（默认100�?            
        返回:
            List[NorthboundHolding]: 持仓明细列表
            
        数据源映�?
            iFinD函数: THS北向持股
            字段映射:
                - hold_amount: 持股数量
                - hold_value: 持股市�?                - hold_ratio: 持股占比
        """
        pass
    
    @abstractmethod
    def analyze_sector_preference(self,
                                 flow_data: List[NorthboundCapitalFlow]) -> Dict[str, float]:
        """分析北向资金行业偏好
        
        参数:
            flow_data: 流向数据
            
        返回:
            Dict[str, float]: 行业配置比例
            
        分析方法:
            1. 统计买入/卖出�?0股票的行业分�?            2. 计算各行业净买入金额
            3. 识别行业轮动趋势
        """
        pass
    
    @abstractmethod
    def detect_smart_money_signal(self,
                                 flow_data: List[NorthboundCapitalFlow],
                                 threshold_days: int = 5,
                                 threshold_amount: float = 60.0) -> Dict:
        """检测聪明钱信号
        
        参数:
            flow_data: 流向数据
            threshold_days: 连续天数阈值（默认5天）
            threshold_amount: 净买入金额阈值（默认60亿元�?            
        返回:
            Dict: 聪明钱信�?            
        信号规则:
            1. 连续5日净买入�?0亿元：新能源、电子板块胜�?0%
            2. 单日净流出�?0亿元：高估值消费股平均回撤5.3%
        """
        pass
```

#### 2.3.2 iFinD实现�?
```python
class IFindNorthboundCapitalMonitor(NorthboundCapitalMonitor):
    """iFinD北向资金监控器实�?    
    索引: IMPLEMENTATION.IFIND_NORTHBOUND.001
    数据�? 同花顺iFinD
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.ifs_client = ths.THSApi()
    
    def fetch_daily_flow(self,
                        start_date: datetime,
                        end_date: datetime) -> List[NorthboundCapitalFlow]:
        """获取北向资金日度流向
        
        iFinD调用示例:
            ths.ED_query(
                'ths北向资金',
                '',
                '交易日期,北向资金净买入,沪股通净买入,深股通净买入,沪股通余�?深股通余�?,
                start_date,
                end_date
            )
        """
        flows = []
        
        try:
            df = self.ifs_client.ED_query(
                'ths北向资金',
                '',
                '交易日期,北向资金净买入,沪股通净买入,深股通净买入,沪股通余�?深股通余�?,
                start_date.strftime('%Y-%m-%d'),
                end_date.strftime('%Y-%m-%d')
            )
            
            for _, row in df.iterrows():
                flow = NorthboundCapitalFlow(
                    trade_date=row['交易日期'],
                    shanghai_connect_net_buy=row['沪股通净买入'] / 10000,
                    shenzhen_connect_net_buy=row['深股通净买入'] / 10000,
                    total_net_buy=row['北向资金净买入'] / 10000,
                    shanghai_connect_balance=row['沪股通余�?] / 10000,
                    shenzhen_connect_balance=row['深股通余�?] / 10000,
                    top_buy_stocks=self._fetch_top_stocks(row['交易日期'], 'buy'),
                    top_sell_stocks=self._fetch_top_stocks(row['交易日期'], 'sell'),
                    sector_allocation={}
                )
                
                flows.append(flow)
                
        except Exception as e:
            print(f"Error fetching northbound capital flow: {e}")
        
        return flows
    
    def fetch_holdings(self,
                      stock_codes: Optional[List[str]] = None,
                      top_n: int = 100) -> List[NorthboundHolding]:
        """获取北向资金持仓明细
        
        iFinD调用示例:
            ths.ED_query(
                'ths北向持股',
                '',
                '证券代码,证券简�?持股数量,持股市�?持股占比,持股变化,持股变化比例',
                '',
                ''
            )
        """
        holdings = []
        
        try:
            df = self.ifs_client.ED_query(
                'ths北向持股',
                '',
                '证券代码,证券简�?持股数量,持股市�?持股占比,持股变化,持股变化比例',
                '',
                ''
            )
            
            if stock_codes:
                df = df[df['证券代码'].isin(stock_codes)]
            
            df = df.head(top_n)
            
            for _, row in df.iterrows():
                holding = NorthboundHolding(
                    stock_code=row['证券代码'],
                    stock_name=row['证券简�?],
                    hold_amount=row['持股数量'],
                    hold_value=row['持股市�?],
                    hold_ratio=row['持股占比'],
                    change_amount=row['持股变化'],
                    change_ratio=row['持股变化比例']
                )
                
                holdings.append(holding)
                
        except Exception as e:
            print(f"Error fetching northbound holdings: {e}")
        
        return holdings
    
    def analyze_sector_preference(self,
                                 flow_data: List[NorthboundCapitalFlow]) -> Dict[str, float]:
        """分析北向资金行业偏好"""
        sector_allocation = {}
        
        for flow in flow_data:
            for stock in flow.top_buy_stocks:
                sector = stock.get('sector', 'Unknown')
                amount = stock.get('buy_amount', 0)
                
                if sector not in sector_allocation:
                    sector_allocation[sector] = 0
                sector_allocation[sector] += amount
        
        total = sum(sector_allocation.values())
        if total > 0:
            sector_allocation = {k: v / total for k, v in sector_allocation.items()}
        
        return sector_allocation
    
    def detect_smart_money_signal(self,
                                 flow_data: List[NorthboundCapitalFlow],
                                 threshold_days: int = 5,
                                 threshold_amount: float = 60.0) -> Dict:
        """检测聪明钱信号"""
        if len(flow_data) < threshold_days:
            return {
                'signal_type': 'INSUFFICIENT_DATA',
                'confidence': 0.0
            }
        
        recent_flows = flow_data[-threshold_days:]
        
        consecutive_buy = all([f.total_net_buy > 0 for f in recent_flows])
        total_buy = sum([f.total_net_buy for f in recent_flows])
        
        if consecutive_buy and total_buy >= threshold_amount:
            return {
                'signal_type': 'STRONG_BUY',
                'total_net_buy': total_buy,
                'consecutive_days': threshold_days,
                'confidence': 0.80,
                'target_sectors': ['新能�?, '电子'],
                'expected_win_rate': 0.80,
                'reasoning': f'北向资金连续{threshold_days}日净买入超{threshold_amount}亿元，历史数据显示新能源、电子板块胜率达80%'
            }
        
        recent_flow = flow_data[-1]
        if recent_flow.total_net_buy < -80:
            return {
                'signal_type': 'RISK_ALERT',
                'net_outflow': abs(recent_flow.total_net_buy),
                'confidence': 0.85,
                'risk_sectors': ['高估值消费股'],
                'expected_drawdown': 0.053,
                'reasoning': f'北向资金单日净流出�?0亿元，历史数据显示高估值消费股平均回撤5.3%'
            }
        
        return {
            'signal_type': 'NEUTRAL',
            'confidence': 0.50,
            'reasoning': '北向资金流向未达到显著信号阈�?
        }
    
    def _fetch_top_stocks(self, trade_date: datetime, direction: str) -> List[Dict]:
        """获取买入/卖出�?0股票"""
        stocks = []
        
        return stocks
```

---

## 🤖 三�?类智能体详细参数配置

### 3.1 主权基金智能体（Sovereign Fund Agent�?
**代号**：AGENT.SOVEREIGN_FUND.001

**行为特征**�?- 市场稳定器，政策驱动
- ETF配置为主，长期持�?- 仅在市场异常波动时介�?
**参数配置**�?
```yaml
sovereign_fund_agent:
  name: "主权基金智能�?
  type: "institutional_investor"
  
  decision_model:
    type: "rule_engine_llm_hybrid"
    rule_weight: 0.70
    llm_weight: 0.30
    llm_model: "GLM-4-7B-Flash"
  
  intervention_threshold:
    market_drop: -0.05
    volatility_spike: 2.0
    sentiment_panic: -0.8
    liquidity_crisis: 0.3
  
  etf_allocation:
    hs300:
      weight: 0.60
      code: "510300.SH"
      description: "沪深300ETF"
    zz500:
      weight: 0.25
      code: "510500.SH"
      description: "中证500ETF"
    zz1000:
      weight: 0.15
      code: "512100.SH"
      description: "中证1000ETF"
  
  position_limit:
    max_single_etf: 0.05
    max_total: 0.15
  
  holding_period:
    min_days: 90
    avg_days: 180
    max_days: 365
  
  policy_signal_sources:
    - "央行公告"
    - "证监会公�?
    - "国务院政策文�?
    - "新华社社�?
  
  market_stability_indicators:
    - "市场波动�?
    - "流动性指�?
    - "市场情绪指数"
    - "蓝筹股资金流�?
  
  reward_function:
    market_stability_weight: 0.50
    policy_alignment_weight: 0.30
    long_term_return_weight: 0.20
  
  risk_control:
    max_intervention_per_day: 1
    cooldown_period: 5
    stop_loss_threshold: -0.10
```

### 3.2 公募基金智能体（Mutual Fund Agent�?
**代号**：AGENT.MUTUAL_FUND.001

**行为特征**�?- 赛道聚焦，高仓位运行
- 基本面驱动，机构协同
- 平均仓位86.40%

**参数配置**�?
```yaml
mutual_fund_agent:
  name: "公募基金智能�?
  type: "institutional_investor"
  
  decision_model:
    type: "rl_fundamental_hybrid"
    rl_algorithm: "SAC"
    rl_weight: 0.60
    fundamental_weight: 0.40
  
  sector_focus:
    ai_computing:
      weight: 0.35
      keywords: ["AI算力", "GPU", "数据中心"]
      target_stocks: ["浪潮信息", "中科曙光", "寒武�?]
    
    medical_tech:
      weight: 0.25
      keywords: ["医疗新科技", "创新�?, "医疗器械"]
      target_stocks: ["恒瑞医药", "迈瑞医疗", "药明康德"]
    
    humanoid_robot:
      weight: 0.20
      keywords: ["人形机器�?, "伺服电机", "减速器"]
      target_stocks: ["三花智控", "汇川技�?, "绿的谐波"]
    
    new_energy:
      weight: 0.20
      keywords: ["新能�?, "光伏", "储能"]
      target_stocks: ["宁德时代", "隆基绿能", "比亚�?]
  
  fundamental_criteria:
    roe_min: 0.12
    revenue_growth_min: 0.15
    profit_growth_min: 0.20
    debt_ratio_max: 0.60
  
  position_management:
    target_position: 0.8640
    min_position: 0.70
    max_position: 0.95
    rebalance_frequency: "quarterly"
  
  institutional_coordination:
    coordination_threshold: 0.60
    peer_holding_weight: 0.30
  
  holding_period:
    min_days: 30
    avg_days: 90
    max_days: 365
  
  reward_function:
    alpha_return_weight: 0.50
    benchmark_beat_weight: 0.30
    risk_adjusted_return_weight: 0.20
  
  risk_control:
    max_single_stock: 0.10
    max_sector: 0.30
    stop_loss_threshold: -0.15
    max_drawdown: -0.20
```

### 3.3 外资智能体（Foreign Capital Agent�?
**代号**：AGENT.FOREIGN_CAPITAL.001

**行为特征**�?- 价值投资，板块轮动
- 聪明钱效应，长期配置
- 放弃传统核心资产，转向高成长制�?
**参数配置**�?
```yaml
foreign_capital_agent:
  name: "外资智能�?
  type: "institutional_investor"
  
  decision_model:
    type: "rl_value_hybrid"
    rl_algorithm: "PPO"
    rl_weight: 0.50
    value_weight: 0.50
  
  value_criteria:
    pe_max: 30
    pb_max: 5
    roe_min: 0.15
    dividend_yield_min: 0.02
  
  sector_rotation:
    growth_manufacturing:
      weight: 0.50
      sectors: ["电子", "基础化工", "电力设备"]
    
    traditional_core:
      weight: 0.20
      sectors: ["食品饮料", "医药"]
    
    scarce_assets:
      weight: 0.30
      sectors: ["中药", "白酒"]
  
  fx_factors:
    usd_cny_weight: 0.30
    dollar_index_weight: 0.20
    risk_premium_weight: 0.20
  
  smart_money_signal:
    consecutive_buy_days: 5
    net_buy_threshold: 60.0
    target_sectors: ["新能�?, "电子"]
    expected_win_rate: 0.80
  
  position_management:
    target_position: 0.85
    min_position: 0.60
    max_position: 0.95
  
  holding_period:
    min_days: 90
    avg_days: 180
    max_days: 730
  
  reward_function:
    long_term_return_weight: 0.50
    value_realization_weight: 0.30
    currency_gain_weight: 0.20
  
  risk_control:
    max_single_stock: 0.08
    max_sector: 0.25
    stop_loss_threshold: -0.20
    fx_hedge_ratio: 0.50
```

### 3.4 量化基金智能体（Quantitative Fund Agent�?
**代号**：AGENT.QUANT_FUND.001

**行为特征**�?- 高频交易，算法驱�?- 分散化，纪律性强
- 持仓时间短至毫秒�?
**参数配置**�?
```yaml
quantitative_fund_agent:
  name: "量化基金智能�?
  type: "institutional_investor"
  
  decision_model:
    type: "high_frequency_algorithm"
    ai_model: "Transformer-LSTM"
    signal_frequency: "millisecond"
  
  trading_strategy:
    type: "multi_strategy"
    strategies:
      - name: "statistical_arbitrage"
        weight: 0.30
        holding_period: "seconds"
      
      - name: "momentum"
        weight: 0.25
        holding_period: "minutes"
      
      - name: "mean_reversion"
        weight: 0.25
        holding_period: "hours"
      
      - name: "market_making"
        weight: 0.20
        holding_period: "milliseconds"
  
  high_frequency_features:
    - "level2_order_book"
    - "tick_by_tick_trade"
    - "order_flow_imbalance"
    - "volume_weighted_price"
  
  position_management:
    max_single_position: 0.02
    max_total_positions: 100
    leverage_ratio: 2.0
  
  execution:
    algorithm: "TWAP_VWAP_hybrid"
    max_slippage: 0.001
    market_impact_limit: 0.002
  
  risk_control:
    stop_loss_pct: -0.02
    take_profit_pct: 0.03
    max_drawdown: -0.05
    var_limit: 0.01
  
  reward_function:
    sharpe_ratio_weight: 0.40
    alpha_weight: 0.30
    execution_quality_weight: 0.30
  
  infrastructure:
    colocation: true
    latency_requirement: "microsecond"
    data_feed: "level2_realtime"
```

### 3.5 热钱智能体（Hot Money Agent�?
**代号**：AGENT.HOT_MONEY.001

**行为特征**�?- 打板手法，快进快�?- 题材驱动，情绪放�?- 持仓周期短（�?周）

**参数配置**�?
```yaml
hot_money_agent:
  name: "热钱智能�?
  type: "speculator"
  
  decision_model:
    type: "rl_emotion_hybrid"
    rl_algorithm: "DQN"
    rl_weight: 0.60
    emotion_weight: 0.40
  
  limit_up_strategy:
    iron_rules:
      - "no_limit_up_no_buy"
      - "no_volume_surge_no_buy"
      - "no_board_no_stop"
    
    entry_timing:
      - "pre_market_hot_topic"
      - "intraday_breakthrough"
      - "late_afternoon_rally"
    
    exit_strategy:
      - "next_day_sell"
      - "profit_target_5pct"
      - "stop_loss_3pct"
  
  topic_detection:
    hot_keywords:
      - "AI"
      - "人形机器�?
      - "新能�?
      - "并购重组"
    
    sentiment_threshold: 0.70
    volume_surge_threshold: 2.0
  
  position_management:
    max_single_position: 0.20
    max_total_positions: 5
    leverage_ratio: 1.5
  
  holding_period:
    min_days: 1
    avg_days: 3
    max_days: 7
  
  reward_function:
    short_term_profit_weight: 0.60
    win_rate_weight: 0.30
    risk_adjusted_return_weight: 0.10
  
  risk_control:
    stop_loss_threshold: -0.05
    take_profit_threshold: 0.10
    max_consecutive_loss: 3
    position_reduce_after_loss: 0.50
```

### 3.6 保险资金智能体（Insurance Fund Agent�?
**代号**：AGENT.INSURANCE_FUND.001

**行为特征**�?- 长期配置，稳健投�?- 高股息偏好，风险厌恶
- 持仓周期长（年度�?
**参数配置**�?
```yaml
insurance_fund_agent:
  name: "保险资金智能�?
  type: "institutional_investor"
  
  decision_model:
    type: "rule_engine_value_hybrid"
    rule_weight: 0.60
    value_weight: 0.40
  
  investment_criteria:
    dividend_yield_min: 0.03
    pe_max: 20
    pb_max: 2
    roe_min: 0.10
    market_cap_min: 500
  
  sector_preference:
    banking:
      weight: 0.35
      reason: "高股息、低估�?
    
    infrastructure:
      weight: 0.25
      reason: "现金流稳�?
    
    real_estate:
      weight: 0.15
      reason: "长期配置"
    
    utilities:
      weight: 0.15
      reason: "防御性强"
    
    other:
      weight: 0.10
  
  position_management:
    target_position: 0.30
    min_position: 0.20
    max_position: 0.40
    rebalance_frequency: "yearly"
  
  holding_period:
    min_days: 365
    avg_days: 730
    max_days: 1825
  
  reward_function:
    dividend_income_weight: 0.40
    capital_preservation_weight: 0.40
    long_term_return_weight: 0.20
  
  risk_control:
    max_single_stock: 0.05
    max_sector: 0.20
    max_drawdown: -0.10
    liquidity_requirement: 0.30
```

### 3.7 产业资本智能体（Industrial Capital Agent�?
**代号**：AGENT.INDUSTRIAL_CAPITAL.001

**行为特征**�?- 信息优势，战略布局
- 增持回购，价值认�?- 长期持有

**参数配置**�?
```yaml
industrial_capital_agent:
  name: "产业资本智能�?
  type: "institutional_investor"
  
  decision_model:
    type: "rule_engine_strategic_hybrid"
    rule_weight: 0.70
    strategic_weight: 0.30
  
  strategic_focus:
    industry_chain_integration:
      weight: 0.40
      description: "产业链整�?
    
    technology_acquisition:
      weight: 0.30
      description: "技术获�?
    
    market_share_expansion:
      weight: 0.30
      description: "市场份额扩张"
  
  buyback_criteria:
    price_below_book: true
    price_below_intrinsic_value: true
    undervaluation_threshold: 0.30
  
  position_management:
    max_single_position: 0.15
    min_holding_period: 365
  
  holding_period:
    min_days: 365
    avg_days: 1095
    max_days: 3650
  
  reward_function:
    strategic_value_weight: 0.50
    long_term_return_weight: 0.30
    market_share_weight: 0.20
  
  risk_control:
    max_single_stock: 0.15
    related_party_transaction_limit: 0.10
```

### 3.8 零售投资者智能体（Retail Investor Agent�?
**代号**：AGENT.RETAIL.001

**行为特征**�?- 羊群效应，情绪驱�?- 追涨杀跌，短期持有
- 信息劣势

**参数配置**�?
```yaml
retail_investor_agent:
  name: "零售投资者智能体"
  type: "retail_investor"
  
  decision_model:
    type: "behavioral_finance"
    herding_weight: 0.40
    emotion_weight: 0.40
    rational_weight: 0.20
  
  behavioral_biases:
    herding_effect:
      weight: 0.40
      description: "跟随主流资金"
    
    disposition_effect:
      weight: 0.30
      description: "卖出盈利股，持有亏损�?
    
    overconfidence:
      weight: 0.20
      description: "过度自信"
    
    loss_aversion:
      weight: 0.10
      description: "损失厌恶"
  
  emotion_indicators:
    fear_greed_index:
      threshold: 0.70
      impact: "buy_when_greedy"
    
    social_media_sentiment:
      weight: 0.30
      sources: ["雪球", "东方财富股吧"]
  
  position_management:
    max_single_position: 0.30
    avg_position_count: 5
    leverage_ratio: 1.0
  
  holding_period:
    min_days: 1
    avg_days: 14
    max_days: 90
  
  reward_function:
    short_term_profit_weight: 0.50
    following_trend_weight: 0.30
    avoiding_loss_weight: 0.20
  
  risk_control:
    stop_loss_threshold: -0.10
    take_profit_threshold: 0.20
    max_consecutive_loss: 5
```

---

## 📦 四、数据获取模块完整实�?
### 4.1 统一数据获取�?
```python
from dataclasses import dataclass
from datetime import datetime
from typing import List, Dict, Optional
import pandas as pd

@dataclass
class MarketParticipantDataBundle:
    """市场参与者数据包
    
    索引: DATA.BUNDLE.001
    用�? 整合所有市场参与者相关数�?    """
    timestamp: datetime
    
    capital_flow_data: Dict  # DDX/DDE/BBD数据
    dragon_tiger_data: List  # 龙虎榜数�?    northbound_flow_data: Dict  # 北向资金流向
    northbound_holdings: List  # 北向资金持仓
    
    level2_data: Optional[Dict] = None  # Level-2行情
    sentiment_data: Optional[Dict] = None  # 市场情绪
    news_data: Optional[List] = None  # 新闻数据

class MarketParticipantDataFetcher:
    """市场参与者数据统一获取�?    
    索引: IMPLEMENTATION.DATA_FETCHER.001
    职责: 统一获取所有市场参与者相关数�?    数据�? 同花顺iFinD
    """
    
    def __init__(self, config: Dict):
        self.config = config
        
        self.capital_flow_fetcher = IFindCapitalFlowFetcher(config)
        self.dragon_tiger_parser = IFindDragonTigerParser(config)
        self.northbound_monitor = IFindNorthboundCapitalMonitor(config)
    
    def fetch_all_data(self,
                      stock_codes: List[str],
                      start_date: datetime,
                      end_date: datetime) -> MarketParticipantDataBundle:
        """获取所有市场参与者数�?        
        参数:
            stock_codes: 股票代码列表
            start_date: 开始日�?            end_date: 结束日期
            
        返回:
            MarketParticipantDataBundle: 整合数据�?        """
        
        capital_flow_data = self.capital_flow_fetcher.fetch_ddx(
            stock_codes, start_date, end_date
        )
        
        dragon_tiger_data = self.dragon_tiger_parser.fetch_dragon_tiger_list(
            start_date, end_date
        )
        
        northbound_flow_data = self.northbound_monitor.fetch_daily_flow(
            start_date, end_date
        )
        
        northbound_holdings = self.northbound_monitor.fetch_holdings(
            stock_codes=stock_codes
        )
        
        return MarketParticipantDataBundle(
            timestamp=datetime.now(),
            capital_flow_data=capital_flow_data,
            dragon_tiger_data=dragon_tiger_data,
            northbound_flow_data=northbound_flow_data,
            northbound_holdings=northbound_holdings
        )
    
    def fetch_realtime_data(self,
                           stock_codes: List[str]) -> MarketParticipantDataBundle:
        """获取实时数据（盘中）
        
        参数:
            stock_codes: 股票代码列表
            
        返回:
            MarketParticipantDataBundle: 实时数据�?        """
        
        capital_flow_data = self.capital_flow_fetcher.fetch_realtime_capital_flow(
            stock_codes
        )
        
        return MarketParticipantDataBundle(
            timestamp=datetime.now(),
            capital_flow_data=capital_flow_data,
            dragon_tiger_data=[],
            northbound_flow_data={},
            northbound_holdings=[]
        )
```

### 4.2 数据缓存与更新策�?
```python
from datetime import datetime, timedelta
from typing import Dict, Optional
import redis
import json

class DataCacheManager:
    """数据缓存管理�?    
    索引: IMPLEMENTATION.CACHE.001
    职责: 管理市场参与者数据缓�?    缓存介质: Redis
    """
    
    def __init__(self, config: Dict):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.get('redis_host', 'localhost'),
            port=config.get('redis_port', 6379),
            db=config.get('redis_db', 0)
        )
        
        self.cache_ttl = {
            'ddx_daily': 86400,
            'ddx_realtime': 180,
            'dragon_tiger': 86400,
            'northbound_flow': 86400,
            'northbound_holdings': 3600
        }
    
    def get_cached_data(self,
                       data_type: str,
                       key: str) -> Optional[Dict]:
        """获取缓存数据
        
        参数:
            data_type: 数据类型（ddx_daily, ddx_realtime等）
            key: 缓存�?            
        返回:
            Optional[Dict]: 缓存数据，不存在则返回None
        """
        cache_key = f"{data_type}:{key}"
        cached = self.redis_client.get(cache_key)
        
        if cached:
            return json.loads(cached)
        
        return None
    
    def set_cached_data(self,
                       data_type: str,
                       key: str,
                       data: Dict) -> None:
        """设置缓存数据
        
        参数:
            data_type: 数据类型
            key: 缓存�?            data: 数据内容
        """
        cache_key = f"{data_type}:{key}"
        ttl = self.cache_ttl.get(data_type, 3600)
        
        self.redis_client.setex(
            cache_key,
            ttl,
            json.dumps(data, default=str)
        )
    
    def clear_cache(self, data_type: Optional[str] = None) -> None:
        """清除缓存
        
        参数:
            data_type: 数据类型（可选，不指定则清除所有）
        """
        if data_type:
            pattern = f"{data_type}:*"
        else:
            pattern = "*"
        
        keys = self.redis_client.keys(pattern)
        if keys:
            self.redis_client.delete(*keys)
```

---

## 📊 五、集成测试与验证

### 5.1 数据获取接口测试用例

```python
import unittest
from datetime import datetime, timedelta

class TestCapitalFlowDataFetcher(unittest.TestCase):
    """资金流向数据获取器测�?""
    
    def setUp(self):
        self.fetcher = IFindCapitalFlowFetcher(config={})
        self.test_stocks = ['600519.SH', '000858.SZ']
        self.test_date = datetime.now() - timedelta(days=7)
        self.end_date = datetime.now()
    
    def test_fetch_ddx(self):
        """测试DDX数据获取"""
        result = self.fetcher.fetch_ddx(
            self.test_stocks,
            self.test_date,
            self.end_date
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('600519.SH', result)
        
        if result['600519.SH']:
            ddx_indicator = result['600519.SH'][0]
            self.assertIsInstance(ddx_indicator, DDXIndicator)
            self.assertIsNotNone(ddx_indicator.ddx_value)
    
    def test_fetch_dde(self):
        """测试DDE数据获取"""
        result = self.fetcher.fetch_dde(
            self.test_stocks,
            self.test_date,
            self.end_date
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('600519.SH', result)
    
    def test_fetch_bbd(self):
        """测试BBD数据获取"""
        result = self.fetcher.fetch_bbd(
            self.test_stocks,
            self.test_date,
            self.end_date
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('600519.SH', result)
    
    def test_fetch_realtime_capital_flow(self):
        """测试实时资金流向获取"""
        result = self.fetcher.fetch_realtime_capital_flow(
            self.test_stocks
        )
        
        self.assertIsInstance(result, dict)
        self.assertIn('600519.SH', result)

class TestNorthboundCapitalMonitor(unittest.TestCase):
    """北向资金监控器测�?""
    
    def setUp(self):
        self.monitor = IFindNorthboundCapitalMonitor(config={})
        self.test_date = datetime.now() - timedelta(days=30)
        self.end_date = datetime.now()
    
    def test_fetch_daily_flow(self):
        """测试日度流向获取"""
        result = self.monitor.fetch_daily_flow(
            self.test_date,
            self.end_date
        )
        
        self.assertIsInstance(result, list)
        if result:
            flow = result[0]
            self.assertIsInstance(flow, NorthboundCapitalFlow)
            self.assertIsNotNone(flow.total_net_buy)
    
    def test_detect_smart_money_signal(self):
        """测试聪明钱信号检�?""
        flow_data = self.monitor.fetch_daily_flow(
            self.test_date,
            self.end_date
        )
        
        signal = self.monitor.detect_smart_money_signal(flow_data)
        
        self.assertIsInstance(signal, dict)
        self.assertIn('signal_type', signal)
        self.assertIn('confidence', signal)
```

---

## 📝 六、更新日�?
| 版本 | 日期 | 更新内容 | 作�?|
|------|------|----------|------|
| v2.0 | 2026-04-03 | 术语标准化、资金流向监控接口、智能体参数配置、数据获取模�?| Spec-Approver |

---

**版本**: v2.0 | **更新**: 2026-04-03 | **状�?*: �?已完�?