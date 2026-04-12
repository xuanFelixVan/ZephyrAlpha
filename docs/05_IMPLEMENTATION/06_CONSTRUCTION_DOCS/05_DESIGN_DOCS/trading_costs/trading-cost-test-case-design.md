---

module_id: TRADING_COST_TEST_CASE_DESIGN_001

version: 1.0.0

status: Active

created_date: 2026-04-07

last_updated: '2026-04-07'

owner: 个人开发者

standard_type: 专业量化机构文档

responsibility:

- 交易策略设计与实施管理与优化维护

layer: layer_05
---



version: 1.0.0

status: Active

created_date: 2026-04-02

last_updated: 2026-04-02

owner: ﻠ۵ﮒﺕﻟﮒﺝﮔﭘﮔﮒﺕ?

responsibility:

  - 交易策略设计与实施管理与优化维护

standard_type: ﻛﺕﻛﺕﻠﮒﮔﭦﮔﮔﭖﻟﺁﻟ؟ﺝﻟ؟۰ﮔﮔ۰۲

applicable_scope: ﻛﭦ۳ﮔﮔﮔ؛ﮔ۷۰ﮒ

compliance_level: ﮔﭘﮔﮔﮒ

parent_document: ../INDEX.md

implementation_status: ﻟﺟﻟ۰ﻛﺕ?---





# ﻛﭦ۳ﮔﮔﮔ؛ﮔﭖﻟﺁﻝ۷ﻛﺝﻟ؟ﺝﻟ؟۰



## 核心定位



提供交易成本的测试用例设计，包含测试场景、测试数据、预期结果等，支持交易成本模型测试。





> **核心职责**: 文档内容说明

> **职责边界**: 

> - ✅ 本文档负责：文档内容说明相关内容

> - ❌ 本文档不负责：其他模块内容





> ﮔﺕﻠ۲ﻠﮒﻝﺏﭨﻝﭨ v5.0 - ﻛﭦ۳ﮔﮔﮔ؛ﮔ۷۰ﮒﮔﭖﻟﺁﻝ۷ﻛﺝﻟﺁ۵ﻝﭨﻟ؟ﺝﻟ؟۰

> **ﻝﺑ۱ﮒﺙ**: `TEST_TRADING_COSTS_001`

> **ﮔﭖﻟﺁﻝﺎﭨﮒ**: ﮒﮒﮔﭖﻟﺁﻙﻠﮔﮔﭖﻟﺁﻙﮔ۶ﻟﺛﮔﭖﻟﺁﻙﻟﺝﺗﻝﮔ۰ﻛﭨﭘﮔﭖﻟﺁ?

> **ﮔﺕﮒﺟﻝ؟ﮔ**: ﻝ۰؟ﻛﺟﻛﭦ۳ﮔﮔﮔ؛ﻟ؟۰ﻝ؟ﻝﺎﺝﻝ۰؟ﻙﮒﺁﻠﻙﻠ،ﮔ۶ﻟﺛ





## 设计目标



### 主要目标



1. **功能完整性**: 确保文档内容完整，满足使用需求

2. **易用性**: 提高文档可读性，便于快速理解

3. **可维护性**: 文档结构清晰，便于后续维护

4. **一致性**: 确保文档格式和风格统一



### 质量目标



- 文档完整性: 100%

- 格式规范性: 100%

- 内容准确性: 100%





## 1. ﮔﭖﻟﺁﻝﻝ۴



### 1.1 ﮔﭖﻟﺁﻝﭦ۶ﮒ،



| ﮔﭖﻟﺁﻝﭦ۶ﮒ، | ﮔﭖﻟﺁﻝ؟ﮔ | ﮔﭖﻟﺁﮔﺗﮔﺏ | ﮔﭖﻟﺁﮒﺓ۴ﮒﺓ |

|----------|----------|----------|----------|

| **ﮒﮒﮔﭖﻟﺁ** | ﻠ۹ﻟﺁﮒﻛﺕ۹ﮒﺛﮔﺍ/ﮔﺗﮔﺏﮔ۲ﻝ۰؟ﮔ?| ﻝﺛﻝﮔﭖﻟﺁﻙﻟﺝﺗﻝﮒﺙﮒﮔ?| pytestﻙunittest |

| **ﻠﮔﮔﭖﻟﺁ** | ﻠ۹ﻟﺁﮔ۷۰ﮒﻠﺑﻛﭦ۳ﻛﭦﮔ۲ﻝ۰؟ﮔ?| ﮔ۴ﮒ۲ﮔﭖﻟﺁﻙﮔﺍﮔ؟ﮔﭖﮔﭖﻟﺁ | pytestﻙmock |

| **ﻝﺏﭨﻝﭨﮔﭖﻟﺁ** | ﻠ۹ﻟﺁﮔﺑﻛﺕ۹ﮔﮔ؛ﻟ؟۰ﻝ؟ﻝﺏﭨﻝﭨ | ﻝ،ﺁﮒﺍﻝ،ﺁﮔﭖﻟﺁﻙﮒﭦﮔﺁﮔﭖﻟﺁ?| pytestﻙﻠﮔﻝﺁﮒ۱?|

| **ﮔ۶ﻟﺛﮔﭖﻟﺁ** | ﻠ۹ﻟﺁﻟ؟۰ﻝ؟ﮔ۶ﻟﺛﮒﻟﭖﮔﭦﻛﺛﺟﻝ?| ﮒﮒﮔﭖﻟﺁﻙﻟﺑﻟﺛﺛﮔﭖﻟﺁ?| pytest-benchmarkﻙmemory-profiler |

| **ﮒﮒﺛﮔﭖﻟﺁ** | ﻠ۹ﻟﺁﻛﺟ؟ﮔﺗﻛﺕﮒﺛﺎﮒﻝﺍﮔﮒﻟ?| ﻟ۹ﮒ۷ﮒﮔﭖﻟﺁﮒ۴ﻛﭨ?| pytestﻙGitHub Actions |



### 1.2 ﮔﭖﻟﺁﻝﺁﮒ۱



```yaml

ﮔﭖﻟﺁﻝﺁﮒ۱ﻠﻝﺛ؟:

  ﮒﺙﮒﻝﺁﮒ۱?

    python_version: "3.13"

    os: "Windows/Linux/macOS"

ﮒﮒ: ">=8GB"

    

  ﮔﭖﻟﺁﮔﺍﮔ؟:

ﮔﺓﮔ؛ﮔﺍﻠ: 1000ﻛﺕ۹ﮔﭖﻟﺁﻟ؟۱ﮒ?

    ﮒﺕﮒﭦﻝﺎﭨﮒ: SH, SZ

    ﻟﺁﮒﺕﻝﺎﭨﮒ،: STOCK, ETF, BOND, CONVERTIBLE_BOND

ﻛﭨﺓﮔﺙﻟﮒﺑ: 0.1-1000ﮒ?

    ﮔﺍﻠﻟﮒﺑ: 100-1000000ﻟ?

    

  ﻛﺝﻟﭖﮒﭦ?

    pytest: ">=7.0"

    pytest-benchmark: ">=3.4"

    pytest-mock: ">=3.10"

    pytest-cov: ">=4.1"

    yaml: ">=6.0"

    numpy: ">=1.24"

    pandas: ">=2.0"

```



### 1.3 ﮔﭖﻟﺁﮔﺍﮔ؟ﮒﮒ۳



```python

ﮔﭖﻟﺁﮔﺍﮔ؟ﻝﮔﻝﻝ۴:

  1. ﮒﭦﻝ۰ﮔﭖﻟﺁﮔﺍﮔ؟: ﮔﮒ۷ﻝﺙﮒﻝﮒﺕﮒﮒﭦﮔ?

  2. ﻠﮔﭦﮔﭖﻟﺁﮔﺍﮔ؟: ﻠﮔﭦﻝﮔﻝﻟﺝﺗﻝﮒﭦﮔ?

  3. ﮒ؟ﻝﮔﭖﻟﺁﮔﺍﮔ؟: ﻛﭨﮒ؟ﻝﻛﭦ۳ﮔﮔ۴ﮒﺟﮔﮒ?

  4. ﮒﺙﮒﺕﺕﮔﭖﻟﺁﮔﺍﮔ؟: ﻠﮔﺏﻟﺝﮒ۴ﻙﻟﺝﺗﻝﮒ?

  

ﮔﭖﻟﺁﮔﺍﮔ؟ﮔﻛﭨﭘ:

  - test_data/basic_orders.json: ﮒﭦﻝ۰ﮔﭖﻟﺁﻟ؟۱ﮒ

  - test_data/random_orders_1000.json: 1000ﻛﺕ۹ﻠﮔﭦﮔﭖﻟﺁﻟ؟۱ﮒ?

- test_data/real_orders_sample.json: ﮒ؟ﻝﻟ؟۱ﮒﮔﺓﮔ؛

  - test_data/edge_cases.json: ﻟﺝﺗﻝﮔ۰ﻛﭨﭘﮔﭖﻟﺁﮔﺍﮔ؟

```



## 2. ﮒﮒﮔﭖﻟﺁﻟ؟ﺝﻟ؟۰



### 2.1 CostCalculator ﻝﺎﭨﮔﭖﻟﺁ?



#### 2.1.1 ﻛﺛ۲ﻠﻟ؟۰ﻝ؟ﮔﭖﻟﺁ



```python

# test_commission.py

import pytest

from decimal import Decimal

from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory



class TestCommissionCalculation:

    """ﻛﺛ۲ﻠﻟ؟۰ﻝ؟ﮔﭖﻟﺁ"""

    

    def test_basic_commission(self):

        """ﮔﭖﻟﺁﮒﭦﻝ۰ﻛﺛ۲ﻠﻟ؟۰ﻝ؟"""

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

        # ﮔﻛﭦ۳ﻠﻠ۱100,000ﮒﺅﺙﻛﺛ۲ﻠﻝ?.03%ﺅﺙﮔﻛﺛ?ﮒ?

        expected_commission = max(100000 * 0.0003, 5.0)

        assert result.commission == pytest.approx(expected_commission, rel=0.01)

    

    def test_min_commission(self):

        """ﮔﭖﻟﺁﮔﻛﺛﻛﺛ۲ﻠ?""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        # ﮒﺍﻠﻠ۱ﻟ؟۱ﮒﺅﺙ1000ﮒﮔﻛﭦ?

        order = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=100,

            price=10.0,

            market=MarketType.SZ,

            category=SecurityCategory.STOCK

        )

        

        result = calculator.calculate_total_cost(order)

        # 1000ﮒﺣ?.03% = 0.3ﮒﺅﺙﻛﺛﮔﻛﺛ?ﮒ?

        assert result.commission == 5.0

    

    def test_tiered_commission(self):

        """ﮔﭖﻟﺁﻠﭘﮔ۱ﺁﻛﺛ۲ﻠ"""

        config = CostConfig()

        config.commission_tiered_rates = [

            TieredRate(threshold=1000000, rate=0.0003),   # 100ﻛﺕﻛﭨ۴ﻛﺕ?

            TieredRate(threshold=5000000, rate=0.00025),  # 100-500ﻛﺕ?

            TieredRate(threshold=None, rate=0.0002)       # 500ﻛﺕﻛﭨ۴ﻛﺕ?

        ]

        

        calculator = CostCalculator(config)

        

        # ﮔﭖﻟﺁﮒﺍﻠﻠ۱ﺅﺙ50ﻛﺕﮒ

        order1 = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=50000,

            price=10.0,  # 50ﻛﺕﮒ

            market=MarketType.SZ,

            category=SecurityCategory.STOCK

        )

        result1 = calculator.calculate_total_cost(order1)

        expected1 = max(500000 * 0.0003, 5.0)  # 150ﮒ?

        assert result1.commission == pytest.approx(expected1, rel=0.01)

        

# ﮔﭖﻟﺁﻛﺕﻠﻠ۱ﺅﺙ300ﻛﺕﮒ

        order2 = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=100000,

            price=30.0,  # 300ﻛﺕﮒ

            market=MarketType.SZ,

            category=SecurityCategory.STOCK

        )

        result2 = calculator.calculate_total_cost(order2)

        expected2 = 3000000 * 0.00025  # 750ﮒ?

        assert result2.commission == pytest.approx(expected2, rel=0.01)

        

        # ﮔﭖﻟﺁﮒ۳۶ﻠﻠ۱ﺅﺙ1000ﻛﺕﮒ

        order3 = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=100000,

            price=100.0,  # 1000ﻛﺕﮒ

            market=MarketType.SZ,

            category=SecurityCategory.STOCK

        )

        result3 = calculator.calculate_total_cost(order3)

        expected3 = 10000000 * 0.0002  # 2000ﮒ?

        assert result3.commission == pytest.approx(expected3, rel=0.01)

    

    def test_commission_exempt(self):

        """ﮔﭖﻟﺁﮒﻛﺛ۲ﻠﻟﺁﮒ?""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        # ﻟﺑ۶ﮒﺕﮒﭦﻠﮒﻛﺛ۲ﻠ?

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

        """ﮔﭖﻟﺁﮔﻠ،ﻛﺛ۲ﻠﻠﮒ?""

        config = CostConfig()

        config.max_commission = 1000.0  # ﮔﻠ،ﻛﺛ۲ﻠ?000ﮒ?

        calculator = CostCalculator(config)

        

        # ﮒ۳۶ﻠ۱ﻟ؟۱ﮒﺅﺙ?000ﻛﺕﮒﺅﺙﻛﺛ۲ﻠﮒﭦﻛﺕ?000ﮒﺅﺙﻛﺛﻠﮒﭘﻛﺕﭦ1000ﮒ?

        order = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=100000,

            price=100.0,  # 1000ﻛﺕﮒ

            market=MarketType.SZ,

            category=SecurityCategory.STOCK

        )

        

        result = calculator.calculate_total_cost(order)

        assert result.commission == 1000.0

    

    @pytest.mark.parametrize("amount,expected", [

        (1000, 5.0),      # ﮔﻛﺛﻛﺛ۲ﻠ?

        (10000, 5.0),     # ﮔﻛﺛﻛﺛ۲ﻠ?

        (50000, 15.0),    # 50000ﺣ0.0003=15

        (100000, 30.0),   # 100000ﺣ0.0003=30

        (1000000, 300.0), # 1000000ﺣ0.0003=300

        (5000000, 1250.0),# 5000000ﺣ0.00025=1250

        (10000000, 2000.0),# 10000000ﺣ0.0002=2000

    ])

    def test_commission_parametrized(self, amount, expected):

        """ﮒﮔﺍﮒﮔﭖﻟﺁﻛﺛ۲ﻠﻟ؟۰ﻝ؟?""

        config = CostConfig()

        config.commission_tiered_rates = [

            TieredRate(threshold=1000000, rate=0.0003),

            TieredRate(threshold=5000000, rate=0.00025),

            TieredRate(threshold=None, rate=0.0002)

        ]

        

        calculator = CostCalculator(config)

        

# ﮔﺗﮔ؟ﻠﻠ۱ﻟ؟۰ﻝ؟ﮔﺍﻠﮒﻛﭨﺓﮔ?

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



#### 2.1.2 ﮒﺍﻟﺎﻝ۷ﻟ؟۰ﻝ؟ﮔﭖﻟﺁ?



```python

# test_stamp_tax.py

import pytest

from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory



class TestStampTaxCalculation:

    """ﮒﺍﻟﺎﻝ۷ﻟ؟۰ﻝ؟ﮔﭖﻟﺁ?""

    

    def test_stamp_tax_on_sell(self):

        """ﮔﭖﻟﺁﮒﮒﭦﮔﭘﮒﺍﻟﺎﻝ۷"""

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

        # ﮒﮒﭦ100,000ﮒﺅﺙﮒﺍﻟﺎﻝ۷?.1% = 100ﮒ?

        expected_stamp_tax = 100000 * 0.001

        assert result.stamp_tax == pytest.approx(expected_stamp_tax, rel=0.01)

    

    def test_stamp_tax_exempt_on_buy(self):

        """ﮔﭖﻟﺁﻛﺗﺍﮒ۴ﮔﭘﮒﮒﺍﻟﺎﻝ۷?""

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

        """ﮔﭖﻟﺁETFﮒﮒﺍﻟﺎﻝ۷"""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        # ETFﮒﮒﭦﻛﺗﮒﭦﮒﮒﺍﻟﺎﻝ۷

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

        """ﮔﭖﻟﺁﮒﭦﮒﺕﮒﮒﺍﻟﺎﻝ۷"""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        # ﮒﭦﮒﺕﮒﮒﭦﻛﺗﮒﭦﮒﮒﺍﻟﺎﻝ۷

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

        """ﮔﭖﻟﺁﮒﺍﻟﺎﻝ۷ﮒﺁﻠﻝﺛ؟"""

        config = CostConfig()

        config.stamp_tax_on_sell_only = False  # ﻛﺗﺍﮒ۴ﻛﺗﮔﭘﮒﺍﻟﺎﻝ۷?

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

        # ﻛﺗﺍﮒ۴ﮔﭘﻛﺗﮔﭘﮒﺍﻟﺎﻝ۷

        expected_stamp_tax = 100000 * 0.001

        assert result.stamp_tax == pytest.approx(expected_stamp_tax, rel=0.01)

```



#### 2.1.3 ﻟﺟﮔﺓﻟﺑﺗﻟ؟۰ﻝ؟ﮔﭖﻟﺁ?



```python

# test_transfer_fee.py

import pytest

from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory



class TestTransferFeeCalculation:

    """ﻟﺟﮔﺓﻟﺑﺗﻟ؟۰ﻝ؟ﮔﭖﻟﺁ?""

    

    def test_sh_transfer_fee_by_par_value(self):

        """ﮔﭖﻟﺁﮔﺎ۹ﮒﺕﻟﺟﮔﺓﻟﺑﺗﺅﺙﮔﻠ۱ﻠ۱ﻟ؟۰ﻝ؟ﺅﺙ"""

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

        # ﮔﺎ۹ﮒﺕﺅﺙ?0000ﻟ۰ﺣ?ﮒﻠ۱ﮒﺙﺣ?.001% = 0.1ﮒﺅﺙﮔﻛﺛ?ﮒ?

        expected_fee = max(10000 * 1.0 * 0.00001, 1.0)

        assert result.transfer_fee == pytest.approx(expected_fee, rel=0.01)

    

    def test_sz_transfer_fee_by_amount(self):

        """ﮔﭖﻟﺁﮔﺓﺎﮒﺕﻟﺟﮔﺓﻟﺑﺗﺅﺙﮔﮔﻛﭦ۳ﻠﻠ۱ﻟ؟۰ﻝ؟ﺅﺙ"""

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

        # ﮔﺓﺎﮒﺕﺅﺙ?00,000ﮒﺣ?.002% = 2ﮒﺅﺙﮔﻛﺛ?ﮒ?

        expected_fee = max(100000 * 0.00002, 1.0)

        assert result.transfer_fee == pytest.approx(expected_fee, rel=0.01)

    

    def test_min_transfer_fee(self):

        """ﮔﭖﻟﺁﮔﻛﺛﻟﺟﮔﺓﻟﺑﺗ"""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        # ﮒﺍﻠﻠ۱ﻟ؟۱ﮒﺅﺙ1000ﮒﮔﻛﭦ۳ﺅﺙﮔﺓﺎﮒﺕ

        order = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=100,

            price=10.0,

            market=MarketType.SZ,

            category=SecurityCategory.STOCK

        )

        

        result = calculator.calculate_total_cost(order)

        # 1000ﮒﺣ?.002% = 0.02ﮒﺅﺙﮔﻛﺛ?ﮒ?

        assert result.transfer_fee == 1.0

    

    def test_transfer_fee_exempt(self):

        """ﮔﭖﻟﺁﮒﻟﺟﮔﺓﻟﺑﺗﻟﺁﮒﺕ"""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        # ﮒﭦﮒﺕﮒﻟﺟﮔﺓﻟﺑﺗ

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

        """ﮔﭖﻟﺁﻟ۹ﮒ؟ﻛﺗﻠ۱ﮒ?""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        # ﻟ۰ﻝ۴۷ﻠ۱ﮒﺙﻛﺕﮔ?ﮒﻝﮔﮒﭖﺅﺙﻝﻟ؟ﭦﻛﺕﻝﺛﻟ۶ﺅﺙ?

        order = OrderInfo(

            symbol="600000.SH",

            side=OrderSide.BUY,

            quantity=10000,

            price=10.0,

            market=MarketType.SH,

            category=SecurityCategory.STOCK,

            par_value=0.1  # ﻠ۱ﮒ?.1ﮒ?

        )

        

        result = calculator.calculate_total_cost(order)

        # ﮔﺎ۹ﮒﺕﺅﺙ?0000ﻟ۰ﺣ?.1ﮒﻠ۱ﮒﺙﺣ?.001% = 0.01ﮒﺅﺙﮔﻛﺛ?ﮒ?

        expected_fee = max(10000 * 0.1 * 0.00001, 1.0)

        assert result.transfer_fee == pytest.approx(expected_fee, rel=0.01)

```



#### 2.1.4 ﻟ۶ﻟﺑﺗﻟ؟۰ﻝ؟ﮔﭖﻟﺁ



```python

# test_regulatory_fees.py

import pytest

from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory



class TestRegulatoryFeesCalculation:

    """ﻟ۶ﻟﺑﺗﻟ؟۰ﻝ؟ﮔﭖﻟﺁ"""

    

    def test_basic_regulatory_fees(self):

        """ﮔﭖﻟﺁﮒﭦﻝ۰ﻟ۶ﻟﺑﺗﻟ؟۰ﻝ؟"""

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

        # ﻟ۶ﻟﺑﺗﺅﺙ?00,000ﮒﺣ?.002% = 2ﮒ?

        expected_fees = 100000 * 0.00002

        assert result.regulatory_fees == pytest.approx(expected_fees, rel=0.01)

    

    def test_regulatory_fees_exempt(self):

        """ﮔﭖﻟﺁﮒﻟ۶ﻟﺑﺗﻟﺁﮒ?""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        # ﮒﭦﮒﺕﮒﻟ۶ﻟﺑ?

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

        """ﮔﭖﻟﺁﻟ۶ﻟﺑﺗﻝﭨﮔﮔﻝﭨ"""

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

        

        # ﻠ۹ﻟﺁﻟ۶ﻟﺑﺗﻝﭨﮔ

        components = config.regulatory_components

        total_rate = sum(components.values())

        expected_fees = 100000 * total_rate

        

        assert result.regulatory_fees == pytest.approx(expected_fees, rel=0.01)

    

    def test_regulatory_fees_on_both_sides(self):

        """ﮔﭖﻟﺁﻟ۶ﻟﺑﺗﮒﮒﮔﭘﮒ"""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        # ﻛﺗﺍﮒ۴ﮒﮒﮒﭦﻠﺛﮒﭦﮔﭘﮒﻟ۶ﻟﺑ?

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

        

        # ﻛﺗﺍﮒ۴ﮒﮒﮒﭦﻝﻟ۶ﻟﺑﺗﮒﭦﻟﺁ۴ﻝﺕﮒ

        assert buy_result.regulatory_fees == pytest.approx(sell_result.regulatory_fees, rel=0.01)

        assert buy_result.regulatory_fees > 0

```



#### 2.1.5 ﮔﭨﻝﺗﮔﮔ؛ﻟ؟۰ﻝ؟ﮔﭖﻟﺁ



```python

# test_slippage.py

import pytest

from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory



class TestSlippageCalculation:

    """ﮔﭨﻝﺗﮔﮔ؛ﻟ؟۰ﻝ؟ﮔﭖﻟﺁ"""

    

    def test_basic_slippage(self):

        """ﮔﭖﻟﺁﮒﭦﻝ۰ﮔﭨﻝﺗﻟ؟۰ﻝ؟"""

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

        # ﮒﭦﻝ۰ﮔﭨﻝﺗﺅﺙ?00,000ﮒﺣ?.02% = 20ﮒ?

        expected_slippage = 100000 * 0.0002

        assert result.slippage == pytest.approx(expected_slippage, rel=0.01)

    

    def test_slippage_with_market_data(self):

        """ﮔﭖﻟﺁﮒﺕ۵ﮒﺕﮒﭦﮔﺍﮔ؟ﻝﮔﭨﻝﺗﻟ؟۰ﻝ؟"""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        # ﻠ،ﮔﭖﮒ۷ﮔ۶ﻟ۰ﻝ۴?

        order1 = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=10000,

            price=10.0,

            market=MarketType.SZ,

            category=SecurityCategory.STOCK,

            market_data={

                "daily_volume": 50000000,  # 5000ﻛﺕﺅﺙﻠ،ﮔﭖﮒ۷ﮔ?

"volatility": 0.02,        # 2%ﮔﺏ۱ﮒ۷ﻝﺅﺙﻛﺕﻝ

                "avg_trade_size": 10000

            }

        )

        

        result1 = calculator.calculate_total_cost(order1)

        # ﮒﭦﻝ۰ﮔﭨﻝﺗﻝ?.02% ﺣ 0.5 ﺣ 1.2 = 0.012%

        expected_slippage1 = 100000 * 0.0002 * 0.5 * 1.2

        assert result1.slippage == pytest.approx(expected_slippage1, rel=0.01)

        

        # ﻛﺛﮔﭖﮒ۷ﮔ۶ﻟ۰ﻝ۴?

        order2 = OrderInfo(

            symbol="000002.SZ",

            side=OrderSide.BUY,

            quantity=10000,

            price=10.0,

            market=MarketType.SZ,

            category=SecurityCategory.STOCK,

            market_data={

                "daily_volume": 500000,    # 50ﻛﺕﺅﺙﻛﺛﮔﭖﮒ۷ﮔ?

                "volatility": 0.04,        # 4%ﮔﺏ۱ﮒ۷ﻝﺅﺙﻠ،?

                "avg_trade_size": 5000

            }

        )

        

        result2 = calculator.calculate_total_cost(order2)

# ﻛﺛﮔﭖﮒ۷ﮔ۶ﺅﺙﮒﮒ2.0ﺅﺙﻠ،ﮔﺏ۱ﮒ۷ﻝﺅﺙﮒﮒ1.5

        # ﮒﭦﻝ۰ﮔﭨﻝﺗﻝ?.02% ﺣ 2.0 ﺣ 1.5 = 0.06%

        expected_slippage2 = 100000 * 0.0002 * 2.0 * 1.5

        assert result2.slippage == pytest.approx(expected_slippage2, rel=0.01)

    

    def test_slippage_order_size_factor(self):

"""ﮔﭖﻟﺁﻟ؟۱ﮒﮒ۳۶ﮒﺍﮒﮒ"""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        # ﮒﺍﮒ

        order1 = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=1000,  # ﮒﺍﮒ

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

# ﮒﺍﮒﺅﺙﮒﮒ?.0

        expected_slippage1 = 10000 * 0.0002 * 1.0 * 1.0 * 1.0

        assert result1.slippage == pytest.approx(expected_slippage1, rel=0.01)

        

        # ﮒ۳۶ﮒ

        order2 = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=200000,  # ﮒ۳۶ﮒﺅﺙ?0ﮒﮒﺗﺏﮒﮔﻛﭦ۳ﻠ۱ﺅﺙ?

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

# ﮒ۳۶ﮒﺅﺙﮒﮒ?.5

        expected_slippage2 = 2000000 * 0.0002 * 1.0 * 1.0 * 1.5

        assert result2.slippage == pytest.approx(expected_slippage2, rel=0.01)

    

    def test_slippage_time_factor(self):

"""ﮔﭖﻟﺁﮔﭘﻠﺑﮒﮒ"""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        # ﮒﺙﻝﮔﭘﮔ؟?

        order1 = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=10000,

            price=10.0,

            market=MarketType.SZ,

            category=SecurityCategory.STOCK,

            timestamp="2026-04-02 09:15:00",  # ﮒﺙﻝﮔﭘﮔ؟?

            market_data={

                "daily_volume": 10000000,

                "volatility": 0.02,

                "avg_trade_size": 10000

            }

        )

        

        result1 = calculator.calculate_total_cost(order1)

# ﮒﺙﻝﮔﭘﮔ؟ﭖﺅﺙﮒﮒ1.5

        expected_slippage1 = 100000 * 0.0002 * 1.0 * 1.0 * 1.0 * 1.5

        assert result1.slippage == pytest.approx(expected_slippage1, rel=0.01)

        

        # ﮒﻠﺑﮔﭘﮔ؟ﭖ

        order2 = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=10000,

            price=10.0,

            market=MarketType.SZ,

            category=SecurityCategory.STOCK,

            timestamp="2026-04-02 12:30:00",  # ﮒﻠﺑﮔﭘﮔ؟ﭖ

            market_data={

                "daily_volume": 10000000,

                "volatility": 0.02,

                "avg_trade_size": 10000

            }

        )

        

        result2 = calculator.calculate_total_cost(order2)

# ﮒﻠﺑﮔﭘﮔ؟ﭖﺅﺙﮒﮒ?.8

        expected_slippage2 = 100000 * 0.0002 * 1.0 * 1.0 * 1.0 * 0.8

        assert result2.slippage == pytest.approx(expected_slippage2, rel=0.01)

    

    def test_slippage_max_rate(self):

        """ﮔﭖﻟﺁﮔﮒ۳۶ﮔﭨﻝﺗﻝﻠﮒﭘ"""

        config = CostConfig()

        calculator = CostCalculator(config)

        

# ﮔﻝ،ﺁﮔﮒﭖﺅﺙﮔﮔﮒﮒﻠﺛﮒﮔﮒ۳۶ﮒ?

        order = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=200000,  # ﮒ۳۶ﮒ

            price=10.0,

            market=MarketType.SZ,

            category=SecurityCategory.STOCK,

            timestamp="2026-04-02 09:15:00",  # ﮒﺙﻝﮔﭘﮔ؟?

            market_data={

                "daily_volume": 500000,    # ﻛﺛﮔﭖﮒ۷ﮔ?

                "volatility": 0.04,        # ﻠ،ﮔﺏ۱ﮒ۷ﻝ

                "avg_trade_size": 5000

            }

        )

        

        result = calculator.calculate_total_cost(order)

        # ﻟ؟۰ﻝ؟ﻝﻟ؟ﭦﮔﭨﻝﺗﻝﺅﺙ0.02% ﺣ 2.0 ﺣ 1.5 ﺣ 1.5 ﺣ 1.5 = 0.135%

        # ﻛﺛﮔﮒ۳۶ﻠﮒﭘﻛﺕﭦ1%ﺅﺙﮔﻛﭨ۴ﮒﭦﻛﺕ?.135% < 1%ﺅﺙﻛﺛﺟﻝ۷ﻟ؟۰ﻝ؟ﮒ?

        # ﮒ۵ﮔﻟﭘﻟﺟ1%ﺅﺙﮒﻠﮒﭘﻛﺕ?%

        

        # ﻠ۹ﻟﺁﮔﭨﻝﺗﻝﻛﺕﻟﭘﻟﺟ1%

        amount = order.quantity * order.price

        slippage_rate = result.slippage / amount if amount > 0 else 0

        assert slippage_rate <= 0.01  # ﻛﺕﻟﭘﻟﺟ?%

```



#### 2.1.6 ﮔﭨﮔﮔ؛ﻟ؟۰ﻝ؟ﮔﭖﻟﺁ?



```python

# test_total_cost.py

import pytest

from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory



class TestTotalCostCalculation:

    """ﮔﭨﮔﮔ؛ﻟ؟۰ﻝ؟ﮔﭖﻟﺁ?""

    

    def test_total_cost_buy(self):

        """ﮔﭖﻟﺁﻛﺗﺍﮒ۴ﮔﭨﮔﮔ?""

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

        

        # ﻟ؟۰ﻝ؟ﮒﻠ۰ﺗﮔﮔ؛

        amount = 100000

        commission = max(amount * 0.0003, 5.0)  # 30ﮒ?

        stamp_tax = 0.0  # ﻛﺗﺍﮒ۴ﮒﮒﺍﻟﺎﻝ۷

        transfer_fee = max(amount * 0.00002, 1.0)  # 2ﮒ?

        regulatory_fees = amount * 0.00002  # 2ﮒ?

        slippage = amount * 0.0002  # 20ﮒ?

        

        expected_total = commission + stamp_tax + transfer_fee + regulatory_fees + slippage

        expected_percentage = expected_total / amount

        

        assert result.total_cost == pytest.approx(expected_total, rel=0.01)

        assert result.as_percentage == pytest.approx(expected_percentage, rel=0.0001)

        assert result.total_cost > 0

    

    def test_total_cost_sell(self):

        """ﮔﭖﻟﺁﮒﮒﭦﮔﭨﮔﮔ?""

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

        

        # ﻟ؟۰ﻝ؟ﮒﻠ۰ﺗﮔﮔ؛

        amount = 100000

        commission = max(amount * 0.0003, 5.0)  # 30ﮒ?

        stamp_tax = amount * 0.001  # 100ﮒ?

        transfer_fee = max(amount * 0.00002, 1.0)  # 2ﮒ?

        regulatory_fees = amount * 0.00002  # 2ﮒ?

        slippage = amount * 0.0002  # 20ﮒ?

        

        expected_total = commission + stamp_tax + transfer_fee + regulatory_fees + slippage

        expected_percentage = expected_total / amount

        

        assert result.total_cost == pytest.approx(expected_total, rel=0.01)

        assert result.as_percentage == pytest.approx(expected_percentage, rel=0.0001)

        

# ﮒﮒﭦﮔﮔ؛ﮒﭦﻠ،ﻛﭦﻛﺗﺍﮒ۴ﮔﮔ؛ﺅﺙﮒﻛﺕﭦﮔﮒﺍﻟﺎﻝ۷ﺅﺙ?

        assert result.total_cost > (expected_total - stamp_tax)

    

    def test_total_cost_etf(self):

        """ﮔﭖﻟﺁETFﮔﭨﮔﮔ؛ﺅﺙﮒﮒﺍﻟﺎﻝ۷ﺅﺙ?""

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

        

        # ETFﮒﮒﭦﮒﮒﺍﻟﺎﻝ۷

        assert result.stamp_tax == 0.0

        

        # ﮔﭨﮔﮔ؛ﮒﭦﻛﺛﻛﭦﻟ۰ﻝ۴۷ﮒﮒﭦﮔﮔ؛

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

        

# ETFﮔﮔ؛ﮒﭦﻛﺛﻛﭦﻟ۰ﻝ۴۷ﮔﮔ؛ﺅﺙﮒﻛﺕﭦﮒﮒﺍﻟﺎﻝ۷ﺅﺙ?

        assert result.total_cost < stock_result.total_cost

    

    def test_cost_breakdown(self):

        """ﮔﭖﻟﺁﻟﺑﺗﻝ۷ﮔﻝﭨ"""

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

        

        # ﻠ۹ﻟﺁﮔﻝﭨﮒﮒ،ﮔﮔﮔﮔ؛ﻝﺎﭨﮒ?

        assert "commission" in breakdown

        assert "stamp_tax" in breakdown

        assert "transfer_fee" in breakdown

        assert "regulatory_fees" in breakdown

        assert "slippage" in breakdown

        

        # ﻠ۹ﻟﺁﮔﻝﭨﻠﻠ۱ﻛﺕﮔﭨﮔﮔ؛ﻛﺕﻟ?

        total_from_breakdown = sum(breakdown.values())

        assert total_from_breakdown == pytest.approx(result.total_cost, rel=0.01)

        

        # ﻠ۹ﻟﺁﮔﻝﭨﻠﻠ۱ﻛﺕﮒﻠ۰ﺗﮔﮔ؛ﻛﺕﻟ?

        assert breakdown["commission"] == pytest.approx(result.commission, rel=0.01)

        assert breakdown["stamp_tax"] == pytest.approx(result.stamp_tax, rel=0.01)

        assert breakdown["transfer_fee"] == pytest.approx(result.transfer_fee, rel=0.01)

        assert breakdown["regulatory_fees"] == pytest.approx(result.regulatory_fees, rel=0.01)

        assert breakdown["slippage"] == pytest.approx(result.slippage, rel=0.01)

    

    def test_cache_functionality(self):

"""ﮔﭖﻟﺁﻝﺙﮒﮒﻟﺛ"""

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

        

        # ﻝ؛؛ﻛﺕﮔ؛۰ﻟ؟۰ﻝ؟?

        result1 = calculator.calculate_total_cost(order)

        

# ﻝ؛؛ﻛﭦﮔ؛۰ﻟ؟۰ﻝ؟ﺅﺙﮒﭦﻛﺛﺟﻝ۷ﻝﺙﮒﺅﺙ

        result2 = calculator.calculate_total_cost(order)

        

        # ﻝﭨﮔﮒﭦﻟﺁ۴ﻝﺕﮒ

        assert result1.total_cost == result2.total_cost

        

# ﻝ۵ﻝ۷ﻝﺙﮒﮒﻠﮔﺍﻟ؟۰ﻝ؟?

        config.cache_enabled = False

        calculator2 = CostCalculator(config)

        result3 = calculator2.calculate_total_cost(order)

        

        # ﻝﭨﮔﮒﭦﻟﺁ۴ﻛﭨﻝﭘﻝﺕﮒ

        assert result1.total_cost == pytest.approx(result3.total_cost, rel=0.01)

```



### 2.2 ﻟﺝﺗﻝﮔ۰ﻛﭨﭘﮔﭖﻟﺁ



```python

# test_edge_cases.py

import pytest

from decimal import Decimal

from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory



class TestEdgeCases:

    """ﻟﺝﺗﻝﮔ۰ﻛﭨﭘﮔﭖﻟﺁ"""

    

    def test_zero_quantity(self):

        """ﮔﭖﻟﺁﻠﭘﮔﺍﻠ?""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        order = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=0,  # ﻠﭘﮔﺍﻠ?

            price=10.0,

            market=MarketType.SZ,

            category=SecurityCategory.STOCK

        )

        

        result = calculator.calculate_total_cost(order)

        

        # ﻠﭘﮔﺍﻠﻟ؟۱ﮒﺅﺙﮔﮔﮔﮔ؛ﮒﭦﻛﺕ?

        assert result.total_cost == 0.0

        assert result.commission == 0.0

        assert result.stamp_tax == 0.0

        assert result.transfer_fee == 0.0

        assert result.regulatory_fees == 0.0

        assert result.slippage == 0.0

        assert result.as_percentage == 0.0

    

    def test_zero_price(self):

"""ﮔﭖﻟﺁﻠﭘﻛﭨﺓﮔ?""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        order = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=10000,

price=0.0,  # ﻠﭘﻛﭨﺓﮔ?

            market=MarketType.SZ,

            category=SecurityCategory.STOCK

        )

        

        result = calculator.calculate_total_cost(order)

        

# ﻠﭘﻛﭨﺓﮔﺙﻟ؟۱ﮒﺅﺙﮔﮔﮔﮔ؛ﮒﭦﻛﺕ?

        assert result.total_cost == 0.0

        assert result.commission == 0.0

        assert result.stamp_tax == 0.0

        assert result.transfer_fee == 0.0

        assert result.regulatory_fees == 0.0

        assert result.slippage == 0.0

        assert result.as_percentage == 0.0

    

    def test_negative_price(self):

"""ﮔﭖﻟﺁﻟﺑﻛﭨﺓﮔﺙﺅﺙﮒﺙﮒﺕﺕﮔﮒﭖﺅﺙ?""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        order = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=10000,

price=-10.0,  # ﻟﺑﻛﭨﺓﮔ?

            market=MarketType.SZ,

            category=SecurityCategory.STOCK

        )

        

        result = calculator.calculate_total_cost(order)

        

# ﻟﺑﻛﭨﺓﮔﺙﻟ؟۱ﮒﺅﺙﮔﻛﭦ۳ﻠﻠ۱ﻛﺕﭦﻟﺑﺅﺙﻛﺛﮔﮔ؛ﻟ؟۰ﻝ؟ﮒﭦﮒ۳ﻝ?

        amount = order.quantity * order.price  # -100,000ﮒ?

        

        # ﻛﺛ۲ﻠﺅﺙﻟﺑﻠﻠ۱ﺣﻟﺑﺗﻝﺅﺙﻛﺛﮔﻛﺛ?ﮒﺅﺙﮒﭦﻛﺕﭦ0ﮔﮒﺙﮒﺕﺕﺅﺙ

# ﮒ؟ﻠﮒ؟ﻝﺍﻛﺕﮒﭦﮒ۳ﻝﻟﺑﻠﻠ۱ﮔﮒ?

# ﻟﺟﻠﮔﭖﻟﺁﮔ۰ﮔﭘﮔﺁﮒ۵ﻟﺛﮔ۲ﻝ۰؟ﮒ۳ﻝ?

        assert result.total_cost <= 0  # ﮔﭨﮔﮔ؛ﮒﺁﻟﺛﻛﺕﭦ0ﮔﻟﺑ

    

    def test_negative_quantity(self):

        """ﮔﭖﻟﺁﻟﺑﮔﺍﻠﺅﺙﮒﺙﮒﺕﺕﮔﮒﭖﺅﺙ?""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        order = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=-10000,  # ﻟﺑﮔﺍﻠ?

            price=10.0,

            market=MarketType.SZ,

            category=SecurityCategory.STOCK

        )

        

        result = calculator.calculate_total_cost(order)

        

        # ﻟﺑﮔﺍﻠﻟ؟۱ﮒﺅﺙﮔﻛﭦ۳ﻠﻠ۱ﻛﺕﭦﻟﺑ

# ﮒ؟ﻠﮒ؟ﻝﺍﻛﺕﮒﭦﮒ۳ﻝﻟﺑﮔﺍﻠﮔﮒ?

        assert result.total_cost <= 0  # ﮔﭨﮔﮔ؛ﮒﺁﻟﺛﻛﺕﭦ0ﮔﻟﺑ

    

    def test_very_small_amount(self):

        """ﮔﭖﻟﺁﮔﮒﺍﻠﻠ۱"""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        order = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=1,  # 1ﻟ?

            price=0.01,  # 0.01ﮒ?

            market=MarketType.SZ,

            category=SecurityCategory.STOCK

        )

        

        result = calculator.calculate_total_cost(order)

        

        # ﮔﮒﺍﻠﻠ۱ﺅﺙ?.01ﮒ?

        amount = 0.01

        

        # ﻛﺛ۲ﻠﺅﺙ?.01ﺣ0.03%=0.000003ﮒﺅﺙﻛﺛﮔﻛﺛ?ﮒ?

        # ﮒ؟ﻠﮒﭦﻛﺕﭦ5ﮒﺅﺙﻛﺛﻠﻠ۱ﮒﺍﻛﭦﻛﺛ۲ﻠﺅﺙﮒﺁﻟﺛﻝﺗﮔ؟ﮒ۳ﻝ

        # ﻟﺟﮔﺓﻟﺑﺗﺅﺙ0.01ﺣ0.002%=0.0000002ﮒﺅﺙﻛﺛﮔﻛﺛ?ﮒ?

        # ﮔﭨﮔﮔ؛ﮒﺁﻟﺛﻟﭘﻟﺟﮔﻛﭦ۳ﻠﻠ۱?

        

        # ﻠ۹ﻟﺁﻟ؟۰ﻝ؟ﻛﺕﻛﺙﮒﺑ۸ﮔﭦ

        assert isinstance(result.total_cost, float)

    

    def test_very_large_amount(self):

        """ﮔﭖﻟﺁﮔﮒ۳۶ﻠﻠ۱"""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        order = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=10000000,  # 1000ﻛﺕﻟ۰

            price=1000.0,  # 1000ﮒ?

            market=MarketType.SZ,

            category=SecurityCategory.STOCK

        )

        

        result = calculator.calculate_total_cost(order)

        

        # ﮔﮒ۳۶ﻠﻠ۱ﺅﺙ?00ﻛﭦ?

        amount = 10000000 * 1000.0

        

        # ﻠ۹ﻟﺁﻟ؟۰ﻝ؟ﻛﺕﻛﺙﮔﭦ۱ﮒﭦ

        assert isinstance(result.total_cost, float)

        assert result.total_cost > 0

        

# ﻠ۹ﻟﺁﮔﮔ؛ﮒﮔﺁﮒﻝ

assert 0 < result.as_percentage < 0.01  # ﮔﮔ؛ﮒﮔﺁﮒﭦﮒﺍﻛﭦ?%

    

    def test_extreme_slippage_factors(self):

"""ﮔﭖﻟﺁﮔﻝ،ﺁﮔﭨﻝﺗﮒﮒ"""

        config = CostConfig()

        calculator = CostCalculator(config)

        

# ﮔﮔﮒﮒﻠﺛﮒﮔﻝ،ﺁﮒ?

        order = OrderInfo(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=200000,  # ﮔﮒ۳۶ﮒ?

            price=10.0,

            market=MarketType.SZ,

            category=SecurityCategory.STOCK,

            timestamp="2026-04-02 09:15:00",  # ﮒﺙﻝﮔﭘﮔ؟?

            market_data={

                "daily_volume": 1000,        # ﮔﻛﺛﮔﭖﮒ۷ﮔ?

                "volatility": 0.1,           # ﮔﻠ،ﮔﺏ۱ﮒ۷ﻝ?

                "avg_trade_size": 100

            }

        )

        

        result = calculator.calculate_total_cost(order)

        

        # ﻠ۹ﻟﺁﮔﭨﻝﺗﻛﺕﻟﭘﻟﺟﮔﮒ۳۶ﻠﮒ?

        amount = order.quantity * order.price

        slippage_rate = result.slippage / amount if amount > 0 else 0

        assert slippage_rate <= 0.01  # ﻛﺕﻟﭘﻟﺟ?%

    

    def test_rounding_edge_cases(self):

        """ﮔﭖﻟﺁﻟﮒ۴ﻟﺝﺗﻝﮔﮒﭖ"""

        config = CostConfig()

        config.precision = 2

        config.rounding_method = "ROUND"

        calculator = CostCalculator(config)

        

        # ﮔﭖﻟﺁﮒﻝ۶ﻟﮒ۴ﮔﮒﭖ

        test_cases = [

            (0.0049, 0.00),  # ﮒﻟﻛﭦﮒ۴ﺅﺙ?.0049 -> 0.00

            (0.0050, 0.01),  # ﮒﻟﻛﭦﮒ۴ﺅﺙ?.0050 -> 0.01

            (0.0149, 0.01),  # ﮒﻟﻛﭦﮒ۴ﺅﺙ?.0149 -> 0.01

            (0.0150, 0.02),  # ﮒﻟﻛﭦﮒ۴ﺅﺙ?.0150 -> 0.02

            (1.2345, 1.23),  # ﮒﻟﻛﭦﮒ۴ﺅﺙ?.2345 -> 1.23

            (1.2350, 1.24),  # ﮒﻟﻛﭦﮒ۴ﺅﺙ?.2350 -> 1.24

        ]

        

        for value, expected in test_cases:

            # ﮒﮒﭨﭦﻛﺕﻛﺕ۹ﻟ؟۱ﮒﺅﺙﻛﺛﺟﮒﺝﻛﺛ۲ﻠﻟ؟۰ﻝ؟ﻝﭨﮔﻛﺕﭦvalue

            # ﻝ؟ﮒﮔﭖﻟﺁﺅﺙﻝﺑﮔ۴ﮔﭖﻟﺁﻟﮒ۴ﮔﺗﮔﺏ

            rounded = calculator._round(value)

            assert rounded == expected, f"ﻟﮒ۴ﻠﻟﺁﺁﺅﺙ{value} -> {rounded}ﺅﺙﻠ۱ﮔﺅﺙ{expected}"

    

    def test_different_rounding_methods(self):

        """ﮔﭖﻟﺁﻛﺕﮒﻟﮒ۴ﮔﺗﮔﺏ"""

        # ﮔﭖﻟﺁﮒﻛﺕﮒﮔﺑ

        config1 = CostConfig()

        config1.precision = 2

        config1.rounding_method = "CEIL"

        calculator1 = CostCalculator(config1)

        

        assert calculator1._round(0.001) == 0.01  # ﮒﻛﺕﮒﮔﺑ

        assert calculator1._round(1.111) == 1.12   # ﮒﻛﺕﮒﮔﺑ

        

        # ﮔﭖﻟﺁﮒﻛﺕﮒﮔﺑ

        config2 = CostConfig()

        config2.precision = 2

        config2.rounding_method = "FLOOR"

        calculator2 = CostCalculator(config2)

        

        assert calculator2._round(0.009) == 0.00  # ﮒﻛﺕﮒﮔﺑ

        assert calculator2._round(1.119) == 1.11   # ﮒﻛﺕﮒﮔﺑ

        

        # ﮔﭖﻟﺁﮒﻟﻛﭦﮒ۴

        config3 = CostConfig()

        config3.precision = 2

        config3.rounding_method = "ROUND"

        calculator3 = CostCalculator(config3)

        

        assert calculator3._round(0.004) == 0.00  # ﮒﻟ

        assert calculator3._round(0.005) == 0.01  # ﻛﭦﮒ۴

```



### 2.3 ﻠﻝﺛ؟ﻠ۹ﻟﺁﮔﭖﻟﺁ



```python

# test_config_validation.py

import pytest

import yaml

from cost_calculator import CostConfig, TieredRate



class TestConfigValidation:

    """ﻠﻝﺛ؟ﻠ۹ﻟﺁﮔﭖﻟﺁ"""

    

    def test_valid_config(self):

        """ﮔﭖﻟﺁﮔﮔﻠﻝﺛ؟"""

        config = CostConfig()

        

        # ﻠ۹ﻟﺁﮒﭦﻝ۰ﻠﻝﺛ؟

        assert config.commission_rate == 0.0003

        assert config.min_commission == 5.0

        assert config.stamp_tax_rate == 0.001

        assert config.sh_transfer_rate == 0.00001

        assert config.sz_transfer_rate == 0.00002

        assert config.regulatory_rate == 0.00002

        

        # ﻠ۹ﻟﺁﻠﭨﻟ؟۳ﮒ?

        assert config.commission_tiered_rates is not None

        assert len(config.commission_tiered_rates) == 3

        assert config.stamp_tax_exempt_categories is not None

        assert len(config.stamp_tax_exempt_categories) == 4

        assert config.regulatory_components is not None

        assert len(config.regulatory_components) == 3

    

    def test_invalid_rate_range(self):

"""ﮔﭖﻟﺁﮔﮔﻟﺑﺗﻝﻟﮒﺑ"""

        # ﻛﺛ۲ﻠﻝﻟﭘﮒﭦﻟﮒ?

        config = CostConfig()

        config.commission_rate = 0.005  # 0.5%ﺅﺙﻟﭘﮒﭦﮒﻝﻟﮒ?

        

# ﮒ؟ﻠﮒ؟ﻝﺍﻛﺕﮒﭦﮔﻠ۹ﻟﺁﮔﭦﮒ?

        # ﻟﺟﻠﮔﭖﻟﺁﻠﻝﺛ؟ﮒﺁﺗﻟﺎ۰ﻟﺛﮒ۵ﮒﮒﭨﭦ

        

    def test_invalid_tiered_rates(self):

"""ﮔﭖﻟﺁﮔﮔﻠﭘﮔ۱ﺁﻟﺑﺗﻝ"""

        # ﻠﮒﺙﻛﺕﻠﮒ۱

        config = CostConfig()

        config.commission_tiered_rates = [

            TieredRate(threshold=5000000, rate=0.0003),

            TieredRate(threshold=1000000, rate=0.00025),  # ﻠﮒﺙﮒﺍﻛﭦﮒﻛﺕﻛﺕ?

            TieredRate(threshold=None, rate=0.0002)

        ]

        

        # ﻟﺑﺗﻝﻛﺕﻠﮒ

        config2 = CostConfig()

        config2.commission_tiered_rates = [

            TieredRate(threshold=1000000, rate=0.0003),

            TieredRate(threshold=5000000, rate=0.00035),  # ﻟﺑﺗﻝﮒ۳۶ﻛﭦﮒﻛﺕﻛﺕ?

            TieredRate(threshold=None, rate=0.0002)

        ]

        

# ﮒ؟ﻠﮒ؟ﻝﺍﻛﺕﮒﭦﮔﻠ۹ﻟﺁﮔﭦﮒ?

    

    def test_config_from_yaml(self):

"""ﮔﭖﻟﺁﻛﭨYAMLﮒﻟﺛﺛﻠﻝﺛ؟"""

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

        

# ﻠ۹ﻟﺁﻠﻝﺛ؟ﮒﻟﺛﺛ

        assert config.commission_rate == 0.00025

        assert config.stamp_tax_rate == 0.001

        assert config.sh_transfer_rate == 0.00001

        assert config.slippage_base_rate == 0.0002

    

    def test_config_validation_tool(self):

        """ﮔﭖﻟﺁﻠﻝﺛ؟ﻠ۹ﻟﺁﮒﺓ۴ﮒﺓ"""

        # ﮒﮒﭨﭦﻠﻝﺛ؟ﻠ۹ﻟﺁﮒﺓ۴ﮒﺓﮔﭖﻟﺁ

# ﮒ؟ﻠﮒ؟ﻝﺍﻛﺕﮒﭦﮔﻛﺕﻠ۷ﻝﻠﻝﺛ؟ﻠ۹ﻟﺁﮒﺓ۴ﮒﺓ

        pass

```



## 3. ﻠﮔﮔﭖﻟﺁﻟ؟ﺝﻟ؟۰



### 3.1 ﮒ۳ﮒﺙﮔﻠﻠﮒ۷ﻠﮔﮔﭖﻟﺁ?



```python

# test_integration_adapters.py

import pytest

from engines.base import BaseEngineAdapter, EngineConfig, UnifiedOrder, OrderSide

from engines.factory import EngineFactory

from cost_calculator import CostCalculator, CostConfig



class TestIntegrationWithAdapters:

    """ﻠﻠﮒ۷ﻠﮔﮔﭖﻟﺁ?""

    

    def test_vnpy_adapter_integration(self):

        """ﮔﭖﻟﺁvn.pyﻠﻠﮒ۷ﻠﮔ?""

        # ﮒﮒﭨﭦvn.pyﻠﻠﮒ۷ﻠﻝﺛ?

        vnpy_config = EngineConfig(

            engine_type="vnpy",

            config_path="config/vnpy_simulation.yaml"

        )

        

        # ﮒﮒﭨﭦﻠﻠﮒ?

        factory = EngineFactory()

        adapter = factory.create_adapter(vnpy_config)

        

        # ﻠ۹ﻟﺁﻠﻠﮒ۷ﮒﮒ،ﮔﮔ؛ﻟ؟۰ﻝ؟ﮒ۷

        assert hasattr(adapter, 'cost_calculator')

        assert isinstance(adapter.cost_calculator, CostCalculator)

        

        # ﮒﮒﭨﭦﻝﭨﻛﺕﻟ؟۱ﮒ

        order = UnifiedOrder(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=10000,

            price=10.0,

            order_type="LIMIT"

        )

        

        # ﮔﭖﻟﺁﮔﮔ؛ﻛﺙﺍﻝ؟

        cost_estimate = adapter.get_cost_estimate(order)

        assert "total_cost" in cost_estimate

        assert "commission" in cost_estimate

        assert "stamp_tax" in cost_estimate

        assert "transfer_fee" in cost_estimate

        assert "regulatory_fees" in cost_estimate

        assert "slippage" in cost_estimate

    

    def test_rqalpha_adapter_integration(self):

        """ﮔﭖﻟﺁRQAlphaﻠﻠﮒ۷ﻠﮔ?""

        # ﻝﺎﭨﻛﺙﺙvn.pyﻠﻠﮒ۷ﮔﭖﻟﺁ?

        pass

    

    def test_cost_report_generation(self):

        """ﮔﭖﻟﺁﮔﮔ؛ﮔ۴ﮒﻝﮔ"""

        # ﮔﭖﻟﺁﻟ؟۱ﮒﮔ۶ﻟ۰ﮒﻝﮔﻟﺁ۵ﻝﭨﮔﮔ؛ﮔ۴ﮒ?

        pass

    

    def test_multiple_adapters_consistency(self):

        """ﮔﭖﻟﺁﮒ۳ﻠﻠﮒ۷ﮔﮔ؛ﻟ؟۰ﻝ؟ﻛﺕﻟﺑﮔ?""

        # ﮒﮒﭨﭦﮒ۳ﻛﺕ۹ﻠﻠﮒ?

        factory = EngineFactory()

        

        vnpy_adapter = factory.create_adapter(

            EngineConfig(engine_type="vnpy")

        )

        

        rqalpha_adapter = factory.create_adapter(

            EngineConfig(engine_type="rqalpha")

        )

        

# ﮒﻛﺕﻟ؟۱ﮒﮒ۷ﻛﺕﮒﻠﻠﮒ۷ﻛﺕﮔﮔ؛ﮒﭦﻛﺕﻟ?

        order = UnifiedOrder(

            symbol="000001.SZ",

            side=OrderSide.BUY,

            quantity=10000,

            price=10.0,

            order_type="LIMIT"

        )

        

        vnpy_cost = vnpy_adapter.get_cost_estimate(order)

        rqalpha_cost = rqalpha_adapter.get_cost_estimate(order)

        

        # ﮔﮔ؛ﻟ؟۰ﻝ؟ﮒﭦﮒﭦﮔ؛ﻛﺕﻟﺑﺅﺙﮒﻟ؟ﺕﮒﺝ؟ﮒﺍﮒﺓ؟ﮒﺙﺅﺙ?

        assert abs(vnpy_cost["total_cost"] - rqalpha_cost["total_cost"]) < 0.01

```



### 3.2 ﻠﻝﺛ؟ﻝ؟۰ﻝﻠﮔﮔﭖﻟﺁ



```python

# test_integration_config.py

import pytest

import yaml

import tempfile

import os

from cost_calculator import CostCalculator, CostConfig



class TestIntegrationWithConfig:

    """ﻠﻝﺛ؟ﻝ؟۰ﻝﻠﮔﮔﭖﻟﺁ"""

    

    def test_config_file_loading(self):

"""ﮔﭖﻟﺁﻠﻝﺛ؟ﮔﻛﭨﭘﮒﻟﺛﺛ"""

        # ﮒﮒﭨﭦﻛﺕﺑﮔﭘﻠﻝﺛ؟ﮔﻛﭨﭘ

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

# ﮒﻟﺛﺛﻠﻝﺛ؟ﮔﻛﭨﭘ

            with open(config_path, 'r') as f:

                config_dict = yaml.safe_load(f)["cost_config"]

            

            # ﮒﮒﭨﭦﻠﻝﺛ؟ﮒﺁﺗﻟﺎ۰

            config = CostConfig(**config_dict)

            calculator = CostCalculator(config)

            

            # ﻠ۹ﻟﺁﻠﻝﺛ؟ﻝﮔ

            order = OrderInfo(

                symbol="000001.SZ",

                side=OrderSide.BUY,

                quantity=10000,

                price=10.0,

                market=MarketType.SZ,

                category=SecurityCategory.STOCK

            )

            

            result = calculator.calculate_total_cost(order)

            

            # ﻛﺛ۲ﻠﻝﮒﭦﻛﺕ?.025%

            expected_commission = max(100000 * 0.00025, 5.0)

            assert result.commission == pytest.approx(expected_commission, rel=0.01)

            

        finally:

            # ﮔﺕﻝﻛﺕﺑﮔﭘﮔﻛﭨﭘ

            os.unlink(config_path)

    

    def test_config_hot_reload(self):

"""ﮔﭖﻟﺁﻠﻝﺛ؟ﻝﻠﻟﺛ?""

        # ﮔﭖﻟﺁﻟﺟﻟ۰ﮔﭘﻛﺟ؟ﮔﺗﻠﻝﺛ?

        pass

    

    def test_config_validation_integration(self):

        """ﮔﭖﻟﺁﻠﻝﺛ؟ﻠ۹ﻟﺁﻠﮔ"""

# ﮔﭖﻟﺁﮒﻟﺛﺛﮔﮔﻠﻝﺛ؟ﮔﭘﻝﻠﻟﺁﺁﮒ۳ﻝ

        pass

```



## 4. ﮔ۶ﻟﺛﮔﭖﻟﺁﻟ؟ﺝﻟ؟۰



### 4.1 ﮒﮔ؛۰ﻟ؟۰ﻝ؟ﮔ۶ﻟﺛﮔﭖﻟﺁ



```python

# test_performance_basic.py

import pytest

import time

from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory



class TestPerformanceBasic:

    """ﮒﭦﻝ۰ﮔ۶ﻟﺛﮔﭖﻟﺁ"""

    

    def test_single_calculation_performance(self):

        """ﮔﭖﻟﺁﮒﮔ؛۰ﻟ؟۰ﻝ؟ﮔ۶ﻟﺛ"""

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

        

# ﻠ۱ﻝ

        for _ in range(10):

            calculator.calculate_total_cost(order)

        

        # ﮔ۶ﻟﺛﮔﭖﻟﺁ

        start_time = time.perf_counter()

        for _ in range(1000):

            calculator.calculate_total_cost(order)

        end_time = time.perf_counter()

        

        total_time = end_time - start_time

        avg_time = total_time / 1000 * 1000  # ﻟﺛ؛ﮔ۱ﻛﺕﭦﮔﺁ،ﻝ۶?

        

        print(f"ﮒﮔ؛۰ﻟ؟۰ﻝ؟ﮒﺗﺏﮒﮔﭘﻠﺑ: {avg_time:.3f}ms")

assert avg_time < 1.0  # ﻝ؟ﮔﺅﺙ?1ms

    

    def test_calculation_with_cache(self):

"""ﮔﭖﻟﺁﮒﺕ۵ﻝﺙﮒﻝﮔ۶ﻟﺛ"""

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

        

# ﻝ؛؛ﻛﺕﮔ؛۰ﻟ؟۰ﻝ؟ﺅﺙﮔﻝﺙﮒﺅﺙ

        start_time1 = time.perf_counter()

        result1 = calculator.calculate_total_cost(order)

        end_time1 = time.perf_counter()

        

        time1 = (end_time1 - start_time1) * 1000

        

# ﻝ؛؛ﻛﭦﮔ؛۰ﻟ؟۰ﻝ؟ﺅﺙﮔﻝﺙﮒﺅﺙ

        start_time2 = time.perf_counter()

        result2 = calculator.calculate_total_cost(order)

        end_time2 = time.perf_counter()

        

        time2 = (end_time2 - start_time2) * 1000

        

print(f"ﻝ؛؛ﻛﺕﮔ؛۰ﻟ؟۰ﻝ؟ﺅﺙﮔﻝﺙﮒﺅﺙ: {time1:.3f}ms")

print(f"ﻝ؛؛ﻛﭦﮔ؛۰ﻟ؟۰ﻝ؟ﺅﺙﮔﻝﺙﮒﺅﺙ: {time2:.3f}ms")

        

# ﻝﺙﮒﮒﺛﻛﺕﮒﮒﭦﮔﺑﮒﺟ،

        assert time2 < time1

        

        # ﻝﭨﮔﮒﭦﻝﺕﮒ?

        assert result1.total_cost == result2.total_cost

```



### 4.2 ﮔﺗﻠﻟ؟۰ﻝ؟ﮔ۶ﻟﺛﮔﭖﻟﺁ



```python

# test_performance_batch.py

import pytest

import time

import random

from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory



class TestPerformanceBatch:

    """ﮔﺗﻠﮔ۶ﻟﺛﮔﭖﻟﺁ"""

    

    def generate_test_orders(self, count=1000):

        """ﻝﮔﮔﭖﻟﺁﻟ؟۱ﮒ"""

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

        """ﮔﭖﻟﺁﮔﺗﻠﻟ؟۰ﻝ؟ﮔ۶ﻟﺛ"""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        # ﻝﮔ1000ﻛﺕ۹ﮔﭖﻟﺁﻟ؟۱ﮒ?

        orders = self.generate_test_orders(1000)

        

# ﻠ۱ﻝ

        for order in orders[:100]:

            calculator.calculate_total_cost(order)

        

        # ﮔﺗﻠﻟ؟۰ﻝ؟ﮔ۶ﻟﺛﮔﭖﻟﺁ

        start_time = time.perf_counter()

        

        results = []

        for order in orders:

            result = calculator.calculate_total_cost(order)

            results.append(result)

        

        end_time = time.perf_counter()

        

        total_time = (end_time - start_time) * 1000  # ﻟﺛ؛ﮔ۱ﻛﺕﭦﮔﺁ،ﻝ۶?

        avg_time = total_time / len(orders)

        

        print(f"ﮔﺗﻠﻟ؟۰ﻝ؟ {len(orders)} ﻛﺕ۹ﻟ؟۱ﮒﺅﺙﮔﭨﮔﭘﻠ? {total_time:.1f}ms")

        print(f"ﮒﺗﺏﮒﮔﺁﻛﺕ۹ﻟ؟۱ﮒﻟ؟۰ﻝ؟ﮔﭘﻠﺑ: {avg_time:.3f}ms")

        

assert avg_time < 0.5  # ﻝ؟ﮔﺅﺙ?0.5ms/ﻟ؟۱ﮒ

        assert len(results) == len(orders)

    

    def test_concurrent_calculation(self):

        """ﮔﭖﻟﺁﮒﺗﭘﮒﻟ؟۰ﻝ؟"""

        # ﮔﭖﻟﺁﮒ۳ﻝﭦﺟﻝ۷?ﮒ۳ﻟﺟﻝ۷ﻟ؟۰ﻝ؟ﮔ۶ﻟﺛ

        pass

    

    def test_memory_usage(self):

"""ﮔﭖﻟﺁﮒﮒﻛﺛﺟﻝ۷"""

        config = CostConfig()

        calculator = CostCalculator(config)

        

# ﮔﭖﻟﺁﻝﺙﮒﮒﮒﮒﻝ۷

        orders = self.generate_test_orders(10000)

        

        import psutil

        import os

        

        process = psutil.Process(os.getpid())

        memory_before = process.memory_info().rss / 1024 / 1024  # MB

        

# ﻟ؟۰ﻝ؟ﮒ۳۶ﻠﻟ؟۱ﮒﺅﺙﮒ۰،ﮒﻝﺙﮒ?

        for order in orders[:1000]:

            calculator.calculate_total_cost(order)

        

        memory_after = process.memory_info().rss / 1024 / 1024  # MB

        memory_increase = memory_after - memory_before

        

print(f"ﮒﮒﻛﺛﺟﻝ۷ﮒ۱ﮒ: {memory_increase:.2f}MB")

        

# ﻠ۹ﻟﺁﮒﮒﮒ۱ﮒﮒﻝ

assert memory_increase < 100  # ﮒ۱ﮒﮒﭦﮒﺍﻛﭦ?00MB

```



### 4.3 ﮒﮒﮔﭖﻟﺁ



```python

# test_performance_stress.py

import pytest

import time

import threading

from cost_calculator import CostCalculator, CostConfig, OrderInfo, OrderSide, MarketType, SecurityCategory



class TestPerformanceStress:

    """ﮒﮒﮔﭖﻟﺁ"""

    

    def test_high_frequency_calculation(self):

        """ﮔﭖﻟﺁﻠ،ﻠ۱ﻟ؟۰ﻝ؟"""

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

        

        # ﮔ۷۰ﮔﻠ،ﻠ۱ﻛﭦ۳ﮔﺅﺙ?ﻝ۶ﮒﻟ؟۰ﻝ؟10000ﮔ؛?

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

        

        print(f"ﮒ؟ﻠﻟ؟۰ﻝ؟ﻠﻝ: {actual_rate:.0f} ﮔ؛?ﻝ۶?)

print(f"ﻝ؟ﮔﻟ؟۰ﻝ؟ﻠﻝ: {calculations_per_second} ﮔ؛?ﻝ۶?)

        print(f"ﮒ؟ﮔﻟ؟۰ﻝ؟ﮔ؛۰ﮔﺍ: {count}")

        

        # ﻠ۹ﻟﺁﻟﺛﮒ۳ﮒ۳ﻝﻠ،ﻠ۱ﻟ؟۰ﻝ؟

assert actual_rate > calculations_per_second * 0.5  # ﻟﺏﮒﺍﻟﺝﺝﮒﺍﻝ؟ﮔﻝ?0%

    

    def test_concurrent_stress(self):

        """ﮔﭖﻟﺁﮒﺗﭘﮒﮒﮒ"""

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

        

        # ﮒﮒﭨﭦﮒ۳ﻛﺕ۹ﻝﭦﺟﻝ۷ﮒﺗﭘﮒﻟ؟۰ﻝ؟

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

        

        # ﮒﺁﮒ۷ﮔﮔﻝﭦﺟﻝ۷?

        for thread in threads:

            thread.start()

        

# ﻝﮒﺝﮔﮔﻝﭦﺟﻝ۷ﮒ؟ﮔ?

        for thread in threads:

            thread.join()

        

        end_time = time.perf_counter()

        

        total_time = end_time - start_time

        total_calculations = thread_count * calculations_per_thread

        calculations_per_second = total_calculations / total_time

        

        print(f"ﮒﺗﭘﮒﻟ؟۰ﻝ؟ﮒ؟ﮔ: {total_calculations} ﮔ؛۰ﻟ؟۰ﻝ؟?)

        print(f"ﮔﭨﮔﭘﻠ? {total_time:.2f}ﻝ۶?)

        print(f"ﻟ؟۰ﻝ؟ﻠﻝ: {calculations_per_second:.0f} ﮔ؛?ﻝ۶?)

        

# ﻠ۹ﻟﺁﮒﺗﭘﮒﻟ؟۰ﻝ؟ﮔ۲ﻝ۰؟ﮔ?

        assert len(results) == total_calculations

        

        # ﮔﮔﻟ؟۰ﻝ؟ﻝﭨﮔﮒﭦﻛﺕﻟ?

        first_result = results[0][2]

        for _, _, result in results:

            assert result == pytest.approx(first_result, rel=0.01)

```



## 5. ﮒﮒﺛﮔﭖﻟﺁﻟ؟ﺝﻟ؟۰



### 5.1 ﮔﭖﻟﺁﻟ۹ﮒ۷ﮒ?



```python

# test_regression.py

import pytest

import json

import os

from pathlib import Path

from cost_calculator import CostCalculator, CostConfig



class TestRegression:

    """ﮒﮒﺛﮔﭖﻟﺁ"""

    

    def load_regression_data(self):

"""ﮒﻟﺛﺛﮒﮒﺛﮔﭖﻟﺁﮔﺍﮔ؟"""

        data_path = Path(__file__).parent / "test_data" / "regression_cases.json"

        with open(data_path, 'r', encoding='utf-8') as f:

            return json.load(f)

    

    def test_regression_cases(self):

        """ﮒﮒﺛﮔﭖﻟﺁﻝ۷ﻛﺝ"""

        config = CostConfig()

        calculator = CostCalculator(config)

        

        regression_cases = self.load_regression_data()

        

        failed_cases = []

        

        for case in regression_cases:

            # ﮒﮒﭨﭦﻟ؟۱ﮒ

            order = OrderInfo(**case["order"])

            

            # ﻟ؟۰ﻝ؟ﮔﮔ؛

            result = calculator.calculate_total_cost(order)

            

            # ﻠ۹ﻟﺁﻝﭨﮔ

            expected = case["expected"]

            

            errors = []

            

            # ﮔ۲ﮔ۴ﮒﻠ۰ﺗﮔﮔ?

            if abs(result.commission - expected["commission"]) > 0.01:

                errors.append(f"ﻛﺛ۲ﻠﻛﺕﮒﺗﻠ? {result.commission} != {expected['commission']}")

            

            if abs(result.stamp_tax - expected["stamp_tax"]) > 0.01:

                errors.append(f"ﮒﺍﻟﺎﻝ۷ﻛﺕﮒﺗﻠ: {result.stamp_tax} != {expected['stamp_tax']}")

            

            if abs(result.transfer_fee - expected["transfer_fee"]) > 0.01:

                errors.append(f"ﻟﺟﮔﺓﻟﺑﺗﻛﺕﮒﺗﻠ: {result.transfer_fee} != {expected['transfer_fee']}")

            

            if abs(result.regulatory_fees - expected["regulatory_fees"]) > 0.01:

                errors.append(f"ﻟ۶ﻟﺑﺗﻛﺕﮒﺗﻠ? {result.regulatory_fees} != {expected['regulatory_fees']}")

            

            if abs(result.slippage - expected["slippage"]) > 0.01:

                errors.append(f"ﮔﭨﻝﺗﻛﺕﮒﺗﻠ? {result.slippage} != {expected['slippage']}")

            

            if abs(result.total_cost - expected["total_cost"]) > 0.01:

                errors.append(f"ﮔﭨﮔﮔ؛ﻛﺕﮒﺗﻠ: {result.total_cost} != {expected['total_cost']}")

            

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

        

        # ﻟﺝﮒﭦﮒ۳ﺎﻟﺑ۴ﻝ۷ﻛﺝ

        if failed_cases:

            print(f"ﮒﮒﺛﮔﭖﻟﺁﮒ۳ﺎﻟﺑ۴ﻝ۷ﻛﺝﮔ? {len(failed_cases)}")

            for failed in failed_cases[:5]:  # ﮒ۹ﮔﺝﻝ۳ﭦﮒ5ﻛﺕ۹ﮒ۳ﺎﻟﺑ۴ﻝ۷ﻛﺝ?

                print(f"ﮒ۳ﺎﻟﺑ۴ﻝ۷ﻛﺝ: {failed['case']}")

                for error in failed['errors']:

                    print(f"  {error}")

            

            assert False, f"ﮒﮒﺛﮔﭖﻟﺁﮒ۳ﺎﻟﺑ۴: {len(failed_cases)} ﻛﺕ۹ﻝ۷ﻛﺝﮔ۹ﻠﻟﺟ"

    

    def test_backward_compatibility(self):

        """ﮔﭖﻟﺁﮒﮒﮒﺙﮒ؟ﺗﮔ?""

        # ﮔﭖﻟﺁﮔﺍﻝﮔ؛ﻛﺕﮔ۶ﻝﮔ؛ﻟ؟۰ﻝ؟ﻝﭨﮔﻝﮒﺙﮒ؟ﺗﮔ?

        pass

    

    def test_config_compatibility(self):

        """ﮔﭖﻟﺁﻠﻝﺛ؟ﮒﺙﮒ؟ﺗﮔ?""

        # ﮔﭖﻟﺁﮔﺍﻠﻝﺛ؟ﻛﺕﮔ۶ﻠﻝﺛ؟ﻝﮒﺙﮒ؟ﺗﮔ?

        pass

```



## 6. ﮔﭖﻟﺁﮔ۶ﻟ۰ﻛﺕﮔ۴ﮒ?



### 6.1 ﮔﭖﻟﺁﮔ۶ﻟ۰ﻟﮔ؛



```python

#!/usr/bin/env python3

# run_tests.py



import sys

import pytest

import time

from pathlib import Path



def run_all_tests():

    """ﻟﺟﻟ۰ﮔﮔﮔﭖﻟﺁ?""

    print("=" * 80)

    print("ﻛﭦ۳ﮔﮔﮔ؛ﮔ۷۰ﮒﮔﭖﻟﺁﮒ۴ﻛﭨﭘ")

    print("=" * 80)

    

    test_dir = Path(__file__).parent / "tests"

    

    # ﻟﺟﻟ۰ﮒﮒﮔﭖﻟﺁ

    print("\n1. ﻟﺟﻟ۰ﮒﮒﮔﭖﻟﺁ...")

    start_time = time.time()

    result = pytest.main([

        str(test_dir / "unit"),

        "-v",

        "--tb=short",

        "--junitxml=test_reports/unit_test_results.xml"

    ])

    unit_time = time.time() - start_time

    

    if result == 0:

        print(f"ﻗ?ﮒﮒﮔﭖﻟﺁﻠﻟﺟﺅﺙﻟﮔﭘ: {unit_time:.1f}ﻝ۶?)

    else:

        print(f"ﻗ?ﮒﮒﮔﭖﻟﺁﮒ۳ﺎﻟﺑ۴ﺅﺙﻟﮔﭘ: {unit_time:.1f}ﻝ۶?)

        return False

    

    # ﻟﺟﻟ۰ﻠﮔﮔﭖﻟﺁ

    print("\n2. ﻟﺟﻟ۰ﻠﮔﮔﭖﻟﺁ...")

    start_time = time.time()

    result = pytest.main([

        str(test_dir / "integration"),

        "-v",

        "--tb=short",

        "--junitxml=test_reports/integration_test_results.xml"

    ])

    integration_time = time.time() - start_time

    

    if result == 0:

        print(f"ﻗ?ﻠﮔﮔﭖﻟﺁﻠﻟﺟﺅﺙﻟﮔﭘ: {integration_time:.1f}ﻝ۶?)

    else:

        print(f"ﻗ?ﻠﮔﮔﭖﻟﺁﮒ۳ﺎﻟﺑ۴ﺅﺙﻟﮔﭘ: {integration_time:.1f}ﻝ۶?)

        return False

    

    # ﻟﺟﻟ۰ﮔ۶ﻟﺛﮔﭖﻟﺁ

    print("\n3. ﻟﺟﻟ۰ﮔ۶ﻟﺛﮔﭖﻟﺁ...")

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

        print(f"ﻗ?ﮔ۶ﻟﺛﮔﭖﻟﺁﮒ؟ﮔﺅﺙﻟﮔﭘ: {performance_time:.1f}ﻝ۶?)

    else:

        print(f"ﻗ?ﮔ۶ﻟﺛﮔﭖﻟﺁﮒ۳ﺎﻟﺑ۴ﺅﺙﻟﮔﭘ: {performance_time:.1f}ﻝ۶?)

        return False

    

    # ﻟﺟﻟ۰ﮒﮒﺛﮔﭖﻟﺁ

    print("\n4. ﻟﺟﻟ۰ﮒﮒﺛﮔﭖﻟﺁ...")

    start_time = time.time()

    result = pytest.main([

        str(test_dir / "regression"),

        "-v",

        "--tb=short",

        "--junitxml=test_reports/regression_test_results.xml"

    ])

    regression_time = time.time() - start_time

    

    if result == 0:

        print(f"ﻗ?ﮒﮒﺛﮔﭖﻟﺁﻠﻟﺟﺅﺙﻟﮔﭘ: {regression_time:.1f}ﻝ۶?)

    else:

        print(f"ﻗ?ﮒﮒﺛﮔﭖﻟﺁﮒ۳ﺎﻟﺑ۴ﺅﺙﻟﮔﭘ: {regression_time:.1f}ﻝ۶?)

        return False

    

    total_time = unit_time + integration_time + performance_time + regression_time

    

    print("\n" + "=" * 80)

    print("ﮔﭖﻟﺁﮔﺎﮔ?)

    print("=" * 80)

    print(f"ﮒﮒﮔﭖﻟﺁ:     {unit_time:.1f}ﻝ۶?)

    print(f"ﻠﮔﮔﭖﻟﺁ:     {integration_time:.1f}ﻝ۶?)

    print(f"ﮔ۶ﻟﺛﮔﭖﻟﺁ:     {performance_time:.1f}ﻝ۶?)

    print(f"ﮒﮒﺛﮔﭖﻟﺁ:     {regression_time:.1f}ﻝ۶?)

    print(f"ﮔﭨﻟ؟۰:         {total_time:.1f}ﻝ۶?)

    print("=" * 80)

    print("ﻗ?ﮔﮔﮔﭖﻟﺁﻠﻟﺟ!")

    

    return True



if __name__ == "__main__":

    success = run_all_tests()

    sys.exit(0 if success else 1)

```



### 6.2 ﮔﭖﻟﺁﮔ۴ﮒﻝﮔ



```python

# generate_test_report.py



import json

import xml.etree.ElementTree as ET

from datetime import datetime

```

