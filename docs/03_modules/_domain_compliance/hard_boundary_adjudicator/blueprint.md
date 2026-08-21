---
module_id: MOD-CMP-005
title: "硬边界功能裁定门禁蓝图 — 能建/禁建清单 + FeatureGate"
doc_type: blueprint
status: Active
version: "0.1.15"
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
priority: P1
blueprint_level: module
---

# MOD-CMP-005 | Hard Boundary Adjudicator 硬边界功能裁定门禁

> **域**: D_COMPLIANCE | **优先级**: P1 | **safety**: H | **ai_autonomy**: ai_modifiable
> **状态**: design | **版本**: 0.1.0 | **SSoT**: depgraph MOD-CMP-005 (node 8661730)

## 1. 模块定位

47 项功能二元裁定（能建/禁建）清单 + 新功能上线门禁流程（BM-BUY-12）。与 30 号 §5 charter 真红线消歧：本模块管**功能建设权**（某功能能不能建/上线，设计/上线时门禁），不管运行时风控阈值。

依据: `43_compliance_discipline.md` §6

## 2. 不变量 (INVARIANTS)

- 未登记 = PENDING 视同 BLOCK（裁定未决 → 暂缓上线，安全优先）
- FORBIDDEN = BLOCK 并提示重评条件
- 登记表不可读 = Fail-Closed，一切新功能 BLOCK
- 裁定原则逐条过：①法规明令禁止→FORBIDDEN 无例外 ②通道/资金不支持→FORBIDDEN（重评=通道变更）③复杂度不承受→FORBIDDEN/降级（重评=团队/AUM）

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| FeatureGateError | ZA-CMP-0004 | 登记表不存在/解析失败 |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 依赖 | catalogs/feature_adjudication_registry.yaml | REG-FEATURE-ADJ-001 | 裁定清单真源（19 条种子；47 项迁移=开放问题） |
| 依赖 | zephyr.compliance.compliance_log | ComplianceLogger | 门禁校验落 compliance_log |
| 消费 | apply_depgraph.py 登记环节 | FeatureGate.check | 设计态模块登记时校验（43 号 §6.4，非独立审批流程） |

## 5. 核心逻辑

```
门禁流程（§6.3）：提案 → 裁定 → 登记 → 门禁校验
check(feature_name):
  登记表不可读 → BLOCK（Fail-Closed）
  未登记 → BLOCK（PENDING 视同 BLOCK）
  FORBIDDEN → BLOCK + re_review_condition 提示
  BUILDABLE → PASS
```

## 6. 接口

```python
FeatureGate(registry_path=None, logger=None)
.check(feature_name: str) -> FeatureGateResult  # decision PASS|BLOCK
.list_entries() -> list[FeatureEntry]
```

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| 清单用 YAML 登记表不建数据库 | 43 号 §6.2：纯登记+校验，成本低 |
| PENDING 视同 BLOCK | steps JSON degradation 一致：裁定未决→安全优先 |
| 种子 19 条而非 47 条 | 源清单（合规架构.md §10/17-D-COMPLIANCE）不在仓内；15 条 harvest 档案裁定+4 条 43 号明示，全量迁移登记开放问题 |

## 8. 测试计划

tests/compliance/test_hard_boundary_adjudicator.py — 8 用例：能建/禁建/未登记/表缺失/表损坏/清单计数/落日志/真表种子完整性回归。

---

## 9. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status=generated）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 9.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-CMP-005`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-CMP-005` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-CMP-005` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-CMP-005 | MOD-CMP-005 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | stable | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
