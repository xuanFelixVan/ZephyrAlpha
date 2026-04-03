---
module_id: FACTOR_README_001
version: 1.0.0
status: Active
created_date: 2026-04-01
last_updated: 2026-04-01
owner: 首席文档架构师
standard_type: 专业量化机构因子标准
applicable_scope: 因子研究与管理
compliance_level: 初始标准
parent_document: ../INDEX.md
implementation_status: 进行中
---

# 数据流水线蓝图

> Layer 0: 数据基础设施 - 多数据源适配、数据清洗、质量控制、每日流水线

---

## 1. 系统架构

```
数据流水线架构
├── 数据源层 (Data Sources)
│   ├── AkShare (免费行情)
│   ├── Tushare Pro (付费行情+财务)
│   ├── iFind (专业数据)
│   └── 东方财富 Choice (备用)
├── 适配器层 (Adapters)
│   ├── DataSourceAdapter (统一接口)
│   ├── RetryHandler (重试机制)
│   └── FallbackManager (降级策略)
├── 清洗层 (Cleaning)
│   ├── MissingValueHandler (缺失值)
│   ├── OutlierDetector (异常值)
│   └── Normalizer (标准化)
├── 质量控制层 (DQC)
│   ├── CompletenessChecker (完整性)
│   ├── ConsistencyChecker (一致性)
│   └── TimelinessChecker (时效性)
├── 存储层 (Storage)
│   ├── Redis (热数据: 实时行情)
│   ├── PostgreSQL (关系数据: 财务)
│   ├── ClickHouse (分析数据: 历史行情)
│   └── Parquet (归档数据: 因子)
└── 调度层 (Scheduler)
    ├── DailyPipeline (每日流水线)
    ├── IncrementalUpdate (增量更新)
    └── EmergencyRefresh (紧急刷新)
```

---

## 2. 多数据源适配器系统

### 2.1 统一接口定义

```python
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Optional, Any
from datetime import datetime, date
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class DataSourceType(Enum):
    AKSHARE = "akshare"
    TUSHARE = "tushare"
    IFIND = "ifind"
    CHOICE = "choice"


class DataQuality(Enum):
    EXCELLENT = "excellent"   # >99%
    GOOD = "good"            # 95-99%
    ACCEPTABLE = "acceptable" # 90-95%
    POOR = "poor"            # <90%


@dataclass
class DataRequest:
    symbol: str
    start_date: date
    end_date: date
    fields: List[str]
    source_priority: List[DataSourceType]
    timeout: int = 30
    retry_count: int = 3


@dataclass
class DataResponse:
    success: bool
    data: Any
    source: DataSourceType
    quality: DataQuality
    timestamp: datetime
    error: Optional[str] = None
    metadata: Dict = None

    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class DataSourceAdapter(ABC):
    """数据源适配器基类"""

    def __init__(self, source_type: DataSourceType):
        self.source_type = source_type
        self.logger = logging.getLogger(f"{__name__}.{source_type.value}")

    @abstractmethod
    def get_ohlcv(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        frequency: str = "1d"
    ) -> DataResponse:
        """获取OHLCV数据

        参数:
            symbol: 股票代码 (如: 000001.SZ)
            start_date: 开始日期
            end_date: 结束日期
            frequency: 频率 (1d, 1w, 1M, 1m, 5m, 15m, 30m, 60m)

        返回:
            DataResponse: 包含数据的响应对象
        """
        pass

    @abstractmethod
    def get_financial(
        self,
        symbol: str,
        start_date: date,
        end_date: date,
        report_type: str = "annual"
    ) -> DataResponse:
        """获取财务报表数据

        参数:
            symbol: 股票代码
            start_date: 开始日期
            end_date: 结束日期
            report_type: 报告类型 (annual, quarterly, ttm)

        返回:
            DataResponse: 包含财务数据的响应对象
        """
        pass

    @abstractmethod
    def get_company_info(self, symbol: str) -> DataResponse:
        """获取公司基本信息"""
        pass

    @abstractmethod
    def get_market_index(self, index_code: str) -> DataResponse:
        """获取指数数据"""
        pass

    def health_check(self) -> bool:
        """健康检查"""
        try:
            return self._ping()
        except Exception as e:
            self.logger.error(f"Health check failed: {e}")
            return False

    @abstractmethod
    def _ping(self) -> bool:
        """实际健康检查"""
        pass
```

### 2.2 多数据源管理器

```python
class MultiSourceManager:
    """多数据源管理器"""

    def __init__(self, config: Dict):
        self.adapters: Dict[DataSourceType, DataSourceAdapter] = {}
        self.fallback_order: List[DataSourceType] = []
        self.source_health: Dict[DataSourceType, bool] = {}
        self._initialize_adapters(config)

    def _initialize_adapters(self, config: Dict):
        """初始化所有适配器"""
        source_config = config.get("data_sources", {})

        if source_config.get("akshare", {}).get("enabled", True):
            self._register_adapter(AKShareAdapter())

        if source_config.get("tushare", {}).get("enabled", False):
            token = source_config["tushare"].get("token")
            self._register_adapter(TushareAdapter(token))

        if source_config.get("ifind", {}).get("enabled", False):
            path = source_config["ifind"].get("path")
            self._register_adapter(IFindAdapter(path))

        self.fallback_order = [ds for ds in self.adapters.keys()]

    def _register_adapter(self, adapter: DataSourceAdapter):
        """注册适配器"""
        self.adapters[adapter.source_type] = adapter
        self.source_health[adapter.source_type] = adapter.health_check()
        self.logger.info(f"Registered adapter: {adapter.source_type.value}")

    def get_data(
        self,
        request: DataRequest,
        force_source: DataSourceType = None
    ) -> DataResponse:
        """获取数据，自动选择最优数据源

        参数:
            request: 数据请求
            force_source: 强制使用的数据源

        返回:
            DataResponse: 数据响应
        """
        if force_source:
            adapter = self.adapters.get(force_source)
            if adapter:
                return self._fetch_with_adapter(adapter, request)

        for source_type in request.source_priority:
            adapter = self.adapters.get(source_type)
            if not adapter or not self.source_health.get(source_type, False):
                self.logger.warning(f"Source {source_type.value} unavailable, skipping")
                continue

            response = self._fetch_with_adapter(adapter, request)
            if response.success and response.quality in [DataQuality.EXCELLENT, DataQuality.GOOD]:
                return response

            self.logger.warning(
                f"Source {source_type.value} quality {response.quality.value}, "
                f"trying fallback"
            )

        return DataResponse(
            success=False,
            data=None,
            source=None,
            quality=DataQuality.POOR,
            timestamp=datetime.now(),
            error="All data sources failed"
        )

    def _fetch_with_adapter(
        self,
        adapter: DataSourceAdapter,
        request: DataRequest
    ) -> DataResponse:
        """使用适配器获取数据"""
        for attempt in range(request.retry_count):
            try:
                response = adapter.get_ohlcv(
                    request.symbol,
                    request.start_date,
                    request.end_date
                )
                if response.success:
                    return response
            except Exception as e:
                self.logger.error(
                    f"Attempt {attempt + 1} failed for {adapter.source_type.value}: {e}"
                )

        return DataResponse(
            success=False,
            data=None,
            source=adapter.source_type,
            quality=DataQuality.POOR,
            timestamp=datetime.now(),
            error=f"Failed after {request.retry_count} attempts"
        )

    def refresh_health_status(self):
        """刷新数据源健康状态"""
        for source_type, adapter in self.adapters.items():
            self.source_health[source_type] = adapter.health_check()
            self.logger.info(f"Health status {source_type.value}: {self.source_health[source_type]}")
```

---

## 3. 数据清洗引擎

### 3.1 清洗处理器

```python
from typing import Callable, Dict, List, Any
import pandas as pd
import numpy as np


class DataCleaner:
    """数据清洗引擎"""

    def __init__(self):
        self.handlers: Dict[str, Callable] = {}
        self._register_default_handlers()

    def _register_default_handlers(self):
        """注册默认处理器"""
        self.handlers["missing_values"] = self._handle_missing_values
        self.handlers["outliers"] = self._handle_outliers
        self.handlers["duplicates"] = self._handle_duplicates
        self.handlers["normalization"] = self._normalize
        self.handlers["alignment"] = self._align_data

    def clean(
        self,
        df: pd.DataFrame,
        cleaning_rules: Dict[str, Any]
    ) -> pd.DataFrame:
        """执行数据清洗

        参数:
            df: 原始数据
            cleaning_rules: 清洗规则配置

        返回:
            清洗后的数据
        """
        result = df.copy()

        for step, params in cleaning_rules.items():
            if step in self.handlers:
                result = self.handlers
                self.logger.debug(f"Applied cleaning step: {step}")

        return result

    def _handle_missing_values(
        self,
        df: pd.DataFrame,
        method: str = "forward_fill",
        columns: List[str] = None
    ) -> pd.DataFrame:
        """处理缺失值

        参数:
            method: 处理方法
                - 'forward_fill': 前向填充
                - 'backward_fill': 后向填充
                - 'interpolate': 插值
                - 'mean': 均值填充
                - 'median': 中位数填充
                - 'drop': 删除
            columns: 需要处理的列，None表示所有列
        """
        result = df.copy()
        cols = columns or result.columns.tolist()

        for col in cols:
            if col not in result.columns:
                continue

            if result[col].isna().sum() == 0:
                continue

            if method == "forward_fill":
                result[col] = result[col].ffill()
            elif method == "backward_fill":
                result[col] = result[col].bfill()
            elif method == "interpolate":
                result[col] = result[col].interpolate(method="linear")
            elif method == "mean":
                result[col] = result[col].fillna(result[col].mean())
            elif method == "median":
                result[col] = result[col].fillna(result[col].median())
            elif method == "drop":
                result = result.dropna(subset=[col])

        return result

    def _handle_outliers(
        self,
        df: pd.DataFrame,
        method: str = "mad",
        threshold: float = 3.0,
        columns: List[str] = None
    ) -> pd.DataFrame:
        """处理异常值

        参数:
            method: 检测方法
                - 'mad': MAD法 (中位数绝对偏差)
                - 'zscore': Z-score法
                - 'iqr': 四分位距法
            threshold: 阈值
            columns: 需要处理的列
        """
        result = df.copy()
        cols = columns or [c for c in result.columns if c not in ['date', 'symbol', 'code']]

        for col in cols:
            if col not in result.columns or not pd.api.types.is_numeric_dtype(result[col]):
                continue

            if method == "mad":
                median = result[col].median()
                mad = (result[col] - median).abs().median()
                if mad == 0:
                    continue
                result[col] = result[col].clip(
                    lower=median - threshold * mad,
                    upper=median + threshold * mad
                )
            elif method == "zscore":
                z_scores = np.abs((result[col] - result[col].mean()) / result[col].std())
                result.loc[z_scores > threshold, col] = np.nan
                result[col] = result[col].ffill()
            elif method == "iqr":
                q1 = result[col].quantile(0.25)
                q3 = result[col].quantile(0.75)
                iqr = q3 - q1
                lower = q1 - threshold * iqr
                upper = q3 + threshold * iqr
                result[col] = result[col].clip(lower=lower, upper=upper)

        return result

    def _handle_duplicates(
        self,
        df: pd.DataFrame,
        subset: List[str] = None,
        keep: str = "first"
    ) -> pd.DataFrame:
        """处理重复数据"""
        return df.drop_duplicates(subset=subset, keep=keep)

    def _normalize(
        self,
        df: pd.DataFrame,
        method: str = "zscore",
        columns: List[str] = None
    ) -> pd.DataFrame:
        """标准化数据

        参数:
            method: 标准化方法
                - 'zscore': Z-score标准化
                - 'minmax': Min-Max归一化
                - 'rank': 排序归一化
        """
        result = df.copy()
        cols = columns or result.select_dtypes(include=[np.number]).columns.tolist()

        for col in cols:
            if col not in result.columns:
                continue

            if method == "zscore":
                mean = result[col].mean()
                std = result[col].std()
                if std > 0:
                    result[col] = (result[col] - mean) / std
            elif method == "minmax":
                min_val = result[col].min()
                max_val = result[col].max()
                if max_val > min_val:
                    result[col] = (result[col] - min_val) / (max_val - min_val)
            elif method == "rank":
                result[col] = result[col].rank(pct=True)

        return result

    def _align_data(
        self,
        df: pd.DataFrame,
        reference_df: pd.DataFrame = None,
        date_col: str = "date"
    ) -> pd.DataFrame:
        """对齐数据"""
        result = df.copy()

        if date_col in result.columns:
            result = result.sort_values(date_col)
            result = result.set_index(date_col)

            if reference_df is not None and date_col in reference_df.columns:
                reference = reference_df.set_index(date_col)
                result = result.reindex(reference.index)

            result = result.reset_index()

        return result
```

---

## 4. 数据质量控制 (DQC)

### 4.1 质量检查器

```python
@dataclass
class QualityCheckResult:
    """质量检查结果"""
    check_name: str
    passed: bool
    score: float  # 0-100
    details: Dict[str, Any]
    suggestions: List[str] = field(default_factory=list)


class DataQualityChecker:
    """数据质量检查器"""

    def __init__(self):
        self.checks: List[Callable] = []

    def check(
        self,
        df: pd.DataFrame,
        data_type: str,
        symbol: str = None
    ) -> List[QualityCheckResult]:
        """执行所有质量检查

        参数:
            df: 待检查数据
            data_type: 数据类型 (ohlcv, financial, index)
            symbol: 股票代码

        返回:
            检查结果列表
        """
        results = []

        results.append(self._check_completeness(df, symbol))
        results.append(self._check_consistency(df, symbol))
        results.append(self._check_timeliness(df, symbol))
        results.append(self._check_accuracy(df, data_type))
        results.append(self._check_uniqueness(df, symbol))

        return results

    def _check_completeness(
        self,
        df: pd.DataFrame,
        symbol: str = None
    ) -> QualityCheckResult:
        """完整性检查"""
        total_cells = df.size
        missing_cells = df.isna().sum().sum()
        completeness_rate = (1 - missing_cells / total_cells) * 100 if total_cells > 0 else 0

        missing_by_column = df.isna().sum()
        columns_with_missing = missing_by_column[missing_by_column > 0]

        suggestions = []
        if completeness_rate < 95:
            suggestions.append(f"数据完整性 {completeness_rate:.1f}% 低于95%，建议检查数据源")

        return QualityCheckResult(
            check_name="completeness",
            passed=completeness_rate >= 95,
            score=completeness_rate,
            details={
                "total_cells": total_cells,
                "missing_cells": missing_cells,
                "completeness_rate": completeness_rate,
                "columns_with_missing": columns_with_missing.to_dict() if len(columns_with_missing) > 0 else {}
            },
            suggestions=suggestions
        )

    def _check_consistency(
        self,
        df: pd.DataFrame,
        symbol: str = None
    ) -> QualityCheckResult:
        """一致性检查"""
        issues = []

        if "close" in df.columns and "open" in df.columns:
            invalid_ranges = ((df["close"] < 0) | (df["open"] < 0) |
                            (df["high"] < df["low"])).sum()
            if invalid_ranges > 0:
                issues.append(f"发现 {invalid_ranges} 条价格范围异常记录")

        if "volume" in df.columns:
            negative_volume = (df["volume"] < 0).sum()
            if negative_volume > 0:
                issues.append(f"发现 {negative_volume} 条负成交量记录")

        consistency_rate = max(0, 100 - len(issues) * 10)

        return QualityCheckResult(
            check_name="consistency",
            passed=len(issues) == 0,
            score=consistency_rate,
            details={"issues": issues},
            suggestions=[f"检查并修复: {issue}" for issue in issues] if issues else []
        )

    def _check_timeliness(
        self,
        df: pd.DataFrame,
        symbol: str = None
    ) -> QualityCheckResult:
        """时效性检查"""
        if "date" not in df.columns and "timestamp" not in df.columns:
            return QualityCheckResult(
                check_name="timeliness",
                passed=False,
                score=0,
                details={"error": "无日期列"},
                suggestions=["添加日期列以便进行时效性检查"]
            )

        date_col = "date" if "date" in df.columns else "timestamp"
        latest_date = pd.to_datetime(df[date_col]).max()
        now = pd.Timestamp.now()

        days_lag = (now - latest_date).days
        is_fresh = days_lag <= 1

        return QualityCheckResult(
            check_name="timeliness",
            passed=is_fresh,
            score=100 if is_fresh else max(0, 100 - days_lag * 10),
            details={
                "latest_date": str(latest_date),
                "days_lag": days_lag,
                "is_fresh": is_fresh
            },
            suggestions=[f"数据滞后 {days_lag} 天，建议更新"] if not is_fresh else []
        )

    def _check_accuracy(
        self,
        df: pd.DataFrame,
        data_type: str
    ) -> QualityCheckResult:
        """准确性检查"""
        accuracy_checks = []

        if data_type == "ohlcv":
            if all(col in df.columns for col in ["open", "high", "low", "close"]):
                price_consistency = (
                    (df["high"] >= df["low"]) &
                    (df["high"] >= df["open"]) &
                    (df["high"] >= df["close"]) &
                    (df["low"] <= df["open"]) &
                    (df["low"] <= df["close"])
                ).mean() * 100
                accuracy_checks.append(("价格逻辑一致性", price_consistency))

        score = np.mean([check[1] for check in accuracy_checks]) if accuracy_checks else 100

        return QualityCheckResult(
            check_name="accuracy",
            passed=score >= 95,
            score=score,
            details={"checks": dict(accuracy_checks)},
            suggestions=[]
        )

    def _check_uniqueness(
        self,
        df: pd.DataFrame,
        symbol: str = None
    ) -> QualityCheckResult:
        """唯一性检查"""
        if "date" in df.columns:
            total_rows = len(df)
            unique_dates = df["date"].nunique()
            duplicate_rate = (1 - unique_dates / total_rows) * 100 if total_rows > 0 else 0

            return QualityCheckResult(
                check_name="uniqueness",
                passed=duplicate_rate < 5,
                score=max(0, 100 - duplicate_rate),
                details={
                    "total_rows": total_rows,
                    "unique_dates": unique_dates,
                    "duplicate_rate": duplicate_rate
                },
                suggestions=[f"发现 {total_rows - unique_dates} 条重复日期记录"] if duplicate_rate > 0 else []
            )

        return QualityCheckResult(
            check_name="uniqueness",
            passed=True,
            score=100,
            details={},
            suggestions=[]
        )

    def generate_report(
        self,
        results: List[QualityCheckResult]
    ) -> str:
        """生成质量报告"""
        report_lines = ["=" * 60, "数据质量检查报告", "=" * 60, ""]

        for result in results:
            status = "✅ 通过" if result.passed else "❌ 未通过"
            report_lines.append(f"【{result.check_name}】{status}")
            report_lines.append(f"  评分: {result.score:.1f}/100")

            if result.details:
                report_lines.append(f"  详情: {result.details}")

            if result.suggestions:
                report_lines.append(f"  建议:")
                for suggestion in result.suggestions:
                    report_lines.append(f"    - {suggestion}")

            report_lines.append("")

        overall_score = np.mean([r.score for r in results])
        report_lines.append("=" * 60)
        report_lines.append(f"综合评分: {overall_score:.1f}/100")
        report_lines.append("=" * 60)

        return "\n".join(report_lines)
```

---

## 5. 每日数据流水线

### 5.1 流水线调度器

```python
from datetime import datetime, time
from typing import Dict, List, Optional
import schedule
import threading
import time as time_module


class DailyPipelineScheduler:
    """每日数据流水线调度器"""

    def __init__(self, config: Dict):
        self.config = config
        self.tasks: List[Dict] = []
        self.running = False
        self.thread: Optional[threading.Thread] = None

        self._register_default_tasks()

    def _register_default_tasks(self):
        """注册默认任务"""

        self.tasks = [
            {
                "name": "pre_market_data_update",
                "time": time(8, 30),
                "enabled": True,
                "description": "盘前数据更新"
            },
            {
                "name": "intraday_data_update",
                "time": time(11, 30),
                "enabled": True,
                "description": "盘中数据更新"
            },
            {
                "name": "post_market_data_update",
                "time": time(16, 0),
                "enabled": True,
                "description": "盘后数据更新"
            },
            {
                "name": "daily_backup",
                "time": time(18, 0),
                "enabled": True,
                "description": "每日备份"
            }
        ]

    def add_task(
        self,
        name: str,
        task_time: time,
        handler: callable,
        enabled: bool = True
    ):
        """添加自定义任务"""
        self.tasks.append({
            "name": name,
            "time": task_time,
            "handler": handler,
            "enabled": enabled
        })

    def start(self):
        """启动调度器"""
        if self.running:
            self.logger.warning("Scheduler already running")
            return

        self.running = True
        self.thread = threading.Thread(target=self._run_scheduler, daemon=True)
        self.thread.start()
        self.logger.info("Pipeline scheduler started")

    def stop(self):
        """停止调度器"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
        self.logger.info("Pipeline scheduler stopped")

    def _run_scheduler(self):
        """运行调度循环"""
        while self.running:
            now = datetime.now()
            for task in self.tasks:
                if not task.get("enabled", True):
                    continue

                task_time = task.get("time")
                if now.time().hour == task_time.hour and now.time().minute == task_time.minute:
                    self.logger.info(f"Executing task: {task['name']}")
                    try:
                        task["handler"]()
                    except Exception as e:
                        self.logger.error(f"Task {task['name']} failed: {e}")

            time_module.sleep(60)

    def get_status(self) -> Dict:
        """获取调度器状态"""
        return {
            "running": self.running,
            "tasks": [
                {
                    "name": t["name"],
                    "time": str(t["time"]),
                    "enabled": t.get("enabled", True)
                }
                for t in self.tasks
            ]
        }


class PipelineTask:
    """流水线任务基类"""

    def __init__(self, name: str):
        self.name = name
        self.logger = logging.getLogger(f"{__name__}.{name}")

    def execute(self, context: Dict):
        """执行任务"""
        raise NotImplementedError

    def rollback(self, context: Dict):
        """回滚任务"""
        pass
```

### 5.2 增量更新策略

```python
class IncrementalUpdateStrategy:
    """增量更新策略"""

    def __init__(self):
        self.last_update: Dict[str, datetime] = {}

    def get_update_window(
        self,
        symbol: str,
        data_type: str
    ) -> tuple:
        """获取更新窗口

        返回:
            (start_date, end_date): 更新日期范围
        """
        last_update = self.last_update.get(f"{symbol}:{data_type}")

        if last_update is None:
            return (None, datetime.now().date())

        return (last_update.date(), datetime.now().date())

    def mark_updated(self, symbol: str, data_type: str, update_time: datetime):
        """标记更新时间"""
        key = f"{symbol}:{data_type}"
        self.last_update[key] = update_time

    def should_full_refresh(self, symbol: str, data_type: str) -> bool:
        """判断是否需要全量刷新"""
        key = f"{symbol}:{data_type}"
        last_update = self.last_update.get(key)

        if last_update is None:
            return True

        days_since_update = (datetime.now() - last_update).days

        return days_since_update > 30
```

---

## 6. 数据库选型策略

### 6.1 分层存储架构

```
存储分层设计
├── 热数据层 (Hot) - Redis
│   ├── 数据: 实时行情(Tick)、当前持仓、资金
│   ├── 访问频率: 每秒数百次
│   ├── 保留期: 当日
│   └── 容量: ~1GB
│
├── 温数据层 (Warm) - PostgreSQL
│   ├── 数据: 财务报表、元数据、用户配置
│   ├── 访问频率: 每分钟数次
│   ├── 保留期: 永久
│   └── 容量: ~10GB
│
├── 冷数据层 (Cold) - ClickHouse
│   ├── 数据: 历史行情(分钟线、日线)、因子值
│   ├── 访问频率: 每日数次
│   ├── 保留期: 永久
│   └── 容量: ~100GB
│
└── 归档层 (Archive) - Parquet + 分区
    ├── 数据: 超过1年的历史数据
    ├── 访问频率: 偶尔
    ├── 保留期: 永久
    └── 容量: ~500GB
```

### 6.2 数据源配置示例

```yaml
# config/data_sources.yaml

data_sources:
  akshare:
    enabled: true
    priority: 1
    rate_limit: 10  # 每秒请求数
    retry_count: 3
    
  tushare:
    enabled: false
    priority: 2
    token: "${TUSHARE_TOKEN}"
    rate_limit: 5
    
  ifind:
    enabled: false
    priority: 3
    path: "C:/IFind/data"
    
storage:
  hot:
    type: redis
    host: localhost
    port: 6379
    db: 0
    ttl: 86400  # 1天
    
  warm:
    type: postgresql
    host: localhost
    port: 5432
    database: quant_system
    pool_size: 10
    
  cold:
    type: clickhouse
    host: localhost
    port: 9000
    database: quant_analytics
    
pipeline:
  schedule:
    pre_market: "08:30"
    intraday: "11:30"
    post_market: "16:00"
    backup: "18:00"
    
  quality:
    completeness_threshold: 95
    consistency_threshold: 95
```

---

## 7. 预期性能指标

| 指标 | 目标 | 说明 |
|------|------|------|
| 实时数据更新延迟 | < 100ms | 从数据源到Redis |
| 历史数据查询延迟 | < 1s | ClickHouse查询 |
| 每日流水线执行时间 | < 30min | 包含所有股票 |
| 数据质量评分 | > 95分 | 综合质量检查 |
| 系统可用性 | > 99.9% | 全年365天 |
| 故障恢复时间 | < 5min | MTTR目标 |

---

## 8. 上游下游接口

### 上游接口
- **数据源**: AkShare API, Tushare API, iFind API

### 下游接口
- **DataHub (M01)**: 提供统一数据访问接口
- **FactorCalculator (M02)**: 提供计算所需数据
- **BacktestEngine (M15)**: 提供历史回测数据

### 内部接口
- **EventBus (M12)**: 发布数据更新事件
- **AlertManager (M14)**: 发送数据异常告警
- **ConfigManager (M09)**: 获取配置参数

---

**版本**: 1.0
**更新**: 2026-03-28
**Layer**: Layer 0 (数据源)
**索引**: BLUEPRINTS.md → 数据流水线蓝图
