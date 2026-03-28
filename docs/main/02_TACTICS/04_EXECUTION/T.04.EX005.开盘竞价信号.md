# T.04.EX005.开盘竞价信号

> 开盘竞价信号识别与量化
>
> **策略编号**：T.04.EX005
> **所属模块**：04_EXECUTION
> **文档类型**：执行信号
> **优先级**：P1
>
> **配套文档**：
> - [T.04.EX004.盘前计划与买入模式.md](./T.04.EX004.盘前计划与买入模式.md) - 盘前计划校准
> - [T.04.EX006.A股交易规则.md](./T.04.EX006.A股交易规则.md) - A股交易规则

---

## 1. 竞价信号数据模型

```python
import pandas as pd
import numpy as np
from datetime import datetime, time
from dataclasses import dataclass
from typing import Optional, List, Dict


@dataclass
class AuctionSignal:
    """
    竞价信号数据结构
    """
    stock_code: str
    stock_name: str
    auction_time: datetime

    pre_close: float
    auction_open: float
    auction_high: float
    auction_low: float

    auction_volume: float
    auction_amount: float

    change_pct: float
    volume_ratio: float

    buy_queue_depth: int
    sell_queue_depth: int

    sector_change: float
    market_change: float

    signal_type: str = None
    confidence: float = None
    action: str = None


class AuctionDataParser:
    """
    竞价数据解析器
    从东方财富/同花顺等数据源解析竞价数据
    """

    AUCTION_START_TIME = time(9, 15)
    AUCTION_END_TIME = time(9, 25)
    AUCTION_FINAL_TIME = time(9, 20)

    def __init__(self):
        self.auction_cache = {}

    def parse_auction_data(self, raw_data: dict) -> AuctionSignal:
        """
        解析原始竞价数据

        参数:
            raw_data: 原始数据字典

        返回:
            AuctionSignal: 竞价信号对象
        """
        pre_close = raw_data.get('昨收', raw_data.get('pre_close'))
        auction_open = raw_data.get('开盘价', raw_data.get('open'))

        change_pct = (auction_open - pre_close) / pre_close * 100 if pre_close > 0 else 0

        auction_volume = raw_data.get('成交量', raw_data.get('volume', 0))
        avg_volume = raw_data.get('均量', raw_data.get('avg_volume', 1))
        volume_ratio = auction_volume / avg_volume if avg_volume > 0 else 0

        return AuctionSignal(
            stock_code=raw_data.get('代码', raw_data.get('code')),
            stock_name=raw_data.get('名称', raw_data.get('name')),
            auction_time=raw_data.get('时间', raw_data.get('time')),
            pre_close=pre_close,
            auction_open=auction_open,
            auction_high=raw_data.get('最高', raw_data.get('high')),
            auction_low=raw_data.get('最低', raw_data.get('low')),
            auction_volume=auction_volume,
            auction_amount=raw_data.get('成交额', raw_data.get('amount')),
            change_pct=change_pct,
            volume_ratio=volume_ratio,
            buy_queue_depth=raw_data.get('买一量', 0) + raw_data.get('买二量', 0) + raw_data.get('买三量', 0),
            sell_queue_depth=raw_data.get('卖一量', 0) + raw_data.get('卖二量', 0) + raw_data.get('卖三量', 0),
            sector_change=raw_data.get('板块涨幅', 0),
            market_change=raw_data.get('大盘涨幅', 0)
        )

    def detect_auction_phase(self, auction_time: datetime) -> str:
        """
        检测竞价所处阶段

        参数:
            auction_time: 竞价时间

        返回:
            phase: '早期试探'/'中期确认'/'尾盘决策'
        """
        t = auction_time.time()

        if t < time(9, 18):
            return '早期试探'
        elif t < time(9, 23):
            return '中期确认'
        else:
            return '尾盘决策'

    def is_final_auction(self, auction_time: datetime) -> bool:
        """
        判断是否为最终竞价阶段
        """
        return auction_time.time() >= self.AUCTION_FINAL_TIME
```

---

## 2. 竞价信号识别引擎

```python
class AuctionSignalRecognizer:
    """
    竞价信号识别引擎

    识别类型:
    - 强势信号: 跳空高开/放量拉升
    - 弱势信号: 跳空低开/缩量下跌
    - 中性信号: 平开/小幅波动
    - 异常信号: 涨停/跌停/停牌
    """

    def __init__(self):
        self.signal_thresholds = {
            'strong_up': 3.0,
            'strong_down': -3.0,
            'moderate_up': 1.5,
            'moderate_down': -1.5,
            'volume_surge': 2.0,
            'volume_shrink': 0.5,
            'queue_imbalance': 0.7,
        }

    def recognize_signal(self, auction: AuctionSignal,
                        historical_data: pd.DataFrame = None) -> AuctionSignal:
        """
        识别竞价信号类型

        参数:
            auction: 竞价信号
            historical_data: 历史竞价数据(可选)

        返回:
            AuctionSignal: 带信号类型和置信度
        """
        signals = []

        signals.append(self._check_limit_up(auction))
        signals.append(self._check_limit_down(auction))
        signals.append(self._check_gap_open(auction))
        signals.append(self._check_volume_surge(auction))
        signals.append(self._check_queue_imbalance(auction))
        signals.append(self._check_sector_alignment(auction))

        valid_signals = [s for s in signals if s is not None]

        if valid_signals:
            primary_signal = max(valid_signals, key=lambda x: x['confidence'])
            auction.signal_type = primary_signal['type']
            auction.confidence = primary_signal['confidence']
            auction.action = primary_signal['action']
        else:
            auction.signal_type = '中性'
            auction.confidence = 0.5
            auction.action = '观望'

        return auction

    def _check_limit_up(self, auction: AuctionSignal) -> Optional[dict]:
        """
        检查涨停信号
        """
        if auction.change_pct >= 9.8:
            return {
                'type': '涨停',
                'confidence': 0.95,
                'action': '排队排板/撤单买入'
            }
        return None

    def _check_limit_down(self, auction: AuctionSignal) -> Optional[dict]:
        """
        检查跌停信号
        """
        if auction.change_pct <= -9.8:
            return {
                'type': '跌停',
                'confidence': 0.95,
                'action': '禁止买入/持有观察'
            }
        return None

    def _check_gap_open(self, auction: AuctionSignal) -> Optional[dict]:
        """
        检查跳空缺口
        """
        thresholds = self.signal_thresholds

        if auction.change_pct >= thresholds['strong_up']:
            return {
                'type': '强势跳空高开',
                'confidence': 0.8,
                'action': '回调买入/确认强势后介入'
            }
        elif auction.change_pct <= thresholds['strong_down']:
            return {
                'type': '弱势跳空低开',
                'confidence': 0.8,
                'action': '观望/不抄底'
            }
        elif auction.change_pct >= thresholds['moderate_up']:
            return {
                'type': '小幅高开',
                'confidence': 0.6,
                'action': '观察量能/突破确认'
            }
        elif auction.change_pct <= thresholds['moderate_down']:
            return {
                'type': '小幅低开',
                'confidence': 0.6,
                'action': '等待企稳'
            }
        return None

    def _check_volume_surge(self, auction: AuctionSignal) -> Optional[dict]:
        """
        检查竞价量能异动
        """
        if auction.volume_ratio >= self.signal_thresholds['volume_surge']:
            return {
                'type': '竞价放量',
                'confidence': 0.7,
                'action': '关注方向/顺势操作'
            }
        elif auction.volume_ratio <= self.signal_thresholds['volume_shrink']:
            return {
                'type': '竞价缩量',
                'confidence': 0.6,
                'action': '方向不明/谨慎操作'
            }
        return None

    def _check_queue_imbalance(self, auction: AuctionSignal) -> Optional[dict]:
        """
        检查买卖队列失衡
        """
        total_queue = auction.buy_queue_depth + auction.sell_queue_depth
        if total_queue == 0:
            return None

        buy_ratio = auction.buy_queue_depth / total_queue
        sell_ratio = auction.sell_queue_depth / total_queue

        if buy_ratio >= self.signal_thresholds['queue_imbalance']:
            return {
                'type': '买盘强势',
                'confidence': 0.65,
                'action': '积极看多'
            }
        elif sell_ratio >= self.signal_thresholds['queue_imbalance']:
            return {
                'type': '卖盘强势',
                'confidence': 0.65,
                'action': '谨慎观望'
            }
        return None

    def _check_sector_alignment(self, auction: AuctionSignal) -> Optional[dict]:
        """
        检查板块共振
        """
        if auction.change_pct > 0 and auction.sector_change > 2:
            return {
                'type': '板块共振上涨',
                'confidence': 0.75,
                'action': '积极做多'
            }
        elif auction.change_pct < 0 and auction.sector_change < -2:
            return {
                'type': '板块共振下跌',
                'confidence': 0.75,
                'action': '规避风险'
            }
        return None
```

---

## 3. 竞价策略执行器

```python
class AuctionExecutionStrategy:
    """
    竞价策略执行器

    根据竞价信号生成具体操作指令
    """

    def __init__(self, recognizer: AuctionSignalRecognizer):
        self.recognizer = recognizer

    def generate_execution_plan(self, auction: AuctionSignal) -> dict:
        """
        生成执行计划

        参数:
            auction: 竞价信号

        返回:
            execution_plan: 执行计划字典
        """
        auction = self.recognizer.recognize_signal(auction)

        strategies = {
            '涨停': self._handle_limit_up,
            '跌停': self._handle_limit_down,
            '强势跳空高开': self._handle_strong_gap_up,
            '弱势跳空低开': self._handle_strong_gap_down,
            '小幅高开': self._handle_moderate_gap_up,
            '小幅低开': self._handle_moderate_gap_down,
            '竞价放量': self._handle_volume_surge,
            '竞价缩量': self._handle_volume_shrink,
            '买盘强势': self._handle_buy_pressure,
            '卖盘强势': self._handle_sell_pressure,
            '板块共振上涨': self._handle_sector_rally,
            '板块共振下跌': self._handle_sector_sell,
            '中性': self._handle_neutral,
        }

        handler = strategies.get(auction.signal_type, self._handle_neutral)
        return handler(auction)

    def _handle_limit_up(self, auction: AuctionSignal) -> dict:
        """
        涨停处理策略
        """
        return {
            'action': '排板买入',
            'entry_type': '涨停板排队',
            'target_position': 0.10,
            'max_price': auction.auction_open * 1.01,
            'stop_loss': None,
            'risk_level': '极高',
            'notes': [
                '涨停板排队买入',
                '仓位控制在10%以内',
                '关注盘中炸板风险'
            ]
        }

    def _handle_limit_down(self, auction: AuctionSignal) -> dict:
        """
        跌停处理策略
        """
        return {
            'action': '禁止买入',
            'entry_type': '观望',
            'target_position': 0,
            'stop_loss': None,
            'risk_level': '极高',
            'notes': [
                '不抄底跌停',
                '持仓设置止损',
                '等待跌停打开'
            ]
        }

    def _handle_strong_gap_up(self, auction: AuctionSignal) -> dict:
        """
        强势跳空高开处理
        """
        if auction.volume_ratio >= 1.5:
            return {
                'action': '回调买入',
                'entry_type': '首板回调/二波启动',
                'target_position': 0.15,
                'entry_range': (auction.pre_close, auction.auction_open * 0.995),
                'stop_loss': auction.pre_close * 0.97,
                'risk_level': '高',
                'notes': [
                    '高开5%以上不追',
                    '回踩不破昨日收盘价可买',
                    '量能是关键'
                ]
            }
        else:
            return {
                'action': '谨慎观望',
                'entry_type': '观望',
                'target_position': 0.05,
                'stop_loss': auction.auction_open * 0.98,
                'risk_level': '中',
                'notes': [
                    '缩量高开需谨慎',
                    '等待开盘后量能确认'
                ]
            }

    def _handle_strong_gap_down(self, auction: AuctionSignal) -> dict:
        """
        弱势跳空低开处理
        """
        return {
            'action': '禁止买入',
            'entry_type': '观望',
            'target_position': 0,
            'stop_loss': None,
            'risk_level': '高',
            'notes': [
                '低开不抄底',
                '等待市场企稳',
                '不接下跌中的飞刀'
            ]
        }

    def _handle_moderate_gap_up(self, auction: AuctionSignal) -> dict:
        """
        小幅高开处理
        """
        if auction.sector_change > 0:
            return {
                'action': '积极关注',
                'entry_type': '突破确认买入',
                'target_position': 0.10,
                'entry_condition': '开盘后突破今日高点',
                'stop_loss': auction.auction_open * 0.98,
                'risk_level': '中',
                'notes': [
                    '跟随板块共振',
                    '突破确认再买入'
                ]
            }
        else:
            return {
                'action': '谨慎观望',
                'entry_type': '观望',
                'target_position': 0.05,
                'stop_loss': auction.auction_open * 0.98,
                'risk_level': '中低',
                'notes': [
                    '无板块共振需谨慎',
                    '等待方向明确'
                ]
            }

    def _handle_moderate_gap_down(self, auction: AuctionSignal) -> dict:
        """
        小幅低开处理
        """
        return {
            'action': '等待观望',
            'entry_type': '观望',
            'target_position': 0,
            'stop_loss': None,
            'risk_level': '中',
            'notes': [
                '等待开盘后方向确认',
                '不盲目抄底'
            ]
        }

    def _handle_volume_surge(self, auction: AuctionSignal) -> dict:
        """
        竞价放量处理
        """
        if auction.change_pct > 0:
            return {
                'action': '积极关注',
                'entry_type': '放量上涨',
                'target_position': 0.15,
                'stop_loss': auction.pre_close * 0.98,
                'risk_level': '中',
                'notes': ['量价齐升是健康形态']
            }
        else:
            return {
                'action': '谨慎观望',
                'entry_type': '放量下跌',
                'target_position': 0,
                'stop_loss': None,
                'risk_level': '高',
                'notes': ['放量下跌需警惕']
            }

    def _handle_volume_shrink(self, auction: AuctionSignal) -> dict:
        """
        竞价缩量处理
        """
        return {
            'action': '方向不明',
            'entry_type': '观望',
            'target_position': 0.05,
            'stop_loss': auction.auction_open * 0.98,
            'risk_level': '中',
            'notes': [
                '缩量方向不明',
                '等待盘中量能信号'
            ]
        }

    def _handle_buy_pressure(self, auction: AuctionSignal) -> dict:
        """
        买盘强势处理
        """
        return {
            'action': '积极看多',
            'entry_type': '买盘主导',
            'target_position': 0.10,
            'stop_loss': auction.auction_open * 0.98,
            'risk_level': '中低',
            'notes': ['买盘占优，可积极关注']
        }

    def _handle_sell_pressure(self, auction: AuctionSignal) -> dict:
        """
        卖盘强势处理
        """
        return {
            'action': '谨慎观望',
            'entry_type': '卖盘主导',
            'target_position': 0,
            'stop_loss': None,
            'risk_level': '中',
            'notes': ['卖盘主导，等待企稳']
        }

    def _handle_sector_rally(self, auction: AuctionSignal) -> dict:
        """
        板块共振上涨处理
        """
        return {
            'action': '积极做多',
            'entry_type': '板块龙头',
            'target_position': 0.20,
            'stop_loss': auction.pre_close * 0.97,
            'risk_level': '中低',
            'notes': [
                '板块共振，最强形态',
                '可适当提高仓位'
            ]
        }

    def _handle_sector_sell(self, auction: AuctionSignal) -> dict:
        """
        板块共振下跌处理
        """
        return {
            'action': '规避风险',
            'entry_type': '空仓观望',
            'target_position': 0,
            'stop_loss': None,
            'risk_level': '极高',
            'notes': [
                '系统风险，避免买入',
                '持仓需严格止损'
            ]
        }

    def _handle_neutral(self, auction: AuctionSignal) -> dict:
        """
        中性信号处理
        """
        return {
            'action': '观望等待',
            'entry_type': '等待信号',
            'target_position': 0.05,
            'stop_loss': auction.auction_open * 0.98,
            'risk_level': '中',
            'notes': ['平开无明显信号，等待盘中机会']
        }
```

---

## 4. 竞价信号评分模型

```python
class AuctionSignalScorer:
    """
    竞价信号综合评分

    评分维度:
    1. 价格维度 (40%): 涨跌幅、跳空幅度
    2. 量能维度 (30%): 竞价量、量比
    3. 资金维度 (20%): 买卖队列、资金流向
    4. 市场维度 (10%): 板块共振、大盘配合
    """

    def __init__(self):
        self.weights = {
            'price': 0.40,
            'volume': 0.30,
            'fund': 0.20,
            'market': 0.10
        }

    def calculate_score(self, auction: AuctionSignal) -> dict:
        """
        计算综合评分

        返回:
            score_result: 包含总分和各维度得分
        """
        price_score = self._calc_price_score(auction)
        volume_score = self._calc_volume_score(auction)
        fund_score = self._calc_fund_score(auction)
        market_score = self._calc_market_score(auction)

        total_score = (
            price_score * self.weights['price'] +
            volume_score * self.weights['volume'] +
            fund_score * self.weights['fund'] +
            market_score * self.weights['market']
        )

        return {
            'total_score': round(total_score, 2),
            'price_score': round(price_score, 2),
            'volume_score': round(volume_score, 2),
            'fund_score': round(fund_score, 2),
            'market_score': round(market_score, 2),
            'rating': self._get_rating(total_score),
            'recommendation': self._get_recommendation(total_score)
        }

    def _calc_price_score(self, auction: AuctionSignal) -> float:
        """
        计算价格维度得分 (0-100)
        """
        change = auction.change_pct

        if change >= 9.8:
            return 100
        elif change >= 5:
            return 85
        elif change >= 3:
            return 70
        elif change >= 1:
            return 55
        elif change >= -1:
            return 40
        elif change >= -3:
            return 25
        elif change >= -5:
            return 15
        elif change >= -9.8:
            return 5
        else:
            return 0

    def _calc_volume_score(self, auction: AuctionSignal) -> float:
        """
        计算量能维度得分 (0-100)
        """
        vol_ratio = auction.volume_ratio

        if vol_ratio >= 3:
            return 90
        elif vol_ratio >= 2:
            return 75
        elif vol_ratio >= 1.5:
            return 60
        elif vol_ratio >= 1:
            return 50
        elif vol_ratio >= 0.5:
            return 35
        elif vol_ratio >= 0.2:
            return 20
        else:
            return 10

    def _calc_fund_score(self, auction: AuctionSignal) -> float:
        """
        计算资金维度得分 (0-100)
        """
        total_queue = auction.buy_queue_depth + auction.sell_queue_depth
        if total_queue == 0:
            return 50

        buy_ratio = auction.buy_queue_depth / total_queue

        return buy_ratio * 100

    def _calc_market_score(self, auction: AuctionSignal) -> float:
        """
        计算市场维度得分 (0-100)
        """
        sector = auction.sector_change
        market = auction.market_change

        score = 50
        score += min(max(sector * 10, -30), 30)
        score += min(max(market * 10, -20), 20)

        return max(0, min(100, score))

    def _get_rating(self, score: float) -> str:
        """
        评分转评级
        """
        if score >= 80:
            return 'S级-极具吸引力'
        elif score >= 65:
            return 'A级-积极关注'
        elif score >= 50:
            return 'B级-谨慎关注'
        elif score >= 35:
            return 'C级-观望'
        else:
            return 'D级-规避'

    def _get_recommendation(self, score: float) -> str:
        """
        评分转建议
        """
        if score >= 80:
            return '强烈建议买入，顺势而为'
        elif score >= 65:
            return '建议买入，积极关注'
        elif score >= 50:
            return '谨慎关注，等待确认'
        elif score >= 35:
            return '建议观望，不盲目操作'
        else:
            return '建议规避，控制风险'
```

---

## 5. 使用示例

```python
def example_auction_signals():
    """
    竞价信号识别示例
    """
    parser = AuctionDataParser()
    recognizer = AuctionSignalRecognizer()
    executor = AuctionExecutionStrategy(recognizer)
    scorer = AuctionSignalScorer()

    raw_data = {
        'code': '000001',
        'name': '平安银行',
        'pre_close': 12.50,
        'open': 12.90,
        'high': 12.95,
        'low': 12.85,
        'volume': 1500000,
        'avg_volume': 800000,
        '买一量': 50000,
        '买二量': 30000,
        '买三量': 20000,
        '卖一量': 8000,
        '卖二量': 5000,
        '卖三量': 3000,
        '板块涨幅': 1.5,
        '大盘涨幅': 0.8,
    }

    auction = parser.parse_auction_data(raw_data)

    print(f"股票: {auction.stock_name}")
    print(f"竞价涨幅: {auction.change_pct:.2f}%")
    print(f"量比: {auction.volume_ratio:.2f}")

    auction = recognizer.recognize_signal(auction)
    print(f"信号类型: {auction.signal_type}")
    print(f"置信度: {auction.confidence:.2f}")
    print(f"建议操作: {auction.action}")

    execution_plan = executor.generate_execution_plan(auction)
    print(f"执行计划: {execution_plan['action']}")
    print(f"建议仓位: {execution_plan['target_position']*100:.0f}%")

    score_result = scorer.calculate_score(auction)
    print(f"综合评分: {score_result['total_score']:.2f}")
    print(f"评级: {score_result['rating']}")
    print(f"建议: {score_result['recommendation']}")
```

---

## 6. 信号判定规则汇总

| 信号类型 | 触发条件 | 建议操作 | 仓位上限 |
|----------|----------|----------|----------|
| 涨停 | 涨幅≥9.8% | 排队排板 | 10% |
| 强势高开 | 涨幅≥5%+放量 | 回调买入 | 15% |
| 小幅高开 | 涨幅1-3% | 确认后买入 | 10% |
| 平开 | -1%~1% | 观望 | 5% |
| 小幅低开 | 跌幅1-3% | 等待企稳 | 0% |
| 弱势低开 | 跌幅≥5% | 禁止买入 | 0% |
| 跌停 | 跌幅≥9.8% | 禁止买入 | 0% |
| 板块共振 | 板块涨幅>2%同向 | 积极做多 | 20% |

---

## 更新记录

| 版本 | 日期 | 变更内容 |
|------|------|----------|
| v1.0 | 2026-03-28 | 新建开盘竞价信号文档 |
