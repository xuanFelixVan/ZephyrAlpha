---
module_id: FACTOR_LIBRARY_BLUEPRINT_001
version: 1.0.0
status: Active
created_date: 2026-04-07
last_updated: 2026-04-07
owner: 因子工程团队
standard_type: 通用文档
applicable_scope: 全系统
compliance_level: 专业标准
---

﻿---
module_id: INDEX_LIBRARY_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构�?
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管�?
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行�?
---


# 因子库对接蓝�?

> 清风量化系统 v5.0 - 因子库系�?
> **索引**: `DATA.003`
> **开发时�?*: 25h
> **核心定位**: 实现"因子定义 �?计算 �?验证 �?存储 �?查询"的完整因子生命周期管�?


## 1. 设计原则

| 原则 | 说明 |
|------|------|
| **复用Talib** | 技术指标使用TA-Lib，不重复实现 |
| **模板化因�?* | 新因子通过模板快速定�?|
| **IC验证** | 因子入库前必须通过IC验证 |
| **版本管理** | 因子版本完整记录 |


## 2. 因子架构

### 2.1 因子分类

| 类别 | 说明 | 示例 |
|------|------|------|
| 技术因�?| TA-Lib计算 | MA, RSI, MACD |
| 量价因子 | 量价关系 | Momentum, Volume |
| 财务因子 | 财务数据 | PE, PB, ROE |
| 另类因子 | 非传统数�?| 舆情、研�?|

### 2.2 因子定义

```python
class Factor:
    """因子定义

    索引: DATA.003-M01
    """

    def __init__(
        self,
        name: str,
        category: str,
        description: str,
        calculator: Callable,
        params: dict = None
    ):
        self.id = f"{name}_{hash(str(params))}"
        self.name = name
        self.category = category
        self.description = description
        self.calculator = calculator
        self.params = params or {}

    def calculate(self, data: pd.DataFrame) -> pd.Series:
        """计算因子�?

        参数:
            data: OHLCV数据

        返回:
            因子值序�?
        """
        return self.calculator(data, **self.params)

    def to_dict(self) -> dict:
        """转换为字�?""
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category,
            'description': self.description,
            'params': self.params
        }
```


## 3. 核心因子�?

### 3.1 TA-Lib因子模板

```python
class TALibFactor:
    """TA-Lib因子工厂

    索引: DATA.003-M02
    """

    @staticmethod
    def create_ma(period: int = 20) -> Factor:
        """创建移动平均因子"""
        def calc(data, period):
            return data['close'].rolling(period).mean()
        return Factor(
            name=f"ma_{period}",
            category="technical",
            description=f"{period}日移动平�?,
            calculator=calc,
            params={'period': period}
        )

    @staticmethod
    def create_rsi(period: int = 14) -> Factor:
        """创建RSI因子"""
        def calc(data, period):
            delta = data['close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(period).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(period).mean()
            rs = gain / loss
            return 100 - (100 / (1 + rs))
        return Factor(
            name=f"rsi_{period}",
            category="technical",
            description=f"{period}日RSI",
            calculator=calc,
            params={'period': period}
        )

    @staticmethod
    def create_macd(fast: int = 12, slow: int = 26, signal: int = 9) -> Factor:
        """创建MACD因子"""
        def calc(data, fast, slow, signal):
            ema_fast = data['close'].ewm(span=fast).mean()
            ema_slow = data['close'].ewm(span=slow).mean()
            macd = ema_fast - ema_slow
            signal_line = macd.ewm(span=signal).mean()
            return macd - signal_line
        return Factor(
            name=f"macd_{fast}_{slow}_{signal}",
            category="technical",
            description="MACD",
            calculator=calc,
            params={'fast': fast, 'slow': slow, 'signal': signal}
        )

    @staticmethod
    def create_bollinger(period: int = 20, std: float = 2.0) -> Factor:
        """创建布林带因�?""
        def calc(data, period, std):
            ma = data['close'].rolling(period).mean()
            std_dev = data['close'].rolling(period).std()
            upper = ma + std_dev * std
            lower = ma - std_dev * std
            return (data['close'] - lower) / (upper - lower)
        return Factor(
            name=f"bb_{period}_{std}",
            category="technical",
            description="布林带位�?,
            calculator=calc,
            params={'period': period, 'std': std}
        )
```

### 3.2 量价因子

```python
class PriceVolumeFactor:
    """量价因子�?

    索引: DATA.003-M03
    """

    @staticmethod
    def momentum(period: int = 20) -> Factor:
        """动量因子"""
        def calc(data, period):
            return data['close'].pct_change(period)
        return Factor(
            name=f"momentum_{period}",
            category="price_volume",
            description=f"{period}日动�?,
            calculator=calc,
            params={'period': period}
        )

    @staticmethod
    def volume_ratio(period: int = 20) -> Factor:
        """成交量比�?""
        def calc(data, period):
            avg_volume = data['volume'].rolling(period).mean()
            return data['volume'] / avg_volume
        return Factor(
            name=f"volume_ratio_{period}",
            category="price_volume",
            description=f"{period}日均量比",
            calculator=calc,
            params={'period': period}
        )

    @staticmethod
    def turnover_rate(period: int = 20) -> Factor:
        """换手率因�?""
        def calc(data, period):
            return data['volume'].rolling(period).sum() / data['float_share']
        return Factor(
            name=f"turnover_{period}",
            category="price_volume",
            description=f"{period}日换手率",
            calculator=calc,
            params={'period': period}
        )
```


## 4. 因子验证

### 4.1 IC验证�?

```python
class FactorValidator:
    """因子验证�?

    索引: DATA.003-M04
    上游: FactorCalculator
    下游: FactorRepository
    """

    def validate(
        self,
        factor_values: pd.DataFrame,
        returns: pd.Series,
        thresholds: dict = None
    ) -> ValidationResult:
        """验证因子

        参数:
            factor_values: 因子�?(index=date, columns=symbols)
            returns: 收益�?
            thresholds: 验证门槛

        返回:
            ValidationResult
        """
        thresholds = thresholds or {
            'ic_mean_min': 0.03,
            'ic_ir_min': 0.3,
            'decay_max': 0.3
        }

        # 计算IC
        ic_series = self._calculate_ic(factor_values, returns)
        ic_mean = ic_series.mean()
        ic_std = ic_series.std()
        ic_ir = ic_mean / ic_std if ic_std > 0 else 0

        # IC衰减
        ic_decay = self._calculate_decay(ic_series)

        # 判定
        passed = (
            ic_mean >= thresholds['ic_mean_min'] and
            ic_ir >= thresholds['ic_ir_min'] and
            ic_decay <= thresholds['decay_max']
        )

        return ValidationResult(
            passed=passed,
            ic_mean=ic_mean,
            ic_ir=ic_ir,
            ic_decay=ic_decay,
            ic_series=ic_series,
            thresholds=thresholds
        )

    def _calculate_ic(
        self,
        factor: pd.DataFrame,
        returns: pd.Series
    ) -> pd.Series:
        """计算IC序列"""
        ic_series = []
        for date in factor.index:
            if date not in returns.index:
                continue
            try:
                ic = factor.loc[date].corr(returns.loc[date])
                ic_series.append((date, ic))
            except:
                continue
        return pd.Series(dict(ic_series), name='ic')
```

### 4.2 验证报告

```python
@dataclass
class ValidationResult:
    """验证结果"""
    passed: bool
    ic_mean: float
    ic_ir: float
    ic_decay: float
    ic_series: pd.Series
    thresholds: dict

    def to_report(self) -> str:
        """生成验证报告"""
        status = "�?通过" if self.passed else "�?未通过"
        return f"""
# 因子验证报告

## 验证结果: {status}

## IC指标
| 指标 | �?| 门槛 | 判定 |
|------|-----|------|------|
| IC均�?| {self.ic_mean:.4f} | {self.thresholds['ic_mean_min']} | {'�? if self.ic_mean >= self.thresholds['ic_mean_min'] else '�?} |
| IC_IR | {self.ic_ir:.4f} | {self.thresholds['ic_ir_min']} | {'�? if self.ic_ir >= self.thresholds['ic_ir_min'] else '�?} |
| IC衰减 | {self.ic_decay:.2%} | {self.thresholds['decay_max']} | {'�? if self.ic_decay <= self.thresholds['decay_max'] else '�?} |

## IC时序
![IC时序图] (已移�? ic_series.png)
"""
```


## 5. 因子存储

### 5.1 因子仓库

```python
class FactorRepository:
    """因子仓库

    索引: DATA.003-M05
    """

    def __init__(self):
        self.db = PostgresClient()
        self.cache = RedisClient()

    def save_factor(self, factor: Factor, validation_result: ValidationResult):
        """保存因子

        参数:
            factor: 因子
            validation_result: 验证结果
        """
        # 保存因子定义
        self.db.execute("""
            INSERT INTO factors (id, name, category, description, params, created_at)
            VALUES (%s, %s, %s, %s, %s, NOW())
            ON CONFLICT (id) DO UPDATE SET
                validation_result = %s,
                updated_at = NOW()
        """, [
            factor.id, factor.name, factor.category,
            factor.description, json.dumps(factor.params),
            json.dumps({
                'ic_mean': validation_result.ic_mean,
                'ic_ir': validation_result.ic_ir,
                'ic_decay': validation_result.ic_decay
            })
        ])

        # 缓存
        self.cache.set(f"factor:{factor.id}", factor.to_dict(), ttl=3600)

    def get_factor(self, factor_id: str) -> Factor:
        """获取因子"""
        # 优先从缓�?
        cached = self.cache.get(f"factor:{factor_id}")
        if cached:
            return Factor(**cached)

        # 从数据库加载
        row = self.db.query("SELECT * FROM factors WHERE id = %s", [factor_id])
        return Factor(**row)

    def list_factors(self, category: str = None) -> List[Factor]:
        """列出因子"""
        if category:
            rows = self.db.query(
                "SELECT * FROM factors WHERE category = %s",
                [category]
            )
        else:
            rows = self.db.query("SELECT * FROM factors")
        return [Factor(**row) for row in rows]
```


## 6. API接口

### 6.1 因子API

```python
# API: /api/v1/factors

class FactorAPI:
    """因子API

    索引: API_FACTOR_001
    """

    @router.post("/factors")
    def create_factor(
        name: str,
        category: str,
        description: str,
        calculator_type: str,
        params: dict
    ) -> Factor:
        """创建因子"""

    @router.get("/factors/{factor_id}")
    def get_factor(factor_id: str) -> Factor:
        """获取因子"""

    @router.get("/factors")
    def list_factors(category: str = None) -> List[Factor]:
        """列出因子"""

    @router.post("/factors/{factor_id}/validate")
    def validate_factor(factor_id: str) -> ValidationResult:
        """验证因子"""

    @router.get("/factors/{factor_id}/values")
    def get_factor_values(
        factor_id: str,
        start_date: str,
        end_date: str,
        symbols: List[str] = None
    ) -> pd.DataFrame:
        """获取因子�?""
```


## 7. 开发任务分�?

### 7.1 任务分解 (25h)

| 任务 | 时间 | 说明 |
|------|------|------|
| TA-Lib因子封装 | 4h | MA/RSI/MACD等封�?|
| 量价因子�?| 4h | Momentum/Volume�?|
| IC验证�?| 6h | IC计算和判�?|
| 因子仓库 | 4h | PostgreSQL存储 |
| 因子API | 3h | REST API |
| 测试 | 4h | 单元测试 |

---

## 变更记录

| 版本 | 日期 | 变更内容 | 变更人 |
|------|------|----------|--------|
| v1.0.0 | 2026-04-06 | 初始版本，补充职责描述和变更记录 | 首席文档架构师 |
