---
module_id: P0_06_ACCOUNT_MANAGEMENT_DETAILED_DESIGN
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 首席文档架构师
---

﻿---
module_id: ACCOUNT_MANAGEMENT_001
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕﻟﮒﺝﮔﭘﮔﮒﺕ?
responsibility:
  - 系统实施与部署管理与优化维护
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﻟﺑ۵ﮔﺓﻝ؟۰ﻝﮔﮒ
applicable_scope: ﻟﺑ۵ﮔﺓﮔﮒ۰ﮔ۷۰ﮒ
compliance_level: ﻛﺕﻛﺕﮔﭦﮔﮔﮒ
parent_document: P0-01_Database_Design_Document.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?---


# ﻟﺑ۵ﮔﺓﻝ؟۰ﻝﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰ﺅﺙﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮒﺅﺙ
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.0 - ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﮒﻟﺑ۵ﮔﺓﻝ؟۰ﻝﻟ؟ﺝﻟ؟۰
> **ﻟ؟ﺝﻟ؟۰ﮔ۷۰ﮒﺙ**: DDDﻠ۱ﮒﻠ۸ﺎﮒ۷ﻟ؟ﺝﻟ؟۰ + ﻟﮒﮔﺗﮔ۷۰ﮒﺙ?
> **ﮔﺕﮒﺟﻟﻟﺑ۲**: ﻟﺑ۵ﮔﺓﻝﮒﺛﮒ۷ﮔﻝ؟۰ﻝﻙﻟﭖﻠﻝ؟۰ﻝﻙﻟﺑ۵ﮔﺓﮒﺟ،ﻝ?

## ﻭ ﮔ۷۰ﮒﮔ۵ﻟﺟﺍ

### ﻟﺑ۵ﮔﺓﻝ؟۰ﻝﮔﭘﮔ

```
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﮒﭦﻝ۷ﮒﺎ?(Application Layer)                ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ?         AccountApplicationService                    ﻗ? ﻗ?
ﻗ? ﻗ? - ﮒﮒﭨﭦﻟﺑ۵ﮔﺓﮒﭦﻝ۷ﮔﮒ۰                                    ﻗ? ﻗ?
ﻗ? ﻗ? - ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮒﭦﻝ۷ﮔﮒ۰                                    ﻗ? ﻗ?
ﻗ? ﻗ? - ﻟﭖﻠﻝ؟۰ﻝﮒﭦﻝ۷ﮔﮒ۰                                    ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
                            ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﻠ۱ﮒﮒﺎ?(Domain Layer)                     ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ?         AccountAggregate (ﻟﺑ۵ﮔﺓﻟﮒﮔ?                ﻗ? ﻗ?
ﻗ? ﻗ? - Account (ﻟﺑ۵ﮔﺓﮒ؟ﻛﺛ)                                 ﻗ? ﻗ?
ﻗ? ﻗ? - AccountSnapshot (ﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶ﮒ؟ﻛﺛ)                     ﻗ? ﻗ?
ﻗ? ﻗ? - AccountDomainService (ﻠ۱ﮒﮔﮒ۰)                    ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
                            ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
ﻗ?                   ﮒﭦﻝ۰ﻟ؟ﺝﮔﺛﮒﺎ?(Infrastructure Layer)          ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗ? ﻗ?         AccountRepository (ﻟﺑ۵ﮔﺓﻛﭨﮒ۷)                 ﻗ? ﻗ?
ﻗ? ﻗ? - PostgreSQL (ﻛﺕﭨﮔﺍﮔ؟ﮒﭦ)                              ﻗ? ﻗ?
ﻗ? ﻗ? - Redis (ﮒ؟ﮔﭘﻝﺙﮒ)                                   ﻗ? ﻗ?
ﻗ? ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ? ﻗ?
ﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗﻗ?
```

---

## 1. ﻠ۱ﮒﮔ۷۰ﮒﻟ؟ﺝﻟ؟۰

### 1.1 ﻟﺑ۵ﮔﺓﻟﮒﮔ?(AccountAggregate)

```python
from dataclasses import dataclass, field
from typing import Optional, List
from decimal import Decimal
from datetime import datetime, date
from enum import Enum

class AccountType(Enum):
    """ﻟﺑ۵ﮔﺓﻝﺎﭨﮒ"""
    SIMULATION = 'simulation'  # ﮔ۷۰ﮔﻟﺑ۵ﮔﺓ
    REAL = 'real'             # ﮒ؟ﻝﻟﺑ۵ﮔﺓ

class AccountStatus(Enum):
    """ﻟﺑ۵ﮔﺓﻝﭘﮔ?""
    ACTIVE = 'active'         # ﮔﺑﭨﻟﺓ
    FROZEN = 'frozen'         # ﮒﭨﻝﭨ
CLOSED = 'closed'         # ﮒﺏﻠ

@dataclass
class Account:
    """ﻟﺑ۵ﮔﺓﮒ؟ﻛﺛ"""
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
        """ﮒﮒ۶ﮒﮒﮒ۳ﻝ"""
        if not self.account_code:
            self.account_code = self._generate_account_code()
    
    def _generate_account_code(self) -> str:
"""ﻝﮔﻟﺑ۵ﮔﺓﻝﺙﻝ"""
        return f"ACC_{datetime.now().strftime('%Y%m%d')}_{self.id or 'NEW'}"
    
    def freeze_cash(self, amount: Decimal) -> bool:
        """ﮒﭨﻝﭨﻟﭖﻠ"""
        if amount <= 0:
            return False
        
        if amount > self.available_cash:
            return False
        
        self.available_cash -= amount
        self.frozen_cash += amount
        self.updated_at = datetime.now()
        
        return True
    
    def unfreeze_cash(self, amount: Decimal) -> bool:
        """ﻟ۶۲ﮒﭨﻟﭖﻠ"""
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
        """ﮔﺑﮔﺍﻟﭖﻠ"""
        self.current_capital = current_capital
        self.available_cash = available_cash
        self.frozen_cash = frozen_cash
        self.total_assets = total_assets
        self.total_pnl = total_assets - self.initial_capital
        self.updated_at = datetime.now()
    
    def update_max_drawdown(self, drawdown: Decimal) -> None:
        """ﮔﺑﮔﺍﮔﮒ۳۶ﮒﮔ?""
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
            self.updated_at = datetime.now()
    
    def freeze_account(self, reason: Optional[str] = None) -> bool:
        """ﮒﭨﻝﭨﻟﺑ۵ﮔﺓ"""
        if self.status == AccountStatus.CLOSED:
            return False
        
        self.status = AccountStatus.FROZEN
        self.metadata['freeze_reason'] = reason
        self.updated_at = datetime.now()
        
        return True
    
    def unfreeze_account(self) -> bool:
        """ﻟ۶۲ﮒﭨﻟﺑ۵ﮔﺓ"""
        if self.status != AccountStatus.FROZEN:
            return False
        
        self.status = AccountStatus.ACTIVE
        self.metadata.pop('freeze_reason', None)
        self.updated_at = datetime.now()
        
        return True
    
    def close_account(self) -> bool:
"""ﮒﺏﻠﻟﺑ۵ﮔﺓ"""
        if self.status == AccountStatus.CLOSED:
            return False
        
        self.status = AccountStatus.CLOSED
        self.updated_at = datetime.now()
        
        return True

@dataclass
class AccountSnapshot:
    """ﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶ﮒ؟ﻛﺛ"""
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

## 2. ﻠ۱ﮒﮔﮒ۰ﻟ؟ﺝﻟ؟۰

### 2.1 ﻟﺑ۵ﮔﺓﻠ۱ﮒﮔﮒ۰ (AccountDomainService)

```python
from typing import List, Optional
from decimal import Decimal
from datetime import date

class AccountDomainService:
    """ﻟﺑ۵ﮔﺓﻠ۱ﮒﮔﮒ۰"""
    
    async def calculate_daily_pnl(
        self,
        account: Account,
        previous_snapshot: Optional[AccountSnapshot]
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﮔ۴ﻝﻛﭦ?""
        if not previous_snapshot:
            return Decimal('0.0000')
        
        return account.total_assets - previous_snapshot.total_assets
    
    async def calculate_daily_pnl_pct(
        self,
        account: Account,
        previous_snapshot: Optional[AccountSnapshot]
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﮔ۴ﻝﻛﭦﻝﺝﮒﮔﺁ"""
        if not previous_snapshot or previous_snapshot.total_assets == 0:
            return Decimal('0.000000')
        
        daily_pnl = await self.calculate_daily_pnl(account, previous_snapshot)
        return daily_pnl / previous_snapshot.total_assets
    
    async def calculate_cumulative_pnl(
        self,
        account: Account
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﻝﺑﺁﻟ؟۰ﻝﻛﭦ"""
        return account.total_assets - account.initial_capital
    
    async def calculate_cumulative_pnl_pct(
        self,
        account: Account
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﻝﺑﺁﻟ؟۰ﻝﻛﭦﻝﺝﮒﮔﺁ?""
        if account.initial_capital == 0:
            return Decimal('0.000000')
        
        cumulative_pnl = await self.calculate_cumulative_pnl(account)
        return cumulative_pnl / account.initial_capital
    
    async def calculate_max_drawdown(
        self,
        snapshots: List[AccountSnapshot]
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﮔﮒ۳۶ﮒﮔ?""
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
        """ﻟ؟۰ﻝ؟ﮒ۳ﮔ؟ﮔﺁﻝ"""
        if len(snapshots) < 2:
            return Decimal('0.000000')
        
        # ﻟ؟۰ﻝ؟ﮔ۴ﮔﭘﻝﻝ
        daily_returns = []
        for i in range(1, len(snapshots)):
            daily_return = snapshots[i].daily_pnl_pct
            daily_returns.append(daily_return)
        
        if not daily_returns:
            return Decimal('0.000000')
        
        # ﻟ؟۰ﻝ؟ﮒﺗﺏﮒﮔﭘﻝﻝ?
        avg_return = sum(daily_returns) / len(daily_returns)
        
# ﻟ؟۰ﻝ؟ﮔﮒﮒﺓ?
        variance = sum((r - avg_return) ** 2 for r in daily_returns) / len(daily_returns)
        std_dev = variance ** Decimal('0.5')
        
        if std_dev == 0:
            return Decimal('0.000000')
        
        # ﻟ؟۰ﻝ؟ﮒ۳ﮔ؟ﮔﺁﻝﺅﺙﮒﺗﺑﮒﺅﺙ
        annualized_return = avg_return * 252
        annualized_std = std_dev * (252 ** Decimal('0.5'))
        
        sharpe_ratio = (annualized_return - risk_free_rate) / annualized_std
        
        return sharpe_ratio
    
    async def calculate_win_rate(
        self,
        snapshots: List[AccountSnapshot]
    ) -> Decimal:
        """ﻟ؟۰ﻝ؟ﻟﻝ"""
        if not snapshots:
            return Decimal('0.000000')
        
        win_count = sum(1 for s in snapshots if s.daily_pnl > 0)
        total_count = len(snapshots)
        
        return Decimal(win_count) / Decimal(total_count)
```

---

## 3. ﮒﭦﻝ۷ﮔﮒ۰ﻟ؟ﺝﻟ؟۰

### 3.1 ﻟﺑ۵ﮔﺓﮒﭦﻝ۷ﮔﮒ۰ (AccountApplicationService)

```python
from typing import List, Optional, Dict, Any
from decimal import Decimal
from datetime import date

class AccountApplicationService:
    """ﻟﺑ۵ﮔﺓﮒﭦﻝ۷ﮔﮒ۰"""
    
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
        """ﮒﮒﭨﭦﻟﺑ۵ﮔﺓ"""
        # ﮒﮒﭨﭦﻟﺑ۵ﮔﺓﮒ؟ﻛﺛ
        account = Account(
            account_name=account_name,
            account_type=AccountType(account_type),
            initial_capital=initial_capital,
            current_capital=initial_capital,
            available_cash=initial_capital,
            broker=broker
        )
        
# ﻛﺟﮒﻟﺑ۵ﮔﺓ
        account = await self.account_repository.create(account)
        
        # ﮒﮒﺕﻟﺑ۵ﮔﺓﮒﮒﭨﭦﻛﭦﻛﭨﭘ
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
        """ﻟﺓﮒﻟﺑ۵ﮔﺓ"""
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
        """ﻟﺓﮒﻟﺑ۵ﮔﺓﮒﻟ۰۷"""
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
        """ﮒﭨﻝﭨﻟﭖﻠ"""
        account = await self.account_repository.find_by_id(account_id)
        
        if not account:
            return False
        
        success = account.freeze_cash(amount)
        
        if success:
            await self.account_repository.update(account)
            
            # ﮒﮒﺕﻟﭖﻠﮒﭨﻝﭨﻛﭦﻛﭨﭘ
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
        """ﻟ۶۲ﮒﭨﻟﭖﻠ"""
        account = await self.account_repository.find_by_id(account_id)
        
        if not account:
            return False
        
        success = account.unfreeze_cash(amount)
        
        if success:
            await self.account_repository.update(account)
            
            # ﮒﮒﺕﻟﭖﻠﻟ۶۲ﮒﭨﻛﭦﻛﭨﭘ
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
        """ﮔﺑﮔﺍﻟﺑ۵ﮔﺓﻟﭖﻠ"""
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
        """ﮒﮒﭨﭦﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶"""
        account = await self.account_repository.find_by_id(account_id)
        
        if not account:
            return {}
        
        # ﻟﺓﮒﮒﻛﺕﮔ۴ﮒﺟ،ﻝ?
        previous_snapshot = await self.account_repository.find_snapshot_by_date(
            account_id,
            snapshot_date
        )
        
# ﻟ؟۰ﻝ؟ﮒﻠ۰ﺗﮔﮔ
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
        
        # ﮒﮒﭨﭦﮒﺟ،ﻝ۶
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
        
# ﻛﺟﮒﮒﺟ،ﻝ۶
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
        """ﮒﭨﻝﭨﻟﺑ۵ﮔﺓ"""
        account = await self.account_repository.find_by_id(account_id)
        
        if not account:
            return False
        
        success = account.freeze_account(reason)
        
        if success:
            await self.account_repository.update(account)
            
            # ﮒﮒﺕﻟﺑ۵ﮔﺓﮒﭨﻝﭨﻛﭦﻛﭨﭘ
            await self.event_publisher.publish({
                'event_type': 'AccountFrozen',
                'account_id': account.id,
                'reason': reason,
                'timestamp': datetime.now().isoformat()
            })
        
        return success
    
    async def unfreeze_account(self, account_id: int) -> bool:
        """ﻟ۶۲ﮒﭨﻟﺑ۵ﮔﺓ"""
        account = await self.account_repository.find_by_id(account_id)
        
        if not account:
            return False
        
        success = account.unfreeze_account()
        
        if success:
            await self.account_repository.update(account)
            
            # ﮒﮒﺕﻟﺑ۵ﮔﺓﻟ۶۲ﮒﭨﻛﭦﻛﭨﭘ
            await self.event_publisher.publish({
                'event_type': 'AccountUnfrozen',
                'account_id': account.id,
                'timestamp': datetime.now().isoformat()
            })
        
        return success
```

---

## 4. ﻛﭨﮒ۷ﮒ؟ﻝﺍﻟ؟ﺝﻟ؟۰

### 4.1 ﻟﺑ۵ﮔﺓﻛﭨﮒ۷ﮒ؟ﻝﺍ (AccountRepositoryImpl)

```python
from typing import List, Optional
from decimal import Decimal
from datetime import date
import asyncpg

class AccountRepositoryImpl:
    """ﻟﺑ۵ﮔﺓﻛﭨﮒ۷ﮒ؟ﻝﺍ"""
    
    def __init__(self, db_pool: asyncpg.Pool, redis_client):
        self.db_pool = db_pool
        self.redis_client = redis_client
    
    async def create(self, account: Account) -> Account:
        """ﮒﮒﭨﭦﻟﺑ۵ﮔﺓ"""
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
            
# ﻝﺙﮒﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁ
            await self._cache_account(account)
            
            return account
    
    async def find_by_id(self, account_id: int) -> Optional[Account]:
"""ﮔﺗﮔ؟IDﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ"""
# ﮒﮔ۴ﻝﺙﮒ
        cached = await self._get_cached_account(account_id)
        if cached:
            return cached
        
        # ﮔ۴ﮔﺍﮔ؟ﮒﭦ
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
            
# ﻝﺙﮒﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁ
            await self._cache_account(account)
            
            return account
    
    async def find_all(
        self,
        account_type: Optional[str] = None,
        status: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> List[Account]:
        """ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓﮒﻟ۰۷"""
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
        """ﮔﺑﮔﺍﻟﺑ۵ﮔﺓ"""
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
            
# ﮔﺑﮔﺍﻝﺙﮒ
            await self._cache_account(account)
            
            return account
    
    async def create_snapshot(self, snapshot: AccountSnapshot) -> AccountSnapshot:
        """ﮒﮒﭨﭦﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶"""
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
"""ﻝﺙﮒﻟﺑ۵ﮔﺓﻛﺟ۰ﮔﺁ"""
        key = f"account:{account.id}"
        await self.redis_client.setex(
            key,
            300,  # 5ﮒﻠﻟﺟﮔ
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
"""ﻟﺓﮒﻝﺙﮒﻝﻟﺑ۵ﮔﺓﻛﺟ۰ﮔ?""
        key = f"account:{account_id}"
        cached = await self.redis_client.get(key)
        
        if cached:
# TODO: ﮒﮒﭦﮒﮒﻝﺙﮒﮔﺍﮔ؟
            return None
        
        return None
    
    def _row_to_account(self, row) -> Account:
        """ﮔﺍﮔ؟ﮒﭦﻟ۰ﻟﺛ؛ﻟﺑ۵ﮔﺓﮒ؟ﻛﺛ?""
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

## 5. ﮔ۶ﻟﺛﻛﺕﻝﮔ?

### 5.1 ﮔ۶ﻟﺛﮔﮔ

| ﮔﻛﺛ | ﮒﮒﭦﮔﭘﻠﺑ | ﮒ۳ﮔﺏ۷ |
|------|----------|------|
| **ﮒﮒﭨﭦﻟﺑ۵ﮔﺓ** | < 300ms | ﮒﮒ،ﮔﺍﮔ؟ﮒﭦﮒﮒ?|
| **ﮔ۴ﻟﺁ۱ﻟﺑ۵ﮔﺓ** | < 50ms | Redisﻝﺙﮒﮒﺛﻛﺕ |
| **ﮔﺑﮔﺍﻟﭖﻠ** | < 200ms | ﮒﮒ،ﮔﺍﮔ؟ﮒﭦﮔﺑﮔ?|
| **ﮒﮒﭨﭦﮒﺟ،ﻝ۶** | < 500ms | ﮒﮒ،ﮔﮔﻟ؟۰ﻝ؟ |

### 5.2 ﻝﺙﮒﻝﻝ۴

| ﮔﺍﮔ؟ﻝﺎﭨﮒ | ﻝﺙﮒﮔﭘﻠﺑ | ﻝﺙﮒﻝﻝ۴ |
|----------|----------|----------|
| **ﻟﺑ۵ﮔﺓﮒﭦﮔ؛ﻛﺟ۰ﮔﺁ** | 5ﮒﻠ | Redisﻝﺙﮒ |
| **ﻟﺑ۵ﮔﺓﻟﭖﻠﻛﺟ۰ﮔﺁ** | 1ﮒﻠ | Redisﻝﺙﮒ |
| **ﻟﺑ۵ﮔﺓﮒﺟ،ﻝ۶** | ﻛﺕﻝﺙﮒ?| ﮒ؟ﮔﭘﮔ۴ﻟﺁ۱ |

---

**ﻝﮔ؛**: 1.0.0 | **ﮔﺑﮔﺍﮔ۴ﮔ**: 2026-04-02 | **ﻝﭘﮔ?*: ﻗ?ﮒﺓﺎﮒ؟ﮔ? 
**ﻛﺕﻛﺕﮔ?*: P0-7 ﻟ؟۱ﮒﻝ؟۰ﻝﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰