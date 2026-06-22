---
module_id: MOD-L00-001
submodule_path: src/zephyr/data
title: "Data Source Core 蓝图+施工图 — 数据接入层·C轨占位"
doc_type: blueprint
status: Active
version: "3.0.0"
layer: L00
layer_name: data_source
functional_domain: data
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: human_plus_agent
valid_from: "2026-05-05"
date: "2026-05-05"
ttl: permanent
construction_progress: partially_implemented
actual_disk_path: "src/zephyr/data/"
belongs_to: "MOD-MASTER-001"
parent_module: ""
codification_level: L1
codification_at: "2026-05-15"
last_verified: "2026-05-15"
last_updated: "2026-05-15"
generation: 3
rule_form: structural
scope: module
stability: evolving
verifiability: hybrid
references:
  - path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture_model\\layers\\l00_data_source.yaml"
    section: ""
    why: "架构层YAML真源"
depends_on:
  - target: MOD-INF-007
    at: "§10"
    why: "数据质量门控联动"
  - target: MOD-INF-012
    at: "§10"
    why: "数据缓存"
  - target: MOD-INF-015
    at: "§10"
    why: "数据摄取监控"
  - target: MOD-INF-035
    at: "§10"
    why: "数据接入注册"
priority: P0
runtime_plane: hot
tags:
  - data-source
  - l00
  - c-track
  - blocked-by-infrastructure
summary: "数据接入层——外部数据源适配接入：行情、基本面、另类数据摄取与标准化。C轨占位——禁止施工。"
---

> ⛔ **C轨占位——业务层未开放，禁止施工**
> 本蓝图属于 C轨（业务层）占位蓝图。当前仅完成骨架代码，不进行主动施工。
> 待 A轨（基础设施层）稳定后按 ARB-11 三梯队优先级启动。
> 任何 AI agent 不得以此蓝图为依据生成新的数据接入业务代码。

> actual_disk_path: src/zephyr/data/ (6 .py files + 2 test files)

# Data Source Core 蓝图+施工图 — 数据接入层·C轨占位

> module_id: MOD-L00-001 | version: 3.0.0 | status: active | domain: data
> actual_disk_path: src/zephyr/data/ | generation: 3 | construction_progress: partially_implemented

## 概述

本蓝图描述 ZephyrAlpha 数据接入层——它解决了外部数据源（行情、基本面、另类数据）格式各异、API限流、数据质量参差不齐的标准化接入问题。核心职责包括：数据源OCP扩展点(DataSourceBase)、数据质量门禁(DataQualityGate)、标准化输出(CTR-001 NormalizedMarketData)。当前规模 1 个数据源(AkShare)，目标容量 5 个数据源。上游依赖 AkShare 等外部 API，下游被 L02/L03/L09 层消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[system-dependency-map.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/system-dependency-map.md)
> - 优化规则：先 Layer 1（蓝图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：`data/databases/depgraph.db`
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[INVARIANTS]/[MODIFY-GUARD]/[CONSUMERS]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-L00-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 |
|---|--------|------------|------|:---:|
| 1 | provider_base.py | §3.1 | DataSourceBase OCP扩展点 + DataSourceMeta | 已实现 |
| 2 | quality_gate.py | §3.1 | DataQualityGate抽象 + QualityReport + QualityFailureReason + RecoveryHint | 已实现 |
| 3 | implementations/akshare_provider.py | §3.1 | AkShare数据源实现 | 已实现 |
| 4 | implementations/default_quality_gate.py | §3.1 | 默认质量校验实现(5项规则) | 已实现 |
| 5 | implementations/memory_provider.py | §3.1 | 内存合成数据源(测试/离线) | 已实现 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | `ls src/zephyr/data/` 逐文件核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| actual_disk_path = §11 产出物路径 | 路径比对 | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.1.0 (占位) | 无代码 | 全部 | blocked_by_infrastructure |
| v2.1.0 (模板升级) | DataSourceBase + DataQualityGate + 3个实现 | connectors/normalizers/storage/cache子模块 | C轨占位 |
| v3.0.0 (回填+对齐) | 同 v2.1.0 | 同 v2.1.0 | C轨占位 |

---

## §1 设计背景与目标

### 1.1 背景

ZephyrAlpha 需要接入多种外部数据源（AkShare/Tushare/Wind等），各数据源API格式各异、限流策略不同、数据质量参差不齐。需要统一的数据接入层将原始数据标准化为 CTR-001 NormalizedMarketData，供下游 L02/L03/L09 消费。

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | 外部数据源标准化接入 | DataSourceBase OCP扩展点可用 |
| 2 | ✅ 包含 | 行情/基本面/另类数据摄取 | AkShareProvider实现完整 |
| 3 | ✅ 包含 | 数据质量门禁 | DataQualityGate可配置校验规则 |
| 4 | ❌ 排除 | 数据存储引擎 | L01 INF-012 Database |
| 5 | ❌ 排除 | 数据清洗/特征工程 | L02 Alpha Factor |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| AkShare API 限流（每分钟60次） | 请求必须限速 + 缓存 |
| 数据源格式可能变更 | Schema版本化 + Drift Detector |
| 网络不可用时需降级 | MemoryProvider提供本地回退 |
| Akshare为同步HTTP客户端 | 需asyncio.to_thread包装避免阻塞事件循环 |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策 | 设计+施工 | 审批权限 |
| L02 Alpha Factor | CTR-001数据格式 | 消费 | 接口兼容性 |
| L03 Signal Generation | CTR-001数据格式 | 消费 | 接口兼容性 |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 数据源数量 | 1 (AkShare) | 5 | 缺4个数据源 | P1 |
| 子模块完整性 | 2/5 (provider+quality) | 5/5 | 缺connectors/normalizers/storage/cache | P0 |
| SLO/可观测性 | 无 | 完整 | 全缺 | P1 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 日线数据摄取 | L02请求行情 | AkshareProvider.fetch_historical → _normalize_columns → DataFrame | OHLCV DataFrame |
| 数据质量校验 | 数据接入后 | DefaultQualityGate.check → QualityReport | QualityReport(passed=True/False) |
| 离线测试 | 测试环境 | MemoryProvider.fetch_historical → 合成数据 | OHLCV DataFrame |
| API限流 | AkShare返回429 | 限速重试 + MemoryProvider降级 | 延迟数据或合成数据 |

---

## §2 模块边界

### 2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 数据源适配 | DataSourceBase抽象 + AkShareProvider/MemoryProvider实现 | 本模块 |
| 2 | ✅ 包含 | 数据质量校验 | DataQualityGate + DefaultQualityGate(5项规则) | 本模块 |
| 3 | ✅ 包含 | 标准化输出 | CTR-001 NormalizedMarketData (OHLCV DataFrame) | 本模块 |
| 4 | ❌ 排除 | 数据持久化 | INF-012 Database负责 | INF-012 |
| 5 | ❌ 排除 | 因子计算 | L02 Alpha Factor负责 | L02 |
| 6 | ❌ 排除 | 信号生成 | L03 Signal Generation负责 | L03 |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | DataSourceBase | 数据源OCP扩展点(ABC) | — | 同步调用 |
| 2 | DataSourceMeta | 数据源元数据(frozen dataclass) | — | 数据类 |
| 3 | DataQualityGate | 数据质量校验(ABC) | DataSourceBase | 同步调用 |
| 4 | QualityReport | 质量校验报告(frozen dataclass) | — | 数据类 |
| 5 | QualityFailureReason | 失败原因枚举 | — | 枚举 |
| 6 | RecoveryHint | 恢复建议枚举 | — | 枚举 |
| 7 | AkShareProvider | AkShare数据源实现 | DataSourceBase | 继承 |
| 8 | DefaultQualityGate | 默认校验规则(5项) | DataQualityGate | 继承 |
| 9 | MemoryProvider | 内存合成数据源 | DataSourceBase | 继承 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | AkShare API | fetch_historical → _normalize_columns → validate_schema | L02/L03/L09 | pd.DataFrame (OHLCV) |
| 2 | MemoryProvider | 合成数据生成 → validate_schema | 测试/L02 | pd.DataFrame (OHLCV) |
| 3 | 任意Provider | fetch → DataQualityGate.check | L02 | QualityReport |

### 3.3 状态生命周期

本模块无状态机。DataSourceBase通过`__init_subclass__`实现自动注册，DataQualityGate同理。

---

## §4 接口契约

> ⚠️ 代码实际使用 `pd.DataFrame` 而非 Pydantic BaseModel。这是 C轨占位阶段的实现选择，待正式施工时按 KBG-0040 迁移为 Pydantic V2。

### 4.1 公共 API

```python
class DataSourceBase(abc.ABC):
    _registry: ClassVar[dict[str, type["DataSourceBase"]]]
    def __init_subclass__(cls, **kwargs): ...
    @abc.abstractmethod
    def fetch_historical(self, symbol: str, start: datetime, end: datetime, interval: str = "1d") -> pd.DataFrame: ...
    @abc.abstractmethod
    def subscribe_realtime(self, symbols: list[str]) -> None: ...
    def validate_schema(self, df: pd.DataFrame) -> bool: ...
    @property
    def is_local(self) -> bool: ...

class DataQualityGate(abc.ABC):
    QUALITY_THRESHOLD: ClassVar[float] = 0.7
    _registry: ClassVar[dict[str, type["DataQualityGate"]]]
    @abc.abstractmethod
    def check(self, symbol: str, open_price: Decimal, high: Decimal, low: Decimal, close: Decimal, volume: Decimal, timestamp: datetime, prev_close: Optional[Decimal] = None) -> QualityReport: ...
    @staticmethod
    def is_within_normal_range(price: Decimal, prev_close: Decimal, limit_pct: Decimal = Decimal("0.10")) -> bool: ...
```

### 4.2 数据模型

```python
@dataclass(frozen=True)
class DataSourceMeta:
    provider_id: str
    provider_name: str
    asset_classes: list[str]
    markets: list[str]
    supports_realtime: bool = False
    supports_historical: bool = True
    supports_local: bool = False
    rate_limit_per_min: int = 60

class QualityFailureReason(str, Enum):
    MISSING_TICK = "missing_tick"
    STALE_DATA = "stale_data"
    OUTLIER_PRICE = "outlier_price"
    TIMESTAMP_FUTURE = "timestamp_future"
    SUSPENSION_DETECTED = "suspension_detected"
    VOLUME_ZERO = "volume_zero"

class RecoveryHint(str, Enum):
    RETRY = "RETRY"
    SKIP_SYMBOL = "SKIP_SYMBOL"
    SWITCH_SOURCE = "SWITCH_SOURCE"
    HALT = "HALT"

@dataclass(frozen=True)
class QualityReport:
    symbol: str
    quality_score: float  # 0.0~1.0, <0.7 不合格
    passed: bool
    failure_reason: Optional[QualityFailureReason] = None
    failed_field: Optional[str] = None
    failed_value: Optional[str] = None
    recovery_hint: RecoveryHint = RecoveryHint.SKIP_SYMBOL
    checked_at: datetime = field(default_factory=datetime.utcnow)
```

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `fetch_historical()` | `symbol` | ✅ | 合法证券代码(6位数字) |
| `fetch_historical()` | `start` / `end` | ✅ | start ≤ end |
| `fetch_historical()` | `interval` | ❌ | "1d"/"1m"/"5m"/"15m"/"30m"/"60m"，默认"1d" |
| `check()` | `symbol` | ✅ | 合法证券代码 |
| `check()` | `open_price/high/low/close/volume` | ✅ | Decimal, >0 |
| `check()` | `timestamp` | ✅ | datetime |
| `check()` | `prev_close` | ❌ | Decimal, 用于涨跌停检测 |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `fetch_historical()` | `pd.DataFrame` (OHLCV列) | 空 DataFrame / `ImportError`(akshare未安装) |
| `validate_schema()` | `bool` | — |
| `check()` | `QualityReport` | — |
| `subscribe_realtime()` | `None` | AkShare不支持实时推送(仅warning) |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增DataSourceBase子类 | ✅ 向后兼容 | OCP扩展 |
| DataFrame列新增 | ✅ 向后兼容 | 不影响已有消费者 |
| DataFrame列删除 | ❌ 破坏性 | 需Owner审批+迁移方案 |
| QualityFailureReason新增枚举值 | ✅ 向后兼容 | 不破坏已有逻辑 |
| QUALITY_THRESHOLD变更 | ❌ 破坏性 | 0.7为硬编码最低线 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | DataSourceBase为OCP扩展点 | 新数据源只加不改 |
| 2 | 数据输出必须标准化 | OHLCV DataFrame (CTR-001) |
| 3 | QUALITY_THRESHOLD = 0.7 | 硬编码最低线，禁止降级 |
| 4 | 禁止静默丢弃数据 | 不合格必须显式返回QualityReport(passed=False) |
| 5 | Akshare为同步HTTP客户端 | 需asyncio.to_thread包装 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 数据源数量 | 1 (AkShare) | 5 | 无上限 | ✅ | OCP扩展 |
| 日行情记录 | ~5000 | ~50000 | 无上限 | ✅ | 分批摄取 |
| API限流 | 60次/分钟 | 100次/分钟 | AkShare限制 | ❌ | 限速+缓存 |

### 5.3 迁移/废弃方案

本蓝图不涉及迁移。

### 5.4 非功能需求与服务水平

| 维度 | NFR指标 | NFR目标 | 测量方式 | SLI | SLO | Error Budget | 告警阈值 |
|------|--------|--------|---------|-----|-----|-------------|---------|
| 可用性 | 数据摄取成功率 | >99% | 日志统计 | fetch成功/总请求 | 99% | 每月允许1%失败 | <95%告警 |
| 延迟 | 单次fetch延迟(P95) | <5s | 计时统计 | fetch耗时P95 | <5s | — | >10s告警 |
| 数据质量 | QualityReport通过率 | >95% | 质检统计 | passed=True/总数 | >95% | 每月允许5%不通过 | <90%告警 |

### 5.7 禁止模式与导入约束

| # | 类型 | 禁止项 | 替代/允许项 | 原因 |
|---|:----:|--------|-----------|------|
| 1 | 编码模式 | 静默丢弃不合格数据 | 返回QualityReport(passed=False) | 下游必须知道数据质量 |
| 2 | 编码模式 | 降级QUALITY_THRESHOLD | 保持0.7硬编码最低线 | 质量底线不可妥协 |
| 3 | 编码模式 | 直接修改DataSourceBase抽象接口 | 继承+实现新子类 | OCP原则 |
| 4 | 导入源 | zephyr.signal.* / zephyr.factor.* | 仅允许被下游导入 | 分层约束：data 不依赖 signal+ |

---

## §6 错误处理

| # | 异常场景 | 检测方式 | 恢复策略 | 影响范围 |
|---|---------|---------|---------|---------|
| 1 | AkShare API限流 | HTTP 429/超时 | 限速重试+缓存 | 数据延迟 |
| 2 | 数据源格式变更 | Schema校验失败(validate_schema) | Drift Detector告警+人工修复 | 解析失败 |
| 3 | 网络不可用 | 连接超时 | MemoryProvider降级 | 无实时数据 |
| 4 | AkShare未安装 | ImportError | 返回空DataFrame+日志 | 无数据 |
| 5 | 质量门禁不通过 | QualityReport.passed=False | 返回报告+RETRY/SKIP/SWITCH | 下游收到不合格标记 |

### 6.1 可观测性规格

| 指标名 | 类型 | 采集方式 | 告警阈值 | 告警级别 |
|--------|------|---------|---------|---------|
| data_fetch_total | Counter | 自动埋点 | — | — |
| data_fetch_error_total | Counter | 自动埋点 | >5%错误率 | P2 |
| data_quality_pass_rate | Gauge | 质检统计 | <90% | P1 |
| data_fetch_latency_seconds | Histogram | 计时 | P95>10s | P2 |

### 6.2 退化矩阵

| 组件 | 失败后可用功能 | 不可用功能 | 降级策略 | 恢复条件 |
|------|-------------|-----------|---------|---------|
| AkShareProvider | MemoryProvider合成数据 | 真实行情数据 | 自动切换MemoryProvider | AkShare API恢复 |
| DefaultQualityGate | 无降级 | 质量校验 | 所有数据标记passed=True(需Owner审批) | 质量门禁修复 |

---

## §8 安全考量

| # | 威胁 | 影响 | 缓解措施 | 验证方式 |
|---|------|------|---------|---------|
| 1 | API密钥泄露 | 中 | 环境变量存储，禁止硬编码 | 扫描脚本检测 |
| 2 | 数据源注入 | 低 | symbol参数校验(6位数字) | 单元测试 |
| 3 | 时间戳伪造 | 中 | TIMESTAMP_FUTURE检测 | DefaultQualityGate校验 |

---

## §9 测试策略

| # | 测试类型 | 覆盖范围 | 关键测试用例 | 通过标准 |
|---|---------|---------|------------|---------|
| 1 | 单元测试 | DataSourceBase | 注册机制+validate_schema | tests/unit/data/test_provider_base_contract.py |
| 2 | 单元测试 | DataQualityGate | QualityReport+QualityFailureReason+is_within_normal_range+QUALITY_THRESHOLD | tests/unit/data/test_quality_gate.py |
| 3 | 集成测试 | AkShareProvider | fetch_historical返回OHLCV | 待补充(需网络) |
| 4 | 集成测试 | MemoryProvider | 合成数据质量 | 待补充 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-INF-007 Gatekeeper | 可选 | 数据质量门控联动 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate-engine\blueprint.md` |
| MOD-INF-012 Database | 可选 | 数据缓存 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\blueprint.md` |
| MOD-INF-015 Telemetry | 必须 | 数据摄取监控 | — | `D:\ZephyrAlpha\docs\03_modules\_domain-infra_ops\system-telemetry\blueprint.md` |
| MOD-INF-035 AutoRuntime | 可选 | 数据接入注册 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ system-dependency-map.md §3.8 | 蓝图声明的每个依赖在依赖图中有对应条目 | 已对齐 | 人工核对 |
| 2 | §11 产出物路径 ↔ 依赖图 §5 MOD-L00-001 | 路径一致 | 已对齐 | 人工核对 |
| 3 | §0 代码文件清单 ↔ 架构层YAML l00_data_source.yaml | 子模块映射 | 已确认不对齐(C轨占位) | YAML定义5子模块(connectors/normalizers/storage/cache/quality)，代码为provider_base/quality_gate/implementations/结构 |

> ⚠️ **架构层YAML与代码结构不对齐**：YAML定义5子模块(connectors/normalizers/storage/cache/quality)全部status=planned，代码实现了provider_base/quality_gate/implementations/结构。这是C轨占位阶段的正常现象——待正式施工时按YAML路径重组代码(GOV-FSTR-001)。

### 10.3 内部依赖图

**执行顺序依赖**：无内部依赖

**数据流依赖**：

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| AkShareProvider | DefaultQualityGate | OHLCV DataFrame | 函数调用 |
| MemoryProvider | DefaultQualityGate | OHLCV DataFrame | 函数调用 |
| DefaultQualityGate | L02/L03 | QualityReport | 函数调用 |

### 10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 现有工具 | 缺口 | 触发方式 | 触发条件 |
|---|---------|:-------:|------|---------|---------|------|---------|---------|
| 1 | 依赖图自动生成 | 否 | C轨占位，子模块少 | — | — | — | — | — |
| 2 | 依赖对齐自动验证 | 否 | 人工核对即可 | — | — | — | — | — |
| 3 | 临时时态内容自动清理 | 否 | 无临时时态内容 | — | — | — | — | — |
| 4 | 施工步骤完成度自动检测 | 是 | 验证代码可导入 | pytest | pytest | 无 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

> §11 产出物路径 MUST 与依赖图 §5 path_mappings 一致。

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain-data\datasource-core\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\data\` | Python 源码 |
| 测试代码 | `D:\ZephyrAlpha\tests\unit\data\` | 测试用例 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| L02 Alpha Factor | CTR-001产出 | NormalizedMarketData (OHLCV DataFrame) | 因子引擎可消费行情数据 |
| L03 Signal Generation | CTR-001产出 | NormalizedMarketData (OHLCV DataFrame) | 信号合成可消费行情数据 |
| INF-015 Telemetry | instrumentation | 数据摄取指标 | 指标可观测 |
| INF-035 AutoRuntime | CapabilityCard注册 | 数据接入注册 | ModuleOnboardingScanner发现 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint-registry.yaml` | construction_progress更新 | 进度变更 |
| 2 | 架构层YAML | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\layers\l00_data_source.yaml` | 补充implementations/子目录文件 | 文件清单同步 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | AkShare API限流 | 高 | 数据延迟 | 请求限速 + 缓存 | 风险 |
| 2 | 数据源格式变更 | 中 | 解析失败 | Schema版本化 + Drift Detector | 风险 |
| 3 | 新数据源需实现DataSourceBase | — | 中 | OCP扩展点设计，新数据源继承即可 | 负面后果 |
| 4 | C轨占位期间不主动施工 | — | 中 | 待A轨稳定后按优先级启动 | 负面后果 |
| 5 | 架构层YAML与代码结构不对齐 | — | 中 | 待GOV-FSTR-001重组 | 负面后果 |

---

## §16 施工指引

> ⛔ C轨占位——禁止施工。以下施工指引仅记录已完成的骨架实现，不新增施工步骤。

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §0 对齐 + §1-§14 架构 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取必备链接中所有真源文件 | 逐个打开确认 | ☐ |
| 3 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |
| 4 | 理解⛔C轨占位禁止施工 | 确认不新增业务代码 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 2 个 Phase（已完成骨架） |
| 施工模式 | 扩展 |
| 核心风险 | 数据源稳定性 |
| 目标 generation | 3 |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | DataSourceBase定义 | hard | ✅ | ✅ |
| 2 | DataQualityGate定义 | hard | ✅ | ✅ |

### 16.3 实施步骤

#### 步骤 1：完善AkShareProvider（已完成）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\data\implementations\akshare_provider.py` |
| 验收标准 | import成功，fetch_historical返回OHLCV DataFrame |
| 验证命令 | `python -c "from zephyr.data.implementations.akshare_provider import AkshareProvider"` |
| G7 检查项 | 上游provider_base.py存在，下游L02可消费 |

#### 步骤 2：完善DefaultQualityGate（已完成）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 |
| 产出位置 | `D:\ZephyrAlpha\src\zephyr\data\implementations\default_quality_gate.py` |
| 验收标准 | 校验规则可配置，check返回QualityReport |
| 验证命令 | `python -c "from zephyr.data.implementations.default_quality_gate import DefaultQualityGate"` |
| G7 检查项 | 上游quality_gate.py存在，下游可调用 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | AkShareProvider实现失败 | 还原implementations/akshare_provider.py |
| 2 | DefaultQualityGate实现失败 | 还原implementations/default_quality_gate.py |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | AkShareProvider存在 | `ls` exit 0 | 完成 | ✅ |
| 2 | DefaultQualityGate存在 | `ls` exit 0 | 完成 | ✅ |
| 3 | MemoryProvider存在 | `ls` exit 0 | 完成 | ✅ |
| 4 | SLO已定义 | §5.4每项SLI有测量方式 | 就绪 | ☐ |
| 5 | 监控指标已埋点 | §6.1每项指标有采集实现 | 就绪 | ☐ |
| 6 | 回滚方案已验证 | §16.4回滚操作可执行 | 就绪 | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | partially_implemented | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

### 16.7 参考实现规格

> 判定：删掉后AI会编造→保留。[时态:施工参考]

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | DataSourceBase注册机制 | 协议 | `__init_subclass__` + `__meta__` → `_registry[provider_id] = cls` | provider_base.py |
| 2 | DefaultQualityGate 5项规则 | 算法 | close≤0→0分; stale>300s→-0.3; future timestamp→-0.5; high<low→-0.5; volume=0→-0.4 | default_quality_gate.py |
| 3 | AkShare列名映射 | 协议 | 日期→date/开盘→open/收盘→close/最高→high/最低→low/成交量→volume/成交额→amount | akshare_provider.py |

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -c "from zephyr.data.provider_base import DataSourceBase"` | 验证DataSourceBase可导入 | — | 无报错 |
| 2 | 命令 | `python -c "from zephyr.data.quality_gate import DataQualityGate"` | 验证DataQualityGate可导入 | — | 无报错 |
| 3 | 配置 | `DataSourceMeta.rate_limit_per_min` | API限流配置 | int, 默认60 | AkShare=60, Memory=999999 |

### 16.10 故障与操作手册

| # | 阶段 | 场景 | 触发条件 | 诊断/操作 | 恢复/产出 | 验证/回退 |
|---|:----:|------|---------|----------|----------|----------|
| 1 | 运行 | AkShare API不可用 | 网络超时/429 | 检查网络+限流 | 切换MemoryProvider | 数据恢复后切回 |
| 2 | 运行 | 数据质量持续不通过 | QualityReport.passed=False | 检查数据源格式变更 | 人工修复+Drift Detector | 修复后质检通过 |
| 3 | 运行 | 紧急冻结 | 安全事件 | 停止所有fetch调用 | — | 威胁解除 |

### 16.12 并发操作模型

| 冲突场景 | 检测方式 | 解决策略 | 合并规则 |
|---------|---------|---------|---------|
| 同symbol并发fetch | 无检测 | AkShare自身限流保护 | 后到者等待 |
| 多AI Session同时修改implementations/ | 锁检测 | RULE-ZERO文件锁 | FIFO |

---

## §17 容量升级附录

### §17.1 容量基线

| 资源 | 当前基线 | 测量方式 |
|------|---------|---------|
| 数据源数量 | 1 (AkShare) | DataSourceBase._registry计数 |
| 日摄取记录 | ~5000 | 日志统计 |
| QualityGate子类 | 1 (Default) | DataQualityGate._registry计数 |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-L00-001 | API限流60次/分钟 | 本地缓存+批量预取 | P1 | 限流触发率>10% | v1.1.0 | 待施工 |
| GAP-L00-002 | 缺connectors/normalizers/storage/cache子模块 | 按架构层YAML创建 | P0 | C轨开工时 | v2.0.0 | 待施工 |
| GAP-L00-003 | DataFrame→Pydantic迁移 | 按KBG-0040迁移 | P2 | L02消费端要求 | v2.0.0 | 待施工 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v0.1.0 | 1 | 占位 | 仅占位文件 | ❌ |
| v2.1.0 | 2 | 模板升级 | §0前移+§7/§15删除+§10拆分 | ⚠️ |
| v3.0.0 | 3 | 回填+对齐 | 模板v4.1合规+代码对齐修正+压缩 | ⚠️ |

### 升级组件清单

| 组件名 | 对应缺口 | 代码文件 | 施工Phase | 状态 |
|--------|---------|---------|----------|:---:|
| RequestThrottler | GAP-L00-001 | throttler.py | Phase 2 | 待施工 |
| Connectors子模块 | GAP-L00-002 | connectors/ | Phase 3 | 待施工 |
| Normalizers子模块 | GAP-L00-002 | normalizers/ | Phase 3 | 待施工 |
| Storage子模块 | GAP-L00-002 | storage/ | Phase 3 | 待施工 |
| Cache子模块 | GAP-L00-002 | cache/ | Phase 4 | 待施工 |

---

## §18 决策记录

| # | 决策ID | 决策 | 选项 | 选中 | 依据 | 日期 |
|---|--------|------|------|------|------|------|
| 1 | D-L00-01 | DataSourceBase使用OCP扩展点 | 继承/注册表/直接调用 | 继承 | 新数据源只加不改 | 2026-05-05 |
| 2 | D-L00-02 | 数据输出格式为DataFrame(非Pydantic) | dict/Pydantic/dataclass/DataFrame | DataFrame | C轨占位阶段DataFrame更灵活，待正式施工按KBG-0040迁移Pydantic | 2026-05-05 |
| 3 | D-L00-03 | QualityGate独立于Provider | 内建/独立 | 独立 | 质量校验与数据获取职责分离 | 2026-05-05 |
| 4 | D-L00-04 | QUALITY_THRESHOLD=0.7硬编码 | 可配置/硬编码 | 硬编码 | 质量底线不可妥协 | 2026-05-05 |
| 5 | D-L00-05 | MemoryProvider用于测试/离线 | Mock/内存/文件 | 内存 | 零网络依赖+合成数据统计特征 | 2026-05-05 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| DataSourceBase | 数据源抽象基类，OCP扩展点 | ProviderBase(旧名) | 代码实际类名为DataSourceBase |
| DataQualityGate | 数据质量门禁抽象基类 | QualityGate(旧名) | 代码实际类名为DataQualityGate |
| CTR-001 | NormalizedMarketData跨层契约 | — | 本层为Producer，L02/L03/L09为Consumer |
| OHLCV | Open/High/Low/Close/Volume标准行情格式 | — | 本模块的标准化输出格式 |
| QUALITY_THRESHOLD | 质量门禁阈值0.7 | — | 低于此值的数据标记为不合格 |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | 架构层YAML定义5子模块但代码结构不同 | 高 | C轨占位阶段实现与规划不一致 | 待GOV-FSTR-001重组代码 | §10.2 #3 | 待解决 |
| 2 | DataFrame未按KBG-0040使用Pydantic | 中 | C轨占位阶段选择灵活实现 | 待v2.0.0迁移 | §5.1 #2 | 待解决 |
| 3 | 无集成测试(需网络) | 中 | AkShare依赖外部API | 待CI环境配置 | §9 #3 | 待解决 |
| 4 | §6.1可观测性指标未实际埋点 | 中 | C轨占位未施工 | 待正式施工时实现 | §6.1 | 待解决 |

---

## 自检与闭合清单

| # | 阶段 | 检查项 | 确认方式 | 状态 |
|---|:----:|--------|---------|:----:|
| 1 | 设计 | §3 每个组件在 §4 有对应接口 | 逐组件核对 | ✅ |
| 2 | 设计 | §4 每个接口在 §16 有对应施工步骤 | 逐接口核对 | ✅ |
| 3 | 设计 | §5 每个约束在 §9 有对应测试 | 逐约束核对 | ⚠️ 部分 |
| 4 | 设计 | §0.1 每个代码文件在 §11 有对应产出物路径 | 逐文件核对 | ✅ |
| 5 | 设计 | §10 每个依赖在依赖图有对应条目 | 逐依赖核对 | ✅ |
| 6 | 前 | 已读取蓝图全文 | 逐节确认 | ☐ |
| 7 | 前 | 术语表中每个术语含义已理解 | 能回答区别 | ☐ |
| 8 | 前 | 成熟度声明中volatile的部分已标记 | 知道哪些可改 | ☐ |
| 9 | 前 | 已知问题登记中未解决的问题已知晓 | 知道哪些坑不能踩 | ☐ |
| 10 | 中 | 每步施工后执行验证命令 | exit 0才进下一步 | ☐ |
| 11 | 中 | 新代码文件头部十字段完整 | 逐文件核对 | ✅ |
| 12 | 后 | §0 代码对齐验证已更新 | construction_progress与实际一致 | ☐ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | evolving | 中 | 5子模块全部实现 | 仅2/5子模块有骨架代码 |
| 接口契约 | evolving | 中 | DataFrame→Pydantic迁移 | C轨占位阶段使用DataFrame |
| 数据模型 | evolving | 中 | Pydantic V2迁移 | 同上 |
| 施工步骤 | stable | 高 | C轨开工时扩展 | 已完成步骤不再变更 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v0.1.0 | 占位文件 | — | 已完成 |
| v2.1.0 | 模板升级+骨架代码 | v0.1.0 | 已完成 |
| v3.0.0 | 模板v4.1合规+代码对齐+压缩 | v2.1.0 | 已完成 |
| v3.1.0 | 可观测性埋点+集成测试 | v3.0.0 | 待施工(C轨) |
| v4.0.0 | 5子模块完整实现+Pydantic迁移 | v3.1.0 | 待施工(C轨) |

---

## ⚠️ Vibe Coding 蓝图编写铁律

| # | 铁律 | 违反后果 |
|---|------|---------|
| 1 | 所有路径必须是绝对路径（含盘符 `D:\`） | 路径错误 |
| 2 | 必备链接不可省略 | 信息缺失 |
| 3 | 蓝图必须是最终设计结果 | 信息淹没 |
| 4 | 产出物路径必须与 GOV-DOC-002 一致 | 路径幻觉 |
| 5 | 涉及文件范围必须明确列出 | 范围漂移 |
| 6 | 容量估算必须写 | 容量瓶颈 |
| 7 | 迁移/废弃方案必须写 | 断链/垃圾积累 |
| 8 | "待定"/"建议"/"按需"等模糊词禁止使用 | 执行漂移 |
| 9 | 蓝图必须自包含 | 信息缺失 |
| 10 | 删除文件必须遵守安全删除协议 | 永久丢失 |
| 11 | construction_progress 必须与代码实际状态一致 | 重复造轮子 |
| 12 | actual_disk_path 必须与 §11 产出物路径一致 | 搜索/导入失败 |
| 13 | 已实现代码不在蓝图中重复——§0.1标记`已实现`的模块，蓝图只保留接口签名（§4），不复制实现代码 | 实现与蓝图漂移 |
| 14 | 临时时态内容执行完毕后从蓝图删除 | 蓝图膨胀 |
| 15 | 蓝图内容拆分判定——职责不同→拆分独立蓝图；职责相同→原地升级 | 职责混乱 |
| 16 | 术语表不可省略 | 术语漂移 |
| 17 | 参考实现规格 vs 已实现代码重复——接口契约无法表达的逻辑规格MUST保留在§16.7 | 关键逻辑实现错误 |
| 18 | 对标验证表格 vs 对标散文——结构化对标表格MUST保留 | 丢表格→无法验证 |
| 19 | SLO必须定义 | 容错策略凭空猜测 |
| 20 | 可观测性不可省略 | 故障无法发现 |
| 21 | 退化矩阵必须声明 | 部分失败时行为不可预测 |

### 蓝图拆分判定标准

| 判定示例 | 职责域数量 | 消费者独立？ | 演进独立？ | 结论 |
|---------|:---:|:---:|:---:|------|
| 数据接入层（本蓝图） | 1 | 否 | 否 | 不拆分 |
| 假设：数据接入+数据缓存 | 2 | 是 | 是 | 拆分为 L00-DataSource + L01-Cache |

---

## ⚠️ 安全删除协议

本蓝图不涉及文件删除。数据接入层为纯新增/扩展型模块，无废弃/迁移文件。

---

## 必备链接

| # | 文件 | module_id | 版本 | 完整绝对路径 | 编写时用途 |
|---|------|-----------|------|------------|----------|
| 1 | 元数据注册表 | PS-STD-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_043_meta_rule_metadata.yaml` | 编号规则、doc_type词表 |
| 2 | 目录结构标准 | GOV-DOC-002 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 路径映射 |
| 3 | 治理方法论 | PS-STD-011 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_024_methodology_diagnosis.yaml` | MTH-012/MTH-013 |
| 4 | 文件命名规范 | GOV-DOC-003 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\rules\trae_028_doc_structure_naming.yaml` | 命名规则 |
| 5 | 模块 ID 注册表 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\module_id_registry.yaml` | 编号注册 |
| 6 | 架构总览 | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\00-overview.md` | 架构上下文 |
| 7 | 治理规则主注册表 | — | — | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\document-metadata-index-registry.yaml` | 现有规则索引 |
| 8 | AI 自治权限注册表 | GOV-AI-001 | 当前版本 | `D:\ZephyrAlpha\docs\01_policies_and_standards\_registry\catalogs\ai_autonomy_authority_registry.yaml` | AI 操作权限 |
| 9 | 架构层YAML | — | — | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\layers\l00_data_source.yaml` | 子模块定义真源 |

---

## 项目中已有类似功能

| # | 已有模块/文件 | 完整绝对路径 | 功能重叠点 | 为什么不能复用 |
|---|-------------|------------|----------|-------------|
| — | 无 | — | — | — |

---

## 涉及的文件范围

| # | 文件/目录 | 完整绝对路径 | 关系 | 变更类型 |
|---|---------|------------|------|---------|
| 1 | provider_base.py | `D:\ZephyrAlpha\src\zephyr\data\provider_base.py` | 读取 | 无变更 |
| 2 | quality_gate.py | `D:\ZephyrAlpha\src\zephyr\data\quality_gate.py` | 读取 | 无变更 |
| 3 | implementations/ | `D:\ZephyrAlpha\src\zephyr\data\implementations\` | 读取 | 无变更 |
| 4 | 测试代码 | `D:\ZephyrAlpha\tests\unit\data\` | 读取 | 无变更 |

---

## 治理信息

### SSoT 声明

| 内容 | 真源 | 非真源 |
|------|------|--------|
| 本蓝图的核心架构设计 | **本文档 §1-§10** | 已被取代的旧蓝图 |
| 本模块的施工步骤 | **本文档 §16** | 已废弃的旧施工图 |
| 本模块的接口契约 | **本文档 §4** | — |
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint-registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |
| 子模块定义 | **架构层YAML** | 本蓝图（派生视图） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | L02 Alpha Factor | §4 接口契约、§10 依赖关系 |
| Tier 1 | L03 Signal Generation | §4 接口契约 |
| Tier 2 | L09 Research | CTR-001 历史数据回测 |
| Tier 3 | INF-015 Telemetry | 数据摄取指标 |
| Tier 3 | INF-035 AutoRuntime | 数据接入注册 |

### 变更审批与同步规则

| 变更类型 | 审批要求 | Tier 1 同步（下游蓝图） | Tier 2 同步（集成系统） |
|---------|---------|---------------------|---------------------|
| 接口契约新增/修改（§4） | 需Owner审批+通知所有消费者 | 下游检查接口兼容性 | 检查集成点兼容性 |
| 模块边界修改（§2） | 需Owner审批 | 下游更新依赖声明 | 更新集成路由 |
| construction_progress 变更 | 需§0对齐验证通过 | 下游更新依赖状态 | 更新集成测试 |
| 施工步骤微调 | AI可自主修改 | 下游更新产出物引用 | 更新配置文件 |
| 非关键补充 | AI可自主修改 | — | — |
| 容量升级方案新增（§17） | 需Owner审批 | 下游评估影响 | 更新容量预算 |


## Consumers
- zephyr.datasource_core (internal)
