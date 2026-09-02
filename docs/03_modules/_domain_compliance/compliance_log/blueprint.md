---
module_id: MOD-CMP-010
title: "合规日志落库蓝图 — compliance_log JSONL append-only 证据链"
doc_type: blueprint
status: Active
version: "0.1.21"
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

# MOD-CMP-010 | Compliance Log 合规日志落库

> **域**: D_COMPLIANCE | **优先级**: P1 | **safety**: M | **ai_autonomy**: ai_modifiable
> **状态**: design | **版本**: 0.1.0 | **SSoT**: depgraph MOD-CMP-010 (node 9651495)

## 1. 模块定位

合规域统一落库载体：data/compliance_log/compliance_log.jsonl（结构化 JSONL，append-only）。43 号 §3.2 裁定：MVP 不建独立"合规数据库"，达 3-5 个同类 artifact 再议生成器（01 号规范 §6）。服务 6 个合规检测器（必做清单/严禁/授权审计/功能门禁/操纵检测/报告门禁）。

依据: `43_compliance_discipline.md` §3.2/§7.6（数据流末端：compliance_log → T+1 监管报送 → 审计证据链）

## 2. 不变量 (INVARIANTS)

- append-only：只增不改不删（自证清白证据链语义，§7.3）
- 每行一条合法 JSON（JSONL）
- 落盘失败返回 None + stderr 留痕，绝不阻断交易链路（Fail-Silent 不 Fail-Open）
- 默认锚定 MAIN_REPO_ROOT（仓级业务证据归主仓）；测试注入 tmp 路径隔离

## 3. 错误契约 (ERROR_CONTRACT)

| 错误类 | error_code | 触发条件 |
|--------|-----------|---------|
| ComplianceLogError | ZA-CMP-0010 | 保留（当前 I/O 失败走 None 返回，不抛出） |

## 4. 依赖关系

| 方向 | 模块 | 契约/事件 | 说明 |
|------|------|---------|------|
| 依赖 | zephyr.shared.io.paths | MAIN_REPO_ROOT | 主仓锚定 |
| 消费 | D_COMPLIANCE 6 检测器 | log(event_type, source, payload) | 统一落库 |

## 5. 核心逻辑

```
log(): 线程锁 → mkdir parents → append 一行 JSON（ts/event_type/source/payload，default=str 兜底）
read_all(): 审计/复盘读回（缺文件=空列表）
```

## 6. 接口

```python
ComplianceLogger(path=None)
.log(event_type, source, payload=None, *, now=None) -> ComplianceLogRecord | None
.read_all() -> list[ComplianceLogRecord]
```

## 7. 设计决策

| 决策 | 理由 |
|------|------|
| JSONL 而非 SQLite | 43 号 §3.2 MVP 裁定；JSONL 人可读、git 外置、零依赖 |
| I/O 失败不抛异常 | 日志层不得成为交易链路故障源；阻断语义由各检测器自身承担 |

## 8. 测试计划

tests/compliance/test_compliance_log.py — 6 用例：读写闭环/父目录自建/序列化兜底/I/O 失败 None/缺文件空列表/记录不可变。

---

## 9. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
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
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-CMP-010`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-CMP-010` 的 1 个 file 节点 | production | `extract_depgraph.py --modules MOD-CMP-010` |
| 数据流图 (dataflow) | （无节点） | N/A | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-CMP-010 | MOD-CMP-010 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | N/A | — |
| file_count | 1 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
