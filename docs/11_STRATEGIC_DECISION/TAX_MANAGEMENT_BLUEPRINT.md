---
module_id: TAX_MANAGEMENT_BLUEPRINT
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
responsibility:
  - TAX_MANAGEMENT蓝图设计
---

﻿---
module_id: TAXMANAGEMENTBLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 文档管理员
responsibility:
  - 系统架构蓝图设计与实施指导与实施方案
layer: Layer 11 (战略决策层)
standard_type: 专业量化机构蓝图
applicable_scope: 全系统
compliance_level: 专业标准
---
---


﻿---
module_id: TAX_MANAGEMENT_001
version: 1.0.0
status: Active
created_date: 2026-04-06
last_updated: 2026-04-06
owner: 首席架构师
standard_type: 专业量化机构级蓝图
applicable_scope: Layer 11.17 - 税务管理系统
compliance_level: 专业标准
reference_models: ["Interactive Brokers Tax Tools", "TurboTax", "Bloomberg TAX"]
open_source_solution: "Beancount + 自研简化版"
priority: P2
---

# 税务管理系统蓝图
> **核心职责**: 税务管理系统蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：税务管理系统蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容

> **核心职责**: Tax Management蓝图设计
> **职责边界**: 
> - ✅ 本文档负责：Tax Management蓝图设计相关内容
> - ❌ 本文档不负责：其他模块内容


## 📋 文档职责说明

### 核心职责

本文档是**模块蓝图，负责特定功能的实现**。

### 职责边界

**负责**：
- ✅ 核心功能实现
- ✅ 接口定义
- ✅ 数据模型设计

**不负责**：
- ❌ 其他模块职责
- ❌ 跨模块协调

### 对接模块

**上游模块**：
- 上游模块

**下游模块**：
- 下游模块

---
> **版本**: v1.0
> **创建日期**: 2026-04-06
> **优先级**: 🟢 P2 - 可选增强
> **开源方案**: Beancount, 自研简化版
> **目标**: 构建A股个人投资者税务管理系统，支持税务计算与优化

---

## 📋 执行摘要

### 核心定位

税务管理系统是Layer 11战略决策层的**税务辅助模块**，负责：
- 交易税费计算（印花税、佣金）
- 持仓成本跟踪（批次管理）
- 税务报告生成
- 税务优化建议

### 专业价值

| 价值维度 | 专业机构实践 | 个人实现方式 | 价值评级 |
|---------|-------------|-------------|---------|
| **印花税计算** | 专业税务系统 | 自动化计算 | ⭐⭐⭐⭐ |
| **成本跟踪** | 专业会计系统 | 批次管理 | ⭐⭐⭐ |
| **税务报告** | 专业报告团队 | 自动化报告 | ⭐⭐⭐ |
| **税务优化** | 专业税务顾问 | 简化建议 | ⭐⭐ |

**综合价值评级**: ⭐⭐⭐ (3/5) - **可选实施**

**注意**: A股个人投资者目前免征资本利得税，本系统主要针对印花税和交易成本管理。

---

## 一、架构设计

### 1.1 系统整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│              税务管理系统架构 (Tax Management System)             │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.17.1 税费计算层                            │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 印花税计算器 (Stamp Tax Calculator)                 │  │ │
│  │  │ ├── 卖出印花税（千分之一）                           │  │ │
│  │  │ ├── 印花税累计（年度累计）                           │  │ │
│  │  │ └── 印花税报告（印花税统计报告）                     │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 交易费用计算器 (Trading Fee Calculator)             │  │ │
│  │  │ ├── 佣金费用（券商佣金）                             │  │ │
│  │  │ ├── 过户费（上海过户费）                             │  │ │
│  │  │ ├── 规费（交易所规费）                               │  │ │
│  │  │ └── 总交易成本（综合交易成本）                       │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.17.2 成本管理层                            │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 批次成本管理 (Lot Cost Management)                  │  │ │
│  │  │ ├── 买入批次记录（每次买入独立记录）                 │  │ │
│  │  │ ├── 卖出批次匹配（FIFO/LIFO/HIFO）                   │  │ │
│  │  │ ├── 成本价计算（加权平均成本）                       │  │ │
│  │  │ └── 持仓成本跟踪（实时成本跟踪）                     │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 盈亏计算器 (P&L Calculator)                         │  │ │
│  │  │ ├── 已实现盈亏（卖出盈亏计算）                       │  │ │
│  │  │ ├── 未实现盈亏（持仓浮盈浮亏）                       │  │ │
│  │  │ ├── 盈亏汇总（年度盈亏汇总）                         │  │ │
│  │  │ └── 盈亏报告（盈亏分析报告）                         │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.17.3 税务报告层                           │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 税务报告生成器 (Tax Report Generator)               │  │ │
│  │  │ ├── 月度税务报告（月度税费统计）                     │  │ │
│  │  │ ├── 年度税务报告（年度税费汇总）                     │  │ │
│  │  │ ├── 交易成本报告（交易成本分析）                     │  │ │
│  │  │ └── 盈亏报告（盈亏分析报告）                         │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 税务数据导出 (Tax Data Export)                      │  │ │
│  │  │ ├── Excel导出（Excel格式导出）                       │  │ │
│  │  │ ├── CSV导出（CSV格式导出）                           │  │ │
│  │  │ └── 报表打印（打印格式报表）                         │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              11.17.4 税务优化层                           │ │
│  │  ┌─────────────────────────────────────────────────────┐  │ │
│  │  │ 成本优化建议 (Cost Optimization Suggestion)         │  │ │
│  │  │ ├── 交易成本优化（降低交易成本建议）                 │  │ │
│  │  │ ├── 持仓优化（持仓成本优化建议）                     │  │ │
│  │  │ └── 交易时机建议（交易时机优化建议）                 │  │ │
│  │  └─────────────────────────────────────────────────────┘  │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 二、核心组件详细设计

### 2.1 税费计算层

```python
from typing import Dict, List, Optional
from datetime import datetime, date
from dataclasses import dataclass, field
from enum import Enum
import pandas as pd
import numpy as np

class TaxType(Enum):
    """税费类型"""
    STAMP_TAX = "stamp_tax"       # 印花税
    COMMISSION = "commission"      # 佣金
    TRANSFER_FEE = "transfer_fee"  # 过户费
    EXCHANGE_FEE = "exchange_fee"  # 规费

@dataclass
class TaxConfig:
    """税费配置"""
    stamp_tax_rate: float = 0.001      # 印花税率（千分之一）
    commission_rate: float = 0.0003    # 佣金率（万三）
    min_commission: float = 5.0        # 最低佣金
    transfer_fee_rate: float = 0.00001 # 过户费率（十万分之一）
    exchange_fee_rate: float = 0.00002 # 规费率

@dataclass
class TaxRecord:
    """税费记录"""
    trade_id: str
    trade_date: datetime
    stock_code: str
    trade_type: str  # 'buy', 'sell'
    trade_amount: float
    tax_type: TaxType
    tax_amount: float

class StampTaxCalculator:
    """印花税计算器"""
    
    def __init__(self, config: TaxConfig):
        self.config = config
        self.tax_records: List[TaxRecord] = []
    
    def calculate_stamp_tax(self,
                           trade_amount: float,
                           trade_type: str) -> float:
        """计算印花税"""
        if trade_type == 'sell':
            tax = trade_amount * self.config.stamp_tax_rate
        else:
            tax = 0.0
        
        return tax
    
    def add_trade(self,
                 trade_id: str,
                 trade_date: datetime,
                 stock_code: str,
                 trade_type: str,
                 trade_amount: float):
        """添加交易记录"""
        tax_amount = self.calculate_stamp_tax(trade_amount, trade_type)
        
        if tax_amount > 0:
            record = TaxRecord(
                trade_id=trade_id,
                trade_date=trade_date,
                stock_code=stock_code,
                trade_type=trade_type,
                trade_amount=trade_amount,
                tax_type=TaxType.STAMP_TAX,
                tax_amount=tax_amount
            )
            self.tax_records.append(record)
    
    def get_annual_stamp_tax(self, year: int) -> float:
        """获取年度印花税"""
        return sum(
            r.tax_amount for r in self.tax_records
            if r.trade_date.year == year
        )
    
    def get_stamp_tax_report(self, year: int) -> pd.DataFrame:
        """生成印花税报告"""
        records = [r for r in self.tax_records if r.trade_date.year == year]
        
        return pd.DataFrame([
            {
                'trade_date': r.trade_date,
                'stock_code': r.stock_code,
                'trade_amount': r.trade_amount,
                'stamp_tax': r.tax_amount
            }
            for r in records
        ])

class TradingFeeCalculator:
    """交易费用计算器"""
    
    def __init__(self, config: TaxConfig):
        self.config = config
    
    def calculate_commission(self, trade_amount: float) -> float:
        """计算佣金"""
        commission = trade_amount * self.config.commission_rate
        return max(commission, self.config.min_commission)
    
    def calculate_transfer_fee(self, 
                              trade_amount: float,
                              exchange: str = 'SH') -> float:
        """计算过户费（仅上海）"""
        if exchange == 'SH':
            return trade_amount * self.config.transfer_fee_rate
        return 0.0
    
    def calculate_exchange_fee(self, trade_amount: float) -> float:
        """计算规费"""
        return trade_amount * self.config.exchange_fee_rate
    
    def calculate_total_fee(self,
                           trade_amount: float,
                           trade_type: str,
                           exchange: str = 'SH') -> Dict[str, float]:
        """计算总交易费用"""
        return {
            'commission': self.calculate_commission(trade_amount),
            'transfer_fee': self.calculate_transfer_fee(trade_amount, exchange),
            'exchange_fee': self.calculate_exchange_fee(trade_amount),
            'stamp_tax': trade_amount * self.config.stamp_tax_rate if trade_type == 'sell' else 0
        }
```

### 2.2 成本管理层

```python
@dataclass
class CostLot:
    """成本批次"""
    lot_id: str
    stock_code: str
    buy_date: datetime
    buy_price: float
    quantity: int
    buy_amount: float
    buy_fees: float
    cost_per_share: float
    remaining_quantity: int
    created_at: datetime = field(default_factory=datetime.now)

@dataclass
class RealizedPnL:
    """已实现盈亏"""
    trade_id: str
    stock_code: str
    sell_date: datetime
    sell_quantity: int
    sell_amount: float
    sell_fees: float
    cost_amount: float
    realized_pnl: float
    pnl_pct: float

class LotCostManager:
    """批次成本管理器"""
    
    def __init__(self, fee_calculator: TradingFeeCalculator):
        self.fee_calculator = fee_calculator
        self.lots: Dict[str, List[CostLot]] = {}  # stock_code -> list of lots
        self.realized_pnls: List[RealizedPnL] = []
        self.lot_counter = 0
    
    def add_buy_trade(self,
                     stock_code: str,
                     buy_date: datetime,
                     buy_price: float,
                     quantity: int,
                     exchange: str = 'SH'):
        """添加买入交易"""
        self.lot_counter += 1
        
        buy_amount = buy_price * quantity
        fees = self.fee_calculator.calculate_total_fee(buy_amount, 'buy', exchange)
        total_fees = fees['commission'] + fees['transfer_fee'] + fees['exchange_fee']
        
        cost_per_share = (buy_amount + total_fees) / quantity
        
        lot = CostLot(
            lot_id=f"LOT_{self.lot_counter:06d}",
            stock_code=stock_code,
            buy_date=buy_date,
            buy_price=buy_price,
            quantity=quantity,
            buy_amount=buy_amount,
            buy_fees=total_fees,
            cost_per_share=cost_per_share,
            remaining_quantity=quantity
        )
        
        if stock_code not in self.lots:
            self.lots[stock_code] = []
        self.lots[stock_code].append(lot)
    
    def process_sell_trade(self,
                          stock_code: str,
                          sell_date: datetime,
                          sell_price: float,
                          quantity: int,
                          exchange: str = 'SH',
                          method: str = 'FIFO') -> RealizedPnL:
        """处理卖出交易"""
        if stock_code not in self.lots:
            return None
        
        sell_amount = sell_price * quantity
        fees = self.fee_calculator.calculate_total_fee(sell_amount, 'sell', exchange)
        total_sell_fees = sum(fees.values())
        
        cost_amount = 0
        remaining_to_sell = quantity
        
        lots = self.lots[stock_code]
        if method == 'FIFO':
            lots_to_process = [lot for lot in lots if lot.remaining_quantity > 0]
        elif method == 'LIFO':
            lots_to_process = [lot for lot in lots if lot.remaining_quantity > 0][::-1]
        else:
            lots_to_process = [lot for lot in lots if lot.remaining_quantity > 0]
        
        for lot in lots_to_process:
            if remaining_to_sell <= 0:
                break
            
            sell_from_lot = min(lot.remaining_quantity, remaining_to_sell)
            cost_amount += sell_from_lot * lot.cost_per_share
            lot.remaining_quantity -= sell_from_lot
            remaining_to_sell -= sell_from_lot
        
        net_sell_amount = sell_amount - total_sell_fees
        realized_pnl = net_sell_amount - cost_amount
        pnl_pct = realized_pnl / cost_amount if cost_amount > 0 else 0
        
        self.lot_counter += 1
        pnl_record = RealizedPnL(
            trade_id=f"PNL_{self.lot_counter:06d}",
            stock_code=stock_code,
            sell_date=sell_date,
            sell_quantity=quantity,
            sell_amount=sell_amount,
            sell_fees=total_sell_fees,
            cost_amount=cost_amount,
            realized_pnl=realized_pnl,
            pnl_pct=pnl_pct
        )
        
        self.realized_pnls.append(pnl_record)
        return pnl_record
    
    def get_current_cost(self, stock_code: str) -> Dict:
        """获取当前持仓成本"""
        if stock_code not in self.lots:
            return None
        
        lots = [lot for lot in self.lots[stock_code] if lot.remaining_quantity > 0]
        
        if not lots:
            return None
        
        total_quantity = sum(lot.remaining_quantity for lot in lots)
        total_cost = sum(lot.remaining_quantity * lot.cost_per_share for lot in lots)
        
        return {
            'stock_code': stock_code,
            'total_quantity': total_quantity,
            'total_cost': total_cost,
            'avg_cost_per_share': total_cost / total_quantity if total_quantity > 0 else 0,
            'lots': lots
        }
    
    def get_unrealized_pnl(self,
                          stock_code: str,
                          current_price: float) -> Dict:
        """获取未实现盈亏"""
        cost_info = self.get_current_cost(stock_code)
        
        if not cost_info:
            return None
        
        market_value = cost_info['total_quantity'] * current_price
        unrealized_pnl = market_value - cost_info['total_cost']
        pnl_pct = unrealized_pnl / cost_info['total_cost'] if cost_info['total_cost'] > 0 else 0
        
        return {
            'stock_code': stock_code,
            'total_quantity': cost_info['total_quantity'],
            'total_cost': cost_info['total_cost'],
            'current_price': current_price,
            'market_value': market_value,
            'unrealized_pnl': unrealized_pnl,
            'pnl_pct': pnl_pct
        }
    
    def get_annual_realized_pnl(self, year: int) -> pd.DataFrame:
        """获取年度已实现盈亏"""
        pnls = [p for p in self.realized_pnls if p.sell_date.year == year]
        
        return pd.DataFrame([
            {
                'sell_date': p.sell_date,
                'stock_code': p.stock_code,
                'sell_quantity': p.sell_quantity,
                'sell_amount': p.sell_amount,
                'cost_amount': p.cost_amount,
                'realized_pnl': p.realized_pnl,
                'pnl_pct': p.pnl_pct
            }
            for p in pnls
        ])
```

### 2.3 税务报告层

```python
class TaxReportGenerator:
    """税务报告生成器"""
    
    def __init__(self,
                 stamp_tax_calc: StampTaxCalculator,
                 lot_cost_manager: LotCostManager):
        self.stamp_tax_calc = stamp_tax_calc
        self.lot_cost_manager = lot_cost_manager
    
    def generate_annual_report(self, year: int) -> str:
        """生成年度税务报告"""
        report = f"A股投资年度税务报告 ({year}年)\n"
        report += "=" * 50 + "\n\n"
        
        annual_stamp_tax = self.stamp_tax_calc.get_annual_stamp_tax(year)
        report += f"年度印花税: {annual_stamp_tax:,.2f}\n\n"
        
        pnl_df = self.lot_cost_manager.get_annual_realized_pnl(year)
        
        if not pnl_df.empty:
            total_realized_pnl = pnl_df['realized_pnl'].sum()
            winning_trades = len(pnl_df[pnl_df['realized_pnl'] > 0])
            total_trades = len(pnl_df)
            
            report += "已实现盈亏统计:\n"
            report += f"  总已实现盈亏: {total_realized_pnl:,.2f}\n"
            report += f"  盈利交易次数: {winning_trades}/{total_trades}\n"
            report += f"  胜率: {winning_trades/total_trades:.1%}\n\n"
        
        report += "注意事项:\n"
        report += "  1. A股个人投资者目前免征资本利得税\n"
        report += "  2. 印花税仅在卖出时收取（千分之一）\n"
        report += "  3. 本报告仅供参考，不构成税务建议\n"
        
        return report
    
    def export_to_excel(self, year: int, file_path: str):
        """导出到Excel"""
        with pd.ExcelWriter(file_path, engine='openpyxl') as writer:
            stamp_tax_df = self.stamp_tax_calc.get_stamp_tax_report(year)
            if not stamp_tax_df.empty:
                stamp_tax_df.to_excel(writer, sheet_name='印花税明细', index=False)
            
            pnl_df = self.lot_cost_manager.get_annual_realized_pnl(year)
            if not pnl_df.empty:
                pnl_df.to_excel(writer, sheet_name='已实现盈亏', index=False)
```

---

## 三、A股税务说明

### 3.1 A股个人投资者税费

| 税费类型 | 买入 | 卖出 | 税率 |
|---------|------|------|------|
| **印花税** | 无 | 有 | 0.1% |
| **佣金** | 有 | 有 | 约0.03%（最低5元） |
| **过户费** | 有（仅沪市） | 有（仅沪市） | 0.001% |
| **资本利得税** | 无 | 无 | 免征 |

### 3.2 重要提示

1. **资本利得税免征**: A股个人投资者目前免征资本利得税
2. **印花税单向收取**: 仅在卖出时收取
3. **分红税**: 持股超过1年免征，不足1年按持股时间阶梯征收

---

## 四、实施路径

### Phase 1: 核心功能（3天）

| 任务 | 预计时间 | 交付物 |
|------|---------|--------|
| 印花税计算器 | 1天 | StampTaxCalculator |
| 交易费用计算器 | 1天 | TradingFeeCalculator |
| 批次成本管理 | 1天 | LotCostManager |

### Phase 2: 报告功能（2天）

| 任务 | 预计时间 | 交付物 |
|------|---------|--------|
| 税务报告生成 | 1天 | TaxReportGenerator |
| 数据导出 | 1天 | Excel/CSV导出 |

---

## 五、相关文档

| 文档 | 说明 |
|------|------|
| BLUEPRINT.md | Layer 11主蓝图 |
| [TCA_BLUEPRINT.md](./TCA_BLUEPRINT.md) | 交易成本分析系统 |

---

**版本**: v1.0 | **更新**: 2026-04-06 | **状态**: ✅ 活跃
---

## 1. 文档治理

### 1.1 System_Manifest.md索引

```markdown
#### Layer 0: 系统架构
##### 0.001. Tax Management
- **模块ID**: TAX_MANAGEMENT_001
- **蓝图文档**: TAX_MANAGEMENT_BLUEPRINT.md
- **技术规格书**: 待创建
- **职责**: Layer 11.17 - 税务管理系统
- **状态**: Active
```

### 1.2 模块职责边界

| 模块 | 职责 | 边界 |
|------|------|------|
| **Tax Management** | Layer 11.17 - 税务管理系统 | **核心模块** |

### 1.3 版本管理

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本创建 | 首席蓝图架构师 |

---

**蓝图版本**: v1.0.0 | **创建日期**: 2026-04-06 | **状态**: Active
