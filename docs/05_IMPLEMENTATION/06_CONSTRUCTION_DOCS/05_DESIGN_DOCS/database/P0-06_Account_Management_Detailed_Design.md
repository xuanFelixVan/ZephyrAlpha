---
module_id: ACCOUNT_MANAGEMENT_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﻟﮒﺝﮔﭘﮔﮒﺕ?
responsibility:
  - 因子计算
  - 交易执行
  - 数据源
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﻟﺑ۵ﮔﺓﻝ؟۰ﻝﮔ ﮒ
applicable_scope: ﻟﺑ۵ﮔﺓﮔﮒ۰ﮔ۷۰ﮒ
compliance_level: ﻛﺕﻛﺕﮔﭦﮔﮔ ﮒ
parent_document: P0-01_Database_Design_Document.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?---


# ﻟﺑ۵ﮔﺓﻝ؟۰ﻝﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰ﺅﺙﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒﺅﺙ
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.0 - ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔ ﮒﻟﺑ۵ﮔﺓﻝ؟۰ﻝﻟ؟ﺝﻟ؟۰
> **ﻟ؟ﺝﻟ؟۰ﮔ۷۰ﮒﺙ**: DDDﻠ۱ﮒﻠ۸ﺎﮒ۷ﻟ؟ﺝﻟ؟۰ + ﻟﮒﮔ ﺗﮔ۷۰ﮒﺙ?
> **ﮔ ﺕﮒﺟﻟﻟﺑ۲**: ﻟﺑ۵ﮔﺓﻝﮒﺛﮒ۷ﮔﻝ؟۰ﻝﻙﻟﭖﻠﻝ؟۰ﻝﻙﻟﺑ۵ﮔﺓﮒﺟ،ﻝ?

## ﻭ ﮔ۷۰ﮒﮔ۵ﻟﺟﺍ

### ﻟﺑ۵ﮔﺓﻝ؟۰ﻝﮔﭘﮔ

```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﮒﭦﻝ۷ﮒﺎ?(Application Layer)                ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ?         AccountApplicationService                    ﻗ? ﻗ?
ﻗ? ﻗ? - ﮒﮒﭨﭦﻟﺑ۵ﮔﺓﮒﭦﻝ۷ﮔﮒ۰                                    ﻗ? ﻗ?
ﻗ? ﻗ? - ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮒﭦﻝ۷ﮔﮒ۰                                    ﻗ? ﻗ?
ﻗ? ﻗ? - ﻟﭖﻠﻝ؟۰ﻝﮒﭦﻝ۷ﮔﮒ۰                                    ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
                            ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﻠ۱ﮒﮒﺎ?(Domain Layer)                     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ?         AccountAggregate (ﻟﺑ۵ﮔﺓﻟﮒﮔ ?                ﻗ? ﻗ?
ﻗ? ﻗ? - Account (ﻟﺑ۵ﮔﺓﮒ؟ﻛﺛ)                                 ﻗ? ﻗ?
ﻗ? ﻗ? - AccountSnapshot (ﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶ﮒ؟ﻛﺛ)                     ﻗ? ﻗ?
ﻗ? ﻗ? - AccountDomainService (ﻠ۱ﮒﮔﮒ۰)                    ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
                            ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﮒﭦﻝ۰ﻟ؟ﺝﮔﺛﮒﺎ?(Infrastructure Layer)          ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ?         AccountRepository (ﻟﺑ۵ﮔﺓﻛﭨﮒ۷)                 ﻗ? ﻗ?
ﻗ? ﻗ? - PostgreSQL (ﻛﺕﭨﮔﺍﮔ؟ﮒﭦ)                              ﻗ? ﻗ?
ﻗ? ﻗ? - Redis (ﮒ؟ﮔﭘﻝﺙﮒ­)                                   ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
```

---

## 1. ﻠ۱ﮒﮔ۷۰ﮒﻟ؟ﺝﻟ؟۰

### 1.1 ﻟﺑ۵ﮔﺓﻟﮒﮔ ?(AccountAggregate)

```python
from dataclasses import dataclass, field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date
from enum import Enum

class AccountType(Enum):
    """ﻟﺑ۵ﮔﺓﻝﺎﭨﮒ"""
    SIMULATION = 'simulation'  # ﮔ۷۰ﮔﻟﺑ۵ﮔﺓ
    REAL = 'real'             # ﮒ؟ﻝﻟﺑ۵ﮔﺓ

class AccountStatus(Enum):
    """ﻟﺑ۵ﮔﺓﻝﭘﮔ?""
    ACTIVE = 'active'         # ﮔﺑﭨﻟﺓ
    FROZEN = 'frozen'         # ﮒﭨﻝﭨ
    CLOSED = 'closed'         # ﮒﺏﻠ­

@dataclass
class Account:
    """ﻟﺑ۵ﮔﺓﮒ؟ﻛﺛ"""
    id: Optional[int] = None
    account_code: str = ""
    account_name: str = ""
    account_type: AccountType = AccountType.SIMULATION
    broker: Optional[str] = None
    initial_capital: Decimal = Decimal('0.0000')
    current_capital: Decimal = Decimal('0.0000')
    available_cash: Decimal = Decimal('0.0000')
    frozen_cash: Decimal = Decimal('0.0000')
    total_assets: Decimal = Decimal('0.0000')
    total_pnl: Decimal = Decimal('0.0000')
    max_drawdown: Decimal = Decimal('0.000000')
    status: AccountStatus = AccountStatus.ACTIVE
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
    metadata: dict = field(default_factory=dict)
    
    def __post_init__(self):
        """ﮒﮒ۶ﮒﮒﮒ۳ﻝ"""
        if not self.account_code:
            self.account_code = self._generate_account_code()
    
    def _generate_account_code(self) -> str:
        """ﻝﮔﻟﺑ۵ﮔﺓﻝﺙﻝ """
        return f"ACC_{datetime.now().strftime('%Y%m%d')}_{self.id or 'NEW'}"
    
    def freeze_cash(self, amount: Decimal) -> bool:
        """ﮒﭨﻝﭨﻟﭖﻠ"""
        if amount <= 0:
            return False
        
        if amount > self.available_cash:
            return False
        
        self.available_cash -= amount
        self.frozen_cash += amount
        self.updated_at = datetime.now()
        
        return True
    
    def unfreeze_cash(self, amount: Decimal) -> bool:
        """ﻟ۶۲ﮒﭨﻟﭖﻠ"""
        if amount <= 0:
            return False
        
        if amount > self.frozen_cash:
            return False
        
        self.frozen_cash -= amount
        self.available_cash += amount
        self.updated_at = datetime.now()
        
        return True
    
    def update_capital(
        self,
        current_capital: Decimal,
        available_cash: Decimal,
        frozen_cash: Decimal,
        total_assets: Decimal
    ) -> None:
        """ﮔﺑﮔﺍﻟﭖﻠ"""
        self.current_capital = current_capital
        self.available_cash = available_cash
        self.frozen_cash = frozen_cash
        self.total_assets = total_assets
        self.total_pnl = total_assets - self.initial_capital
        self.updated_at = datetime.now()
    
    def update_max_drawdown(self, drawdown: Decimal) -> None:
        """ﮔﺑﮔﺍﮔﮒ۳۶ﮒﮔ?""
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
            self.updated_at = datetime.now()
    
    def freeze_account(self, reason: Optional[str] = None) -> bool:
        """ﮒﭨﻝﭨﻟﺑ۵ﮔﺓ"""
        if self.status == AccountStatus.CLOSED:
            return False
        
        self.status = AccountStatus.FROZEN
        self.metadata['freeze_reason'] = reason
        self.updated_at = datetime.now()
        
        return True
    
    def unfreeze_account(self) -> bool:
        """ﻟ۶۲ﮒﭨﻟﺑ۵ﮔﺓ"""
        if self.status != AccountStatus.FROZEN:
            return False
        
        self.status = AccountStatus.ACTIVE
        self.metadata.pop('freeze_reason', None)
        self.updated_at = datetime.now()
        
        return True
    
    def close_account(self) -> bool:
        """ﮒﺏﻠ­ﻟﺑ۵ﮔﺓ"""
        if self.status == AccountStatus.CLOSED:
            return False
        
        self.status = AccountStatus.CLOSED
        self.updated_at = datetime.now()
        
        return True

@dataclass
class AccountSnapshot:
    """ﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶ﮒ؟ﻛﺛ"""
    id: Optional[int] = None
    account_id: int = 0
    snapshot_date: date = field(default_factory=date.today)
    total_assets: Decimal = Decimal('0.0000')
    available_cash: Decimal = Decimal('0.0000')
    total_market_value: Decimal = Decimal('0.0000')
    daily_pnl: Decimal = Decimal('0.0000')
    daily_pnl_pct: Decimal = Decimal('0.000000')
    cumulative_pnl: Decimal = Decimal('0.0000')
    cumulative_pnl_pct: Decimal = Decimal('0.000000')
    max_drawdown: Decimal = Decimal('0.000000')
    sharpe_ratio: Decimal = Decimal('0.000000')
    win_rate: Decimal = Decimal('0.000000')
    created_at: datetime = field(default_factory=datetime.now)
```

---

## 2. ﻠ۱ﮒﮔﮒ۰ﻟ؟ﺝﻟ؟۰

### 2.1 ﻟﺑ۵ﮔﺓﻠ۱ﮒﮔﮒ۰ (AccountDomainService)

```python
from typing import List, Optional
from decimal import Decimal
from datetime import date

class AccountDomainService:
    """ﻟﺑ۵ﮔﺓﻠ۱ﮒﮔﮒ۰"""
    
    async def calculate_daily_pnl(
        self,
        account: Account,
        previous_snapshot: Optional[AccountSnapshot]
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﮔ۴ﻝﻛﭦ?""
        if not previous_snapshot:
            return Decimal('0.0000')
        
        return account.total_assets - previous_snapshot.total_assets
    
    async def calculate_daily_pnl_pct(
        self,
        account: Account,
        previous_snapshot: Optional[AccountSnapshot]
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﮔ۴ﻝﻛﭦﻝﺝﮒﮔﺁ"""
        if not previous_snapshot or previous_snapshot.total_assets == 0:
            return Decimal('0.000000')
        
        daily_pnl = await self.calculate_daily_pnl(account, previous_snapshot)
        return daily_pnl / previous_snapshot.total_assets
    
    async def calculate_cumulative_pnl(
        self,
        account: Account
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﻝﺑﺁﻟ؟۰ﻝﻛﭦ"""
        return account.total_assets - account.initial_capital
    
    async def calculate_cumulative_pnl_pct(
        self,
        account: Account
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﻝﺑﺁﻟ؟۰ﻝﻛﭦﻝﺝﮒﮔﺁ?""
        if account.initial_capital == 0:
            return Decimal('0.000000')
        
        cumulative_pnl = await self.calculate_cumulative_pnl(account)
        return cumulative_pnl / account.initial_capital
    
    async def calculate_max_drawdown(
        self,
        snapshots: List[AccountSnapshot]
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﮔﮒ۳۶ﮒﮔ?""
        if not snapshots:
            return Decimal('0.000000')
        
        max_drawdown = Decimal('0.000000')
        peak = snapshots[0].total_assets
        
        for snapshot in snapshots:
            if snapshot.total_assets > peak:
                peak = snapshot.total_assets
            
            drawdown = (peak - snapshot.total_assets) / peak
            if drawdown > max_drawdown:
                max_drawdown = drawdown
        
        return max_drawdown
    
    async def calculate_sharpe_ratio(
        self,
        snapshots: List[AccountSnapshot],
        risk_free_rate: Decimal = Decimal('0.03')
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﮒ۳ﮔ؟ﮔﺁﻝ"""
        if len(snapshots) < 2:
            return Decimal('0.000000')
        
        # ﻟ؟۰ﻝ؟ﮔ۴ﮔﭘﻝﻝ
        daily_returns = []
        for i in range(1, len(snapshots)):
            daily_return = snapshots[i].daily_pnl_pct
            daily_returns.append(daily_return)
        
        if not daily_returns:
            return Decimal('0.000000')
        
        # ﻟ؟۰ﻝ؟ﮒﺗﺏﮒﮔﭘﻝﻝ?
        avg_return = sum(daily_returns) / len(daily_returns)
        
        # ﻟ؟۰ﻝ؟ﮔ ﮒﮒﺓ?
        variance = sum((r - avg_return) ** 2 for r in daily_returns) / len(daily_returns)
        std_dev = variance ** Decimal('0.5')
        
        if std_dev == 0:
            return Decimal('0.000000')
        
        # ﻟ؟۰ﻝ؟ﮒ۳ﮔ؟ﮔﺁﻝﺅﺙﮒﺗﺑﮒﺅﺙ
        annualized_return = avg_return * 252
        annualized_std = std_dev * (252 ** Decimal('0.5'))
        
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_std
        
        return sharpe_ratio
    
    async def calculate_win_rate(
        self,
        snapshots: List[AccountSnapshot]
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﻟﻝ"""
        if not snapshots:
            return Decimal('0.000000')
        
        win_count = sum(1 for s in snapshots if s.daily_pnl > 0)
        total_count = len(snapshots)
        
        return Decimal(win_count) / Decimal(total_count)
```

---

## 3. ﮒﭦﻝ۷ﮔﮒ۰ﻟ؟ﺝﻟ؟۰

### 3.1 ﻟﺑ۵ﮔﺓﮒﭦﻝ۷ﮔﮒ۰ (AccountApplicationService)

```python
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date

class AccountApplicationService:
    """ﻟﺑ۵ﮔﺓﮒﭦﻝ۷ﮔﮒ۰"""
    
    def __init__(
        self,
        account_repository,
        account_domain_service: AccountDomainService,
        event_publisher
    ):
        self.account_repository = account_repository
        self.domain_service = account_domain_service
        self.event_publisher = event_publisher
    
    async def create_account(
        self,
        account_name: str,
        account_type: str,
        initial_capital: Decimal,
        broker: Optional[str] = None
    ) -> Dict[str, Any]:
        """ﮒﮒﭨﭦﻟﺑ۵ﮔﺓ"""
        # ﮒﮒﭨﭦﻟﺑ۵ﮔﺓﮒ؟ﻛﺛ
        account = Account(
            account_name=account_name,
            account_type=AccountType(account_type),
            initial_capital=initial_capital,
            current_capital=initial_capital,
            available_cash=initial_capital,
            broker=broker
        )
        
        # ﻛﺟﮒ­ﻟﺑ۵ﮔﺓ
        account = await self.account_repository.create(account)
        
        # ﮒﮒﺕﻟﺑ۵ﮔﺓﮒﮒﭨﭦﻛﭦﻛﭨﭘ
        await self.event_publisher.publish({
            'event_type': 'AccountCreated',
            'account_id': account.id,
            'account_code': account.account_code,
            'account_name': account.account_name,
            'initial_capital': float(account.initial_capital),
            'timestamp': datetime.now().isoformat()
        })
        
        return {
            'id': account.id,
            'account_code': account.account_code,
            'account_name': account.account_name,
            'account_type': account.account_type.value,
            'initial_capital': float(account.initial_capital),
            'current_capital': float(account.current_capital),
            'available_cash': float(account.available_cash),
            'status': account.status.value
        }
    
    async def get_account(self, account_id: int) -> Optional[Dict[str, Any]]:
        """ﻟﺓﮒﻟﺑ۵ﮔﺓ"""
        account = await self.account_repository.find_by_id(account_id)
        
        if not account:
            return None
        
        return {
            'id': account.id,
            'account_code': account.account_code,
            'account_name': account.account_name,
            'account_type': account.account_type.value,
            'broker': account.broker,
            'initial_capital': float(account.initial_capital),
            'current_capital': float(account.current_capital),
            'available_cash': float(account.available_cash),
            'frozen_cash': float(account.frozen_cash),
            'total_assets': float(account.total_assets),
            'total_pnl': float(account.total_pnl),
            'max_drawdown': float(account.max_drawdown),
            'status': account.status.value,
            'created_at': account.created_at.isoformat(),
            'updated_at': account.updated_at.isoformat()
        }
    
    async def get_accounts(
        self,
        account_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Dict[str, Any]:
        """ﻟﺓﮒﻟﺑ۵ﮔﺓﮒﻟ۰۷"""
        accounts = await self.account_repository.find_all(
            account_type=account_type,
            status=status,
            page=page,
            page_size=page_size
        )
        
        total = await self.account_repository.count(
            account_type=account_type,
            status=status
        )
        
        return {
            'total': total,
            'page': page,
            'page_size': page_size,
            'accounts': [
                {
                    'id': acc.id,
                    'account_code': acc.account_code,
                    'account_name': acc.account_name,
                    'account_type': acc.account_type.value,
                    'total_assets': float(acc.total_assets),
                    'total_pnl': float(acc.total_pnl),
                    'status': acc.status.value
                }
                for acc in accounts
            ]
        }
    
    async def freeze_cash(
        self,
        account_id: int,
        amount: Decimal
    ) -> bool:
        """ﮒﭨﻝﭨﻟﭖﻠ"""
        account = await self.account_repository.find_by_id(account_id)
        
        if not account:
            return False
        
        success = account.freeze_cash(amount)
        
        if success:
            await self.account_repository.update(account)
            
            # ﮒﮒﺕﻟﭖﻠﮒﭨﻝﭨﻛﭦﻛﭨﭘ
            await self.event_publisher.publish({
                'event_type': 'CashFrozen',
                'account_id': account.id,
                'amount': float(amount),
                'timestamp': datetime.now().isoformat()
            })
        
        return success
    
    async def unfreeze_cash(
        self,
        account_id: int,
        amount: Decimal
    ) -> bool:
        """ﻟ۶۲ﮒﭨﻟﭖﻠ"""
        account = await self.account_repository.find_by_id(account_id)
        
        if not account:
            return False
        
        success = account.unfreeze_cash(amount)
        
        if success:
            await self.account_repository.update(account)
            
            # ﮒﮒﺕﻟﭖﻠﻟ۶۲ﮒﭨﻛﭦﻛﭨﭘ
            await self.event_publisher.publish({
                'event_type': 'CashUnfrozen',
                'account_id': account.id,
                'amount': float(amount),
                'timestamp': datetime.now().isoformat()
            })
        
        return success
    
    async def update_account_capital(
        self,
        account_id: int,
        current_capital: Decimal,
        available_cash: Decimal,
        frozen_cash: Decimal,
        total_assets: Decimal
    ) -> bool:
        """ﮔﺑﮔﺍﻟﺑ۵ﮔﺓﻟﭖﻠ"""
        account = await self.account_repository.find_by_id(account_id)
        
        if not account:
            return False
        
        account.update_capital(
            current_capital,
            available_cash,
            frozen_cash,
            total_assets
        )
        
        await self.account_repository.update(account)
        
        return True
    
    async def create_account_snapshot(
        self,
        account_id: int,
        snapshot_date: date
    ) -> Dict[str, Any]:
        """ﮒﮒﭨﭦﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶"""
        account = await self.account_repository.find_by_id(account_id)
        
        if not account:
            return {}
        
        # ﻟﺓﮒﮒﻛﺕﮔ۴ﮒﺟ،ﻝ?
        previous_snapshot = await self.account_repository.find_snapshot_by_date(
            account_id,
            snapshot_date
        )
        
        # ﻟ؟۰ﻝ؟ﮒﻠ۰ﺗﮔﮔ 
        daily_pnl = await self.domain_service.calculate_daily_pnl(
            account,
            previous_snapshot
        )
        
        daily_pnl_pct = await self.domain_service.calculate_daily_pnl_pct(
            account,
            previous_snapshot
        )
        
        cumulative_pnl = await self.domain_service.calculate_cumulative_pnl(account)
        cumulative_pnl_pct = await self.domain_service.calculate_cumulative_pnl_pct(account)
        
        # ﮒﮒﭨﭦﮒﺟ،ﻝ۶
        snapshot = AccountSnapshot(
            account_id=account_id,
            snapshot_date=snapshot_date,
            total_assets=account.total_assets,
            available_cash=account.available_cash,
            total_market_value=account.total_assets - account.available_cash,
            daily_pnl=daily_pnl,
            daily_pnl_pct=daily_pnl_pct,
            cumulative_pnl=cumulative_pnl,
            cumulative_pnl_pct=cumulative_pnl_pct,
            max_drawdown=account.max_drawdown
        )
        
        # ﻛﺟﮒ­ﮒﺟ،ﻝ۶
        snapshot = await self.account_repository.create_snapshot(snapshot)
        
        return {
            'id': snapshot.id,
            'account_id': snapshot.account_id,
            'snapshot_date': snapshot.snapshot_date.isoformat(),
            'total_assets': float(snapshot.total_assets),
            'daily_pnl': float(snapshot.daily_pnl),
            'cumulative_pnl': float(snapshot.cumulative_pnl)
        }
    
    async def freeze_account(
        self,
        account_id: int,
        reason: Optional[str] = None
    ) -> bool:
        """ﮒﭨﻝﭨﻟﺑ۵ﮔﺓ"""
        account = await self.account_repository.find_by_id(account_id)
        
        if not account:
            return False
        
        success = account.freeze_account(reason)
        
        if success:
            await self.account_repository.update(account)
            
            # ﮒﮒﺕﻟﺑ۵ﮔﺓﮒﭨﻝﭨﻛﭦﻛﭨﭘ
            await self.event_publisher.publish({
                'event_type': 'AccountFrozen',
                'account_id': account.id,
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            })
        
        return success
    
    async def unfreeze_account(self, account_id: int) -> bool:
        """ﻟ۶۲ﮒﭨﻟﺑ۵ﮔﺓ"""
        account = await self.account_repository.find_by_id(account_id)
        
        if not account:
            return False
        
        success = account.unfreeze_account()
        
        if success:
            await self.account_repository.update(account)
            
            # ﮒﮒﺕﻟﺑ۵ﮔﺓﻟ۶۲ﮒﭨﻛﭦﻛﭨﭘ
            await self.event_publisher.publish({
                'event_type': 'AccountUnfrozen',
                'account_id': account.id,
                'timestamp': datetime.now().isoformat()
            })
        
        return success
```

---

## 4. ﻛﭨﮒ۷ﮒ؟ﻝﺍﻟ؟ﺝﻟ؟۰

### 4.1 ﻟﺑ۵ﮔﺓﻛﭨﮒ۷ﮒ؟ﻝﺍ (AccountRepositoryImpl)

```python
from typing import List, Optional
from decimal import Decimal
from datetime import date
import asyncpg

class AccountRepositoryImpl:
    """ﻟﺑ۵ﮔﺓﻛﭨﮒ۷ﮒ؟ﻝﺍ"""
    
    def __init__(self, db_pool: asyncpg.Pool, redis_client):
        self.db_pool = db_pool
        self.redis_client = redis_client
    
    async def create(self, account: Account) -> Account:
        """ﮒﮒﭨﭦﻟﺑ۵ﮔﺓ"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO accounts (
                    account_code, account_name, account_type, broker,
                    initial_capital, current_capital, available_cash,
                    frozen_cash, total_assets, total_pnl, max_drawdown,
                    status, created_at, updated_at, metadata
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15)
                RETURNING id, account_code
                """,
                account.account_code,
                account.account_name,
                account.account_type.value,
                account.broker,
                account.initial_capital,
                account.current_capital,
                account.available_cash,
                account.frozen_cash,
                account.total_assets,
                account.total_pnl,
                account.max_drawdown,
                account.status.value,
                account.created_at,
                account.updated_at,
                account.metadata
            )
            
            account.id = row['id']
            account.account_code = row['account_code']
            
            # ﻝﺙﮒ­ﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁ
            await self._cache_account(account)
            
            return account
    
    async def find_by_id(self, account_id: int) -> Optional[Account]:
        """ﮔ ﺗﮔ؟IDﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ"""
        # ﮒﮔ۴ﻝﺙﮒ­
        cached = await self._get_cached_account(account_id)
        if cached:
            return cached
        
        # ﮔ۴ﮔﺍﮔ؟ﮒﭦ
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                SELECT * FROM accounts WHERE id = $1
                """,
                account_id
            )
            
            if not row:
                return None
            
            account = self._row_to_account(row)
            
            # ﻝﺙﮒ­ﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁ
            await self._cache_account(account)
            
            return account
    
    async def find_all(
        self,
        account_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[Account]:
        """ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮒﻟ۰۷"""
        async with self.db_pool.acquire() as conn:
            offset = (page - 1) * page_size
            
            conditions = []
            params = []
            param_index = 1
            
            if account_type:
                conditions.append(f"account_type = ${param_index}")
                params.append(account_type)
                param_index += 1
            
            if status:
                conditions.append(f"status = ${param_index}")
                params.append(status)
                param_index += 1
            
            where_clause = " AND ".join(conditions) if conditions else "TRUE"
            
            rows = await conn.fetch(
                f"""
                SELECT * FROM accounts
                WHERE {where_clause}
                ORDER BY created_at DESC
                LIMIT ${param_index} OFFSET ${param_index + 1}
                """,
                *params,
                page_size,
                offset
            )
            
            return [self._row_to_account(row) for row in rows]
    
    async def update(self, account: Account) -> Account:
        """ﮔﺑﮔﺍﻟﺑ۵ﮔﺓ"""
        async with self.db_pool.acquire() as conn:
            await conn.execute(
                """
                UPDATE accounts SET
                    account_name = $2,
                    current_capital = $3,
                    available_cash = $4,
                    frozen_cash = $5,
                    total_assets = $6,
                    total_pnl = $7,
                    max_drawdown = $8,
                    status = $9,
                    updated_at = $10,
                    metadata = $11
                WHERE id = $1
                """,
                account.id,
                account.account_name,
                account.current_capital,
                account.available_cash,
                account.frozen_cash,
                account.total_assets,
                account.total_pnl,
                account.max_drawdown,
                account.status.value,
                account.updated_at,
                account.metadata
            )
            
            # ﮔﺑﮔﺍﻝﺙﮒ­
            await self._cache_account(account)
            
            return account
    
    async def create_snapshot(self, snapshot: AccountSnapshot) -> AccountSnapshot:
        """ﮒﮒﭨﭦﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶"""
        async with self.db_pool.acquire() as conn:
            row = await conn.fetchrow(
                """
                INSERT INTO account_snapshots (
                    account_id, snapshot_date, total_assets, available_cash,
                    total_market_value, daily_pnl, daily_pnl_pct,
                    cumulative_pnl, cumulative_pnl_pct, max_drawdown,
                    sharpe_ratio, win_rate, created_at
                ) VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13)
                RETURNING id
                """,
                snapshot.account_id,
                snapshot.snapshot_date,
                snapshot.total_assets,
                snapshot.available_cash,
                snapshot.total_market_value,
                snapshot.daily_pnl,
                snapshot.daily_pnl_pct,
                snapshot.cumulative_pnl,
                snapshot.cumulative_pnl_pct,
                snapshot.max_drawdown,
                snapshot.sharpe_ratio,
                snapshot.win_rate,
                snapshot.created_at
            )
            
            snapshot.id = row['id']
            
            return snapshot
    
    async def _cache_account(self, account: Account) -> None:
        """ﻝﺙﮒ­ﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁ"""
        key = f"account:{account.id}"
        await self.redis_client.setex(
            key,
            300,  # 5ﮒﻠﻟﺟﮔ
            str({
                'id': account.id,
                'account_code': account.account_code,
                'account_name': account.account_name,
                'current_capital': float(account.current_capital),
                'available_cash': float(account.available_cash),
                'frozen_cash': float(account.frozen_cash),
                'total_assets': float(account.total_assets)
            })
        )
    
    async def _get_cached_account(self, account_id: int) -> Optional[Account]:
        """ﻟﺓﮒﻝﺙﮒ­ﻝﻟﺑ۵ﮔﺓﻛﺟ۰ﮔ?""
        key = f"account:{account_id}"
        cached = await self.redis_client.get(key)
        
        if cached:
            # TODO: ﮒﮒﭦﮒﮒﻝﺙﮒ­ﮔﺍﮔ؟
            return None
        
        return None
    
    def _row_to_account(self, row) -> Account:
        """ﮔﺍﮔ؟ﮒﭦﻟ۰ﻟﺛ؛ﻟﺑ۵ﮔﺓﮒ؟ﻛﺛ?""
        return Account(
            id=row['id'],
            account_code=row['account_code'],
            account_name=row['account_name'],
            account_type=AccountType(row['account_type']),
            broker=row['broker'],
            initial_capital=row['initial_capital'],
            current_capital=row['current_capital'],
            available_cash=row['available_cash'],
            frozen_cash=row['frozen_cash'],
            total_assets=row['total_assets'],
            total_pnl=row['total_pnl'],
            max_drawdown=row['max_drawdown'],
            status=AccountStatus(row['status']),
            created_at=row['created_at'],
            updated_at=row['updated_at'],
            metadata=row['metadata']
        )
```

---

## 5. ﮔ۶ﻟﺛﻛﺕﻝﮔ?

### 5.1 ﮔ۶ﻟﺛﮔﮔ 

| ﮔﻛﺛ | ﮒﮒﭦﮔﭘﻠﺑ | ﮒ۳ﮔﺏ۷ |
|------|----------|------|
| **ﮒﮒﭨﭦﻟﺑ۵ﮔﺓ** | < 300ms | ﮒﮒ،ﮔﺍﮔ؟ﮒﭦﮒﮒ?|
| **ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ** | < 50ms | Redisﻝﺙﮒ­ﮒﺛﻛﺕ­ |
| **ﮔﺑﮔﺍﻟﭖﻠ** | < 200ms | ﮒﮒ،ﮔﺍﮔ؟ﮒﭦﮔﺑﮔ?|
| **ﮒﮒﭨﭦﮒﺟ،ﻝ۶** | < 500ms | ﮒﮒ،ﮔﮔ ﻟ؟۰ﻝ؟ |

### 5.2 ﻝﺙﮒ­ﻝ­ﻝ۴

| ﮔﺍﮔ؟ﻝﺎﭨﮒ | ﻝﺙﮒ­ﮔﭘﻠﺑ | ﻝﺙﮒ­ﻝ­ﻝ۴ |
|----------|----------|----------|
| **ﻟﺑ۵ﮔﺓﮒﭦﮔ؛ﻛﺟ۰ﮔﺁ** | 5ﮒﻠ | Redisﻝﺙﮒ­ |
| **ﻟﺑ۵ﮔﺓﻟﭖﻠﻛﺟ۰ﮔﺁ** | 1ﮒﻠ | Redisﻝﺙﮒ­ |
| **ﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶** | ﻛﺕﻝﺙﮒ­?| ﮒ؟ﮔﭘﮔ۴ﻟﺁ۱ |

---

**ﻝﮔ؛**: 1.0.0 | **ﮔﺑﮔﺍﮔ۴ﮔ**: 2026-04-02 | **ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ? 
**ﻛﺕﻛﺕﮔ­?*: P0-7 ﻟ؟۱ﮒﻝ؟۰ﻝﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰