---
module_id: TRADING_COST_TEST_CASE_DESIGN_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 个人开发者
standard_type: 专业量化机构文档
responsibility:
  - 扩展功能、辅助模块
---
---

---
module_id: TEST_DESIGN_002
version: 1.0.0
status: Active
created_date: 2026-04-02
last_updated: 2026-04-02
owner: ﻠ۵ﮒﺕ­ﻟﮒﺝﮔﭘﮔﮒﺕ?
responsibility:
  - 因子计算
  - 交易执行
  - 机器学习
standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﭖﻟﺁﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲
applicable_scope: ﻛﭦ۳ﮔﮔﮔ؛ﮔ۷۰ﮒ
compliance_level: ﮔﭘﮔﮔ ﮒ
parent_document: ../INDEX.md
implementation_status: ﻟﺟﻟ۰ﻛﺕ?---


# ﻛﭦ۳ﮔﮔﮔ؛ﮔﭖﻟﺁﻝ۷ﻛﺝﻟ؟ﺝﻟ؟۰
> **核心职责**: 文档内容说明
> **职责边界**: 
> - ✅ 本文档负责：文档内容说明相关内容
> - ❌ 本文档不负责：其他模块内容


> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.0 - ﻛﭦ۳ﮔﮔﮔ؛ﮔ۷۰ﮒﮔﭖﻟﺁﻝ۷ﻛﺝﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰
> **ﻝﺑ۱ﮒﺙ**: `TEST_TRADING_COSTS_001`
> **ﮔﭖﻟﺁﻝﺎﭨﮒ**: ﮒﮒﮔﭖﻟﺁﻙﻠﮔﮔﭖﻟﺁﻙﮔ۶ﻟﺛﮔﭖﻟﺁﻙﻟﺝﺗﻝﮔ۰ﻛﭨﭘﮔﭖﻟﺁ?
> **ﮔ ﺕﮒﺟﻝ؟ﮔ **: ﻝ۰؟ﻛﺟﻛﭦ۳ﮔﮔﮔ؛ﻟ؟۰ﻝ؟ﻝﺎﺝﻝ۰؟ﻙﮒﺁﻠ ﻙﻠ،ﮔ۶ﻟﺛ

## 1. ﮔﭖﻟﺁﻝ­ﻝ۴

### 1.1 ﮔﭖﻟﺁﻝﭦ۶ﮒ،

| ﮔﭖﻟﺁﻝﭦ۶ﮒ، | ﮔﭖﻟﺁﻝ؟ﮔ  | ﮔﭖﻟﺁﮔﺗﮔﺏ | ﮔﭖﻟﺁﮒﺓ۴ﮒﺓ |
|----------|----------|----------|----------|
| **ﮒﮒﮔﭖﻟﺁ** | ﻠ۹ﻟﺁﮒﻛﺕ۹ﮒﺛﮔﺍ/ﮔﺗﮔﺏﮔ­۲ﻝ۰؟ﮔ?| ﻝﺛﻝﮔﭖﻟﺁﻙﻟﺝﺗﻝﮒﺙﮒﮔ?| pytestﻙunittest |
| **ﻠﮔﮔﭖﻟﺁ** | ﻠ۹ﻟﺁﮔ۷۰ﮒﻠﺑﻛﭦ۳ﻛﭦﮔ­۲ﻝ۰؟ﮔ?| ﮔ۴ﮒ۲ﮔﭖﻟﺁﻙﮔﺍﮔ؟ﮔﭖﮔﭖﻟﺁ | pytestﻙmock |
| **ﻝﺏﭨﻝﭨﮔﭖﻟﺁ** | ﻠ۹ﻟﺁﮔﺑﻛﺕ۹ﮔﮔ؛ﻟ؟۰ﻝ؟ﻝﺏﭨﻝﭨ | ﻝ،ﺁﮒﺍﻝ،ﺁﮔﭖﻟﺁﻙﮒﭦﮔﺁﮔﭖﻟﺁ?| pytestﻙﻠﮔﻝﺁﮒ۱?|
| **ﮔ۶ﻟﺛﮔﭖﻟﺁ** | ﻠ۹ﻟﺁﻟ؟۰ﻝ؟ﮔ۶ﻟﺛﮒﻟﭖﮔﭦﻛﺛﺟﻝ?| ﮒﮒﮔﭖﻟﺁﻙﻟﺑﻟﺛﺛﮔﭖﻟﺁ?| pytest-benchmarkﻙmemory-profiler |
| **ﮒﮒﺛﮔﭖﻟﺁ** | ﻠ۹ﻟﺁﻛﺟ؟ﮔﺗﻛﺕﮒﺛﺎﮒﻝﺍﮔﮒﻟ?| ﻟ۹ﮒ۷ﮒﮔﭖﻟﺁﮒ۴ﻛﭨ?| pytestﻙGitHub Actions |

### 1.2 ﮔﭖﻟﺁﻝﺁﮒ۱

```yaml
ﮔﭖﻟﺁﻝﺁﮒ۱ﻠﻝﺛ؟:
  ﮒﺙﮒﻝﺁﮒ۱?
    python_version: "3.13"
    os: "Windows/Linux/macOS"
    ﮒﮒ­: ">=8GB"
    
  ﮔﭖﻟﺁﮔﺍﮔ؟:
    ﮔ ﺓﮔ؛ﮔﺍﻠ: 1000ﻛﺕ۹ﮔﭖﻟﺁﻟ؟۱ﮒ?
    ﮒﺕﮒﭦﻝﺎﭨﮒ: SH, SZ
    ﻟﺁﮒﺕﻝﺎﭨﮒ،: STOCK, ETF, BOND, CONVERTIBLE_BOND
    ﻛﭨﺓﮔ ﺙﻟﮒﺑ: 0.1-1000ﮒ?
    ﮔﺍﻠﻟﮒﺑ: 100-1000000ﻟ?
    
  ﻛﺝﻟﭖﮒﭦ?
    pytest: ">=7.0"
    pytest-benchmark: ">=3.4"
    pytest-mock: ">=3.10"
    pytest-cov: ">=4.1"
    yaml: ">=6.0"
    numpy: ">=1.24"
    pandas: ">=2.0"
```

### 1.3 ﮔﭖﻟﺁﮔﺍﮔ؟ﮒﮒ۳

```python
ﮔﭖﻟﺁﮔﺍﮔ؟ﻝﮔﻝ­ﻝ۴:
  1. ﮒﭦﻝ۰ﮔﭖﻟﺁﮔﺍﮔ؟: ﮔﮒ۷ﻝﺙﮒﻝﮒﺕﮒﮒﭦﮔ?
  2. ﻠﮔﭦﮔﭖﻟﺁﮔﺍﮔ؟: ﻠﮔﭦﻝﮔﻝﻟﺝﺗﻝﮒﭦﮔ?
  3. ﮒ؟ﻝﮔﭖﻟﺁﮔﺍﮔ؟: ﻛﭨﮒ؟ﻝﻛﭦ۳ﮔﮔ۴ﮒﺟﮔﮒ?
  4. ﮒﺙﮒﺕﺕﮔﭖﻟﺁﮔﺍﮔ؟: ﻠﮔﺏﻟﺝﮒ۴ﻙﻟﺝﺗﻝﮒ?
  
ﮔﭖﻟﺁﮔﺍﮔ؟ﮔﻛﭨﭘ:
  - test_data/basic_orders.json: ﮒﭦﻝ۰ﮔﭖﻟﺁﻟ؟۱ﮒ
  - test_data/random_orders_1000.json: 1000ﻛﺕ۹ﻠﮔﭦﮔﭖﻟﺁﻟ؟۱ﮒ?
  - test_data/real_orders_sample.json: ﮒ؟ﻝﻟ؟۱ﮒﮔ ﺓﮔ؛
  - test_data/edge_cases.json: ﻟﺝﺗﻝﮔ۰ﻛﭨﭘﮔﭖﻟﺁﮔﺍﮔ؟
```

## 2. ﮒﮒﮔﭖﻟﺁﻟ؟ﺝﻟ؟۰

### 2.1 CostCalculator ﻝﺎﭨﮔﭖﻟﺁ?

#### 2.1.1 ﻛﺛ۲ﻠﻟ؟۰ﻝ؟ﮔﭖﻟﺁ

```python
# test_commission.py
import pytest
from decimal import Decimal
from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory

class TestCommissionCalculation:
    """ﻛﺛ۲ﻠﻟ؟۰ﻝ؟ﮔﭖﻟﺁ"""
    
    def test_basic_commission(self):
        """ﮔﭖﻟﺁﮒﭦﻝ۰ﻛﺛ۲ﻠﻟ؟۰ﻝ؟"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        # ﮔﻛﭦ۳ﻠﻠ۱100,000ﮒﺅﺙﻛﺛ۲ﻠﻝ?.03%ﺅﺙﮔﻛﺛ?ﮒ?
        expected_commission = max(100000 * 0.0003, 5.0)
        assert result.commission == pytest.approx(expected_commission, rel=0.01)
    
    def test_min_commission(self):
        """ﮔﭖﻟﺁﮔﻛﺛﻛﺛ۲ﻠ?""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        # ﮒﺍﻠﻠ۱ﻟ؟۱ﮒﺅﺙ1000ﮒﮔﻛﭦ?
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=100,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        # 1000ﮒﺣ?.03% = 0.3ﮒﺅﺙﻛﺛﮔﻛﺛ?ﮒ?
        assert result.commission == 5.0
    
    def test_tiered_commission(self):
        """ﮔﭖﻟﺁﻠﭘﮔ۱ﺁﻛﺛ۲ﻠ"""
        config = CostConfig()
        config.commission_tiered_rates = [
            TieredRate(threshold=1000000, rate=0.0003),   # 100ﻛﺕﻛﭨ۴ﻛﺕ?
            TieredRate(threshold=5000000, rate=0.00025),  # 100-500ﻛﺕ?
            TieredRate(threshold=None, rate=0.0002)       # 500ﻛﺕﻛﭨ۴ﻛﺕ?
        ]
        
        calculator = CostCalculator(config)
        
        # ﮔﭖﻟﺁﮒﺍﻠﻠ۱ﺅﺙ50ﻛﺕﮒ
        order1 = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=50000,
            price=10.0,  # 50ﻛﺕﮒ
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        result1 = calculator.calculate_total_cost(order1)
        expected1 = max(500000 * 0.0003, 5.0)  # 150ﮒ?
        assert result1.commission == pytest.approx(expected1, rel=0.01)
        
        # ﮔﭖﻟﺁﻛﺕ­ﻠﻠ۱ﺅﺙ300ﻛﺕﮒ
        order2 = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=100000,
            price=30.0,  # 300ﻛﺕﮒ
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        result2 = calculator.calculate_total_cost(order2)
        expected2 = 3000000 * 0.00025  # 750ﮒ?
        assert result2.commission == pytest.approx(expected2, rel=0.01)
        
        # ﮔﭖﻟﺁﮒ۳۶ﻠﻠ۱ﺅﺙ1000ﻛﺕﮒ
        order3 = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=100000,
            price=100.0,  # 1000ﻛﺕﮒ
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        result3 = calculator.calculate_total_cost(order3)
        expected3 = 10000000 * 0.0002  # 2000ﮒ?
        assert result3.commission == pytest.approx(expected3, rel=0.01)
    
    def test_commission_exempt(self):
        """ﮔﭖﻟﺁﮒﻛﺛ۲ﻠﻟﺁﮒ?""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        # ﻟﺑ۶ﮒﺕﮒﭦﻠﮒﻛﺛ۲ﻠ?
        order = OrderInfo(
            symbol="511880.SH",
            side=OrderSide.BUY,
            quantity=10000,
            price=100.0,
            market=MarketType.SH,
            category=SecurityCategory.MONEY_FUND
        )
        
        result = calculator.calculate_total_cost(order)
        assert result.commission == 0.0
    
    def test_commission_max_limit(self):
        """ﮔﭖﻟﺁﮔﻠ،ﻛﺛ۲ﻠﻠﮒ?""
        config = CostConfig()
        config.max_commission = 1000.0  # ﮔﻠ،ﻛﺛ۲ﻠ?000ﮒ?
        calculator = CostCalculator(config)
        
        # ﮒ۳۶ﻠ۱ﻟ؟۱ﮒﺅﺙ?000ﻛﺕﮒﺅﺙﻛﺛ۲ﻠﮒﭦﻛﺕ?000ﮒﺅﺙﻛﺛﻠﮒﭘﻛﺕﭦ1000ﮒ?
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=100000,
            price=100.0,  # 1000ﻛﺕﮒ
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        assert result.commission == 1000.0
    
    @pytest.mark.parametrize("amount,expected", [
        (1000, 5.0),      # ﮔﻛﺛﻛﺛ۲ﻠ?
        (10000, 5.0),     # ﮔﻛﺛﻛﺛ۲ﻠ?
        (50000, 15.0),    # 50000ﺣ0.0003=15
        (100000, 30.0),   # 100000ﺣ0.0003=30
        (1000000, 300.0), # 1000000ﺣ0.0003=300
        (5000000, 1250.0),# 5000000ﺣ0.00025=1250
        (10000000, 2000.0),# 10000000ﺣ0.0002=2000
    ])
    def test_commission_parametrized(self, amount, expected):
        """ﮒﮔﺍﮒﮔﭖﻟﺁﻛﺛ۲ﻠﻟ؟۰ﻝ؟?""
        config = CostConfig()
        config.commission_tiered_rates = [
            TieredRate(threshold=1000000, rate=0.0003),
            TieredRate(threshold=5000000, rate=0.00025),
            TieredRate(threshold=None, rate=0.0002)
        ]
        
        calculator = CostCalculator(config)
        
        # ﮔ ﺗﮔ؟ﻠﻠ۱ﻟ؟۰ﻝ؟ﮔﺍﻠﮒﻛﭨﺓﮔ ?
        price = 10.0
        quantity = int(amount / price)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=quantity,
            price=price,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        assert result.commission == pytest.approx(expected, rel=0.01)
```

#### 2.1.2 ﮒﺍﻟﺎﻝ۷ﻟ؟۰ﻝ؟ﮔﭖﻟﺁ?

```python
# test_stamp_tax.py
import pytest
from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory

class TestStampTaxCalculation:
    """ﮒﺍﻟﺎﻝ۷ﻟ؟۰ﻝ؟ﮔﭖﻟﺁ?""
    
    def test_stamp_tax_on_sell(self):
        """ﮔﭖﻟﺁﮒﮒﭦﮔﭘﮒﺍﻟﺎﻝ۷"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.SELL,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        # ﮒﮒﭦ100,000ﮒﺅﺙﮒﺍﻟﺎﻝ۷?.1% = 100ﮒ?
        expected_stamp_tax = 100000 * 0.001
        assert result.stamp_tax == pytest.approx(expected_stamp_tax, rel=0.01)
    
    def test_stamp_tax_exempt_on_buy(self):
        """ﮔﭖﻟﺁﻛﺗﺍﮒ۴ﮔﭘﮒﮒﺍﻟﺎﻝ۷?""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        assert result.stamp_tax == 0.0
    
    def test_etf_stamp_tax_exempt(self):
        """ﮔﭖﻟﺁETFﮒﮒﺍﻟﺎﻝ۷"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        # ETFﮒﮒﭦﻛﺗﮒﭦﮒﮒﺍﻟﺎﻝ۷
        order = OrderInfo(
            symbol="510300.SH",
            side=OrderSide.SELL,
            quantity=10000,
            price=3.0,
            market=MarketType.SH,
            category=SecurityCategory.ETF
        )
        
        result = calculator.calculate_total_cost(order)
        assert result.stamp_tax == 0.0
    
    def test_bond_stamp_tax_exempt(self):
        """ﮔﭖﻟﺁﮒﭦﮒﺕﮒﮒﺍﻟﺎﻝ۷"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        # ﮒﭦﮒﺕﮒﮒﭦﻛﺗﮒﭦﮒﮒﺍﻟﺎﻝ۷
        order = OrderInfo(
            symbol="123456.SZ",
            side=OrderSide.SELL,
            quantity=1000,
            price=100.0,
            market=MarketType.SZ,
            category=SecurityCategory.BOND
        )
        
        result = calculator.calculate_total_cost(order)
        assert result.stamp_tax == 0.0
    
    def test_stamp_tax_configurable(self):
        """ﮔﭖﻟﺁﮒﺍﻟﺎﻝ۷ﮒﺁﻠﻝﺛ؟"""
        config = CostConfig()
        config.stamp_tax_on_sell_only = False  # ﻛﺗﺍﮒ۴ﻛﺗﮔﭘﮒﺍﻟﺎﻝ۷?
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        # ﻛﺗﺍﮒ۴ﮔﭘﻛﺗﮔﭘﮒﺍﻟﺎﻝ۷
        expected_stamp_tax = 100000 * 0.001
        assert result.stamp_tax == pytest.approx(expected_stamp_tax, rel=0.01)
```

#### 2.1.3 ﻟﺟﮔﺓﻟﺑﺗﻟ؟۰ﻝ؟ﮔﭖﻟﺁ?

```python
# test_transfer_fee.py
import pytest
from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory

class TestTransferFeeCalculation:
    """ﻟﺟﮔﺓﻟﺑﺗﻟ؟۰ﻝ؟ﮔﭖﻟﺁ?""
    
    def test_sh_transfer_fee_by_par_value(self):
        """ﮔﭖﻟﺁﮔﺎ۹ﮒﺕﻟﺟﮔﺓﻟﺑﺗﺅﺙﮔﻠ۱ﻠ۱ﻟ؟۰ﻝ؟ﺅﺙ"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="600000.SH",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SH,
            category=SecurityCategory.STOCK,
            par_value=1.0
        )
        
        result = calculator.calculate_total_cost(order)
        # ﮔﺎ۹ﮒﺕﺅﺙ?0000ﻟ۰ﺣ?ﮒﻠ۱ﮒﺙﺣ?.001% = 0.1ﮒﺅﺙﮔﻛﺛ?ﮒ?
        expected_fee = max(10000 * 1.0 * 0.00001, 1.0)
        assert result.transfer_fee == pytest.approx(expected_fee, rel=0.01)
    
    def test_sz_transfer_fee_by_amount(self):
        """ﮔﭖﻟﺁﮔﺓﺎﮒﺕﻟﺟﮔﺓﻟﺑﺗﺅﺙﮔﮔﻛﭦ۳ﻠﻠ۱ﻟ؟۰ﻝ؟ﺅﺙ"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        # ﮔﺓﺎﮒﺕﺅﺙ?00,000ﮒﺣ?.002% = 2ﮒﺅﺙﮔﻛﺛ?ﮒ?
        expected_fee = max(100000 * 0.00002, 1.0)
        assert result.transfer_fee == pytest.approx(expected_fee, rel=0.01)
    
    def test_min_transfer_fee(self):
        """ﮔﭖﻟﺁﮔﻛﺛﻟﺟﮔﺓﻟﺑﺗ"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        # ﮒﺍﻠﻠ۱ﻟ؟۱ﮒﺅﺙ1000ﮒﮔﻛﭦ۳ﺅﺙﮔﺓﺎﮒﺕ
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=100,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        # 1000ﮒﺣ?.002% = 0.02ﮒﺅﺙﮔﻛﺛ?ﮒ?
        assert result.transfer_fee == 1.0
    
    def test_transfer_fee_exempt(self):
        """ﮔﭖﻟﺁﮒﻟﺟﮔﺓﻟﺑﺗﻟﺁﮒﺕ"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        # ﮒﭦﮒﺕﮒﻟﺟﮔﺓﻟﺑﺗ
        order = OrderInfo(
            symbol="123456.SZ",
            side=OrderSide.BUY,
            quantity=1000,
            price=100.0,
            market=MarketType.SZ,
            category=SecurityCategory.BOND
        )
        
        result = calculator.calculate_total_cost(order)
        assert result.transfer_fee == 0.0
    
    def test_par_value_override(self):
        """ﮔﭖﻟﺁﻟ۹ﮒ؟ﻛﺗﻠ۱ﮒ?""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        # ﻟ۰ﻝ۴۷ﻠ۱ﮒﺙﻛﺕﮔ?ﮒﻝﮔﮒﭖﺅﺙﻝﻟ؟ﭦﻛﺕﻝﺛﻟ۶ﺅﺙ?
        order = OrderInfo(
            symbol="600000.SH",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SH,
            category=SecurityCategory.STOCK,
            par_value=0.1  # ﻠ۱ﮒ?.1ﮒ?
        )
        
        result = calculator.calculate_total_cost(order)
        # ﮔﺎ۹ﮒﺕﺅﺙ?0000ﻟ۰ﺣ?.1ﮒﻠ۱ﮒﺙﺣ?.001% = 0.01ﮒﺅﺙﮔﻛﺛ?ﮒ?
        expected_fee = max(10000 * 0.1 * 0.00001, 1.0)
        assert result.transfer_fee == pytest.approx(expected_fee, rel=0.01)
```

#### 2.1.4 ﻟ۶ﻟﺑﺗﻟ؟۰ﻝ؟ﮔﭖﻟﺁ

```python
# test_regulatory_fees.py
import pytest
from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory

class TestRegulatoryFeesCalculation:
    """ﻟ۶ﻟﺑﺗﻟ؟۰ﻝ؟ﮔﭖﻟﺁ"""
    
    def test_basic_regulatory_fees(self):
        """ﮔﭖﻟﺁﮒﭦﻝ۰ﻟ۶ﻟﺑﺗﻟ؟۰ﻝ؟"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        # ﻟ۶ﻟﺑﺗﺅﺙ?00,000ﮒﺣ?.002% = 2ﮒ?
        expected_fees = 100000 * 0.00002
        assert result.regulatory_fees == pytest.approx(expected_fees, rel=0.01)
    
    def test_regulatory_fees_exempt(self):
        """ﮔﭖﻟﺁﮒﻟ۶ﻟﺑﺗﻟﺁﮒ?""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        # ﮒﭦﮒﺕﮒﻟ۶ﻟﺑ?
        order = OrderInfo(
            symbol="123456.SZ",
            side=OrderSide.BUY,
            quantity=1000,
            price=100.0,
            market=MarketType.SZ,
            category=SecurityCategory.BOND
        )
        
        result = calculator.calculate_total_cost(order)
        assert result.regulatory_fees == 0.0
    
    def test_regulatory_components(self):
        """ﮔﭖﻟﺁﻟ۶ﻟﺑﺗﻝﭨﮔﮔﻝﭨ"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        
        # ﻠ۹ﻟﺁﻟ۶ﻟﺑﺗﻝﭨﮔ
        components = config.regulatory_components
        total_rate = sum(components.values())
        expected_fees = 100000 * total_rate
        
        assert result.regulatory_fees == pytest.approx(expected_fees, rel=0.01)
    
    def test_regulatory_fees_on_both_sides(self):
        """ﮔﭖﻟﺁﻟ۶ﻟﺑﺗﮒﮒﮔﭘﮒ"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        # ﻛﺗﺍﮒ۴ﮒﮒﮒﭦﻠﺛﮒﭦﮔﭘﮒﻟ۶ﻟﺑ?
        buy_order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        sell_order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.SELL,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        buy_result = calculator.calculate_total_cost(buy_order)
        sell_result = calculator.calculate_total_cost(sell_order)
        
        # ﻛﺗﺍﮒ۴ﮒﮒﮒﭦﻝﻟ۶ﻟﺑﺗﮒﭦﻟﺁ۴ﻝﺕﮒ
        assert buy_result.regulatory_fees == pytest.approx(sell_result.regulatory_fees, rel=0.01)
        assert buy_result.regulatory_fees > 0
```

#### 2.1.5 ﮔﭨﻝﺗﮔﮔ؛ﻟ؟۰ﻝ؟ﮔﭖﻟﺁ

```python
# test_slippage.py
import pytest
from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory

class TestSlippageCalculation:
    """ﮔﭨﻝﺗﮔﮔ؛ﻟ؟۰ﻝ؟ﮔﭖﻟﺁ"""
    
    def test_basic_slippage(self):
        """ﮔﭖﻟﺁﮒﭦﻝ۰ﮔﭨﻝﺗﻟ؟۰ﻝ؟"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        # ﮒﭦﻝ۰ﮔﭨﻝﺗﺅﺙ?00,000ﮒﺣ?.02% = 20ﮒ?
        expected_slippage = 100000 * 0.0002
        assert result.slippage == pytest.approx(expected_slippage, rel=0.01)
    
    def test_slippage_with_market_data(self):
        """ﮔﭖﻟﺁﮒﺕ۵ﮒﺕﮒﭦﮔﺍﮔ؟ﻝﮔﭨﻝﺗﻟ؟۰ﻝ؟"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        # ﻠ،ﮔﭖﮒ۷ﮔ۶ﻟ۰ﻝ۴?
        order1 = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK,
            market_data={
                "daily_volume": 50000000,  # 5000ﻛﺕﺅﺙﻠ،ﮔﭖﮒ۷ﮔ?
                "volatility": 0.02,        # 2%ﮔﺏ۱ﮒ۷ﻝﺅﺙﻛﺕ­ﻝ­
                "avg_trade_size": 10000
            }
        )
        
        result1 = calculator.calculate_total_cost(order1)
        # ﻠ،ﮔﭖﮒ۷ﮔ۶ﺅﺙﮒ ﮒ­0.5ﺅﺙﻛﺕ­ﻝ­ﮔﺏ۱ﮒ۷ﻝﺅﺙﮒ ﮒ­?.2
        # ﮒﭦﻝ۰ﮔﭨﻝﺗﻝ?.02% ﺣ 0.5 ﺣ 1.2 = 0.012%
        expected_slippage1 = 100000 * 0.0002 * 0.5 * 1.2
        assert result1.slippage == pytest.approx(expected_slippage1, rel=0.01)
        
        # ﻛﺛﮔﭖﮒ۷ﮔ۶ﻟ۰ﻝ۴?
        order2 = OrderInfo(
            symbol="000002.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK,
            market_data={
                "daily_volume": 500000,    # 50ﻛﺕﺅﺙﻛﺛﮔﭖﮒ۷ﮔ?
                "volatility": 0.04,        # 4%ﮔﺏ۱ﮒ۷ﻝﺅﺙﻠ،?
                "avg_trade_size": 5000
            }
        )
        
        result2 = calculator.calculate_total_cost(order2)
        # ﻛﺛﮔﭖﮒ۷ﮔ۶ﺅﺙﮒ ﮒ­2.0ﺅﺙﻠ،ﮔﺏ۱ﮒ۷ﻝﺅﺙﮒ ﮒ­1.5
        # ﮒﭦﻝ۰ﮔﭨﻝﺗﻝ?.02% ﺣ 2.0 ﺣ 1.5 = 0.06%
        expected_slippage2 = 100000 * 0.0002 * 2.0 * 1.5
        assert result2.slippage == pytest.approx(expected_slippage2, rel=0.01)
    
    def test_slippage_order_size_factor(self):
        """ﮔﭖﻟﺁﻟ؟۱ﮒﮒ۳۶ﮒﺍﮒ ﮒ­"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        # ﮒﺍﮒ
        order1 = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=1000,  # ﮒﺍﮒ
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK,
            market_data={
                "daily_volume": 10000000,
                "volatility": 0.02,
                "avg_trade_size": 10000
            }
        )
        
        result1 = calculator.calculate_total_cost(order1)
        # ﮒﺍﮒﺅﺙﮒ ﮒ­?.0
        expected_slippage1 = 10000 * 0.0002 * 1.0 * 1.0 * 1.0
        assert result1.slippage == pytest.approx(expected_slippage1, rel=0.01)
        
        # ﮒ۳۶ﮒ
        order2 = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=200000,  # ﮒ۳۶ﮒﺅﺙ?0ﮒﮒﺗﺏﮒﮔﻛﭦ۳ﻠ۱ﺅﺙ?
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK,
            market_data={
                "daily_volume": 10000000,
                "volatility": 0.02,
                "avg_trade_size": 10000
            }
        )
        
        result2 = calculator.calculate_total_cost(order2)
        # ﮒ۳۶ﮒﺅﺙﮒ ﮒ­?.5
        expected_slippage2 = 2000000 * 0.0002 * 1.0 * 1.0 * 1.5
        assert result2.slippage == pytest.approx(expected_slippage2, rel=0.01)
    
    def test_slippage_time_factor(self):
        """ﮔﭖﻟﺁﮔﭘﻠﺑﮒ ﮒ­"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        # ﮒﺙﻝﮔﭘﮔ؟?
        order1 = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK,
            timestamp="2026-04-02 09:15:00",  # ﮒﺙﻝﮔﭘﮔ؟?
            market_data={
                "daily_volume": 10000000,
                "volatility": 0.02,
                "avg_trade_size": 10000
            }
        )
        
        result1 = calculator.calculate_total_cost(order1)
        # ﮒﺙﻝﮔﭘﮔ؟ﭖﺅﺙﮒ ﮒ­1.5
        expected_slippage1 = 100000 * 0.0002 * 1.0 * 1.0 * 1.0 * 1.5
        assert result1.slippage == pytest.approx(expected_slippage1, rel=0.01)
        
        # ﮒﻠﺑﮔﭘﮔ؟ﭖ
        order2 = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK,
            timestamp="2026-04-02 12:30:00",  # ﮒﻠﺑﮔﭘﮔ؟ﭖ
            market_data={
                "daily_volume": 10000000,
                "volatility": 0.02,
                "avg_trade_size": 10000
            }
        )
        
        result2 = calculator.calculate_total_cost(order2)
        # ﮒﻠﺑﮔﭘﮔ؟ﭖﺅﺙﮒ ﮒ­?.8
        expected_slippage2 = 100000 * 0.0002 * 1.0 * 1.0 * 1.0 * 0.8
        assert result2.slippage == pytest.approx(expected_slippage2, rel=0.01)
    
    def test_slippage_max_rate(self):
        """ﮔﭖﻟﺁﮔﮒ۳۶ﮔﭨﻝﺗﻝﻠﮒﭘ"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        # ﮔﻝ،ﺁﮔﮒﭖﺅﺙﮔﮔﮒ ﮒ­ﻠﺛﮒﮔﮒ۳۶ﮒ?
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=200000,  # ﮒ۳۶ﮒ
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK,
            timestamp="2026-04-02 09:15:00",  # ﮒﺙﻝﮔﭘﮔ؟?
            market_data={
                "daily_volume": 500000,    # ﻛﺛﮔﭖﮒ۷ﮔ?
                "volatility": 0.04,        # ﻠ،ﮔﺏ۱ﮒ۷ﻝ
                "avg_trade_size": 5000
            }
        )
        
        result = calculator.calculate_total_cost(order)
        # ﻟ؟۰ﻝ؟ﻝﻟ؟ﭦﮔﭨﻝﺗﻝﺅﺙ0.02% ﺣ 2.0 ﺣ 1.5 ﺣ 1.5 ﺣ 1.5 = 0.135%
        # ﻛﺛﮔﮒ۳۶ﻠﮒﭘﻛﺕﭦ1%ﺅﺙﮔﻛﭨ۴ﮒﭦﻛﺕ?.135% < 1%ﺅﺙﻛﺛﺟﻝ۷ﻟ؟۰ﻝ؟ﮒ?
        # ﮒ۵ﮔﻟﭘﻟﺟ1%ﺅﺙﮒﻠﮒﭘﻛﺕ?%
        
        # ﻠ۹ﻟﺁﮔﭨﻝﺗﻝﻛﺕﻟﭘﻟﺟ1%
        amount = order.quantity * order.price
        slippage_rate = result.slippage / amount if amount > 0 else 0
        assert slippage_rate <= 0.01  # ﻛﺕﻟﭘﻟﺟ?%
```

#### 2.1.6 ﮔﭨﮔﮔ؛ﻟ؟۰ﻝ؟ﮔﭖﻟﺁ?

```python
# test_total_cost.py
import pytest
from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory

class TestTotalCostCalculation:
    """ﮔﭨﮔﮔ؛ﻟ؟۰ﻝ؟ﮔﭖﻟﺁ?""
    
    def test_total_cost_buy(self):
        """ﮔﭖﻟﺁﻛﺗﺍﮒ۴ﮔﭨﮔﮔ?""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        
        # ﻟ؟۰ﻝ؟ﮒﻠ۰ﺗﮔﮔ؛
        amount = 100000
        commission = max(amount * 0.0003, 5.0)  # 30ﮒ?
        stamp_tax = 0.0  # ﻛﺗﺍﮒ۴ﮒﮒﺍﻟﺎﻝ۷
        transfer_fee = max(amount * 0.00002, 1.0)  # 2ﮒ?
        regulatory_fees = amount * 0.00002  # 2ﮒ?
        slippage = amount * 0.0002  # 20ﮒ?
        
        expected_total = commission + stamp_tax + transfer_fee + regulatory_fees + slippage
        expected_percentage = expected_total / amount
        
        assert result.total_cost == pytest.approx(expected_total, rel=0.01)
        assert result.as_percentage == pytest.approx(expected_percentage, rel=0.0001)
        assert result.total_cost > 0
    
    def test_total_cost_sell(self):
        """ﮔﭖﻟﺁﮒﮒﭦﮔﭨﮔﮔ?""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.SELL,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        
        # ﻟ؟۰ﻝ؟ﮒﻠ۰ﺗﮔﮔ؛
        amount = 100000
        commission = max(amount * 0.0003, 5.0)  # 30ﮒ?
        stamp_tax = amount * 0.001  # 100ﮒ?
        transfer_fee = max(amount * 0.00002, 1.0)  # 2ﮒ?
        regulatory_fees = amount * 0.00002  # 2ﮒ?
        slippage = amount * 0.0002  # 20ﮒ?
        
        expected_total = commission + stamp_tax + transfer_fee + regulatory_fees + slippage
        expected_percentage = expected_total / amount
        
        assert result.total_cost == pytest.approx(expected_total, rel=0.01)
        assert result.as_percentage == pytest.approx(expected_percentage, rel=0.0001)
        
        # ﮒﮒﭦﮔﮔ؛ﮒﭦﻠ،ﻛﭦﻛﺗﺍﮒ۴ﮔﮔ؛ﺅﺙﮒ ﻛﺕﭦﮔﮒﺍﻟﺎﻝ۷ﺅﺙ?
        assert result.total_cost > (expected_total - stamp_tax)
    
    def test_total_cost_etf(self):
        """ﮔﭖﻟﺁETFﮔﭨﮔﮔ؛ﺅﺙﮒﮒﺍﻟﺎﻝ۷ﺅﺙ?""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="510300.SH",
            side=OrderSide.SELL,
            quantity=10000,
            price=3.0,
            market=MarketType.SH,
            category=SecurityCategory.ETF
        )
        
        result = calculator.calculate_total_cost(order)
        
        # ETFﮒﮒﭦﮒﮒﺍﻟﺎﻝ۷
        assert result.stamp_tax == 0.0
        
        # ﮔﭨﮔﮔ؛ﮒﭦﻛﺛﻛﭦﻟ۰ﻝ۴۷ﮒﮒﭦﮔﮔ؛
        amount = 30000
        stock_order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.SELL,
            quantity=10000,
            price=3.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        stock_result = calculator.calculate_total_cost(stock_order)
        
        # ETFﮔﮔ؛ﮒﭦﻛﺛﻛﭦﻟ۰ﻝ۴۷ﮔﮔ؛ﺅﺙﮒ ﻛﺕﭦﮒﮒﺍﻟﺎﻝ۷ﺅﺙ?
        assert result.total_cost < stock_result.total_cost
    
    def test_cost_breakdown(self):
        """ﮔﭖﻟﺁﻟﺑﺗﻝ۷ﮔﻝﭨ"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        breakdown = result.breakdown
        
        # ﻠ۹ﻟﺁﮔﻝﭨﮒﮒ،ﮔﮔﮔﮔ؛ﻝﺎﭨﮒ?
        assert "commission" in breakdown
        assert "stamp_tax" in breakdown
        assert "transfer_fee" in breakdown
        assert "regulatory_fees" in breakdown
        assert "slippage" in breakdown
        
        # ﻠ۹ﻟﺁﮔﻝﭨﻠﻠ۱ﻛﺕﮔﭨﮔﮔ؛ﻛﺕﻟ?
        total_from_breakdown = sum(breakdown.values())
        assert total_from_breakdown == pytest.approx(result.total_cost, rel=0.01)
        
        # ﻠ۹ﻟﺁﮔﻝﭨﻠﻠ۱ﻛﺕﮒﻠ۰ﺗﮔﮔ؛ﻛﺕﻟ?
        assert breakdown["commission"] == pytest.approx(result.commission, rel=0.01)
        assert breakdown["stamp_tax"] == pytest.approx(result.stamp_tax, rel=0.01)
        assert breakdown["transfer_fee"] == pytest.approx(result.transfer_fee, rel=0.01)
        assert breakdown["regulatory_fees"] == pytest.approx(result.regulatory_fees, rel=0.01)
        assert breakdown["slippage"] == pytest.approx(result.slippage, rel=0.01)
    
    def test_cache_functionality(self):
        """ﮔﭖﻟﺁﻝﺙﮒ­ﮒﻟﺛ"""
        config = CostConfig()
        config.cache_enabled = True
        config.cache_ttl = 60
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        # ﻝ؛؛ﻛﺕﮔ؛۰ﻟ؟۰ﻝ؟?
        result1 = calculator.calculate_total_cost(order)
        
        # ﻝ؛؛ﻛﭦﮔ؛۰ﻟ؟۰ﻝ؟ﺅﺙﮒﭦﻛﺛﺟﻝ۷ﻝﺙﮒ­ﺅﺙ
        result2 = calculator.calculate_total_cost(order)
        
        # ﻝﭨﮔﮒﭦﻟﺁ۴ﻝﺕﮒ
        assert result1.total_cost == result2.total_cost
        
        # ﻝ۵ﻝ۷ﻝﺙﮒ­ﮒﻠﮔﺍﻟ؟۰ﻝ؟?
        config.cache_enabled = False
        calculator2 = CostCalculator(config)
        result3 = calculator2.calculate_total_cost(order)
        
        # ﻝﭨﮔﮒﭦﻟﺁ۴ﻛﭨﻝﭘﻝﺕﮒ
        assert result1.total_cost == pytest.approx(result3.total_cost, rel=0.01)
```

### 2.2 ﻟﺝﺗﻝﮔ۰ﻛﭨﭘﮔﭖﻟﺁ

```python
# test_edge_cases.py
import pytest
from decimal import Decimal
from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory

class TestEdgeCases:
    """ﻟﺝﺗﻝﮔ۰ﻛﭨﭘﮔﭖﻟﺁ"""
    
    def test_zero_quantity(self):
        """ﮔﭖﻟﺁﻠﭘﮔﺍﻠ?""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=0,  # ﻠﭘﮔﺍﻠ?
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        
        # ﻠﭘﮔﺍﻠﻟ؟۱ﮒﺅﺙﮔﮔﮔﮔ؛ﮒﭦﻛﺕ?
        assert result.total_cost == 0.0
        assert result.commission == 0.0
        assert result.stamp_tax == 0.0
        assert result.transfer_fee == 0.0
        assert result.regulatory_fees == 0.0
        assert result.slippage == 0.0
        assert result.as_percentage == 0.0
    
    def test_zero_price(self):
        """ﮔﭖﻟﺁﻠﭘﻛﭨﺓﮔ ?""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=0.0,  # ﻠﭘﻛﭨﺓﮔ ?
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        
        # ﻠﭘﻛﭨﺓﮔ ﺙﻟ؟۱ﮒﺅﺙﮔﮔﮔﮔ؛ﮒﭦﻛﺕ?
        assert result.total_cost == 0.0
        assert result.commission == 0.0
        assert result.stamp_tax == 0.0
        assert result.transfer_fee == 0.0
        assert result.regulatory_fees == 0.0
        assert result.slippage == 0.0
        assert result.as_percentage == 0.0
    
    def test_negative_price(self):
        """ﮔﭖﻟﺁﻟﺑﻛﭨﺓﮔ ﺙﺅﺙﮒﺙﮒﺕﺕﮔﮒﭖﺅﺙ?""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=-10.0,  # ﻟﺑﻛﭨﺓﮔ ?
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        
        # ﻟﺑﻛﭨﺓﮔ ﺙﻟ؟۱ﮒﺅﺙﮔﻛﭦ۳ﻠﻠ۱ﻛﺕﭦﻟﺑﺅﺙﻛﺛﮔﮔ؛ﻟ؟۰ﻝ؟ﮒﭦﮒ۳ﻝ?
        amount = order.quantity * order.price  # -100,000ﮒ?
        
        # ﻛﺛ۲ﻠﺅﺙﻟﺑﻠﻠ۱ﺣﻟﺑﺗﻝﺅﺙﻛﺛﮔﻛﺛ?ﮒﺅﺙﮒﭦﻛﺕﭦ0ﮔﮒﺙﮒﺕﺕﺅﺙ
        # ﮒ؟ﻠﮒ؟ﻝﺍﻛﺕ­ﮒﭦﮒ۳ﻝﻟﺑﻠﻠ۱ﮔﮒ?
        # ﻟﺟﻠﮔﭖﻟﺁﮔ۰ﮔﭘﮔﺁﮒ۵ﻟﺛﮔ­۲ﻝ۰؟ﮒ۳ﻝ?
        assert result.total_cost <= 0  # ﮔﭨﮔﮔ؛ﮒﺁﻟﺛﻛﺕﭦ0ﮔﻟﺑ
    
    def test_negative_quantity(self):
        """ﮔﭖﻟﺁﻟﺑﮔﺍﻠﺅﺙﮒﺙﮒﺕﺕﮔﮒﭖﺅﺙ?""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=-10000,  # ﻟﺑﮔﺍﻠ?
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        
        # ﻟﺑﮔﺍﻠﻟ؟۱ﮒﺅﺙﮔﻛﭦ۳ﻠﻠ۱ﻛﺕﭦﻟﺑ
        # ﮒ؟ﻠﮒ؟ﻝﺍﻛﺕ­ﮒﭦﮒ۳ﻝﻟﺑﮔﺍﻠﮔﮒ?
        assert result.total_cost <= 0  # ﮔﭨﮔﮔ؛ﮒﺁﻟﺛﻛﺕﭦ0ﮔﻟﺑ
    
    def test_very_small_amount(self):
        """ﮔﭖﻟﺁﮔﮒﺍﻠﻠ۱"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=1,  # 1ﻟ?
            price=0.01,  # 0.01ﮒ?
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        
        # ﮔﮒﺍﻠﻠ۱ﺅﺙ?.01ﮒ?
        amount = 0.01
        
        # ﻛﺛ۲ﻠﺅﺙ?.01ﺣ0.03%=0.000003ﮒﺅﺙﻛﺛﮔﻛﺛ?ﮒ?
        # ﮒ؟ﻠﮒﭦﻛﺕﭦ5ﮒﺅﺙﻛﺛﻠﻠ۱ﮒﺍﻛﭦﻛﺛ۲ﻠﺅﺙﮒﺁﻟﺛﻝﺗﮔ؟ﮒ۳ﻝ
        # ﻟﺟﮔﺓﻟﺑﺗﺅﺙ0.01ﺣ0.002%=0.0000002ﮒﺅﺙﻛﺛﮔﻛﺛ?ﮒ?
        # ﮔﭨﮔﮔ؛ﮒﺁﻟﺛﻟﭘﻟﺟﮔﻛﭦ۳ﻠﻠ۱?
        
        # ﻠ۹ﻟﺁﻟ؟۰ﻝ؟ﻛﺕﻛﺙﮒﺑ۸ﮔﭦ
        assert isinstance(result.total_cost, float)
    
    def test_very_large_amount(self):
        """ﮔﭖﻟﺁﮔﮒ۳۶ﻠﻠ۱"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000000,  # 1000ﻛﺕﻟ۰
            price=1000.0,  # 1000ﮒ?
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        result = calculator.calculate_total_cost(order)
        
        # ﮔﮒ۳۶ﻠﻠ۱ﺅﺙ?00ﻛﭦ?
        amount = 10000000 * 1000.0
        
        # ﻠ۹ﻟﺁﻟ؟۰ﻝ؟ﻛﺕﻛﺙﮔﭦ۱ﮒﭦ
        assert isinstance(result.total_cost, float)
        assert result.total_cost > 0
        
        # ﻠ۹ﻟﺁﮔﮔ؛ﮒ ﮔﺁﮒﻝ
        assert 0 < result.as_percentage < 0.01  # ﮔﮔ؛ﮒ ﮔﺁﮒﭦﮒﺍﻛﭦ?%
    
    def test_extreme_slippage_factors(self):
        """ﮔﭖﻟﺁﮔﻝ،ﺁﮔﭨﻝﺗﮒ ﮒ­"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        # ﮔﮔﮒ ﮒ­ﻠﺛﮒﮔﻝ،ﺁﮒ?
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=200000,  # ﮔﮒ۳۶ﮒ?
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK,
            timestamp="2026-04-02 09:15:00",  # ﮒﺙﻝﮔﭘﮔ؟?
            market_data={
                "daily_volume": 1000,        # ﮔﻛﺛﮔﭖﮒ۷ﮔ?
                "volatility": 0.1,           # ﮔﻠ،ﮔﺏ۱ﮒ۷ﻝ?
                "avg_trade_size": 100
            }
        )
        
        result = calculator.calculate_total_cost(order)
        
        # ﻠ۹ﻟﺁﮔﭨﻝﺗﻛﺕﻟﭘﻟﺟﮔﮒ۳۶ﻠﮒ?
        amount = order.quantity * order.price
        slippage_rate = result.slippage / amount if amount > 0 else 0
        assert slippage_rate <= 0.01  # ﻛﺕﻟﭘﻟﺟ?%
    
    def test_rounding_edge_cases(self):
        """ﮔﭖﻟﺁﻟﮒ۴ﻟﺝﺗﻝﮔﮒﭖ"""
        config = CostConfig()
        config.precision = 2
        config.rounding_method = "ROUND"
        calculator = CostCalculator(config)
        
        # ﮔﭖﻟﺁﮒﻝ۶ﻟﮒ۴ﮔﮒﭖ
        test_cases = [
            (0.0049, 0.00),  # ﮒﻟﻛﭦﮒ۴ﺅﺙ?.0049 -> 0.00
            (0.0050, 0.01),  # ﮒﻟﻛﭦﮒ۴ﺅﺙ?.0050 -> 0.01
            (0.0149, 0.01),  # ﮒﻟﻛﭦﮒ۴ﺅﺙ?.0149 -> 0.01
            (0.0150, 0.02),  # ﮒﻟﻛﭦﮒ۴ﺅﺙ?.0150 -> 0.02
            (1.2345, 1.23),  # ﮒﻟﻛﭦﮒ۴ﺅﺙ?.2345 -> 1.23
            (1.2350, 1.24),  # ﮒﻟﻛﭦﮒ۴ﺅﺙ?.2350 -> 1.24
        ]
        
        for value, expected in test_cases:
            # ﮒﮒﭨﭦﻛﺕﻛﺕ۹ﻟ؟۱ﮒﺅﺙﻛﺛﺟﮒﺝﻛﺛ۲ﻠﻟ؟۰ﻝ؟ﻝﭨﮔﻛﺕﭦvalue
            # ﻝ؟ﮒﮔﭖﻟﺁﺅﺙﻝﺑﮔ۴ﮔﭖﻟﺁﻟﮒ۴ﮔﺗﮔﺏ
            rounded = calculator._round(value)
            assert rounded == expected, f"ﻟﮒ۴ﻠﻟﺁﺁﺅﺙ{value} -> {rounded}ﺅﺙﻠ۱ﮔﺅﺙ{expected}"
    
    def test_different_rounding_methods(self):
        """ﮔﭖﻟﺁﻛﺕﮒﻟﮒ۴ﮔﺗﮔﺏ"""
        # ﮔﭖﻟﺁﮒﻛﺕﮒﮔﺑ
        config1 = CostConfig()
        config1.precision = 2
        config1.rounding_method = "CEIL"
        calculator1 = CostCalculator(config1)
        
        assert calculator1._round(0.001) == 0.01  # ﮒﻛﺕﮒﮔﺑ
        assert calculator1._round(1.111) == 1.12   # ﮒﻛﺕﮒﮔﺑ
        
        # ﮔﭖﻟﺁﮒﻛﺕﮒﮔﺑ
        config2 = CostConfig()
        config2.precision = 2
        config2.rounding_method = "FLOOR"
        calculator2 = CostCalculator(config2)
        
        assert calculator2._round(0.009) == 0.00  # ﮒﻛﺕﮒﮔﺑ
        assert calculator2._round(1.119) == 1.11   # ﮒﻛﺕﮒﮔﺑ
        
        # ﮔﭖﻟﺁﮒﻟﻛﭦﮒ۴
        config3 = CostConfig()
        config3.precision = 2
        config3.rounding_method = "ROUND"
        calculator3 = CostCalculator(config3)
        
        assert calculator3._round(0.004) == 0.00  # ﮒﻟ
        assert calculator3._round(0.005) == 0.01  # ﻛﭦﮒ۴
```

### 2.3 ﻠﻝﺛ؟ﻠ۹ﻟﺁﮔﭖﻟﺁ

```python
# test_config_validation.py
import pytest
import yaml
from cost_calculator import CostConfig, TieredRate

class TestConfigValidation:
    """ﻠﻝﺛ؟ﻠ۹ﻟﺁﮔﭖﻟﺁ"""
    
    def test_valid_config(self):
        """ﮔﭖﻟﺁﮔﮔﻠﻝﺛ؟"""
        config = CostConfig()
        
        # ﻠ۹ﻟﺁﮒﭦﻝ۰ﻠﻝﺛ؟
        assert config.commission_rate == 0.0003
        assert config.min_commission == 5.0
        assert config.stamp_tax_rate == 0.001
        assert config.sh_transfer_rate == 0.00001
        assert config.sz_transfer_rate == 0.00002
        assert config.regulatory_rate == 0.00002
        
        # ﻠ۹ﻟﺁﻠﭨﻟ؟۳ﮒ?
        assert config.commission_tiered_rates is not None
        assert len(config.commission_tiered_rates) == 3
        assert config.stamp_tax_exempt_categories is not None
        assert len(config.stamp_tax_exempt_categories) == 4
        assert config.regulatory_components is not None
        assert len(config.regulatory_components) == 3
    
    def test_invalid_rate_range(self):
        """ﮔﭖﻟﺁﮔ ﮔﻟﺑﺗﻝﻟﮒﺑ"""
        # ﻛﺛ۲ﻠﻝﻟﭘﮒﭦﻟﮒ?
        config = CostConfig()
        config.commission_rate = 0.005  # 0.5%ﺅﺙﻟﭘﮒﭦﮒﻝﻟﮒ?
        
        # ﮒ؟ﻠﮒ؟ﻝﺍﻛﺕ­ﮒﭦﮔﻠ۹ﻟﺁﮔﭦﮒ?
        # ﻟﺟﻠﮔﭖﻟﺁﻠﻝﺛ؟ﮒﺁﺗﻟﺎ۰ﻟﺛﮒ۵ﮒﮒﭨﭦ
        
    def test_invalid_tiered_rates(self):
        """ﮔﭖﻟﺁﮔ ﮔﻠﭘﮔ۱ﺁﻟﺑﺗﻝ"""
        # ﻠﮒﺙﻛﺕﻠﮒ۱
        config = CostConfig()
        config.commission_tiered_rates = [
            TieredRate(threshold=5000000, rate=0.0003),
            TieredRate(threshold=1000000, rate=0.00025),  # ﻠﮒﺙﮒﺍﻛﭦﮒﻛﺕﻛﺕ?
            TieredRate(threshold=None, rate=0.0002)
        ]
        
        # ﻟﺑﺗﻝﻛﺕﻠﮒ
        config2 = CostConfig()
        config2.commission_tiered_rates = [
            TieredRate(threshold=1000000, rate=0.0003),
            TieredRate(threshold=5000000, rate=0.00035),  # ﻟﺑﺗﻝﮒ۳۶ﻛﭦﮒﻛﺕﻛﺕ?
            TieredRate(threshold=None, rate=0.0002)
        ]
        
        # ﮒ؟ﻠﮒ؟ﻝﺍﻛﺕ­ﮒﭦﮔﻠ۹ﻟﺁﮔﭦﮒ?
    
    def test_config_from_yaml(self):
        """ﮔﭖﻟﺁﻛﭨYAMLﮒ ﻟﺛﺛﻠﻝﺛ؟"""
        yaml_content = """
cost_config:
  commission:
    base_rate: 0.00025
    min_amount: 5.0
    tiered_rates:
      - threshold: 1000000
        rate: 0.00025
      - threshold: null
        rate: 0.0002
  stamp_tax:
    rate: 0.001
    on_sell_only: true
  transfer_fee:
    sh_rate: 0.00001
    sz_rate: 0.00002
    min_amount: 1.0
  regulatory_fees:
    total_rate: 0.00002
  slippage:
    base_rate: 0.0002
    max_rate: 0.01
"""
        
        config_dict = yaml.safe_load(yaml_content)["cost_config"]
        config = CostConfig(**config_dict)
        
        # ﻠ۹ﻟﺁﻠﻝﺛ؟ﮒ ﻟﺛﺛ
        assert config.commission_rate == 0.00025
        assert config.stamp_tax_rate == 0.001
        assert config.sh_transfer_rate == 0.00001
        assert config.slippage_base_rate == 0.0002
    
    def test_config_validation_tool(self):
        """ﮔﭖﻟﺁﻠﻝﺛ؟ﻠ۹ﻟﺁﮒﺓ۴ﮒﺓ"""
        # ﮒﮒﭨﭦﻠﻝﺛ؟ﻠ۹ﻟﺁﮒﺓ۴ﮒﺓﮔﭖﻟﺁ
        # ﮒ؟ﻠﮒ؟ﻝﺍﻛﺕ­ﮒﭦﮔﻛﺕﻠ۷ﻝﻠﻝﺛ؟ﻠ۹ﻟﺁﮒﺓ۴ﮒﺓ
        pass
```

## 3. ﻠﮔﮔﭖﻟﺁﻟ؟ﺝﻟ؟۰

### 3.1 ﮒ۳ﮒﺙﮔﻠﻠﮒ۷ﻠﮔﮔﭖﻟﺁ?

```python
# test_integration_adapters.py
import pytest
from engines.base import BaseEngineAdapter, EngineConfig, UnifiedOrder, OrderSide
from engines.factory import EngineFactory
from cost_calculator import CostCalculator, CostConfig

class TestIntegrationWithAdapters:
    """ﻠﻠﮒ۷ﻠﮔﮔﭖﻟﺁ?""
    
    def test_vnpy_adapter_integration(self):
        """ﮔﭖﻟﺁvn.pyﻠﻠﮒ۷ﻠﮔ?""
        # ﮒﮒﭨﭦvn.pyﻠﻠﮒ۷ﻠﻝﺛ?
        vnpy_config = EngineConfig(
            engine_type="vnpy",
            config_path="config/vnpy_simulation.yaml"
        )
        
        # ﮒﮒﭨﭦﻠﻠﮒ?
        factory = EngineFactory()
        adapter = factory.create_adapter(vnpy_config)
        
        # ﻠ۹ﻟﺁﻠﻠﮒ۷ﮒﮒ،ﮔﮔ؛ﻟ؟۰ﻝ؟ﮒ۷
        assert hasattr(adapter, 'cost_calculator')
        assert isinstance(adapter.cost_calculator, CostCalculator)
        
        # ﮒﮒﭨﭦﻝﭨﻛﺕﻟ؟۱ﮒ
        order = UnifiedOrder(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            order_type="LIMIT"
        )
        
        # ﮔﭖﻟﺁﮔﮔ؛ﻛﺙﺍﻝ؟
        cost_estimate = adapter.get_cost_estimate(order)
        assert "total_cost" in cost_estimate
        assert "commission" in cost_estimate
        assert "stamp_tax" in cost_estimate
        assert "transfer_fee" in cost_estimate
        assert "regulatory_fees" in cost_estimate
        assert "slippage" in cost_estimate
    
    def test_rqalpha_adapter_integration(self):
        """ﮔﭖﻟﺁRQAlphaﻠﻠﮒ۷ﻠﮔ?""
        # ﻝﺎﭨﻛﺙﺙvn.pyﻠﻠﮒ۷ﮔﭖﻟﺁ?
        pass
    
    def test_cost_report_generation(self):
        """ﮔﭖﻟﺁﮔﮔ؛ﮔ۴ﮒﻝﮔ"""
        # ﮔﭖﻟﺁﻟ؟۱ﮒﮔ۶ﻟ۰ﮒﻝﮔﻟﺁ۵ﻝﭨﮔﮔ؛ﮔ۴ﮒ?
        pass
    
    def test_multiple_adapters_consistency(self):
        """ﮔﭖﻟﺁﮒ۳ﻠﻠﮒ۷ﮔﮔ؛ﻟ؟۰ﻝ؟ﻛﺕﻟﺑﮔ?""
        # ﮒﮒﭨﭦﮒ۳ﻛﺕ۹ﻠﻠﮒ?
        factory = EngineFactory()
        
        vnpy_adapter = factory.create_adapter(
            EngineConfig(engine_type="vnpy")
        )
        
        rqalpha_adapter = factory.create_adapter(
            EngineConfig(engine_type="rqalpha")
        )
        
        # ﮒﻛﺕﻟ؟۱ﮒﮒ۷ﻛﺕﮒﻠﻠﮒ۷ﻛﺕ­ﮔﮔ؛ﮒﭦﻛﺕﻟ?
        order = UnifiedOrder(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            order_type="LIMIT"
        )
        
        vnpy_cost = vnpy_adapter.get_cost_estimate(order)
        rqalpha_cost = rqalpha_adapter.get_cost_estimate(order)
        
        # ﮔﮔ؛ﻟ؟۰ﻝ؟ﮒﭦﮒﭦﮔ؛ﻛﺕﻟﺑﺅﺙﮒﻟ؟ﺕﮒﺝ؟ﮒﺍﮒﺓ؟ﮒﺙﺅﺙ?
        assert abs(vnpy_cost["total_cost"] - rqalpha_cost["total_cost"]) < 0.01
```

### 3.2 ﻠﻝﺛ؟ﻝ؟۰ﻝﻠﮔﮔﭖﻟﺁ

```python
# test_integration_config.py
import pytest
import yaml
import tempfile
import os
from cost_calculator import CostCalculator, CostConfig

class TestIntegrationWithConfig:
    """ﻠﻝﺛ؟ﻝ؟۰ﻝﻠﮔﮔﭖﻟﺁ"""
    
    def test_config_file_loading(self):
        """ﮔﭖﻟﺁﻠﻝﺛ؟ﮔﻛﭨﭘﮒ ﻟﺛﺛ"""
        # ﮒﮒﭨﭦﻛﺕﺑﮔﭘﻠﻝﺛ؟ﮔﻛﭨﭘ
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml_content = """
cost_config:
  commission:
    base_rate: 0.00025
    min_amount: 5.0
  stamp_tax:
    rate: 0.001
    on_sell_only: true
  transfer_fee:
    sh_rate: 0.00001
    sz_rate: 0.00002
    min_amount: 1.0
  regulatory_fees:
    total_rate: 0.00002
  slippage:
    base_rate: 0.0002
"""
            f.write(yaml_content)
            config_path = f.name
        
        try:
            # ﮒ ﻟﺛﺛﻠﻝﺛ؟ﮔﻛﭨﭘ
            with open(config_path, 'r') as f:
                config_dict = yaml.safe_load(f)["cost_config"]
            
            # ﮒﮒﭨﭦﻠﻝﺛ؟ﮒﺁﺗﻟﺎ۰
            config = CostConfig(**config_dict)
            calculator = CostCalculator(config)
            
            # ﻠ۹ﻟﺁﻠﻝﺛ؟ﻝﮔ
            order = OrderInfo(
                symbol="000001.SZ",
                side=OrderSide.BUY,
                quantity=10000,
                price=10.0,
                market=MarketType.SZ,
                category=SecurityCategory.STOCK
            )
            
            result = calculator.calculate_total_cost(order)
            
            # ﻛﺛ۲ﻠﻝﮒﭦﻛﺕ?.025%
            expected_commission = max(100000 * 0.00025, 5.0)
            assert result.commission == pytest.approx(expected_commission, rel=0.01)
            
        finally:
            # ﮔﺕﻝﻛﺕﺑﮔﭘﮔﻛﭨﭘ
            os.unlink(config_path)
    
    def test_config_hot_reload(self):
        """ﮔﭖﻟﺁﻠﻝﺛ؟ﻝ­ﻠﻟﺛ?""
        # ﮔﭖﻟﺁﻟﺟﻟ۰ﮔﭘﻛﺟ؟ﮔﺗﻠﻝﺛ?
        pass
    
    def test_config_validation_integration(self):
        """ﮔﭖﻟﺁﻠﻝﺛ؟ﻠ۹ﻟﺁﻠﮔ"""
        # ﮔﭖﻟﺁﮒ ﻟﺛﺛﮔ ﮔﻠﻝﺛ؟ﮔﭘﻝﻠﻟﺁﺁﮒ۳ﻝ
        pass
```

## 4. ﮔ۶ﻟﺛﮔﭖﻟﺁﻟ؟ﺝﻟ؟۰

### 4.1 ﮒﮔ؛۰ﻟ؟۰ﻝ؟ﮔ۶ﻟﺛﮔﭖﻟﺁ

```python
# test_performance_basic.py
import pytest
import time
from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory

class TestPerformanceBasic:
    """ﮒﭦﻝ۰ﮔ۶ﻟﺛﮔﭖﻟﺁ"""
    
    def test_single_calculation_performance(self):
        """ﮔﭖﻟﺁﮒﮔ؛۰ﻟ؟۰ﻝ؟ﮔ۶ﻟﺛ"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        # ﻠ۱ﻝ­
        for _ in range(10):
            calculator.calculate_total_cost(order)
        
        # ﮔ۶ﻟﺛﮔﭖﻟﺁ
        start_time = time.perf_counter()
        for _ in range(1000):
            calculator.calculate_total_cost(order)
        end_time = time.perf_counter()
        
        total_time = end_time - start_time
        avg_time = total_time / 1000 * 1000  # ﻟﺛ؛ﮔ۱ﻛﺕﭦﮔﺁ،ﻝ۶?
        
        print(f"ﮒﮔ؛۰ﻟ؟۰ﻝ؟ﮒﺗﺏﮒﮔﭘﻠﺑ: {avg_time:.3f}ms")
        assert avg_time < 1.0  # ﻝ؟ﮔ ﺅﺙ?1ms
    
    def test_calculation_with_cache(self):
        """ﮔﭖﻟﺁﮒﺕ۵ﻝﺙﮒ­ﻝﮔ۶ﻟﺛ"""
        config = CostConfig()
        config.cache_enabled = True
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        # ﻝ؛؛ﻛﺕﮔ؛۰ﻟ؟۰ﻝ؟ﺅﺙﮔ ﻝﺙﮒ­ﺅﺙ
        start_time1 = time.perf_counter()
        result1 = calculator.calculate_total_cost(order)
        end_time1 = time.perf_counter()
        
        time1 = (end_time1 - start_time1) * 1000
        
        # ﻝ؛؛ﻛﭦﮔ؛۰ﻟ؟۰ﻝ؟ﺅﺙﮔﻝﺙﮒ­ﺅﺙ
        start_time2 = time.perf_counter()
        result2 = calculator.calculate_total_cost(order)
        end_time2 = time.perf_counter()
        
        time2 = (end_time2 - start_time2) * 1000
        
        print(f"ﻝ؛؛ﻛﺕﮔ؛۰ﻟ؟۰ﻝ؟ﺅﺙﮔ ﻝﺙﮒ­ﺅﺙ: {time1:.3f}ms")
        print(f"ﻝ؛؛ﻛﭦﮔ؛۰ﻟ؟۰ﻝ؟ﺅﺙﮔﻝﺙﮒ­ﺅﺙ: {time2:.3f}ms")
        
        # ﻝﺙﮒ­ﮒﺛﻛﺕ­ﮒﮒﭦﮔﺑﮒﺟ،
        assert time2 < time1
        
        # ﻝﭨﮔﮒﭦﻝﺕﮒ?
        assert result1.total_cost == result2.total_cost
```

### 4.2 ﮔﺗﻠﻟ؟۰ﻝ؟ﮔ۶ﻟﺛﮔﭖﻟﺁ

```python
# test_performance_batch.py
import pytest
import time
import random
from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory

class TestPerformanceBatch:
    """ﮔﺗﻠﮔ۶ﻟﺛﮔﭖﻟﺁ"""
    
    def generate_test_orders(self, count=1000):
        """ﻝﮔﮔﭖﻟﺁﻟ؟۱ﮒ"""
        orders = []
        symbols = ["000001.SZ", "000002.SZ", "600000.SH", "600036.SH"]
        sides = [OrderSide.BUY, OrderSide.SELL]
        categories = [SecurityCategory.STOCK, SecurityCategory.ETF]
        
        for i in range(count):
            symbol = random.choice(symbols)
            market = MarketType.SH if symbol.startswith("6") else MarketType.SZ
            
            order = OrderInfo(
                symbol=symbol,
                side=random.choice(sides),
                quantity=random.randint(100, 100000),
                price=random.uniform(1.0, 100.0),
                market=market,
                category=random.choice(categories)
            )
            orders.append(order)
        
        return orders
    
    def test_batch_calculation_performance(self):
        """ﮔﭖﻟﺁﮔﺗﻠﻟ؟۰ﻝ؟ﮔ۶ﻟﺛ"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        # ﻝﮔ1000ﻛﺕ۹ﮔﭖﻟﺁﻟ؟۱ﮒ?
        orders = self.generate_test_orders(1000)
        
        # ﻠ۱ﻝ­
        for order in orders[:100]:
            calculator.calculate_total_cost(order)
        
        # ﮔﺗﻠﻟ؟۰ﻝ؟ﮔ۶ﻟﺛﮔﭖﻟﺁ
        start_time = time.perf_counter()
        
        results = []
        for order in orders:
            result = calculator.calculate_total_cost(order)
            results.append(result)
        
        end_time = time.perf_counter()
        
        total_time = (end_time - start_time) * 1000  # ﻟﺛ؛ﮔ۱ﻛﺕﭦﮔﺁ،ﻝ۶?
        avg_time = total_time / len(orders)
        
        print(f"ﮔﺗﻠﻟ؟۰ﻝ؟ {len(orders)} ﻛﺕ۹ﻟ؟۱ﮒﺅﺙﮔﭨﮔﭘﻠ? {total_time:.1f}ms")
        print(f"ﮒﺗﺏﮒﮔﺁﻛﺕ۹ﻟ؟۱ﮒﻟ؟۰ﻝ؟ﮔﭘﻠﺑ: {avg_time:.3f}ms")
        
        assert avg_time < 0.5  # ﻝ؟ﮔ ﺅﺙ?0.5ms/ﻟ؟۱ﮒ
        assert len(results) == len(orders)
    
    def test_concurrent_calculation(self):
        """ﮔﭖﻟﺁﮒﺗﭘﮒﻟ؟۰ﻝ؟"""
        # ﮔﭖﻟﺁﮒ۳ﻝﭦﺟﻝ۷?ﮒ۳ﻟﺟﻝ۷ﻟ؟۰ﻝ؟ﮔ۶ﻟﺛ
        pass
    
    def test_memory_usage(self):
        """ﮔﭖﻟﺁﮒﮒ­ﻛﺛﺟﻝ۷"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        # ﮔﭖﻟﺁﻝﺙﮒ­ﮒﮒ­ﮒ ﻝ۷
        orders = self.generate_test_orders(10000)
        
        import psutil
        import os
        
        process = psutil.Process(os.getpid())
        memory_before = process.memory_info().rss / 1024 / 1024  # MB
        
        # ﻟ؟۰ﻝ؟ﮒ۳۶ﻠﻟ؟۱ﮒﺅﺙﮒ۰،ﮒﻝﺙﮒ­?
        for order in orders[:1000]:
            calculator.calculate_total_cost(order)
        
        memory_after = process.memory_info().rss / 1024 / 1024  # MB
        memory_increase = memory_after - memory_before
        
        print(f"ﮒﮒ­ﻛﺛﺟﻝ۷ﮒ۱ﮒ : {memory_increase:.2f}MB")
        
        # ﻠ۹ﻟﺁﮒﮒ­ﮒ۱ﮒ ﮒﻝ
        assert memory_increase < 100  # ﮒ۱ﮒ ﮒﭦﮒﺍﻛﭦ?00MB
```

### 4.3 ﮒﮒﮔﭖﻟﺁ

```python
# test_performance_stress.py
import pytest
import time
import threading
from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory

class TestPerformanceStress:
    """ﮒﮒﮔﭖﻟﺁ"""
    
    def test_high_frequency_calculation(self):
        """ﮔﭖﻟﺁﻠ،ﻠ۱ﻟ؟۰ﻝ؟"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        # ﮔ۷۰ﮔﻠ،ﻠ۱ﻛﭦ۳ﮔﺅﺙ?ﻝ۶ﮒﻟ؟۰ﻝ؟10000ﮔ؛?
        calculations_per_second = 10000
        duration = 1.0  # 1ﻝ۶?
        
        start_time = time.perf_counter()
        count = 0
        
        while time.perf_counter() - start_time < duration:
            calculator.calculate_total_cost(order)
            count += 1
        
        end_time = time.perf_counter()
        actual_duration = end_time - start_time
        actual_rate = count / actual_duration
        
        print(f"ﮒ؟ﻠﻟ؟۰ﻝ؟ﻠﻝ: {actual_rate:.0f} ﮔ؛?ﻝ۶?)
        print(f"ﻝ؟ﮔ ﻟ؟۰ﻝ؟ﻠﻝ: {calculations_per_second} ﮔ؛?ﻝ۶?)
        print(f"ﮒ؟ﮔﻟ؟۰ﻝ؟ﮔ؛۰ﮔﺍ: {count}")
        
        # ﻠ۹ﻟﺁﻟﺛﮒ۳ﮒ۳ﻝﻠ،ﻠ۱ﻟ؟۰ﻝ؟
        assert actual_rate > calculations_per_second * 0.5  # ﻟﺏﮒﺍﻟﺝﺝﮒﺍﻝ؟ﮔ ﻝ?0%
    
    def test_concurrent_stress(self):
        """ﮔﭖﻟﺁﮒﺗﭘﮒﮒﮒ"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        order = OrderInfo(
            symbol="000001.SZ",
            side=OrderSide.BUY,
            quantity=10000,
            price=10.0,
            market=MarketType.SZ,
            category=SecurityCategory.STOCK
        )
        
        results = []
        lock = threading.Lock()
        
        def calculate_thread(thread_id, count):
            for i in range(count):
                result = calculator.calculate_total_cost(order)
                with lock:
                    results.append((thread_id, i, result.total_cost))
        
        # ﮒﮒﭨﭦﮒ۳ﻛﺕ۹ﻝﭦﺟﻝ۷ﮒﺗﭘﮒﻟ؟۰ﻝ؟
        thread_count = 10
        calculations_per_thread = 1000
        
        threads = []
        for i in range(thread_count):
            thread = threading.Thread(
                target=calculate_thread,
                args=(i, calculations_per_thread)
            )
            threads.append(thread)
        
        start_time = time.perf_counter()
        
        # ﮒﺁﮒ۷ﮔﮔﻝﭦﺟﻝ۷?
        for thread in threads:
            thread.start()
        
        # ﻝ­ﮒﺝﮔﮔﻝﭦﺟﻝ۷ﮒ؟ﮔ?
        for thread in threads:
            thread.join()
        
        end_time = time.perf_counter()
        
        total_time = end_time - start_time
        total_calculations = thread_count * calculations_per_thread
        calculations_per_second = total_calculations / total_time
        
        print(f"ﮒﺗﭘﮒﻟ؟۰ﻝ؟ﮒ؟ﮔ: {total_calculations} ﮔ؛۰ﻟ؟۰ﻝ؟?)
        print(f"ﮔﭨﮔﭘﻠ? {total_time:.2f}ﻝ۶?)
        print(f"ﻟ؟۰ﻝ؟ﻠﻝ: {calculations_per_second:.0f} ﮔ؛?ﻝ۶?)
        
        # ﻠ۹ﻟﺁﮒﺗﭘﮒﻟ؟۰ﻝ؟ﮔ­۲ﻝ۰؟ﮔ?
        assert len(results) == total_calculations
        
        # ﮔﮔﻟ؟۰ﻝ؟ﻝﭨﮔﮒﭦﻛﺕﻟ?
        first_result = results[0][2]
        for _, _, result in results:
            assert result == pytest.approx(first_result, rel=0.01)
```

## 5. ﮒﮒﺛﮔﭖﻟﺁﻟ؟ﺝﻟ؟۰

### 5.1 ﮔﭖﻟﺁﻟ۹ﮒ۷ﮒ?

```python
# test_regression.py
import pytest
import json
import os
from pathlib import Path
from cost_calculator import CostCalculator, CostConfig

class TestRegression:
    """ﮒﮒﺛﮔﭖﻟﺁ"""
    
    def load_regression_data(self):
        """ﮒ ﻟﺛﺛﮒﮒﺛﮔﭖﻟﺁﮔﺍﮔ؟"""
        data_path = Path(__file__).parent / "test_data" / "regression_cases.json"
        with open(data_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def test_regression_cases(self):
        """ﮒﮒﺛﮔﭖﻟﺁﻝ۷ﻛﺝ"""
        config = CostConfig()
        calculator = CostCalculator(config)
        
        regression_cases = self.load_regression_data()
        
        failed_cases = []
        
        for case in regression_cases:
            # ﮒﮒﭨﭦﻟ؟۱ﮒ
            order = OrderInfo(**case["order"])
            
            # ﻟ؟۰ﻝ؟ﮔﮔ؛
            result = calculator.calculate_total_cost(order)
            
            # ﻠ۹ﻟﺁﻝﭨﮔ
            expected = case["expected"]
            
            errors = []
            
            # ﮔ۲ﮔ۴ﮒﻠ۰ﺗﮔﮔ?
            if abs(result.commission - expected["commission"]) > 0.01:
                errors.append(f"ﻛﺛ۲ﻠﻛﺕﮒﺗﻠ? {result.commission} != {expected['commission']}")
            
            if abs(result.stamp_tax - expected["stamp_tax"]) > 0.01:
                errors.append(f"ﮒﺍﻟﺎﻝ۷ﻛﺕﮒﺗﻠ: {result.stamp_tax} != {expected['stamp_tax']}")
            
            if abs(result.transfer_fee - expected["transfer_fee"]) > 0.01:
                errors.append(f"ﻟﺟﮔﺓﻟﺑﺗﻛﺕﮒﺗﻠ: {result.transfer_fee} != {expected['transfer_fee']}")
            
            if abs(result.regulatory_fees - expected["regulatory_fees"]) > 0.01:
                errors.append(f"ﻟ۶ﻟﺑﺗﻛﺕﮒﺗﻠ? {result.regulatory_fees} != {expected['regulatory_fees']}")
            
            if abs(result.slippage - expected["slippage"]) > 0.01:
                errors.append(f"ﮔﭨﻝﺗﻛﺕﮒﺗﻠ? {result.slippage} != {expected['slippage']}")
            
            if abs(result.total_cost - expected["total_cost"]) > 0.01:
                errors.append(f"ﮔﭨﮔﮔ؛ﻛﺕﮒﺗﻠ: {result.total_cost} != {expected['total_cost']}")
            
            if errors:
                failed_cases.append({
                    "case": case["description"],
                    "order": case["order"],
                    "errors": errors,
                    "actual": {
                        "commission": result.commission,
                        "stamp_tax": result.stamp_tax,
                        "transfer_fee": result.transfer_fee,
                        "regulatory_fees": result.regulatory_fees,
                        "slippage": result.slippage,
                        "total_cost": result.total_cost
                    },
                    "expected": expected
                })
        
        # ﻟﺝﮒﭦﮒ۳ﺎﻟﺑ۴ﻝ۷ﻛﺝ
        if failed_cases:
            print(f"ﮒﮒﺛﮔﭖﻟﺁﮒ۳ﺎﻟﺑ۴ﻝ۷ﻛﺝﮔ? {len(failed_cases)}")
            for failed in failed_cases[:5]:  # ﮒ۹ﮔﺝﻝ۳ﭦﮒ5ﻛﺕ۹ﮒ۳ﺎﻟﺑ۴ﻝ۷ﻛﺝ?
                print(f"ﮒ۳ﺎﻟﺑ۴ﻝ۷ﻛﺝ: {failed['case']}")
                for error in failed['errors']:
                    print(f"  {error}")
            
            assert False, f"ﮒﮒﺛﮔﭖﻟﺁﮒ۳ﺎﻟﺑ۴: {len(failed_cases)} ﻛﺕ۹ﻝ۷ﻛﺝﮔ۹ﻠﻟﺟ"
    
    def test_backward_compatibility(self):
        """ﮔﭖﻟﺁﮒﮒﮒﺙﮒ؟ﺗﮔ?""
        # ﮔﭖﻟﺁﮔﺍﻝﮔ؛ﻛﺕﮔ۶ﻝﮔ؛ﻟ؟۰ﻝ؟ﻝﭨﮔﻝﮒﺙﮒ؟ﺗﮔ?
        pass
    
    def test_config_compatibility(self):
        """ﮔﭖﻟﺁﻠﻝﺛ؟ﮒﺙﮒ؟ﺗﮔ?""
        # ﮔﭖﻟﺁﮔﺍﻠﻝﺛ؟ﻛﺕﮔ۶ﻠﻝﺛ؟ﻝﮒﺙﮒ؟ﺗﮔ?
        pass
```

## 6. ﮔﭖﻟﺁﮔ۶ﻟ۰ﻛﺕﮔ۴ﮒ?

### 6.1 ﮔﭖﻟﺁﮔ۶ﻟ۰ﻟﮔ؛

```python
#!/usr/bin/env python3
# run_tests.py

import sys
import pytest
import time
from pathlib import Path

def run_all_tests():
    """ﻟﺟﻟ۰ﮔﮔﮔﭖﻟﺁ?""
    print("=" * 80)
    print("ﻛﭦ۳ﮔﮔﮔ؛ﮔ۷۰ﮒﮔﭖﻟﺁﮒ۴ﻛﭨﭘ")
    print("=" * 80)
    
    test_dir = Path(__file__).parent / "tests"
    
    # ﻟﺟﻟ۰ﮒﮒﮔﭖﻟﺁ
    print("\n1. ﻟﺟﻟ۰ﮒﮒﮔﭖﻟﺁ...")
    start_time = time.time()
    result = pytest.main([
        str(test_dir / "unit"),
        "-v",
        "--tb=short",
        "--junitxml=test_reports/unit_test_results.xml"
    ])
    unit_time = time.time() - start_time
    
    if result == 0:
        print(f"ﻗ?ﮒﮒﮔﭖﻟﺁﻠﻟﺟﺅﺙﻟﮔﭘ: {unit_time:.1f}ﻝ۶?)
    else:
        print(f"ﻗ?ﮒﮒﮔﭖﻟﺁﮒ۳ﺎﻟﺑ۴ﺅﺙﻟﮔﭘ: {unit_time:.1f}ﻝ۶?)
        return False
    
    # ﻟﺟﻟ۰ﻠﮔﮔﭖﻟﺁ
    print("\n2. ﻟﺟﻟ۰ﻠﮔﮔﭖﻟﺁ...")
    start_time = time.time()
    result = pytest.main([
        str(test_dir / "integration"),
        "-v",
        "--tb=short",
        "--junitxml=test_reports/integration_test_results.xml"
    ])
    integration_time = time.time() - start_time
    
    if result == 0:
        print(f"ﻗ?ﻠﮔﮔﭖﻟﺁﻠﻟﺟﺅﺙﻟﮔﭘ: {integration_time:.1f}ﻝ۶?)
    else:
        print(f"ﻗ?ﻠﮔﮔﭖﻟﺁﮒ۳ﺎﻟﺑ۴ﺅﺙﻟﮔﭘ: {integration_time:.1f}ﻝ۶?)
        return False
    
    # ﻟﺟﻟ۰ﮔ۶ﻟﺛﮔﭖﻟﺁ
    print("\n3. ﻟﺟﻟ۰ﮔ۶ﻟﺛﮔﭖﻟﺁ...")
    start_time = time.time()
    result = pytest.main([
        str(test_dir / "performance"),
        "-v",
        "--tb=no",
        "--benchmark-only",
        "--benchmark-json=test_reports/performance_benchmark.json"
    ])
    performance_time = time.time() - start_time
    
    if result == 0:
        print(f"ﻗ?ﮔ۶ﻟﺛﮔﭖﻟﺁﮒ؟ﮔﺅﺙﻟﮔﭘ: {performance_time:.1f}ﻝ۶?)
    else:
        print(f"ﻗ?ﮔ۶ﻟﺛﮔﭖﻟﺁﮒ۳ﺎﻟﺑ۴ﺅﺙﻟﮔﭘ: {performance_time:.1f}ﻝ۶?)
        return False
    
    # ﻟﺟﻟ۰ﮒﮒﺛﮔﭖﻟﺁ
    print("\n4. ﻟﺟﻟ۰ﮒﮒﺛﮔﭖﻟﺁ...")
    start_time = time.time()
    result = pytest.main([
        str(test_dir / "regression"),
        "-v",
        "--tb=short",
        "--junitxml=test_reports/regression_test_results.xml"
    ])
    regression_time = time.time() - start_time
    
    if result == 0:
        print(f"ﻗ?ﮒﮒﺛﮔﭖﻟﺁﻠﻟﺟﺅﺙﻟﮔﭘ: {regression_time:.1f}ﻝ۶?)
    else:
        print(f"ﻗ?ﮒﮒﺛﮔﭖﻟﺁﮒ۳ﺎﻟﺑ۴ﺅﺙﻟﮔﭘ: {regression_time:.1f}ﻝ۶?)
        return False
    
    total_time = unit_time + integration_time + performance_time + regression_time
    
    print("\n" + "=" * 80)
    print("ﮔﭖﻟﺁﮔﺎﮔ?)
    print("=" * 80)
    print(f"ﮒﮒﮔﭖﻟﺁ:     {unit_time:.1f}ﻝ۶?)
    print(f"ﻠﮔﮔﭖﻟﺁ:     {integration_time:.1f}ﻝ۶?)
    print(f"ﮔ۶ﻟﺛﮔﭖﻟﺁ:     {performance_time:.1f}ﻝ۶?)
    print(f"ﮒﮒﺛﮔﭖﻟﺁ:     {regression_time:.1f}ﻝ۶?)
    print(f"ﮔﭨﻟ؟۰:         {total_time:.1f}ﻝ۶?)
    print("=" * 80)
    print("ﻗ?ﮔﮔﮔﭖﻟﺁﻠﻟﺟ!")
    
    return True

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
```

### 6.2 ﮔﭖﻟﺁﮔ۴ﮒﻝﮔ

```python
# generate_test_report.py

import json
import xml.etree.ElementTree as ET
from datetime import datetime