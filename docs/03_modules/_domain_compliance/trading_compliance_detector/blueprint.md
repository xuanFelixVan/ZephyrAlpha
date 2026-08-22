---
module_id: MOD-CMP-007
title: "交易合规检测器蓝图 — 异常交易 2 条 + 市场操纵 4 类"
doc_type: blueprint
status: Active
version: "0.1.19"
ttl: permanent
design_maturity: production
layer: L1_foundation
layer_name: compliance
functional_domain: compliance
responsibility_domain: 
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-15"
last_updated: "2026-08-15"
priority: P0
blueprint_level: module
---

# MOD-CMP-007 | Trading Compliance Detector 交易合规检测器

> **域**: D_COMPLIANCE | **优先级**: P0 | **safety**: H | **ai_autonomy**: ai_modifiable
> **状态**: design | **版本**: 0.1.0 | **SSoT**: depgraph MOD-CMP-007 (node 8661732)

## 1. 模块定位

合规检测层（管"法"）：异常交易行为（拉抬打压/大额成交）+ 市场操纵 4 类（Spoofing/Layering/Wash Trade/尾盘操纵）。检测目标=**自我监控+证据留存**（监管问询可自证"未实施操纵"），检测器嵌入 C-004，输出落 compliance_log 并 T+1 归档。区别于 BM-BUY-08-B（行为纪律，管"人"）。

依据: `43_compliance_discipline.md` §7（BM-BUY-15 补强）

## 2. 不变量 (INVARIANTS)

- 命中一律 Hard Block + 告警
- 检测引擎失效 → Hard Block 拒发任何订单（Fail-Closed）
- 速率/撤单率计数器消费 24 号 §3.7/40 号既有实现，不重复造
- 50μs 时间锁不实现（§7.5 裁定不适用，降为记录性参数）

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| TradingComplianceError | ZA-CMP-0005 | 检测器内部错误 |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 依赖 | zephyr.compliance.compliance_log | ComplianceLogger | 命中落 compliance_log（证据链） |
| 消费 | C-004 风控引擎 | check_* 系列 | Pre-Trade/盘中实时嵌入（43 号 §7.1）——**已接线**（AI-ASM-001，trading_session 逐单检测：大额成交/拉抬打压/尾盘操纵；Spoofing/Layering/WashTrade 由盘中实时流驱动） |
| 协同 | 40 号 CancelRateGuard/price_cage | 计数器消费 | 撤单率/价格笼子真源（§7.6） |
| 协同 | 41 号尾盘执行窗口 | 错峰约束 | 尾盘操纵检测联动（§7.3） |

## 5. 核心逻辑

```
阈值（§7.2/§7.3；ramp/large 为 MVP 初始值待校准）：
RAMP_DUMP: |5min 价格偏离| ≥3% 且我方量占比 >30% → HARD_BLOCK
LARGE_TRADE: 单笔 > 50% 分钟均量 → HARD_BLOCK
SPOOFING: 挂单 >20% 分钟均量且 10s 内撤单，30min 内 ≥3 次 → HARD_BLOCK
LAYERING: 同侧 ≥3 档梯度单且序列撤单率 >80% → HARD_BLOCK
WASH_TRADE: 自成交（买卖同账户）零容忍 → HARD_BLOCK + 立即人工复核
CLOSE_MANIPULATION: 14:57-15:00 申报价偏离收盘前 VWAP >2% 且量占比 >30% → HARD_BLOCK
```

## 6. 接口

```python
TradingComplianceDetector(thresholds=None, logger=None)
.check_ramp_dump(price_change_pct, our_volume_share) -> ManipulationVerdict | None
.check_large_trade(order_qty, minute_avg_volume) -> ManipulationVerdict | None
.check_spoofing(orders: list[ComplianceOrderRecord], minute_avg_volume) -> ManipulationVerdict | None
.check_layering(orders: list[ComplianceOrderRecord]) -> ManipulationVerdict | None
.check_wash_trade(trade: ComplianceTradeRecord) -> ManipulationVerdict | None
.check_close_manipulation(order_price, order_qty, pre_close_vwap, window_total_volume, at_time) -> ManipulationVerdict | None
.run_all(*verdicts) -> list[ManipulationVerdict]  # 聚合过滤，C-004 统一阻断
```

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| 个人低频也要建 | 43 号 §7.3：2026 穿透监管按实控人合并计算；正常改单可能被误认定——检测器同时是自证清白的证据链生成器 |
| 检测函数纯输入输出 | 单账户低频系统，模式识别输入由调用方按窗口预筛，本模块不做流式状态机（MVP 防过度工程） |
| 幌骗 10s 窗口 + 重复 ≥3 次 | 单次快撤=正常改单，防误伤（内部撤单率 ≤15% 远低于官方监控线） |

## 8. 测试计划

tests/compliance/test_trading_compliance_detector.py — 17 用例：六类检测命中/不命中/边界（窗口外/低频/少量/零均量）+聚合+落日志。

---

## 9. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 9.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/compliance/test_compliance_report_registry.py` | ✅ 已实现 | |
| `tests/compliance/test_discipline_must_do_checker.py` | ✅ 已实现 | |
| `tests/compliance/test_discipline_prohibition_checker.py` | ✅ 已实现 | |
| `tests/compliance/test_license_usage_auditor.py` | ✅ 已实现 | |
| `tests/compliance/test_manipulation_stream_driver.py` | ✅ 已实现 | |
| `tests/compliance/test_trading_compliance_detector.py` | ✅ 已实现 | |

### 9.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §9（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-CMP-007`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-CMP-007` 的 8 个 file 节点 | production | `extract_depgraph.py --modules MOD-CMP-007` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-CMP-007 | MOD-CMP-007 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 8 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
