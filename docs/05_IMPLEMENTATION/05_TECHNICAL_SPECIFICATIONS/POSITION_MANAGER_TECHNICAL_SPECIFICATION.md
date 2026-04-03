---
module_id: POSITION_MANAGER_SPEC_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: 首席技术评审官
standard_type: 专业量化机构技术规格书
applicable_scope: Layer 5 策略执行层 | 业务架构: 三级时间框架融合架构
compliance_level: 专业标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# PositionManager持仓管理器模块技术规格书

> 清风量化系统 v5.2 - PositionManager持仓管理器模块详细技术设计
> **模块ID**: `POSITION_MANAGER_001`
> **版本**: v1.0.0
> **状态**: ✅ 正式


## 1. 概述

### 1.1 设计背景与业务目标
- **业务需求**: 系统需要统一的持仓管理器进行持仓计算和管理
- **技术痛点**: 
  - 持仓计算复杂：持仓计算涉及成本、市值、盈亏等多个维度
  - 持仓更新频繁：交易频繁导致持仓更新频繁
  - 持仓查询多样：需要支持多种持仓查询方式
  - 风险控制严格：持仓需要严格的风险控制
- **预期价值**: 
  - 建立统一的持仓计算机制
  - 提供高效的持仓更新机制
  - 支持多种持仓查询方式
  - 实现严格的持仓风险控制

### 1.2 技术定位与架构层归属
- **Layer定位**: Layer 5 - 策略执行层 (符合ARCHITECTURE.md定义)
- **模块类别**: 核心持仓管理模块
- **架构角色**: Layer 5策略执行核心，负责持仓计算和管理

### 1.3 版本信息
| 版本 | 日期 | 作者 | 变更说明 | 状态 |
|------|------|------|----------|------|
| v1.0.0 | 2026-04-02 | 首席技术评审官 | 初始版本 | Active |

---

## 2. 详细架构设计

### 2.1 系统架构图
```
┌─────────────────────────────────────────────────────────────┐
│                    Layer 5: 策略执行层                       │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────────────────────────────────────────────┐  │
│  │        PositionManager (持仓管理器主模块)              │  │
│  │  - 持仓计算                                            │  │
│  │  - 持仓更新                                            │  │
│  │  - 持仓查询                                            │  │
│  │  - 风险控制                                            │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          核心组件                                      │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │PositionCalc │ │PositionUpdt │ │PositionQuery│  │  │
│  │  │持仓计算器    │  │持仓更新器   │  │持仓查询器   │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  │  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐  │  │
│  │  │RiskControl │ │PositionRepo │ │PositionCache│  │  │
│  │  │风险控制器    │  │持仓仓储     │  │持仓缓存     │  │  │
│  │  └─────────────┘  └─────────────┘  └─────────────┘  │  │
│  └──────────────────────────────────────────────────────┘  │
│                           ↓                                  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          数据存储层                                   │  │
│  │  - PostgreSQL (持久化存储)                           │  │
│  │  - Redis (缓存)                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Layer定位详细说明
- **Layer归属**: Layer 5 - 策略执行层
- **职责范围**: 持仓计算、持仓更新、持仓查询、风险控制
- **上下层接口**: 
  - 上层依赖: Layer 5 QMTExecutor (提供交易执行结果)
  - 下层依赖: Layer 6 组合优化层 (提供持仓信息)

### 2.3 模块职责与边界定义
- **核心职责**: 持仓计算、持仓更新、持仓查询、风险控制
- **职责边界**: 
  - ✅ 本模块负责: 持仓计算、持仓更新、持仓查询、风险控制
  - ❌ 本模块不负责: 交易执行、策略决策、数据获取、风险模型
- **接口契约**: 提供统一的Python API接口

### 2.4 依赖关系
| 依赖模块 | 依赖类型 | 接口方式 | 版本要求 | 备注 |
|----------|----------|----------|----------|------|
| psycopg2 | 强依赖 | Python库 | >=2.9 | PostgreSQL驱动 |
| redis | 强依赖 | Python库 | >=4.0 | Redis客户端 |
| decimal | 强依赖 | Python标准库 | >=3.8 | 高精度计算 |

---

## 3. 接口定义

### 3.1 API接口规范

#### 3.1.1 主接口类
```python
from typing import Dict, List, Optional, Any
from datetime import datetime, date
from dataclasses import dataclass
from decimal import Decimal
from enum import Enum
import psycopg2
import redis
import json
import logging


class OrderSide(Enum):
    """订单方向枚举"""
    BUY = "buy"
    SELL = "sell"


@dataclass
class Position:
    """持仓信息"""
    position_id: int
    account_id: int
    stock_code: str
    stock_name: str
    exchange: str
    quantity: int
    available_quantity: int
    frozen_quantity: int
    avg_cost: Decimal
    current_price: Decimal
    market_value: Decimal
    unrealized_pnl: Decimal
    unrealized_pnl_pct: Decimal
    realized_pnl: Decimal
    position_pct: Decimal
    first_buy_date: date
    last_trade_date: date


@dataclass
class PositionSnapshot:
    """持仓快照"""
    snapshot_id: int
    account_id: int
    snapshot_date: date
    total_market_value: Decimal
    total_unrealized_pnl: Decimal
    positions: List[Position]


class PositionRepository:
    """持仓仓储"""
    
    def __init__(self, db_config: Dict[str, Any]):
        self.db_config = db_config
        self.logger = logging.getLogger(__name__)
        self._init_connection()
    
    def _init_connection(self) -> None:
        """初始化数据库连接"""
        self.conn = psycopg2.connect(
            host=self.db_config['host'],
            port=self.db_config['port'],
            database=self.db_config['database'],
            user=self.db_config['user'],
            password=self.db_config['password']
        )
        self.logger.info("Position repository initialized")
    
    def create_position(
        self,
        account_id: int,
        stock_code: str,
        stock_name: str,
        exchange: str,
        quantity: int,
        avg_cost: Decimal
    ) -> Position:
        """创建持仓
        
        参数:
            account_id: 账户ID
            stock_code: 股票代码
            stock_name: 股票名称
            exchange: 交易所
            quantity: 数量
            avg_cost: 平均成本
            
        返回:
            持仓信息
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            INSERT INTO positions (
                account_id, stock_code, stock_name, exchange,
                quantity, available_quantity, frozen_quantity,
                avg_cost, current_price, market_value,
                unrealized_pnl, unrealized_pnl_pct, realized_pnl,
                position_pct, first_buy_date, last_trade_date
            ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
            RETURNING id
        ''', (
            account_id, stock_code, stock_name, exchange,
            quantity, 0, 0, avg_cost, Decimal('0'), Decimal('0'),
            Decimal('0'), Decimal('0'), Decimal('0'),
            Decimal('0'), date.today(), date.today()
        ))
        
        position_id = cursor.fetchone()[0]
        self.conn.commit()
        cursor.close()
        
        return Position(
            position_id=position_id,
            account_id=account_id,
            stock_code=stock_code,
            stock_name=stock_name,
            exchange=exchange,
            quantity=quantity,
            available_quantity=0,
            frozen_quantity=0,
            avg_cost=avg_cost,
            current_price=Decimal('0'),
            market_value=Decimal('0'),
            unrealized_pnl=Decimal('0'),
            unrealized_pnl_pct=Decimal('0'),
            realized_pnl=Decimal('0'),
            position_pct=Decimal('0'),
            first_buy_date=date.today(),
            last_trade_date=date.today()
        )
    
    def find_by_account(
        self,
        account_id: int,
        stock_code: Optional[str] = None
    ) -> List[Position]:
        """查询账户持仓
        
        参数:
            account_id: 账户ID
            stock_code: 股票代码（可选）
            
        返回:
            持仓列表
        """
        cursor = self.conn.cursor()
        
        if stock_code:
            cursor.execute('''
                SELECT id, account_id, stock_code, stock_name, exchange,
                       quantity, available_quantity, frozen_quantity,
                       avg_cost, current_price, market_value,
                       unrealized_pnl, unrealized_pnl_pct, realized_pnl,
                       position_pct, first_buy_date, last_trade_date
                FROM positions
                WHERE account_id = %s AND stock_code = %s
            ''', (account_id, stock_code))
        else:
            cursor.execute('''
                SELECT id, account_id, stock_code, stock_name, exchange,
                       quantity, available_quantity, frozen_quantity,
                       avg_cost, current_price, market_value,
                       unrealized_pnl, unrealized_pnl_pct, realized_pnl,
                       position_pct, first_buy_date, last_trade_date
                FROM positions
                WHERE account_id = %s
            ''', (account_id,))
        
        rows = cursor.fetchall()
        cursor.close()
        
        positions = []
        for row in rows:
            positions.append(Position(
                position_id=row[0],
                account_id=row[1],
                stock_code=row[2],
                stock_name=row[3],
                exchange=row[4],
                quantity=row[5],
                available_quantity=row[6],
                frozen_quantity=row[7],
                avg_cost=row[8],
                current_price=row[9],
                market_value=row[10],
                unrealized_pnl=row[11],
                unrealized_pnl_pct=row[12],
                realized_pnl=row[13],
                position_pct=row[14],
                first_buy_date=row[15],
                last_trade_date=row[16]
            ))
        
        return positions
    
    def update_position(
        self,
        position_id: int,
        quantity: int,
        available_quantity: int,
        frozen_quantity: int,
        avg_cost: Decimal,
        current_price: Decimal,
        market_value: Decimal,
        unrealized_pnl: Decimal,
        unrealized_pnl_pct: Decimal,
        realized_pnl: Decimal,
        position_pct: Decimal
    ) -> bool:
        """更新持仓
        
        参数:
            position_id: 持仓ID
            quantity: 数量
            available_quantity: 可用数量
            frozen_quantity: 冻结数量
            avg_cost: 平均成本
            current_price: 当前价格
            market_value: 市值
            unrealized_pnl: 浮动盈亏
            unrealized_pnl_pct: 浮动盈亏比例
            realized_pnl: 已实现盈亏
            position_pct: 仓位占比
            
        返回:
            是否成功
        """
        cursor = self.conn.cursor()
        
        cursor.execute('''
            UPDATE positions SET
                quantity = %s,
                available_quantity = %s,
                frozen_quantity = %s,
                avg_cost = %s,
                current_price = %s,
                market_value = %s,
                unrealized_pnl = %s,
                unrealized_pnl_pct = %s,
                realized_pnl = %s,
                position_pct = %s,
                last_trade_date = %s
            WHERE id = %s
        ''', (
            quantity, available_quantity, frozen_quantity,
            avg_cost, current_price, market_value,
            unrealized_pnl, unrealized_pnl_pct, realized_pnl,
            position_pct, date.today(), position_id
        ))
        
        self.conn.commit()
        cursor.close()
        
        return True


class PositionCache:
    """持仓缓存"""
    
    def __init__(self, redis_config: Dict[str, Any]):
        self.redis_client = redis.Redis(
            host=redis_config['host'],
            port=redis_config['port'],
            db=redis_config.get('db', 0),
            password=redis_config.get('password'),
            decode_responses=True
        )
        self.logger = logging.getLogger(__name__)
    
    def get_position(
        self,
        account_id: int,
        stock_code: str
    ) -> Optional[Position]:
        """获取持仓缓存
        
        参数:
            account_id: 账户ID
            stock_code: 股票代码
            
        返回:
            持仓信息（如果存在）
        """
        key = f"position:{account_id}:{stock_code}"
        data = self.redis_client.get(key)
        
        if data:
            position_dict = json.loads(data)
            return Position(**position_dict)
        
        return None
    
    def set_position(
        self,
        position: Position,
        ttl: int = 3600
    ) -> None:
        """设置持仓缓存
        
        参数:
            position: 持仓信息
            ttl: 过期时间（秒）
        """
        key = f"position:{position.account_id}:{position.stock_code}"
        
        position_dict = {
            'position_id': position.position_id,
            'account_id': position.account_id,
            'stock_code': position.stock_code,
            'stock_name': position.stock_name,
            'exchange': position.exchange,
            'quantity': position.quantity,
            'available_quantity': position.available_quantity,
            'frozen_quantity': position.frozen_quantity,
            'avg_cost': str(position.avg_cost),
            'current_price': str(position.current_price),
            'market_value': str(position.market_value),
            'unrealized_pnl': str(position.unrealized_pnl),
            'unrealized_pnl_pct': str(position.unrealized_pnl_pct),
            'realized_pnl': str(position.realized_pnl),
            'position_pct': str(position.position_pct),
            'first_buy_date': position.first_buy_date.isoformat(),
            'last_trade_date': position.last_trade_date.isoformat()
        }
        
        self.redis_client.setex(key, ttl, json.dumps(position_dict))
    
    def delete_position(
        self,
        account_id: int,
        stock_code: str
    ) -> None:
        """删除持仓缓存
        
        参数:
            account_id: 账户ID
            stock_code: 股票代码
        """
        key = f"position:{account_id}:{stock_code}"
        self.redis_client.delete(key)


class PositionCalculator:
    """持仓计算器"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def calculate_market_value(
        self,
        quantity: int,
        current_price: Decimal
    ) -> Decimal:
        """计算市值
        
        参数:
            quantity: 数量
            current_price: 当前价格
            
        返回:
            市值
        """
        return Decimal(quantity) * current_price
    
    def calculate_unrealized_pnl(
        self,
        quantity: int,
        avg_cost: Decimal,
        current_price: Decimal
    ) -> Decimal:
        """计算浮动盈亏
        
        参数:
            quantity: 数量
            avg_cost: 平均成本
            current_price: 当前价格
            
        返回:
            浮动盈亏
        """
        return Decimal(quantity) * (current_price - avg_cost)
    
    def calculate_unrealized_pnl_pct(
        self,
        avg_cost: Decimal,
        current_price: Decimal
    ) -> Decimal:
        """计算浮动盈亏比例
        
        参数:
            avg_cost: 平均成本
            current_price: 当前价格
            
        返回:
            浮动盈亏比例
        """
        if avg_cost == Decimal('0'):
            return Decimal('0')
        
        return (current_price - avg_cost) / avg_cost
    
    def calculate_position_pct(
        self,
        market_value: Decimal,
        total_value: Decimal
    ) -> Decimal:
        """计算仓位占比
        
        参数:
            market_value: 市值
            total_value: 总资产
            
        返回:
            仓位占比
        """
        if total_value == Decimal('0'):
            return Decimal('0')
        
        return market_value / total_value


class PositionUpdater:
    """持仓更新器"""
    
    def __init__(
        self,
        repository: PositionRepository,
        cache: PositionCache,
        calculator: PositionCalculator
    ):
        self.repository = repository
        self.cache = cache
        self.calculator = calculator
        self.logger = logging.getLogger(__name__)
    
    def update_position_from_trade(
        self,
        account_id: int,
        stock_code: str,
        side: OrderSide,
        quantity: int,
        price: Decimal,
        total_value: Decimal
    ) -> Position:
        """根据成交更新持仓
        
        参数:
            account_id: 账户ID
            stock_code: 股票代码
            side: 买卖方向
            quantity: 数量
            price: 价格
            total_value: 总资产
            
        返回:
            更新后的持仓
        """
        positions = self.repository.find_by_account(account_id, stock_code)
        
        if side == OrderSide.BUY:
            return self._add_position(
                account_id, stock_code, quantity, price, total_value, positions
            )
        else:
            return self._reduce_position(
                account_id, stock_code, quantity, price, total_value, positions
            )
    
    def _add_position(
        self,
        account_id: int,
        stock_code: str,
        quantity: int,
        price: Decimal,
        total_value: Decimal,
        positions: List[Position]
    ) -> Position:
        """增加持仓
        
        参数:
            account_id: 账户ID
            stock_code: 股票代码
            quantity: 数量
            price: 价格
            total_value: 总资产
            positions: 现有持仓
            
        返回:
            更新后的持仓
        """
        cost = Decimal(quantity) * price
        
        if positions:
            position = positions[0]
            
            new_quantity = position.quantity + quantity
            new_cost = position.avg_cost * position.quantity + cost
            new_avg_cost = new_cost / Decimal(new_quantity)
            
            market_value = self.calculator.calculate_market_value(new_quantity, price)
            unrealized_pnl = self.calculator.calculate_unrealized_pnl(new_quantity, new_avg_cost, price)
            unrealized_pnl_pct = self.calculator.calculate_unrealized_pnl_pct(new_avg_cost, price)
            position_pct = self.calculator.calculate_position_pct(market_value, total_value)
            
            self.repository.update_position(
                position.position_id,
                new_quantity,
                position.available_quantity,
                position.frozen_quantity,
                new_avg_cost,
                price,
                market_value,
                unrealized_pnl,
                unrealized_pnl_pct,
                position.realized_pnl,
                position_pct
            )
            
            updated_position = Position(
                position_id=position.position_id,
                account_id=account_id,
                stock_code=stock_code,
                stock_name=position.stock_name,
                exchange=position.exchange,
                quantity=new_quantity,
                available_quantity=position.available_quantity,
                frozen_quantity=position.frozen_quantity,
                avg_cost=new_avg_cost,
                current_price=price,
                market_value=market_value,
                unrealized_pnl=unrealized_pnl,
                unrealized_pnl_pct=unrealized_pnl_pct,
                realized_pnl=position.realized_pnl,
                position_pct=position_pct,
                first_buy_date=position.first_buy_date,
                last_trade_date=date.today()
            )
            
            self.cache.set_position(updated_position)
            
            return updated_position
        else:
            position = self.repository.create_position(
                account_id, stock_code, stock_code, "SH",
                quantity, price
            )
            
            market_value = self.calculator.calculate_market_value(quantity, price)
            unrealized_pnl = self.calculator.calculate_unrealized_pnl(quantity, price, price)
            unrealized_pnl_pct = self.calculator.calculate_unrealized_pnl_pct(price, price)
            position_pct = self.calculator.calculate_position_pct(market_value, total_value)
            
            self.repository.update_position(
                position.position_id,
                quantity,
                0,
                0,
                price,
                price,
                market_value,
                unrealized_pnl,
                unrealized_pnl_pct,
                Decimal('0'),
                position_pct
            )
            
            updated_position = Position(
                position_id=position.position_id,
                account_id=account_id,
                stock_code=stock_code,
                stock_name=stock_code,
                exchange="SH",
                quantity=quantity,
                available_quantity=0,
                frozen_quantity=0,
                avg_cost=price,
                current_price=price,
                market_value=market_value,
                unrealized_pnl=unrealized_pnl,
                unrealized_pnl_pct=unrealized_pnl_pct,
                realized_pnl=Decimal('0'),
                position_pct=position_pct,
                first_buy_date=date.today(),
                last_trade_date=date.today()
            )
            
            self.cache.set_position(updated_position)
            
            return updated_position
    
    def _reduce_position(
        self,
        account_id: int,
        stock_code: str,
        quantity: int,
        price: Decimal,
        total_value: Decimal,
        positions: List[Position]
    ) -> Position:
        """减少持仓
        
        参数:
            account_id: 账户ID
            stock_code: 股票代码
            quantity: 数量
            price: 价格
            total_value: 总资产
            positions: 现有持仓
            
        返回:
            更新后的持仓
        """
        if not positions:
            raise ValueError(f"No position found for {stock_code}")
        
        position = positions[0]
        
        if quantity > position.quantity:
            raise ValueError(f"Insufficient position: {position.quantity} < {quantity}")
        
        new_quantity = position.quantity - quantity
        
        realized_pnl = Decimal(quantity) * (price - position.avg_cost)
        total_realized_pnl = position.realized_pnl + realized_pnl
        
        market_value = self.calculator.calculate_market_value(new_quantity, price)
        unrealized_pnl = self.calculator.calculate_unrealized_pnl(new_quantity, position.avg_cost, price)
        unrealized_pnl_pct = self.calculator.calculate_unrealized_pnl_pct(position.avg_cost, price)
        position_pct = self.calculator.calculate_position_pct(market_value, total_value)
        
        self.repository.update_position(
            position.position_id,
            new_quantity,
            position.available_quantity,
            position.frozen_quantity,
            position.avg_cost,
            price,
            market_value,
            unrealized_pnl,
            unrealized_pnl_pct,
            total_realized_pnl,
            position_pct
        )
        
        updated_position = Position(
            position_id=position.position_id,
            account_id=account_id,
            stock_code=stock_code,
            stock_name=position.stock_name,
            exchange=position.exchange,
            quantity=new_quantity,
            available_quantity=position.available_quantity,
            frozen_quantity=position.frozen_quantity,
            avg_cost=position.avg_cost,
            current_price=price,
            market_value=market_value,
            unrealized_pnl=unrealized_pnl,
            unrealized_pnl_pct=unrealized_pnl_pct,
            realized_pnl=total_realized_pnl,
            position_pct=position_pct,
            first_buy_date=position.first_buy_date,
            last_trade_date=date.today()
        )
        
        self.cache.set_position(updated_position)
        
        return updated_position


class PositionQuery:
    """持仓查询器"""
    
    def __init__(
        self,
        repository: PositionRepository,
        cache: PositionCache
    ):
        self.repository = repository
        self.cache = cache
        self.logger = logging.getLogger(__name__)
    
    def get_position(
        self,
        account_id: int,
        stock_code: str
    ) -> Optional[Position]:
        """获取持仓
        
        参数:
            account_id: 账户ID
            stock_code: 股票代码
            
        返回:
            持仓信息（如果存在）
        """
        position = self.cache.get_position(account_id, stock_code)
        
        if position:
            return position
        
        positions = self.repository.find_by_account(account_id, stock_code)
        
        if positions:
            position = positions[0]
            self.cache.set_position(position)
            return position
        
        return None
    
    def get_all_positions(
        self,
        account_id: int
    ) -> List[Position]:
        """获取所有持仓
        
        参数:
            account_id: 账户ID
            
        返回:
            持仓列表
        """
        return self.repository.find_by_account(account_id)


class RiskController:
    """风险控制器"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
    
    def check_position_limit(
        self,
        position: Position,
        max_position_pct: Decimal
    ) -> bool:
        """检查持仓上限
        
        参数:
            position: 持仓信息
            max_position_pct: 最大持仓比例
            
        返回:
            是否通过
        """
        return position.position_pct <= max_position_pct
    
    def get_position_limit(
        self,
        total_value: Decimal,
        current_price: Decimal,
        max_position_pct: Decimal,
        current_quantity: int = 0
    ) -> int:
        """获取持仓上限
        
        参数:
            total_value: 总资产
            current_price: 当前价格
            max_position_pct: 最大持仓比例
            current_quantity: 当前持仓数量
            
        返回:
            最大可买入数量
        """
        if current_price == Decimal('0'):
            return 0
        
        max_total_quantity = int(total_value * max_position_pct / current_price)
        
        return max(0, max_total_quantity - current_quantity)


class PositionManager:
    """持仓管理器主类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        
        self.repository = PositionRepository(config['db_config'])
        self.cache = PositionCache(config['redis_config'])
        self.calculator = PositionCalculator()
        self.updater = PositionUpdater(self.repository, self.cache, self.calculator)
        self.query = PositionQuery(self.repository, self.cache)
        self.risk_controller = RiskController(config.get('risk_config', {}))
        
        self.logger = logging.getLogger(__name__)
    
    def update_position(
        self,
        account_id: int,
        stock_code: str,
        side: OrderSide,
        quantity: int,
        price: Decimal,
        total_value: Decimal
    ) -> Position:
        """更新持仓
        
        参数:
            account_id: 账户ID
            stock_code: 股票代码
            side: 买卖方向
            quantity: 数量
            price: 价格
            total_value: 总资产
            
        返回:
            更新后的持仓
        """
        return self.updater.update_position_from_trade(
            account_id, stock_code, side, quantity, price, total_value
        )
    
    def get_position(
        self,
        account_id: int,
        stock_code: str
    ) -> Optional[Position]:
        """获取持仓
        
        参数:
            account_id: 账户ID
            stock_code: 股票代码
            
        返回:
            持仓信息（如果存在）
        """
        return self.query.get_position(account_id, stock_code)
    
    def get_all_positions(
        self,
        account_id: int
    ) -> List[Position]:
        """获取所有持仓
        
        参数:
            account_id: 账户ID
            
        返回:
            持仓列表
        """
        return self.query.get_all_positions(account_id)
    
    def check_position_limit(
        self,
        position: Position
    ) -> bool:
        """检查持仓上限
        
        参数:
            position: 持仓信息
            
        返回:
            是否通过
        """
        max_position_pct = Decimal(str(self.config.get('max_position_pct', 0.1)))
        return self.risk_controller.check_position_limit(position, max_position_pct)
    
    def get_position_limit(
        self,
        total_value: Decimal,
        current_price: Decimal,
        stock_code: str,
        account_id: int
    ) -> int:
        """获取持仓上限
        
        参数:
            total_value: 总资产
            current_price: 当前价格
            stock_code: 股票代码
            account_id: 账户ID
            
        返回:
            最大可买入数量
        """
        max_position_pct = Decimal(str(self.config.get('max_position_pct', 0.1)))
        
        position = self.get_position(account_id, stock_code)
        current_quantity = position.quantity if position else 0
        
        return self.risk_controller.get_position_limit(
            total_value, current_price, max_position_pct, current_quantity
        )
```

### 3.2 性能指标要求
| 性能指标 | 目标值 | 测量方法 |
|----------|--------|----------|
| 持仓更新时间 | < 50ms | 单次更新 |
| 持仓查询时间 | < 20ms | 单次查询 |
| 缓存命中率 | ≥ 90% | 缓存监控 |
| 数据一致性 | 100% | 数据验证 |

### 3.3 安全机制
- **数据一致性**: 使用数据库事务保证数据一致性
- **并发控制**: 使用乐观锁控制并发更新
- **数据备份**: 定期备份持仓数据

---

## 4. 数据模型与存储

### 4.1 核心数据结构

#### 4.1.1 持仓表模型
```sql
CREATE TABLE positions (
    id BIGSERIAL PRIMARY KEY,
    account_id BIGINT NOT NULL,
    stock_code VARCHAR(20) NOT NULL,
    stock_name VARCHAR(50),
    exchange VARCHAR(10) NOT NULL,
    quantity BIGINT NOT NULL DEFAULT 0,
    available_quantity BIGINT NOT NULL DEFAULT 0,
    frozen_quantity BIGINT NOT NULL DEFAULT 0,
    avg_cost DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
    current_price DECIMAL(12,4) NOT NULL DEFAULT 0.0000,
    market_value DECIMAL(20,4) NOT NULL DEFAULT 0.0000,
    unrealized_pnl DECIMAL(20,4) NOT NULL DEFAULT 0.0000,
    unrealized_pnl_pct DECIMAL(12,6) NOT NULL DEFAULT 0.000000,
    realized_pnl DECIMAL(20,4) NOT NULL DEFAULT 0.0000,
    position_pct DECIMAL(12,6) NOT NULL DEFAULT 0.000000,
    first_buy_date DATE,
    last_trade_date DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_positions_account ON positions(account_id);
CREATE INDEX idx_positions_stock ON positions(stock_code);
CREATE INDEX idx_positions_account_stock ON positions(account_id, stock_code);
```

### 4.2 缓存策略
| 缓存类型 | TTL | 淘汰策略 | 最大容量 |
|----------|-----|----------|----------|
| 持仓缓存 | 1小时 | LRU | 10000条记录 |
| 快照缓存 | 1天 | LRU | 365份快照 |

### 4.3 数据持久化
- **持久化需求**: 所有持仓数据需要持久化存储
- **存储格式**: PostgreSQL数据库
- **备份策略**: 每日备份

---

## 5. 算法实现说明

### 5.1 核心算法

#### 5.1.1 持仓计算算法
```python
def calculate_unrealized_pnl(
    self,
    quantity: int,
    avg_cost: Decimal,
    current_price: Decimal
) -> Decimal:
    """
    浮动盈亏计算算法
    
    算法原理:
    浮动盈亏 = 数量 * (当前价格 - 平均成本)
    
    复杂度: O(1)
    """
    return Decimal(quantity) * (current_price - avg_cost)
```

#### 5.1.2 持仓更新算法
```python
def update_position_from_trade(
    self,
    account_id: int,
    stock_code: str,
    side: OrderSide,
    quantity: int,
    price: Decimal,
    total_value: Decimal
) -> Position:
    """
    持仓更新算法
    
    算法原理:
    1. 查询现有持仓
    2. 根据买卖方向更新持仓
    3. 计算新的持仓指标
    4. 更新数据库和缓存
    
    复杂度: O(1)
    """
    positions = self.repository.find_by_account(account_id, stock_code)
    
    if side == OrderSide.BUY:
        return self._add_position(
            account_id, stock_code, quantity, price, total_value, positions
        )
    else:
        return self._reduce_position(
            account_id, stock_code, quantity, price, total_value, positions
        )
```

---

## 6. 实施技术栈

### 6.1 语言与框架
| 技术选型 | 版本要求 | 用途 | 选择理由 |
|----------|----------|------|----------|
| Python | >=3.8 | 主要开发语言 | 量化系统标准语言 |
| psycopg2 | >=2.9 | PostgreSQL驱动 | 成熟稳定 |
| redis | >=4.0 | Redis客户端 | 高性能缓存 |

### 6.2 第三方依赖
```yaml
requirements:
  - psycopg2-binary>=2.9.0
  - redis>=4.0.0
```

---

## 7. 测试策略

### 7.1 单元测试
| 测试项 | 测试内容 | 覆盖率目标 |
|--------|----------|------------|
| 持仓计算 | 计算正确性 | 100% |
| 持仓更新 | 更新正确性 | 100% |
| 持仓查询 | 查询正确性 | 100% |
| 风险控制 | 控制正确性 | 100% |

### 7.2 集成测试
```python
def test_position_manager_integration():
    """集成测试示例"""
    config = {
        'db_config': {
            'host': 'localhost',
            'port': 5432,
            'database': 'test_db',
            'user': 'test_user',
            'password': 'test_password'
        },
        'redis_config': {
            'host': 'localhost',
            'port': 6379,
            'db': 0
        },
        'max_position_pct': 0.1
    }
    
    manager = PositionManager(config)
    
    position = manager.update_position(
        account_id=1,
        stock_code='600000.SH',
        side=OrderSide.BUY,
        quantity=100,
        price=Decimal('10.0'),
        total_value=Decimal('100000.0')
    )
    
    assert position.quantity == 100
    assert position.avg_cost == Decimal('10.0')
```

---

## 8. 风险与约束

### 8.1 技术风险
| 风险ID | 风险描述 | 风险等级 | 缓解措施 |
|--------|----------|----------|----------|
| R001 | 数据库连接失败 | P1 | 实现连接重试机制 |
| R002 | 缓存失效 | P2 | 实现缓存预热机制 |
| R003 | 并发更新冲突 | P1 | 实现乐观锁机制 |

### 8.2 约束条件
- **技术约束**: 依赖PostgreSQL和Redis
- **资源约束**: 内存使用<1GB，磁盘使用<10GB
- **时间约束**: 预计开发时间12小时
- **质量约束**: 测试覆盖率≥90%

---

## 9. 验收标准

### 9.1 功能验收标准
| 功能项 | 验收标准 | 验证方法 |
|--------|----------|----------|
| 持仓计算 | 计算正确 | 单元测试 |
| 持仓更新 | 更新正确 | 单元测试 |
| 持仓查询 | 查询正确 | 单元测试 |
| 风险控制 | 控制正确 | 单元测试 |

### 9.2 性能验收标准
| 性能指标 | 验收标准 | 验证方法 |
|----------|----------|----------|
| 持仓更新时间 | < 50ms | 性能测试 |
| 持仓查询时间 | < 20ms | 性能测试 |
| 缓存命中率 | ≥ 90% | 性能测试 |

### 9.3 质量验收标准
| 质量指标 | 验收标准 | 验证方法 |
|----------|----------|----------|
| 测试覆盖率 | ≥ 90% | pytest-cov |
| 代码质量 | 无严重问题 | pylint |

---

## 10. 实施路线图

### 10.1 Phase 1: 核心功能开发 (3天)
- **Day 1**: 持仓仓储、持仓缓存
- **Day 2**: 持仓计算器、持仓更新器
- **Day 3**: 持仓查询器、风险控制器

---

## 附录

### A. 配置示例
```yaml
position_manager:
  db_config:
    host: "localhost"
    port: 5432
    database: "zephyr_alpha"
    user: "postgres"
    password: "password"
  
  redis_config:
    host: "localhost"
    port: 6379
    db: 0
    password: null
  
  risk_config:
    max_position_pct: 0.1
  
  cache:
    ttl: 3600
    max_size: 10000
```

### B. 错误码定义
| 错误码 | 错误类型 | 错误描述 | 处理方式 |
|--------|----------|----------|----------|
| ERR_POS_001 | DatabaseError | 数据库错误 | 记录日志，返回错误 |
| ERR_POS_002 | CacheError | 缓存错误 | 记录日志，降级处理 |
| ERR_POS_003 | PositionError | 持仓错误 | 记录日志，返回错误 |

### C. 参考文档
- [架构定义](../../01_FRAMEWORK/ARCHITECTURE.md)
- [模块职责边界](../../01_FRAMEWORK/MODULE_RESPONSIBILITY_BOUNDARIES.md)
- [数据库设计](../../design/database/P0-01_Database_Design_Document.md)


**文档版本**: v1.0.0 | **创建日期**: 2026-04-02 | **维护者**: 策略执行层负责人
