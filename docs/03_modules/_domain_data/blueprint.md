---
module_id: MOD-L00-001
submodule_path: src/zephyr/data
title: "Data Source Core 蓝图+施工图 — 数据接入层"
doc_type: blueprint
status: Active
version: "4.0.0"
layer: L2_domain
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
belongs_to: "MOD-MASTER_BLUEPRINT"
parent_module: ""
codification_level: L1
codification_at: "2026-05-15"
last_verified: "2026-05-15"
last_updated: "2026-07-04"
generation: 4
rule_form: structural
scope: module
stability: evolving
verifiability: hybrid
references:
  - path: "D:\\ZephyrAlpha\\docs\\02_enterprise_architecture\\target-architecture\\architecture_model\\layers\\l00_data_source.yaml"
    section: ""
    why: "架构层YAML真源"
  - path: "D:\\ZephyrAlpha\\docs\\03_modules\\_cross_layer\\database\\business_data_architecture.md"
    section: "§5 品类全景 / §6 插拔式品类管理 / §7 回测调度策略 / §8 能造/硬性边界"
    why: "业务数据库母蓝图——数据源接入层的上游设计真源"
depends_on:
  - target: MOD-GATE_ENGINE
    at: "§10"
    why: "数据质量门控联动"
  - target: MOD-DATABASE
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
summary: "数据接入层——业务数据库母蓝图(MOD-ARCH-BIZDB)上游，对接69品类全景，多数据源标准化接入(AkShare/miniQMT/iFind/tushare/爬虫)，原料/成品/事务三层分类，质量门禁对接CTR契约，calc_mode标注(replay/preload/hybrid)支撑回测调度，为C1~C4仓库提供原料数据。"
---

> **v4.0.0 重建中** — 旧C轨占位代码已清理（2026-07-01），抽象层+实现层已按业务数据库母蓝图重建，多品类扩展(对接母蓝图§6插拔机制)待施工。

> actual_disk_path: src/zephyr/data/ (抽象层+实现层5文件已重建，多品类扩展待施工)

# Data Source Core 蓝图+施工图 — 数据接入层

> module_id: MOD-L00-001 | version: 4.0.0 | status: active | domain: data
> actual_disk_path: src/zephyr/data/ | generation: 4 | construction_progress: partially_implemented

> ⚠️ **职责拆分通知（2026-07-06）**
>
> 本蓝图的 **Provider 抽象部分（DataSourceBase / DataSourceMeta / per-source 实现）** 已移交新蓝图：
> 👉 [data_source_integrator_blueprint.md](data_source_integrator_blueprint.md)（MOD-L00-004 数据源集成器）
>
> **移交原因**：本蓝图 §0.1/§0.3/§16.6 声称 Provider "已实现/已重建"，但 `src/zephyr/data/` 实际为空目录（仅 `__init__.py`），声明与磁盘不符。借 MOD-L00-004 一并重建，同时补齐本蓝图未设计的**调度编排层 / per-source 策略注册表 / 进度统一存储 / 告警**四块短板。
>
> **本蓝图保留职责**：
> - 数据质量门禁（DataQualityGate）——与下载调度解耦，由消费方读取时调用
> - 标准化输出契约（CTR-001/CTR-002/CTR-003）——数据格式规范不变
> - 品类全景对接（母蓝图 §5/§6）
>
> **后续施工以 MOD-L00-004 为准**。本蓝图 §3.1/§4/§16.6/§16.7.1 的 Provider 相关章节仅作历史设计参考，不再维护。

## 概述

本蓝图描述 ZephyrAlpha 数据接入层——它是业务数据库母蓝图([MOD-ARCH-BIZDB](file:///d:/ZephyrAlpha/docs/03_modules/_cross_layer/database/business_data_architecture.md))的**上游**，为 C1/C2/C3 仓库提供原料数据，解决外部数据源格式各异、API限流、数据质量参差不齐的标准化接入问题。

核心职责：
- **数据源OCP扩展点**(DataSourceBase)：多数据源标准化接入
- **数据质量门禁**(DataQualityGate)：对接 CTR 契约质量门禁
- **标准化输出**(CTR-001~CTR-003)：NormalizedMarketData 及新闻/宏观契约
- **对接母蓝图§5品类全景**：69 品类摄取能力（行情/基本面/另类/宏观/新闻/舆情）
- **对接母蓝图§6插拔机制**：品类注册表 enabled 二元开关（硬边界品类 enabled=false 预留）
- **对接母蓝图§7回测调度**：calc_mode 标注（replay/preload/hybrid）

支持多数据源标准化接入：AkShare(免费行情+基本面)、miniQMT(实盘行情)、iFind(付费基本面+另类)、tushare(新闻+基本面)、爬虫(舆情)。支持原料/成品/事务三层分类（原料=tick/新闻原文接入即存，成品=K线/指标可预计算）。上游依赖各类外部 API，下游为 C1~C4 仓库层及 D_FACTOR/D_SIGNAL/D_RESEARCH 层提供标准化原料数据。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint-construction-template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint-construction-template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 代码头部标准：[code-construction-standards.md §7](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/governance/engineering/code-construction-standards.md)
> - 依赖图：[dependency_path_panorama.md](file:///d:/ZephyrAlpha/docs/02_enterprise_architecture/04_architecture_principles_decisions/dependency_path_panorama.md)
> - 优化规则：先 Layer 1（蓝图模板合规）→ 后 Layer 2（规格化砍削）

---

## §0 代码对齐验证

### §0.1 代码文件清单

> **架构归属SSoT**：见 AGENTS.md §7「代码规范」（depgraph SSoT 真源唯一指针）
> **代码头部规范**：`[BLUEPRINT]/[MODULE]/[DOMAIN]/[DEPENDENCIES]/[CONSUMERS]/[STARTUP]/[MATURITY]/[INVARIANTS]/[MODIFY-GUARD]/[STABILITY]/[SAFETY]/[AI_AUTONOMY]/[ERROR_CONTRACT]/[TESTS]/[TTL]` — 见防幻觉十八条

> **完整文件清单SSoT**：`python scripts/governance/extract_depgraph.py --modules MOD-L00-001`

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 |
|---|--------|------------|------|:---:|
| 1 | provider_base.py | §3.1 | DataSourceBase OCP扩展点 + DataSourceMeta | 已实现 |
| 2 | quality_gate.py | §3.1 | DataQualityGate抽象 + QualityReport + QualityFailureReason + RecoveryHint | 已实现 |
| 3 | implementations/akshare_provider.py | §3.1 | AkShare数据源实现 | 已实现 |
| 4 | implementations/default_quality_gate.py | §3.1 | 默认质量校验实现(5项规则) | 已实现 |
| 5 | implementations/memory_provider.py | §3.1 | 内存合成数据源(测试/离线) | 已实现 |
| 6 | implementations/miniqmt_provider.py | §16.7.1 | MiniQMT实盘行情(Tick+5档盘口) | 待施工 |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| construction_progress = partially_implemented → 已实现章节的代码存在 | `ls src/zephyr/data/` 逐文件核对 | ☐ |
| 蓝图描述的类/函数名 = 代码中的类/函数名 | `grep "class\|def" *.py` | ☐ |
| actual_disk_path = §11 产出物路径 | 路径比对 | ☐ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.1.0 (占位) | 无代码 | 全部 | partially_implemented |
| v2.1.0 (模板升级) | DataSourceBase + DataQualityGate + 3个实现 | connectors/normalizers/storage/cache子模块 | C轨占位 |
| v3.0.0 (回填+对齐) | 同 v2.1.0 | 同 v2.1.0 | C轨占位 |
| v4.0.0 (重建) | DataSourceBase + DataQualityGate + 3个实现(已重建) | 多品类扩展(category_id/calc_mode/CategoryManager) + §16.7.1 MiniQMT Provider规格(待施工) | 待Spiral扩展 |

---

## §1 设计背景与目标

### 1.1 背景

ZephyrAlpha 业务数据库母蓝图(MOD-ARCH-BIZDB §5)定义了 **69 个数据品类全景**：行情数据(10)、基本面(10)、另类(10)、宏观(11)、因子值(5大类)、技术指标(1组)、图形识别(6类)、信号历史(1)、主力行为(1)、板块强度(1)、知识图谱(5类)、回测结果(2)、交易事务(3)、补充品类(9)。数据源接入层作为业务数据库的**上游**，需为 C1/C2/C3 仓库提供这 69 品类的原料数据摄取能力。

各数据源 API 格式各异、限流策略不同、数据质量参差不齐，需统一接入层将原始数据标准化为 CTR 系列契约输出。母蓝图§6 要求**品类插拔式管理**（品类注册表 + DDL-as-Code + CTR 契约 + CategoryManager 发现 4 层机制）；母蓝图§7.5 要求品类标注 **calc_mode**（replay/preload/hybrid）以支撑回测调度策略；母蓝图§8 要求硬边界品类(Level-2/卫星/Barra等)以 enabled=false 预留接口。

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | 多数据源标准化接入 | AkShare/miniQMT/iFind/tushare/爬虫，DataSourceBase OCP扩展点 |
| 2 | ✅ 包含 | 品类摄取覆盖母蓝图69品类 | 行情/基本面/另类/宏观/新闻/舆情原料摄取 |
| 3 | ✅ 包含 | 数据质量门禁 | DataQualityGate 对接 CTR 契约质量门禁 |
| 4 | ✅ 包含 | 标准化输出 | CTR-001~CTR-003 (NormalizedMarketData/新闻/宏观) |
| 5 | ✅ 包含 | calc_mode 标注 | replay/preload/hybrid 支撑母蓝图§7回测调度 |
| 6 | ✅ 包含 | 品类注册表 enabled 二元开关 | 硬边界品类 enabled=false 预留接口(母蓝图§8.2) |
| 7 | ✅ 包含 | 原料/成品/事务三层分类 | 原料=tick/新闻原文接入即存，成品=K线/指标可预计算 |
| 8 | ❌ 排除 | 数据存储(C1~C4仓库) | 母蓝图 MOD-ARCH-BIZDB 负责 |
| 9 | ❌ 排除 | 因子计算 | D_FACTOR Alpha Factor 负责 |
| 10 | ❌ 排除 | 信号生成 | D_SIGNAL Signal Generation 负责 |
| 11 | ❌ 排除 | DDL-as-Code 建表 | 母蓝图§6.2 第2层负责 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| AkShare API 限流（每分钟60次） | 请求必须限速 + 缓存 |
| 多数据源格式差异（中文列名/字段命名/时区） | 标准化映射 + Schema版本化 + Drift Detector |
| 付费数据源(iFind)需API密钥 | 环境变量存储，禁止硬编码 |
| 数据源格式可能变更 | Schema版本化 + Drift Detector |
| 网络不可用时需降级 | MemoryProvider 提供本地回退 |
| akshare 为同步HTTP客户端 | 需 asyncio.to_thread 包装避免阻塞事件循环 |
| 硬边界品类(Level-2/卫星/Barra) | enabled=false 预留接口不摄取(母蓝图§8.2) |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | 架构决策 | 设计+施工 | 审批权限 |
| 母蓝图 MOD-ARCH-BIZDB | 品类全景/插拔机制/调度策略上游对齐 | 设计 | 数据源接入层为其上游 |
| D_FACTOR Alpha Factor | CTR-001数据格式 | 消费 | 接口兼容性 |
| D_SIGNAL Signal Generation | CTR-001数据格式 | 消费 | 接口兼容性 |
| C1~C4 仓库层 | 原料数据摄取 | 消费 | 品类→库映射(母蓝图§5.2) |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 数据源数量 | 1 (AkShare已重建) | 5 (AkShare/miniQMT/iFind/tushare/爬虫) | 缺4个数据源，**miniQMT Provider规格已就绪(§16.7.1)，待施工** | P1 |
| 品类覆盖 | OHLCV行情(CTR-001) | 69品类(CTR-001~003+) | 缺基本面/另类/宏观/新闻等 | P0 |
| calc_mode 标注 | 无 | replay/preload/hybrid | 待实现(母蓝图§7.5) | P1 |
| 品类注册表对接 | 无 | enabled 二元开关 | 待实现(母蓝图§6/§8.2) | P1 |
| 抽象层+实现层 | 5文件已重建 | 5文件+多品类扩展 | 多品类扩展待施工(步骤3) | P0 |
| SLO/可观测性 | 无 | 完整 | 全缺 | P1 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 日线行情摄取 | D_FACTOR请求行情 | AkshareProvider.fetch_historical → _normalize_columns → DataFrame | OHLCV DataFrame (CTR-001) |
| 新闻原文摄取(成品原料) | C3仓库请求新闻 | tushare/爬虫Provider.fetch → 标准化 → QualityGate.check | 新闻原文 (CTR-002) |
| 宏观数据摄取 | C3仓库请求宏观 | iFindProvider.fetch → 标准化 → QualityGate.check | 宏观指标 (CTR-003) |
| 数据质量校验 | 数据接入后 | DefaultQualityGate.check → QualityReport | QualityReport(passed=True/False) |
| 离线测试 | 测试环境 | MemoryProvider.fetch_historical → 合成数据 | OHLCV DataFrame |
| API限流 | AkShare返回429 | 限速重试 + MemoryProvider降级 | 延迟数据或合成数据 |
| 硬边界品类预留 | Level-2/卫星品类注册 | enabled=false，CategoryManager发现但不加载 | 预留接口(不摄取) |

---

## §2 模块边界

### 2.1 职责边界

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 数据源适配 | DataSourceBase 抽象 + AkShareProvider/MemoryProvider 实现(多数据源OCP扩展) | 本模块 |
| 2 | ✅ 包含 | 数据质量校验 | DataQualityGate + DefaultQualityGate(5项规则) 对接 CTR 契约门禁 | 本模块 |
| 3 | ✅ 包含 | 标准化输出 | CTR-001~003 (NormalizedMarketData/新闻/宏观) | 本模块 |
| 4 | ✅ 包含 | 品类注册表对接 | category_id + enabled 二元开关(母蓝图§6/§8.2) | 本模块 |
| 5 | ✅ 包含 | calc_mode 标注 | replay/preload/hybrid(母蓝图§7.5) | 本模块 |
| 6 | ✅ 包含 | 原料/成品/事务三层分类 | 原料接入即存，成品可预计算(母蓝图§5) | 本模块 |
| 7 | ❌ 排除 | 数据持久化(C1~C4仓库) | 母蓝图 MOD-ARCH-BIZDB 负责 | 母蓝图 |
| 8 | ❌ 排除 | 因子计算 | D_FACTOR Alpha Factor 负责 | D_FACTOR |
| 9 | ❌ 排除 | 信号生成 | D_SIGNAL Signal Generation 负责 | D_SIGNAL |
| 10 | ❌ 排除 | DDL-as-Code 建表 | 母蓝图§6.2 第2层负责 | 母蓝图 |

---

## §3 架构设计

### 3.1 组件架构

> 对接母蓝图§6 插拔式品类管理 4 层机制：第1层品类注册表 → 第2层 DDL-as-Code → 第3层 CTR 契约 → 第4层 CategoryManager 发现与路由。

| # | 组件 | 职责 | 依赖 | 交互方式 | 母蓝图对接 |
|---|------|------|------|---------|---------|
| 1 | DataSourceBase | 数据源OCP扩展点(ABC)，支持多品类fetch | — | 同步调用 | §6 第3层CTR契约Producer |
| 2 | DataSourceMeta | 数据源元数据(frozen dataclass)，含 category_id/calc_mode/enabled | — | 数据类 | §6 第1层注册表字段 + §7.5 calc_mode |
| 3 | DataQualityGate | 数据质量校验(ABC)，对接CTR契约门禁 | DataSourceBase | 同步调用 | §6 第3层质量门禁 |
| 4 | QualityReport | 质量校验报告(frozen dataclass) | — | 数据类 | — |
| 5 | QualityFailureReason | 失败原因枚举 | — | 枚举 | — |
| 6 | RecoveryHint | 恢复建议枚举 | — | 枚举 | — |
| 7 | AkShareProvider | AkShare数据源实现(免费行情+基本面) | DataSourceBase | 继承 | — |
| 8 | DefaultQualityGate | 默认校验规则(5项) | DataQualityGate | 继承 | — |
| 9 | MemoryProvider | 内存合成数据源(测试/离线) | DataSourceBase | 继承 | — |
| 10 | CategoryManager | 品类发现与路由(母蓝图§6 第4层) | 品类注册表 | 自动扫描 | **未来Spiral(不在当前§0.1代码清单)** |

> ⚠️ CategoryManager 为母蓝图§6 第4层机制，属未来 Spiral 扩展（步骤3），不纳入当前§0.1代码清单。当前由 DataSourceBase 的 `__init_subclass__` 自动注册机制承担发现职责。

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 |
|---|--------|---------|---------|---------|
| 1 | AkShare API | fetch_historical → _normalize_columns → validate_schema | C1仓库/D_FACTOR/D_SIGNAL/D_RESEARCH | pd.DataFrame (OHLCV, CTR-001) |
| 2 | tushare/爬虫 | fetch → 标准化 → QualityGate.check | C3仓库 | 新闻原文 (CTR-002) |
| 3 | iFind API | fetch → 标准化 → QualityGate.check | C3仓库 | 宏观指标 (CTR-003) |
| 4 | MemoryProvider | 合成数据生成 → validate_schema | 测试/D_FACTOR | pd.DataFrame (OHLCV) |
| 5 | 任意Provider | fetch → DataQualityGate.check | 仓库层 | QualityReport |

> 数据流方向：外部API → DataSourceBase.fetch(多品类) → 标准化 → QualityGate.check → CTR契约输出 → C1~C4仓库层。

### 3.3 状态生命周期

本模块无状态机。DataSourceBase 通过 `__init_subclass__` 实现自动注册（key=provider_id），DataQualityGate 同理。多品类扩展后，品类发现由 CategoryManager 启动扫描注册表（未来 Spiral）。

---

## §4 接口契约

> ⚠️ v4.0.0重建决策：数据输出格式使用 `pd.DataFrame`（CTR-001 NormalizedMarketData），待 KBG-0040 迁移窗口再评估 Pydantic V2 迁移。
> ⚠️ v4.0.0对接母蓝图：DataSourceBase/DataSourceMeta 扩展 category_id/calc_mode/enabled 字段（步骤3施工），保持向后兼容(默认值)。

### 4.1 公共 API

```python
class DataSourceBase(abc.ABC):
    _registry: ClassVar[dict[str, type["DataSourceBase"]]]
    def __init_subclass__(cls, **kwargs): ...
    # v4.0.0 对接母蓝图§6/§7 扩展（步骤3施工，默认值保证向后兼容）
    category_id: ClassVar[str] = "market_ohlcv"   # 品类标识(母蓝图§6 第1层 category_id)
    calc_mode: ClassVar[str] = "preload"           # 回测调度模式(母蓝图§7.5): replay/preload/hybrid
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
    # v4.0.0 对接母蓝图§6/§7/§8 扩展字段（步骤3施工，默认值保证向后兼容）
    category_id: str = "market_ohlcv"   # 品类标识(母蓝图§5品类→库映射)
    calc_mode: str = "preload"          # replay/preload/hybrid(母蓝图§7.5)
    enabled: bool = True                # 硬边界品类 enabled=False 预留(母蓝图§8.2)

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

> **契约引用**：本模块为 Producer，输出 CTR-001 NormalizedMarketData(OHLCV)。多品类扩展后引用 CTR-002(新闻原文)、CTR-003(宏观指标) 等契约（母蓝图§6 第3层）。当前§0.1代码仅实现 CTR-001，多品类契约为步骤3扩展。

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
| `fetch_historical()` | `pd.DataFrame` (OHLCV列, CTR-001) | 空 DataFrame / `ImportError`(akshare未安装) |
| `validate_schema()` | `bool` | — |
| `check()` | `QualityReport` | — |
| `subscribe_realtime()` | `None` | AkShare不支持实时推送(仅warning) |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增DataSourceBase子类 | ✅ 向后兼容 | OCP扩展(新数据源/新品类) |
| DataSourceMeta新增 category_id/calc_mode/enabled | ✅ 向后兼容 | 默认值保证(母蓝图§6/§7/§8) |
| DataFrame列新增 | ✅ 向后兼容 | 不影响已有消费者 |
| DataFrame列删除 | ❌ 破坏性 | 需Owner审批+迁移方案 |
| QualityFailureReason新增枚举值 | ✅ 向后兼容 | 不破坏已有逻辑 |
| QUALITY_THRESHOLD变更 | ❌ 破坏性 | 0.7为硬编码最低线 |
| calc_mode 取值集合扩展 | ✅ 向后兼容 | replay/preload/hybrid 之外的新值需Owner审批 |

**变更通知**：破坏性变更→Owner审批+蓝图minor+1。兼容性变更→AI自主+patch+1。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | DataSourceBase 为OCP扩展点 | 新数据源/新品类只加不改 |
| 2 | 数据输出必须标准化 | CTR-001~003 (母蓝图§6 第3层契约) |
| 3 | QUALITY_THRESHOLD = 0.7 | 硬编码最低线，禁止降级 |
| 4 | 禁止静默丢弃数据 | 不合格必须显式返回 QualityReport(passed=False) |
| 5 | akshare 为同步HTTP客户端 | 需 asyncio.to_thread 包装 |
| 6 | 品类注册表 enabled 二元开关 | 每品类 true/false(母蓝图§6.5)，硬边界品类 enabled=false 预留(母蓝图§8.2) |
| 7 | calc_mode 必须标注 | 每品类标注 replay/preload/hybrid(母蓝图§7.5) |
| 8 | 硬边界品类预留接口不摄取 | Level-2/卫星/Barra 等 enabled=false(母蓝图§8.2) |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|:------:|:------:|:------:|:------:|---------|
| 数据源数量 | 1 (AkShare) | 5 | 无上限 | ✅ | OCP扩展 |
| 品类覆盖 | 1 (OHLCV) | 69 (母蓝图§5) | 无上限 | ❌ | 多品类扩展(步骤3) |
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
| 4 | 编码模式 | 硬边界品类enabled=true摄取 | enabled=false预留接口(母蓝图§8.2) | 资金/合规硬边界 |
| 5 | 编码模式 | 品类未标注calc_mode接入 | 每品类标注replay/preload/hybrid | 母蓝图§7.5回测调度要求 |
| 6 | 导入源 | zephyr.signal.* / zephyr.factor.* | 仅允许被下游导入 | 分层约束：data 不依赖 signal+ |

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
| 1 | 单元测试 | DataSourceBase | 注册机制+validate_schema | tests/data/test_provider_base_contract.py |
| 2 | 单元测试 | DataQualityGate | QualityReport+QualityFailureReason+is_within_normal_range+QUALITY_THRESHOLD | tests/data/test_quality_gate.py |
| 3 | 集成测试 | AkShareProvider | fetch_historical返回OHLCV | 待补充(需网络) |
| 4 | 集成测试 | MemoryProvider | 合成数据质量 | 待补充 |

---

## §10 依赖关系

### 10.1 依赖声明

| 依赖模块 | 依赖类型 | 依赖内容 | 版本要求 | 蓝图路径 |
|---------|---------|---------|---------|---------|
| MOD-GATE_ENGINE Gatekeeper | 可选 | 数据质量门控联动 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\gate_engine\blueprint.md` |
| MOD-DATABASE Database | 可选 | 数据缓存 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\blueprint.md` |
| MOD-INF-015 Telemetry | 必须 | 数据摄取监控 | — | `D:\ZephyrAlpha\docs\03_modules\_domain_infrastructure_operations\system_telemetry\blueprint.md` |
| MOD-INF-035 AutoRuntime | 可选 | 数据接入注册 | — | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\auto-runtime-core\blueprint.md` |

### 10.2 依赖图对齐声明

| # | 对齐项 | 对齐方式 | 对齐状态 | 验证命令 |
|---|--------|---------|:-------:|---------|
| 1 | §10.1 依赖声明 ↔ dependency_path_panorama.md §3.8 | 蓝图声明的每个依赖在依赖图中有对应条目 | 已对齐 | 人工核对 |
| 2 | §11 产出物路径 ↔ 依赖图 §5 MOD-L00-001 | 路径一致 | 已对齐 | 人工核对 |
| 3 | §0 代码文件清单 ↔ 架构层YAML l00_data_source.yaml | 子模块映射 | 待重建后对齐 | v4.0.0重建后按架构层YAML 5子模块规划施工 |

> ⚠️ **v4.0.0 重建对齐策略**：旧C轨代码已清理（2026-07-01），重建时按架构层YAML l00_data_source.yaml 定义的5子模块(connectors/normalizers/storage/cache/quality)规划施工，消除历史不对齐。

### 10.3 内部依赖图

**执行顺序依赖**：无内部依赖

**数据流依赖**：

| 生产者 | 消费者 | 数据类型 | 传输方式 |
|--------|--------|---------|---------|
| AkShareProvider | DefaultQualityGate | OHLCV DataFrame | 函数调用 |
| MemoryProvider | DefaultQualityGate | OHLCV DataFrame | 函数调用 |
| DefaultQualityGate | D_FACTOR/D_SIGNAL | QualityReport | 函数调用 |

### 10.4 自动化规格

| # | 自动化项 | 是否需要 | 理由 | 实现方式 | 现有工具 | 缺口 | 触发方式 | 触发条件 |
|---|---------|:-------:|------|---------|---------|------|---------|---------|
| 1 | 依赖图自动生成 | 否 | 5文件已重建，多品类扩展待施工 | — | — | — | — | — |
| 2 | 依赖对齐自动验证 | 否 | 人工核对即可 | — | — | — | — | — |
| 3 | 临时时态内容自动清理 | 否 | 无临时时态内容 | — | — | — | — | — |
| 4 | 施工步骤完成度自动检测 | 是 | 验证代码可导入 | pytest | pytest | 无 | CI pipeline | 代码提交时 |

---

## §11 产出物存放目录

> §11 产出物路径 MUST 与依赖图 §5 path_mappings 一致。

| 产出物类型 | 存放完整绝对路径 | 说明 |
|----------|---------------|------|
| 蓝图文件 | `D:\ZephyrAlpha\docs\03_modules\_domain_data\blueprint.md` | 本文件 |
| 业务代码 | `D:\ZephyrAlpha\src\zephyr\data\` | Python 源码 |
| 测试代码 | `D:\ZephyrAlpha\tests\unit\data\` | 测试用例 |

---

## §12 集成目标

| 集成目标系统 | 集成方式 | 集成点 | 验证方法 |
|------------|---------|--------|---------|
| D_FACTOR Alpha Factor | CTR-001产出 | NormalizedMarketData (OHLCV DataFrame) | 因子引擎可消费行情数据 |
| D_SIGNAL Signal Generation | CTR-001产出 | NormalizedMarketData (OHLCV DataFrame) | 信号合成可消费行情数据 |
| INF-015 Telemetry | instrumentation | 数据摄取指标 | 指标可观测 |
| INF-035 AutoRuntime | CapabilityCard注册 | 数据接入注册 | ModuleOnboardingScanner发现 |

---

## §13 需要更新的相关内容

| # | 需更新的文件 | 完整绝对路径 | 更新内容 | 更新原因 |
|---|------------|------------|---------|---------|
| 1 | 蓝图注册表 | `D:\ZephyrAlpha\docs\03_modules\blueprint_registry.yaml` | construction_progress更新 | 进度变更 |
| 2 | 架构层YAML | `D:\ZephyrAlpha\docs\02_enterprise_architecture\target-architecture\architecture_model\layers\l00_data_source.yaml` | 补充implementations/子目录文件 | 文件清单同步 |

---

## §14 已知风险与缓解

| # | 风险/负面后果 | 概率 | 影响 | 缓解策略 | 类型 |
|---|-------------|------|------|---------|------|
| 1 | AkShare API限流 | 高 | 数据延迟 | 请求限速 + 缓存 | 风险 |
| 2 | 数据源格式变更 | 中 | 解析失败 | Schema版本化 + Drift Detector | 风险 |
| 3 | 新数据源需实现DataSourceBase | — | 中 | OCP扩展点设计，新数据源继承即可 | 负面后果 |
| 4 | v4.0.0重建期间代码不可用 | — | 中 | 优先重建抽象层+实现层 | 负面后果 |
| 5 | 架构层YAML与代码结构不对齐 | — | 中 | v4.0.0重建时消除 | 负面后果 |

---

## §16 施工指引

> 🚧 v4.0.0 重建施工指引——对接母蓝图 MOD-ARCH-BIZDB Spiral 开发顺序。抽象层+实现层已重建，多品类扩展(对接母蓝图§6插拔机制)为未来 Spiral 工作。

### ⚠️ AI 施工前检查清单

| # | 检查项 | 确认方式 | 状态 |
|---|--------|---------|:----:|
| 1 | 已读取本蓝图全部内容（概述 + §0 对齐 + §1-§14 架构 + §16 施工指引） | 逐节确认 | ☐ |
| 2 | 已读取母蓝图 §5/§6/§7/§8 关键章节 | 逐个打开确认 | ☐ |
| 3 | §0 代码对齐验证已填写且与实际代码一致 | 逐项核对 | ☐ |
| 4 | 理解v4.0.0对接母蓝图重建策略 | 确认按母蓝图69品类/插拔/calc_mode施工 | ☐ |

### 16.1 施工策略

| 项目 | 内容 |
|------|------|
| 施工阶段数 | 3 个步骤（对接母蓝图 Spiral 开发顺序） |
| 施工模式 | 重建 + 多品类扩展 |
| 核心风险 | 数据源稳定性 + 多品类标准化对齐 |
| 目标 generation | 4 |
| Spiral 归属 | Spiral 1：数据源接入层（当前） |

### 16.2 前置条件

| # | 依赖项 | 依赖类型 | 当前状态 | 是否满足 |
|---|--------|---------|:---:|:---:|
| 1 | provider_base.py 重建 | hard | 已重建 | ✅ |
| 2 | quality_gate.py 重建 | hard | 已重建 | ✅ |
| 3 | 母蓝图 MOD-ARCH-BIZDB 品类注册表 | soft | 设计完成 | ☐ |

### 16.3 实施步骤

#### 步骤 1：重建抽象层（已重建）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 / §4.2 |
| 产出位置 | `provider_base.py` + `quality_gate.py` |
| 验收标准 | DataSourceBase 可继承注册，DataQualityGate 可继承注册 |
| 验证命令 | `python -c "from zephyr.data.provider_base import DataSourceBase"` |
| 状态 | ✅ 已重建 |
| G7 检查项 | 上游无依赖，下游D_FACTOR可消费 |

#### 步骤 2：重建实现层（已重建）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 |
| 产出位置 | `implementations/akshare_provider.py` + `default_quality_gate.py` + `memory_provider.py` |
| 验收标准 | AkshareProvider/DefaultQualityGate/MemoryProvider 可导入并实例化 |
| 验证命令 | `python -c "from zephyr.data.implementations.akshare_provider import AkshareProvider"` |
| 状态 | ✅ 已重建 |
| G7 检查项 | 上游抽象层存在，下游D_FACTOR可消费 |

#### 步骤 3：扩展多品类支持（待施工）

| 项目 | 内容 |
|------|------|
| 对应蓝图契约 | §4.1 category_id/calc_mode + §4.2 enabled + §3.1 CategoryManager |
| 产出位置 | `provider_base.py`(扩展字段) + 未来 CategoryManager(不在当前§0.1清单) |
| 对接母蓝图 | §6 插拔式4层机制 / §5 69品类 / §7.5 calc_mode / §8.2 硬边界enabled |
| 验收标准 | DataSourceMeta 支持 category_id/calc_mode/enabled；品类注册表enabled二元开关生效 |
| 验证命令 | 待施工后补充 |
| 状态 | ⬜ 待施工（未来 Spiral） |
| G7 检查项 | 向后兼容(默认值)，硬边界品类enabled=false不破坏现有消费 |

### 16.4 回滚方案

| 步骤 | 如果出问题 | 回滚操作 |
|------|----------|---------|
| 1 | 抽象层重建失败 | 删除provider_base.py/quality_gate.py |
| 2 | 实现层重建失败 | 删除implementations/下文件 |
| 3 | 多品类扩展失败 | category_id/calc_mode/enabled 回退为默认值(向后兼容) |

### 16.5 施工完成与生产就绪标准

| # | 检查项 | 通过标准 | 类型 | 状态 |
|---|--------|---------|:----:|:----:|
| 1 | provider_base.py存在 | `ls` exit 0 | 完成 | ✅ |
| 2 | quality_gate.py存在 | `ls` exit 0 | 完成 | ✅ |
| 3 | 3个implementations文件存在 | `ls` exit 0 | 完成 | ✅ |
| 4 | 多品类扩展完成 | category_id/calc_mode/enabled 生效 | 就绪 | ☐ |
| 5 | SLO已定义 | §5.4每项SLI有测量方式 | 就绪 | ☐ |
| 6 | 监控指标已埋点 | §6.1每项指标有采集实现 | 就绪 | ☐ |
| 7 | 回滚方案已验证 | §16.4回滚操作可执行 | 就绪 | ☐ |

### 16.6 施工状态

| 字段 | 值 | 填写者 |
|------|-----|-------|
| construction_status | partially_rebuilt (步骤1-2完成，步骤3待施工) | 施工者 |
| verification_status | unverified | 审计者 |
| code_alignment_verified | no | 审计者 |

### 16.7 参考实现规格

> 判定：删掉后AI会编造→保留。[时态:施工参考]

| # | 规格名称 | 类型 | 规格内容 | 对应代码 |
|---|---------|------|---------|---------|
| 1 | DataSourceBase注册机制 | 协议 | `__init_subclass__` + `__meta__` → `_registry[provider_id] = cls` | provider_base.py |
| 2 | DefaultQualityGate 5项规则 | 算法 | close≤0→0分; stale>300s→-0.3; future timestamp→-0.5; high<low→-0.5; volume=0→-0.4 | default_quality_gate.py |
| 3 | AkShare列名映射 | 协议 | 日期→date/开盘→open/收盘→close/最高→high/最低→low/成交量→volume/成交额→amount | akshare_provider.py |
| 4 | calc_mode 取值集合 | 协议 | replay(回测实时重算) / preload(预计算值) / hybrid(预计算+微调) — 对接母蓝图§7.5 | provider_base.py(步骤3) |
| 5 | MiniQMT Provider Tick字段映射 | 协议 | xtdata Tick 18字段→标准化DataFrame(含5档盘口) — 见§16.7.1 | miniqmt_provider.py(待施工) |

### §16.7.1 MiniQMT Provider 详细规格（Tick+5档盘口）

> 来源：tmp/test_download_tick.py 实测验证（2026-07-04），国金证券MiniQMT终端
> 状态：✅ 数据源API已验证可用，⬜ Provider实现待施工

**数据源特性**:
- 数据源类型：本地终端（miniQMT）+ Python SDK（xtquant）
- 数据通道：xtdata（行情）+ xttrader（交易，由D_EX_CORE实现）
- 部署形态：Windows本地运行，需先启动 XtMiniQmt.exe 终端
- 资质门槛：券商10万资产门槛（国金证券已满足，Level-2免费赠送）
- API限制：xtdata 模块无需登录即可使用（行情免费），xttrader 需开通A股实盘权限

**Provider 元数据**:
```python
class MiniQmtProvider(DataSourceBase):
    provider_id = "miniqmt"
    provider_name = "MiniQMT 实盘行情"
    asset_classes = ["stock", "etf", "convertible_bond", "futures", "options"]
    markets = ["SH", "SZ"]
    supports_realtime = True       # ✅ 支持5档盘口实时订阅
    supports_historical = True     # ✅ 支持历史Tick/K线下载
    supports_local = True          # ✅ 本地终端
    rate_limit_per_min = 999999    # 本地终端无限流
    category_id = "market_tick_l1" # 品类:Level-1 Tick(含5档盘口)
    calc_mode = "replay"           # 回测调度:Tick回放模式
    enabled = True                 # 已开通
```

**Tick 数据字段映射**（xtdata → DataFrame 标准化）:

| xtdata原始字段 | DataFrame列名 | 类型 | 说明 |
|----------------|----------------|------|------|
| time | timestamp | datetime | 时间戳(毫秒级) |
| lastPrice | last_price | Decimal | 最新价 |
| open | open | Decimal | 开盘价 |
| high | high | Decimal | 最高价 |
| low | low | Decimal | 最低价 |
| lastClose | prev_close | Decimal | 昨收价 |
| amount | amount | Decimal | 成交额 |
| volume | volume | Decimal | 成交量 |
| pvolume | pvolume | Decimal | 内外盘成交量 |
| stockStatus | stock_status | int | 股票状态(停牌/ST等) |
| openInt | open_interest | int | 持仓量(期货) |
| lastSettlementPrice | last_settlement | Decimal | 昨结算价(期货) |
| **askPrice[0..4]** | **ask_price_1..5** | **Decimal[5]** | **5档卖价** |
| **bidPrice[0..4]** | **bid_price_1..5** | **Decimal[5]** | **5档买价** |
| **askVol[0..4]** | **ask_vol_1..5** | **Decimal[5]** | **5档卖量** |
| **bidVol[0..4]** | **bid_vol_1..5** | **Decimal[5]** | **5档买量** |
| settlementPrice | settlement_price | Decimal | 结算价 |
| transactionNum | transaction_num | int | 成交笔数 |

**核心API规格**:

```python
class MiniQmtProvider(DataSourceBase):
    """MiniQMT 实盘行情Provider——对接xtdata，提供Tick+5档盘口"""

    def __init__(self, path: str = "", session_id: str = "zephyr_session"):
        """
        初始化MiniQMT连接

        Args:
            path: miniQMT安装路径(默认自动检测)
            session_id: 会话ID(用于xttrader,行情无需)
        """
        # xtdata 模块导入(本地终端已安装)
        from xtquant import xtdata
        self._xtdata = xtdata

    def fetch_historical(
        self,
        symbol: str,
        start: datetime,
        end: datetime,
        interval: str = "tick"  # tick/1m/5m/15m/30m/60m/1d
    ) -> pd.DataFrame:
        """
        获取历史数据(支持Tick级)

        Args:
            symbol: 证券代码(格式: 600000.SH / 000001.SZ)
            start/end: 时间范围
            interval: 周期(tick=逐笔,1m=1分钟,1d=日线)

        Returns:
            pd.DataFrame: 标准化字段(见上表),Tick数据含5档盘口
        """
        # 1. 下载历史数据到本地缓存
        self._xtdata.download_history_data(symbol, interval, start_str, end_str)
        # 2. 获取数据
        data = self._xtdata.get_market_data_ex(
            stock_list=[symbol], period=interval,
            start_time=start_str, end_time=end_str
        )
        # 3. 标准化为DataFrame(18字段→CTR-001扩展)
        return self._normalize_tick_data(data[symbol])

    def subscribe_realtime(
        self,
        symbols: list[str],
        callback: Callable[[pd.DataFrame], None]
    ) -> None:
        """
        订阅实时Tick行情(含5档盘口)

        Args:
            symbols: 证券代码列表
            callback: Tick回调函数(每Tick触发)
        """
        for symbol in symbols:
            self._xtdata.subscribe_quote(symbol, period="tick", callback=callback)

    def get_order_book(self, symbol: str) -> dict:
        """
        获取当前5档盘口快照

        Returns:
            dict: {
                "ask_price": [Decimal×5],
                "bid_price": [Decimal×5],
                "ask_vol": [Decimal×5],
                "bid_vol": [Decimal×5],
                "last_price": Decimal,
                "timestamp": datetime
            }
        """
        tick = self._xtdata.get_full_tick([symbol])[symbol]
        return self._parse_order_book(tick)
```

**质量校验扩展**（MiniQMT专属规则）:

| 规则 | 阈值 | 失败原因 |
|------|------|---------|
| 5档盘口完整性 | askPrice/bidPrice 数组长度=5 | ORDER_BOOK_INCOMPLETE |
| 盘口价格单调性 | ask_price[i] > ask_price[i-1] > last_price > bid_price[i-1] > bid_price[i] | ORDER_BOOK_CROSSED |
| Tick时间连续性 | 相邻Tick间隔 < 5秒(交易时段) | TICK_GAP_TOO_LARGE |
| 盘口量为正 | ask_vol[i] > 0 且 bid_vol[i] > 0 | ORDER_BOOK_ZERO_VOL |

**与 D_BACKTEST/D_EX_CORE/D_FRONTEND 的协同**:

| 消费方 | 用途 | 接口 |
|--------|------|------|
| D_BACKTEST (data_handler.py) | Tick回放回测 | fetch_historical(interval="tick") |
| D_EX_CORE (miniqmt_broker.py) | 实盘下单参考价 | get_order_book() |
| D_FRONTEND (order_book.py) | 5档盘口实时展示 | subscribe_realtime() + get_order_book() |
| D_FRONTEND (tick_replay.py) | 秒级做T盘口回放 | fetch_historical(interval="tick") |

**部署约束**:
- 必须先启动 XtMiniQmt.exe 终端(独立交易模式)
- xtquant 库需从 QMT 安装目录 `bin.x64/Lib/site-packages/xtquant` 拷贝到Python环境
- Python 版本：3.6/3.7/3.8（QMT内置3.6，自定义环境用3.8最稳）
- 操作系统：仅 Windows（miniQMT终端为Windows应用）

**已知限制**:
- ❌ 不支持 Tick 级回测（xtdata本身是数据接口，回测由D_BACKTEST实现）
- ❌ Level-2 十档盘口需额外开通（当前Level-1五档足够用）
- ⚠️ 实时订阅需 miniQMT 终端保持运行（断线自动重连）

### 16.8 施工参考卡

| # | 类型 | 名称 | 用途/说明 | 参数/字段 | 输出/约束 |
|---|:----:|------|----------|----------|----------|
| 1 | 命令 | `python -c "from zephyr.data.provider_base import DataSourceBase"` | 验证DataSourceBase可导入 | — | 无报错 |
| 2 | 命令 | `python -c "from zephyr.data.quality_gate import DataQualityGate"` | 验证DataQualityGate可导入 | — | 无报错 |
| 3 | 配置 | `DataSourceMeta.rate_limit_per_min` | API限流配置 | int, 默认60 | AkShare=60, Memory=999999 |
| 4 | 配置 | `DataSourceMeta.calc_mode` | 回测调度模式(母蓝图§7.5) | str, 默认"preload" | replay/preload/hybrid |
| 5 | 配置 | `DataSourceMeta.enabled` | 硬边界品类开关(母蓝图§8.2) | bool, 默认True | false=预留不摄取 |

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
| 数据源数量 | 2 (AkShare+Memory) | DataSourceBase._registry计数 |
| 日摄取记录 | ~5000 | 日志统计 |
| QualityGate子类 | 1 (Default) | DataQualityGate._registry计数 |

### §17.2 缺口清单

| 缺口ID | 当前瓶颈 | 升级方案 | 优先级 | 触发阈值 | 目标版本 | 状态 |
|--------|---------|---------|:------:|---------|---------|:----:|
| GAP-L00-001 | API限流60次/分钟 | 本地缓存+批量预取 | P1 | 限流触发率>10% | v1.1.0 | 待施工 |
| GAP-L00-002 | 缺connectors/normalizers/storage/cache子模块 | 按架构层YAML创建 | P0 | v4.0.0重建时 | v4.0.0 | 待施工 |
| GAP-L00-003 | DataFrame→Pydantic迁移 | 按KBG-0040迁移 | P2 | D_FACTOR消费端要求 | v2.0.0 | 待施工 |

### §17.3 升级版本矩阵

| 版本 | generation | 升级类型 | 核心变更 | 代码覆盖 |
|------|:---:|---------|---------|:---:|
| v0.1.0 | 1 | 占位 | 仅占位文件 | ❌ |
| v2.1.0 | 2 | 模板升级 | §0前移+§7/§15删除+§10拆分 | ⚠️ |
| v3.0.0 | 3 | 回填+对齐 | 模板v4.1合规+代码对齐修正+压缩 | ⚠️ |
| v4.0.0 | 4 | 重建 | 旧C轨代码清理+按母蓝图重新施工 | ⚠️ |

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
| 2 | D-L00-02 | 数据输出格式为DataFrame(非Pydantic) | dict/Pydantic/dataclass/DataFrame | DataFrame | v4.0.0重建使用DataFrame，待KBG-0040迁移窗口 | 2026-05-05 |
| 3 | D-L00-03 | QualityGate独立于Provider | 内建/独立 | 独立 | 质量校验与数据获取职责分离 | 2026-05-05 |
| 4 | D-L00-04 | QUALITY_THRESHOLD=0.7硬编码 | 可配置/硬编码 | 硬编码 | 质量底线不可妥协 | 2026-05-05 |
| 5 | D-L00-05 | MemoryProvider用于测试/离线 | Mock/内存/文件 | 内存 | 零网络依赖+合成数据统计特征 | 2026-05-05 |
| 6 | D-L00-06 | 对接母蓝图69品类全景 | 独立设计/对接母蓝图 | 对接母蓝图 | 数据源接入层为业务数据库上游 | 2026-07-01 |
| 7 | D-L00-07 | calc_mode三值(replay/preload/hybrid) | 二值/三值 | 三值 | 对接母蓝图§7.5回测调度策略 | 2026-07-01 |
| 8 | D-L00-08 | 硬边界品类enabled=false预留 | 不预留/预留接口 | 预留接口 | 对接母蓝图§8.2硬性边界 | 2026-07-01 |

---

## 术语表

| 术语 | 精确定义 | 易混淆术语 | 区别 |
|------|---------|-----------|------|
| DataSourceBase | 数据源抽象基类，OCP扩展点 | ProviderBase(旧名) | 代码实际类名为DataSourceBase |
| DataQualityGate | 数据质量门禁抽象基类 | QualityGate(旧名) | 代码实际类名为DataQualityGate |
| CTR-001 | NormalizedMarketData跨层契约 | — | 本层为Producer，D_FACTOR/D_SIGNAL/D_RESEARCH为Consumer |
| OHLCV | Open/High/Low/Close/Volume标准行情格式 | — | 本模块的标准化输出格式(CTR-001) |
| QUALITY_THRESHOLD | 质量门禁阈值0.7 | — | 低于此值的数据标记为不合格 |
| 母蓝图 | 业务数据库顶层架构设计书(MOD-ARCH-BIZDB) | — | 本数据源接入层的上游设计真源 |
| category_id | 品类标识(母蓝图§6 第1层注册表) | — | 对接母蓝图69品类唯一标识 |
| calc_mode | 品类回测计算模式(母蓝图§7.5) | — | replay/preload/hybrid 三值 |
| enabled | 品类启用开关(母蓝图§8.2) | — | 硬边界品类enabled=false预留接口 |
| 原料/成品/事务 | 数据三层分类(母蓝图§5) | — | 原料=接入即存，成品=可预计算，事务=实时写 |

---

## 已知问题与盲点登记

| # | 问题 | 严重性 | 根因 | 解决方案 | 约束编号 | 状态 |
|---|------|:------:|------|---------|---------|:----:|
| 1 | 架构层YAML定义5子模块但代码结构不同 | 高 | 历史C轨占位实现与规划不一致 | v4.0.0重建时消除 | §10.2 #3 | 待解决 |
| 2 | DataFrame未按KBG-0040使用Pydantic | 中 | v4.0.0重建选择DataFrame | 待KBG-0040迁移窗口 | §5.1 #2 | 待解决 |
| 3 | 无集成测试(需网络) | 中 | AkShare依赖外部API | 待CI环境配置 | §9 #3 | 待解决 |
| 4 | §6.1可观测性指标未实际埋点 | 中 | 代码已重建但未埋点 | 多品类扩展时实现 | §6.1 | 待解决 |

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
| 11 | 中 | 新代码文件头部十五字段完整 | 逐文件核对 | ✅ |
| 12 | 后 | §0 代码对齐验证已更新 | construction_progress与实际一致 | ☐ |

---

## 成熟度声明

| 设计维度 | 成熟度 | 信心 | 升级标准 | 说明 |
|---------|:------:|:---:|---------|------|
| 核心架构 | evolving | 中 | 5子模块全部实现 | 5文件已重建，多品类扩展待施工 |
| 接口契约 | evolving | 中 | DataFrame→Pydantic迁移 | v4.0.0重建使用DataFrame |
| 数据模型 | evolving | 中 | Pydantic V2迁移 | 同上 |
| 施工步骤 | evolving | 高 | 重建步骤扩展 | 重建步骤待执行 |

---

## 版本演进路线图

| 版本 | 核心变更 | 前置版本 | 施工状态 |
|------|---------|---------|:-------:|
| v0.1.0 | 占位文件 | — | 已完成 |
| v2.1.0 | 模板升级+骨架代码 | v0.1.0 | 已完成 |
| v3.0.0 | 模板v4.1合规+代码对齐+压缩 | v2.1.0 | 已完成 |
| v4.0.0 | 旧C轨代码清理+按母蓝图重新施工 | v3.0.0 | 重建中 |

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
| 假设：数据接入+数据缓存 | 2 | 是 | 是 | 拆分为 D_DATA-DataSource + 基础设施-Cache |

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
| 10 | 业务数据库母蓝图 | MOD-ARCH-BIZDB | 1.0.0 | `D:\ZephyrAlpha\docs\03_modules\_cross_layer\database\business_data_architecture.md` | 上游设计真源(§5品类/§6插拔/§7调度/§8边界) |

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
| 代码文件清单与对齐状态 | **本文档 §0** | blueprint_registry.yaml（派生） |
| 容量升级方案 | **本文档 §17** | 独立升级文档（已废弃） |
| 子模块定义 | **架构层YAML** | 本蓝图（派生视图） |
| 69品类全景/插拔机制/调度策略 | **母蓝图 MOD-ARCH-BIZDB** | 本蓝图（上游对接视图） |

**任何与本蓝图冲突的定义，以本蓝图为准。**

### 消费者注册表

| Tier | 消费者 | 依赖内容 |
|:----:|--------|---------|
| Tier 1 | D_FACTOR Alpha Factor | §4 接口契约、§10 依赖关系 |
| Tier 1 | D_SIGNAL Signal Generation | §4 接口契约 |
| Tier 2 | D_RESEARCH Research | CTR-001 历史数据回测 |
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
