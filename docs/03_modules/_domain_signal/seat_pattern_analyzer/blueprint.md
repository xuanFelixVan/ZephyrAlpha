---
module_id: MOD-SIG-056
belongs_to: MOD-L03-001
title: "Seat Pattern Analyzer 蓝图+施工图 — 龙虎榜席位形态分析（谁在买）"
doc_type: blueprint
status: Draft
version: "0.1.3"
layer: L2_domain
functional_domain: ashare_signal
responsibility_domain: 
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
created_by: ai_agent
date: "2026-08-18"
last_updated: "2026-08-18"
last_verified: "2026-08-18"
ttl: permanent
generation: 1
actual_disk_path: "src/zephyr/signal_ashare/seat_pattern_analyzer.py"
depends_on:
  - target: REG-SEAT-001
    at: seats
    why: 席位身份/风格档案 SSoT（15 席位）
  - target: DS-080
    at: market_data.lhb_detail
    why: 龙虎榜明细数据集（JOB-076 接入，东财口径）
references:
  - path: "docs/01_policies_and_standards/_registry/catalogs/seat_registry.yaml"
    section: "seat_analysis_framework"
    why: "六维分析框架真源（定性/资金力度/位置/题材/结构/连续性）"
  - path: "docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml"
    section: "CAND-SEAT-001"
    why: "候选条目——本蓝图即其转正设计"
ssot_claims:
  - "席位形态分析算法（身份识别/联动/跟随信号合成）唯一真源"
  - "跟随信号阈值默认值（SeatPatternConfig）唯一真源"
summary: "龙虎榜席位形态分析 MVP——席位画像/席位联动/跟随信号三件套，管『谁在买』，与 chart_pattern 管『怎么买』正交"
tags: [龙虎榜, 席位, 信号, D_ASHARE_SIGNAL, CAND-SEAT-001]
priority: P1
---

# Seat Pattern Analyzer 蓝图+施工图 — 龙虎榜席位形态分析（谁在买）

> module_id: MOD-SIG-056 | version: 0.1.3 | status: Draft | layer: L2_domain
> actual_disk_path: src/zephyr/signal_ashare/seat_pattern_analyzer.py | generation: 1

## 概述

> temporal_type: permanent

本蓝图描述龙虎榜席位形态分析器——它解决了 A 股短线交易中"跟主力/跟游资"的席位身份/风格/结构无结构化管理的问题。核心职责包括：席位身份识别（seat_registry 15 席位档案匹配）、席位联动分析（同票多席位共现结构）、跟随信号合成（0-100 分三档方向）。当前规模 15 席位档案/单日榜，目标容量全市场每日上榜票（约 50-100 只/日）。上游依赖 seat_registry（REG-SEAT-001）+ DS-080 龙虎榜数据集（JOB-076），下游候选被 daban 类策略与席位溢价因子消费。

---

> **标准锚点（防幻觉）**——本蓝图必须严格遵循以下标准：
> - 蓝图+施工图模板：[blueprint_construction_template.md](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/templates/blueprint_construction_template.md)
> - AI 压缩工作流标准：[trae_030_doc_numbering_metadata.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml)
> - 机器真源：PostgreSQL depgraph（`python scripts/governance/extract_depgraph.py --modules MOD-SIG-056`）

---

## §0 代码对齐验证

### §0.1 代码文件清单

<!-- AUTOGEN: source=depgraph.nodes, generator=extract_depgraph.py, reconciler=blueprint_frontmatter_reconciler.py -->

> 真源：PostgreSQL depgraph.nodes 表（`blueprint_id = 'MOD-SIG-056'`）。禁止手写。

| # | 文件名 | 对应蓝图章节 | 职责 | 存在性 | 归属判定 | 阻塞原因 |
|---|--------|------------|------|:-----:|---------|---------|
| 1 | seat_pattern_analyzer.py | §3.1 | 席位形态分析器全部算法（A1 识别/A2 联动/A3 信号） | 已实现 | 本模块 | — |
| 2 | test_seat_pattern_analyzer.py | §8 | 17 用例（识别4/联动3/信号5/降级契约5） | 已实现 | 本模块（tests/ 豁免注册） | — |

### §0.2 对齐验证矩阵

| 验证项 | 验证方法 | 结果 |
|--------|---------|:---:|
| 蓝图类/函数名 = 代码类/函数名 | `grep "class\|def" seat_pattern_analyzer.py` | ☑ |
| 代码 [BLUEPRINT] 头部 = MOD-SIG-056 | `grep "\[BLUEPRINT\]" seat_pattern_analyzer.py` | ☑ |
| §4.2 数据模型在 SSoT 文件存在 | `grep "class SeatRecord\|class SeatProfile\|class SeatLinkage\|class FollowSignal"` | ☑ |
| §0.1 文件职责无重叠 | 单文件模块，交叉比对 | ☑ |

### §0.3 版本-代码映射

| 蓝图版本 | 代码覆盖范围 | 缺失组件 | 缺失原因 |
|---------|------------|---------|---------|
| v0.1.0 (基线) | A1 识别/A2 联动/A3 信号/降级路径/17 测试 | 维度3(位置)/4(题材)/6(连续性) | MVP 裁剪，v0.2 接入 |

### §0.4 SSoT与责任唯一性声明

| # | 声明维度 | 本蓝图是真源 | 真源在别处 | 委托目标 |
|---|---------|:----------:|:---------:|---------|
| 1 | 席位身份/风格档案 | ❌ | ✅ | REG-SEAT-001 seat_registry.yaml |
| 2 | 龙虎榜明细数据 | ❌ | ✅ | DS-080 / JOB-076（D_DATA） |
| 3 | 席位形态分析算法 | ✅ | ❌ | — |
| 4 | 跟随信号阈值默认值 | ✅ | ❌ | — |

### §0.5 代码目录唯一性声明

| # | 声明项 | 值 |
|---|--------|-----|
| 1 | 主代码目录 | `src/zephyr/signal_ashare/`（与 frontmatter.actual_disk_path 一致） |
| 2 | 已知副本目录 | 无 |
| 3 | 副本处置状态 | 无副本 |

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-056`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-056` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-SIG-056` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-056 | MOD-SIG-056 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 1 文件 | 2 文件（§0.1） | ❌ |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## §1 设计背景与目标

### 1.1 背景

> temporal_type: permanent

A 股短线交易"跟主力/跟游资"是核心 alpha 来源，但席位身份/胜率/风格无结构化管理，人工复盘不可持续。数据前提已就绪：JOB-076 龙虎榜管道 production（DS-080），seat_registry 15 席位档案已建（REG-SEAT-001 v1.2.0）。CAND-SEAT-001 候选条目触发信号满足（数据管道落地+SSoT 已建），本蓝图为其转正设计。

### 1.2 目标范围

| # | 类型 | 内容 | 标准/原因 |
|---|:----:|------|----------|
| 1 | ✅ 包含 | 席位身份识别（registry 精确/别名匹配→provider 粗分类回退） | 15 席位档案可查证 |
| 2 | ✅ 包含 | 席位联动（类型共现 4 标签 + 买一买二集中度，六维之维度1/5） | 框架维度5"买一买二40-60%最佳" |
| 3 | ✅ 包含 | 跟随信号（0-100 分 + long/neutral/avoid + 理由链） | 理由链保证信号可解释可追溯 |
| 4 | ✅ 包含 | 降级路径（无数据/registry 缺失/零成交额→degraded 中性） | 风险优先：不臆造信号 |
| 5 | ❌ 排除 | 席位历史胜率回测回填（history_win_rate/avg_premium） | 依赖≥3个月数据积累，v0.2 |
| 6 | ❌ 排除 | 股价位置（维度3）/题材（维度4）/三日连续性（维度6） | 依赖外部域输入（行情/题材/历史窗口），v0.2 |
| 7 | ❌ 排除 | CH 直查/数据拉取 | 纯函数模块，取数是上游/datafeed 职责 |

### 1.4 运行场景约束

| 约束 | 影响 |
|------|------|
| A 股 T+1、不能做空 | 跟随信号仅 long 方向有交易语义；avoid 用于回避/卖出提示 |
| 龙虎榜为日度披露（收盘后） | 信号为 T 日收盘后产出，T+1 可用；无盘中形态 |
| seat_registry 胜率字段全 null | v0.1 算法不消费胜率，只用身份/风格/结构 |

### 1.5 利益相关者映射

| 角色 | 关注点 | 参与阶段 | 约束 |
|------|--------|---------|------|
| Owner | MVP 范围裁剪/阈值默认值 | 设计裁定 | 架构决策审批 |
| daban 类策略（strategy_registry） | 席位增强特征 | 下游消费（候选） | 信号可解释 |
| factor_registry（席位溢价因子候选） | net_buy_ratio/top2_concentration 特征 | 下游消费（候选） | PIT 纪律 |

### 1.6 当前态/目标态差距

| 维度 | 当前态 | 目标态 | 差距 | 优先级 |
|------|--------|--------|------|:------:|
| 席位分析 | 人工复盘 | A1/A2/A3 自动化三件套 | v0.1 已落地 | P1 |
| 胜率实证 | null | 回测回填 15 席位胜率 | 需≥3月数据+回测批 | P2 |
| 维度3/4/6 | 未实现 | 位置/题材/连续性接入 | 外部域输入依赖 | P2 |

### 1.7 典型场景

| 场景 | 触发 | 处理流程 | 输出 |
|------|------|---------|------|
| 知名游资上买入榜 | T 日收盘后 JOB-076 拉取 | SeatRecord 列表→A1 识别命中 SEAT-YOUZI-xxx→A2 联动→A3 信号 | FollowSignal(long, ≥60) |
| 量化席位主导 | 同上 | A1 命中 SEAT-QUANT→A3 量化占比>30%→-20 | FollowSignal(avoid, ≤40) |
| 无榜数据 | 标的当日未上榜 | 空输入 | degraded=True 中性信号 |

---

## §2 模块边界

### 2.1 职责边界

> **核心职责声明**：本蓝图的核心职责是 `龙虎榜席位形态分析（谁在买→能不能跟）`。职责数量：3。

| # | 类型 | 职责 | 详情 | 负责方 |
|---|:----:|------|------|--------|
| 1 | ✅ 包含 | 席位身份识别 | seat_name/aliases 匹配 registry→provider 粗分类回退 | 本模块 |
| 2 | ✅ 包含 | 席位联动分析 | 类型共现矩阵+买一买二集中度 | 本模块 |
| 3 | ✅ 包含 | 跟随信号合成 | 基准50+身份/结构加减分→三档方向 | 本模块 |
| 4 | ❌ 排除 | 龙虎榜数据拉取/存储 | JOB-076/DS-080 | D_DATA |
| 5 | ❌ 排除 | 席位档案维护（胜率回填/席位增删） | REG-SEAT-001 | MOD-GOVERNANCE |
| 6 | ❌ 排除 | 价格形态识别（怎么买） | chart_pattern_registry | D_ASHARE_SIGNAL 形态族 |
| 7 | ❌ 排除 | 信号落库/推送 | 候选消费方自行消费返回值 | 上游编排 |

#### 职责唯一性声明

| 声明项 | 无重叠模块 | 验证方式 |
|--------|-----------|---------|
| 席位身份识别 | MOD-SIG-021（主力行为=分时价量行为学，非披露席位） | `check_ssot_uniqueness.py --blueprint MOD-SIG-056` |
| 席位联动/跟随信号 | MOD-SIG-033（游资接力情绪=情绪周期，非席位结构） | 同上 |

---

## §3 架构设计

### 3.1 组件架构

| # | 组件 | 职责 | 依赖 | 交互方式 |
|---|------|------|------|---------|
| 1 | SeatPatternAnalyzer | 编排 A1→A2→A3 主流程 | seat_registry.yaml（只读） | 同步调用 |
| 2 | SeatRecord/SeatProfile/SeatLinkage/FollowSignal/SeatPatternResult | Pydantic V2 数据模型 | pydantic | 内存对象 |

### 3.2 数据流

| # | 上游 | 处理逻辑 | 下游 | 数据格式 | 转换规则 |
|---|--------|---------|---------|---------|---------|
| 1 | c1_market.dragon_tiger_seat（JOB-076） | ①SeatRecord 构造（上游/调用方）→②A1 识别→③A2 联动→④A3 合成 | 候选：daban 策略/seat_premium 因子 | SeatPatternResult（Pydantic） | DB 行→SeatRecord→Profile/Linkage→FollowSignal |
| 2 | seat_registry.yaml | 加载为 {name/alias 小写： 档案} 查找表 | A1 识别器 | YAML→dict | seat_name 精确→aliases→provider 回退 |

### 3.3 状态生命周期

本模块无状态机（纯函数式，分析结果不可变）。

---

## §4 接口契约

### 4.1 公共 API

```python
class SeatPatternAnalyzer:
    """龙虎榜席位形态分析器——纯函数式，无内部状态。"""
    def __init__(self, config: SeatPatternConfig | None = None) -> None: ...
    def identify_seat(self, record: SeatRecord, total_turnover: float) -> SeatProfile: ...
    def analyze_linkage(self, profiles: list[SeatProfile], records: list[SeatRecord]) -> SeatLinkage: ...
    def synthesize_follow_signal(self, profiles: list[SeatProfile], linkage: SeatLinkage, total_turnover: float) -> FollowSignal: ...
    def analyze(self, records: list[SeatRecord]) -> SeatPatternResult: ...
```

| 方法 | 执行流程 | 关键决策点 |
|------|---------|-----------|
| `analyze()` | ①非空+单票单日校验→②A1 逐席位识别→③A2 联动→④A3 信号→⑤聚合 | 空输入→degraded 中性；多票/多日→SeatPatternDataError |
| `identify_seat()` | ①seat_name 小写精确匹配→②aliases 匹配→③provider_seat_type 回退 | 命中与否决定 matched_registry |
| `analyze_linkage()` | ①type_set 去重→②买方排序算 top2→③四类净额求和→④tag 判定 | 机构+游资双正→relay；量化+散户→grinder |
| `synthesize_follow_signal()` | ①基准50→②身份加减（机构+15/知名游资+10/量化-20/散户-15）→③结构加减（独食-10/力度±10/-5）→④联动标签修正→⑤clamp+三档 | 独食判定需 buyer_count≥3（2席买方时恒 100% 为假阳性，已修） |

### 4.2 数据模型

| 模型名 | SSoT文件 | 其他定义位置 | 状态 |
|--------|---------|------------|------|
| SeatRecord | seat_pattern_analyzer.py | — | ✅ 唯一源 |
| SeatProfile | seat_pattern_analyzer.py | — | ✅ 唯一源 |
| SeatLinkage | seat_pattern_analyzer.py | — | ✅ 唯一源 |
| FollowSignal | seat_pattern_analyzer.py | — | ✅ 唯一源 |
| SeatPatternResult | seat_pattern_analyzer.py | — | ✅ 唯一源 |
| SeatPatternConfig | seat_pattern_analyzer.py | — | ✅ 唯一源 |
| FollowDirection | seat_pattern_analyzer.py | — | ✅ 唯一源 |

### 4.3 输入契约

| 接口 | 输入字段 | 必填 | 约束 |
|------|---------|:---:|------|
| `analyze()` | `records` | ✅ | 全部同 symbol+同 trade_date；buy/sell_amount≥0；buy_rank/sell_rank ∈ [1,5] 或 None |
| `SeatPatternConfig.registry_path` | 路径 | ❌ | 缺省指向项目 seat_registry.yaml；不存在→空档案降级（warning 日志） |

### 4.4 输出契约

| 接口 | 成功输出 | 失败输出 |
|------|---------|---------|
| `analyze()` | `SeatPatternResult`：profiles+linkage+follow_signal+degraded | `SeatPatternDataError`（混票/混日） |

### 4.5 MCP 接口

本模块不暴露 MCP 接口。

### 4.6 契约版本

| 契约部分 | 兼容性 | 说明 |
|---------|:---:|------|
| 新增字段/加减分项 | ✅ 向后兼容 | 理由链追加不改变语义 |
| 删除/重命名字段/阈值默认值变更 | ❌ 破坏性 | 需 Owner 审批+蓝图 minor+1 |
| 新增枚举值（FollowDirection/linkage_tag） | ✅ 向后兼容 | — |

### 4.7 OCP 扩展点

本模块无 OCP 扩展点（v0.1 单实现；v0.2 维度3/4/6 接入时评审是否抽策略基类）。

---

## §5 约束条件

### 5.1 技术约束

| # | 约束 | 值 |
|---|------|-----|
| 1 | 数据模型 | Pydantic V2 BaseModel（禁 @dataclass） |
| 2 | 胜率字段 | v0.1 禁消费 history_win_rate/avg_premium（registry 全 null） |
| 3 | 无数据行为 | degraded=True + 中性 50 分，禁止臆造方向 |

### 5.2 容量估算

| 维度 | 当前规模 | 峰值需求 | 系统极限 | 是否够用 | 扩展方案 |
|------|---------|---------|---------|---------|---------|
| 单日上榜票 | ~50-100 只 | 200 只 | 纯内存计算，单票<1ms | ✅ | 无需 |
| 席位档案 | 15 条 | 100 条 | dict 查找 O(1) | ✅ | 无需 |

### 5.3 迁移

无（新建模块，无迁移）。

### 5.4 非功能需求与服务水平

| 维度 | 要求 |
|------|------|
| 延迟 | 单票分析 <1ms（纯内存 dict/循环） |
| 可解释 | 每个信号附 reasons 理由链（加减分明细） |
| 可测试 | 全部算法纯函数，17 用例覆盖 |

### 5.5 自动化触发机制

无（被调用型模块，由上游编排触发）。

### 5.7 禁止模式与导入约束

| # | 禁止 | 原因 |
|---|------|------|
| 1 | 直连 CH/PG 取数 | 纯函数模块纪律，取数是上游职责 |
| 2 | 写 seat_registry.yaml | 注册表归 MOD-GOVERNANCE 维护 |
| 3 | 消费胜率 null 字段 | 未回测字段不可参与打分 |

---

## §6 错误处理

### 6.1 可观测性

| 信号 | 方式 |
|------|------|
| registry 缺失/解析失败 | logger.warning + 空档案降级 |
| degraded 结果 | SeatPatternResult.degraded=True 显式标记 |

### 6.2 退化矩阵

| 异常 | 行为 | 信号可用性 |
|------|------|-----------|
| 空 records | degraded 中性 50 分 | 不可用于决策 |
| 总成交额=0 | degraded=True（profiles/linkage 正常算） | 占比类特征失效 |
| registry 文件缺失 | 空档案，全部 matched_registry=False 回退 provider 类型 | 可用（身份粒度降粗） |
| 混票/混日输入 | raise SeatPatternDataError | 硬失败（契约违规） |

---

## §7 安全考量

无敏感数据处理（公开披露数据）；无外部调用；输入经 Pydantic 校验（金额非负/排名区间）。

---

## §8 测试策略

| 层 | 内容 | 用例数 |
|----|------|:---:|
| A1 识别 | 精确/别名/回退/大小写空白 | 4 |
| A2 联动 | 接力/集中度/散户主导 | 3 |
| A3 信号 | long/avoid/neutral/独食罚分/截断 | 5 |
| 降级契约 | 空输入/混票/混日/registry 缺失/零成交额 | 5 |
| 合计 | `pytest tests/signal_ashare/test_seat_pattern_analyzer.py` | 17 |

---

## §9 依赖关系

| 依赖 | 类型 | 说明 |
|------|------|------|
| seat_registry.yaml (REG-SEAT-001) | data | 席位档案 SSoT，只读 |
| DS-080 / JOB-076 | data | 龙虎榜明细数据集（上游供数，非代码依赖） |
| pydantic / pyyaml | runtime | 模型+YAML 加载 |

### 9.5 概念重叠声明

| 概念 | 本模块 | 他处 | 边界 |
|------|--------|------|------|
| "谁在买" | 披露席位结构化分析 | MOD-SIG-021 主力行为（分时价量推断） | 数据源正交：披露 vs 推断 |
| 游资接力 | 席位共现结构 | MOD-SIG-033 游资接力情绪（情绪周期） | 维度正交：结构 vs 情绪 |

### 9.6 依赖链风险评级

| 链 | 风险 | 缓解 |
|----|------|------|
| seat_registry 漂移（游资换席位） | 中 | registry 人工维护纪律+matched_registry 标记可监控命中率 |

---

## §10 产出物

| 产出 | 类型 | consumer_min | 消费方 |
|------|------|:---:|------|
| SeatPatternResult | Pydantic 模型 | 1 | daban 类策略（候选） |
| FollowSignal.follow_score/direction | 信号字段 | 1 | L2 买入决策（晋升后） |
| net_buy_ratio/top2_concentration | 特征字段 | 0 | seat_premium 因子（候选） |

---

## §11 集成目标

| 阶段 | 集成 | 状态 |
|------|------|------|
| v0.1 | depgraph design 节点 + 17 测试 + 五登记链 | 本批 |
| v0.2 | strategy/factor 消费方接入 + 维度3/4/6 | 待数据积累 |

---

## §12 需要更新

| 触发 | 更新 |
|------|------|
| seat_registry 席位增删/风格改 | 无需改代码（运行时读档案）；风格白名单变化→SeatPatternConfig.youzi_follow_styles |
| 胜率回填完成 | v0.2 算法接入胜率加权 |

---

## §13 风险

| 风险 | 等级 | 缓解 |
|------|:---:|------|
| AKShare 学术 license 实盘合规 | 中 | SRC-AKSHARE-001 compliance 约束既有登记 |
| 东财反爬致历史回补不全 | 中 | 既有管道策略（3 次跳过） |
| 阈值未经回测（拍脑袋值） | 高 | v0.1 阈值全部来自六维框架公开经验值；v0.2 回测校准前信号仅作参考特征不作独立交易依据 |
| 席位归属漂移 | 中 | §9.6 缓解 |

---

## §14 施工指引

### 14.7 参考实现规格

| 算法 | 规格 |
|------|------|
| A1 识别 | seat_name.strip().lower() 精确→aliases(setdefault 防覆盖)→provider_seat_type→unknown |
| A2 联动 | 买方=net>0 且 buy_rank 非空；top2=rank1+2 净买/Σ买方净买；tag 优先级 relay>grinder>retail_dominated>balanced |
| A3 信号 | 基准50；机构+15/知名游资（白名单风格）+10/量化占比>30% −20/散户占比>30% −15/独食（≥3买方且 top2>70%）−10/力度>10% +10/力度∈(0,5%) −5/relay+5/grinder−10/retail_dominated−5；clamp[0,100]；≥60 long ≤40 avoid |

### 14.8 施工参考卡

| 项 | 值 |
|----|-----|
| 模块 | src/zephyr/signal_ashare/seat_pattern_analyzer.py |
| 测试 | tests/signal_ashare/test_seat_pattern_analyzer.py（17 用例） |
| 验证 | `python -m pytest tests/signal_ashare/test_seat_pattern_analyzer.py -q` 两轮全绿 |

### 14.10 故障与操作

| 故障 | 处置 |
|------|------|
| registry 缺失 warning | 检查 registry_path 配置/文件存在性 |
| matched_registry 命中率骤降 | seat_registry 档案滞后，人工维护 |

### 14.12 并发操作

纯函数无共享状态，线程安全；registry 加载为构造期一次性只读。

---

## §15 容量升级

v0.2 触发条件：①DS-080 积累≥3 个月→胜率回测回填+胜率加权；②消费方（daban/因子）接入→维度3（股价位置，依赖行情域）/维度4（题材，依赖题材域）/维度6（三日连续性，历史窗口聚合）；③阈值回测校准。

---

## §16 决策记录

| # | 决策 | 理由 |
|---|------|------|
| 1 | MVP 只落维度1/2/5，裁剪 3/4/6 | 第一性原理：3/4/6 依赖外部域输入（行情/题材/历史窗口），MVP 不引入跨域依赖 |
| 2 | v0.1 不消费胜率字段 | registry 胜率全 null，消费未回测字段=臆造 |
| 3 | 纯函数模块，不直连 CH | 取数是上游职责；可测试性；与 MOD-SIG-021/025 同构 |
| 4 | 独食判定需 buyer_count≥3 | 2 席买方时 top2 恒 100% 为假阳性（施工实证修正） |
| 5 | 模块落 signal_ashare 包非任务书字面 ashare_signal | depgraph 真源：D_ASHARE_SIGNAL 域物理包=src/zephyr/signal_ashare/（37 节点） |

---

## 术语表

| 术语 | 含义 |
|------|------|
| 龙虎榜 | 沪深交易所每日交易公开信息（涨跌幅/换手/振幅偏离披露买卖前五席位） |
| 席位画像 | 单席位身份（类型/风格）+当日行为（买卖净额/占比） |
| 席位联动 | 同票同日多席位共现结构（谁和谁一起买） |
| 独食 | 买一买二集中度>70%，筹码集中次日砸盘风险 |
| 拉萨系 | 散户集合席位（拉萨金融城/东环路等），接盘风险标志 |

## 已知问题

| # | 问题 | 处置 |
|---|------|------|
| 1 | provider_seat_type 粗分类与 registry 类型词表不完全同构（connect vs northbound） | v0.2 统一词表 |
| 2 | 阈值未回测 | §13 风险3，v0.2 校准 |

## 自检与闭合清单

- [x] 17 测试两轮全绿
- [x] 代码头部十五字段（[MATURITY] design 与 depgraph planned 一致）
- [x] depgraph design 节点已登记（blueprint_id=MOD-SIG-056，物理 node_id 查 depgraph 真源）
- [x] 五登记链（token/capability/translation/depgraph/蓝图）
- [x] ARCH 条目登记

## 成熟度

design（v0.1 代码已实现+测试，depgraph design 态；merge 后统筹重扫转 production）

## 版本演进路线图

| 版本 | 内容 |
|------|------|
| v0.1.0 | MVP 三件套（维度1/2/5） |
| v0.2.0 | 胜率加权+维度3/4/6+阈值回测校准 |

---

## pre_1 Vibe Coding

本模块为 AI 施工产物（AI-SEAT-001，2026-08-18）。

## pre_2 安全删除

删除本模块前 MUST：①确认无消费方（grep SeatPatternAnalyzer）②depgraph --remove-design-node + design-evidence ③五登记链反向清理。

## pre_3 必备链接

- seat_registry：[seat_registry.yaml](file:///d:/ZephyrAlpha/docs/01_policies_and_standards/_registry/catalogs/seat_registry.yaml)
- 候选条目：candidate_module_registry.yaml CAND-SEAT-001
- 数据资产：data_asset_registry.yaml DS-080/JOB-076

## pre_4 已有类似功能

全项目 grep 无席位形态分析代码（CAND-SEAT-001 design_admission.q1 实证 2026-08-14）；MOD-SIG-021/033 为近邻但正交（§9.5）。

## pre_5 涉及的文件范围

| 文件 | 操作 |
|------|------|
| src/zephyr/signal_ashare/seat_pattern_analyzer.py | 新建 |
| tests/signal_ashare/test_seat_pattern_analyzer.py | 新建 |
| docs/03_modules/_domain_signal/seat_pattern_analyzer/blueprint.md | 新建（本文件） |
| capability_canonical_file_registry.yaml / module_translation_registry.yaml / architecture_issue_registry.yaml | 追加登记 |

---

## 1. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 1.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 1.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §1（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


