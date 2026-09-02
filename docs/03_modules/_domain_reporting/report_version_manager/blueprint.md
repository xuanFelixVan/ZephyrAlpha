---
module_id: MOD-RPT-013
title: "报告版本管理器蓝图 — 版本存储+差异引擎+快照管理+哈希链审计"
doc_type: blueprint
status: Active
version: "0.1.3"
ttl: permanent
layer: L07_reporting
layer_name: reporting
functional_domain: reporting
owner: ZephyrAlpha-Owner
created_by: agent
date: "2026-08-02"
last_updated: "2026-08-02"
priority: P2
blueprint_level: module
responsibility_domain: 
design_maturity: production
build_status: production
---

# MOD-RPT-013 Report Version Manager — 报告版本管理器 蓝图

> **module_id**: MOD-RPT-013 | **域**: D_REPORTING | **层**: L07 报告
> **优先级**: P2 | **成熟度**: production | **对标能力**: C-010(报告归档/审计)
> **SSoT**: depgraph MOD-RPT-013 | **设计真源**: D:\临时工作区\依赖图\10-D-REPORTING-报告域.md §1.3 D-REPORTING-13, §4.3 审计校验, §5.8

## 1. 定位

报告版本管理器——报告域版本化基座。为所有报告(归因/风险/PnL/监管)提供:
版本存储(append-only)+差异引擎(版本间 diff)+快照管理(create/get/list)+哈希链审计
(篡改可检测, Tamper-Evident)。

复用 POS-009/EX-15 的哈希链模式, 满足 §4 审计约束(交易日志≥7年/不可篡改)。
属 A 类基础设施(确定性版本管理), 纯消费层不发布事件(D-RPT-D01)。
**纯基础设施: 不决定报告内容, 只负责"存版本/算差异/验完整性"。**

## 2. 输入 / 输出

| 方向 | 内容 | 契约/事件 |
|------|------|-----------|
| 输入 | report_id (报告逻辑标识) | — |
| 输入 | content (报告内容, JSON 可序列化 dict) | — |
| 输出 | ReportVersion (含哈希链的不可变版本) | — |
| 输出 | VersionDiff (版本间差异) | — |
| 输出 | verify_chain 结果 (bool, 完整性校验) | — |

## 3. 核心规则

### 3.1 版本存储 (Append-Only)

- 每次存储创建新版本, 版本号 per report_id 单调递增 (1, 2, 3, ...)
- 不可变: 已存储版本禁止修改/删除 (append-only, 满足审计要求)
- 阶段1: 内存存储 (dict + list); 阶段2: SQLite 持久化 (见 §4)

### 3.2 哈希链 (Tamper-Evident)

复用 POS-009/EX-15 模式:
```
content_hash = SHA-256(canonical_json(content))     # 内容指纹
record_hash  = SHA-256(version_id + timestamp + report_id
                        + version_number + content_hash + prev_hash)  # 链指纹
prev_hash(v_n) = record_hash(v_{n-1})               # 链接前版本
```
首个版本 prev_hash="" (空串)。任何内容篡改 → content_hash 变 → record_hash 变 →
后续所有 record_hash 失效 → verify_chain 返回 False。

### 3.3 差异引擎

对两个版本的 content (dict) 做键级 diff:
- additions: 新增键 (key → new_value)
- deletions: 删除键 (key → old_value)
- modifications: 修改键 (key → (old_value, new_value))
- has_changes: 三者均空则为 False

### 3.4 快照管理

- store(report_id, content) → ReportVersion (自动版本号 + 哈希链)
- get_version(report_id, version_number) → ReportVersion | None
- get_latest(report_id) → ReportVersion | None
- list_versions(report_id) → list[ReportVersion] (按版本号升序)
- list_reports() → list[str] (所有 report_id)

### 3.5 审计链验证

- verify_chain(report_id) → bool: 遍历版本, 重算 content_hash/record_hash, 比对 prev_hash 链接
- 满足 §4.3: 启动校验/每日校验/按需校验 (调用方控制频率)

## 4. 关键不变量 (INVARIANTS)

- ReportVersion / VersionDiff 为 frozen dataclass (不可变)
- 版本号 per report_id 单调递增, 不复用不回退
- 哈希链: prev_hash(v_n) == record_hash(v_{n-1}) 恒成立 (verify_chain 校验)
- append-only: 已存储版本禁止修改/删除
- content 必须为 JSON 可序列化 dict (canonical_json 用 sort_keys 确保确定性)
- 线程安全: 内部加 Lock 保护版本存储 (多线程 store/get 并发)

## 5. 错误契约

- `InvalidVersionInputError` (ZA-RPT-0002): content 非 dict / 版本号不存在 / diff 版本非法

## 6. 数据模型

```python
@dataclass(frozen=True)
class ReportVersion:
    version_id: str          # UUID
    report_id: str           # 逻辑报告标识
    version_number: int      # per report_id 单调递增
    timestamp: datetime
    content: dict            # JSON 可序列化报告内容
    content_hash: str        # SHA-256(canonical_json(content))
    prev_hash: str           # record_hash(v_{n-1}), 首版本为 ""
    record_hash: str         # SHA-256(链指纹)
    schema_version: str = "1.0"

@dataclass(frozen=True)
class VersionDiff:
    from_version: int
    to_version: int
    additions: dict          # key → new_value
    deletions: dict          # key → old_value
    modifications: dict      # key → (old_value, new_value)
    @property
    def has_changes(self) -> bool: ...
```

## 7. API

```python
class ReportVersionManager:
    def store(self, report_id: str, content: dict) -> ReportVersion: ...
    def get_version(self, report_id: str, version_number: int) -> ReportVersion | None: ...
    def get_latest(self, report_id: str) -> ReportVersion | None: ...
    def list_versions(self, report_id: str) -> list[ReportVersion]: ...
    def list_reports(self) -> list[str]: ...
    def diff(self, report_id: str, from_version: int, to_version: int) -> VersionDiff: ...
    def verify_chain(self, report_id: str) -> bool: ...
```

## 8. 依赖

- `zephyr.shared.foundation.errors` (ZephyrBaseError)
- 标准库: hashlib, json, uuid, datetime, threading
- 消费者: D-REPORTING 各报告模块(归因/风险/PnL/监管报告的版本化归档)
- 设计真源: D-REPORTING §1.3 D-REPORTING-13, §4.3 审计校验, §5.8

## 9. 测试

- `tests/reporting/test_report_version_manager.py`
- 覆盖: 版本存储(单调递增)、哈希链完整性(verify_chain)、差异引擎(add/del/mod/无变化)、
  快照管理(get/list/latest)、append-only不可变、篡改检测(改content→verify失败)、
  多报告隔离、线程安全、边界值(空content/非dict拒绝/版本不存在)

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-RPT-013`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-RPT-013` 的 2 个 file 节点 | production | `extract_depgraph.py --modules MOD-RPT-013` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | active | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Active | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-RPT-013 | MOD-RPT-013 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | production | production | ✅ |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。

---

## 10. 已实现代码完整路径索引

> **AGENTS.md §6.1 蓝图-代码同步强制约定**——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 10.1 测试文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| `tests/reporting/test_report_version_manager.py` | ✅ 已实现 | |

### 10.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §10（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于 `D:\ZephyrAlpha\\`
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下


