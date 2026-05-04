---
module_id: GOV-ARCH-005
title: Phase Transition Protocol / 阶段过渡双门协议
doc_type: protocol
status: active
version: 1.1.0
date: 2026-04-24
layer: cross_layer
owner: ZephyrAlpha-Owner
classification: confidential
language: zh
last_updated: 2026-05-01
created_by: human_plus_agent
summary: 定义 Phase 0-4 之间过渡的"退出-准入"双门协议。每个 Phase 必须同时声明 exit_criteria（DoD）+ next_phase_entry_criteria（前置验证），并由 validate_ssot.py 扩展的 validate_phase_transition.py 自动化校验，防止 Phase 之间偷跑/压栈/漂移。
rule_form: declarative
scope: global
stability: stable
verifiability: automated
depends_on:
  - {target: PS-STD-001, at: "§5.2.1", why: "module_id DOMAIN 注册表"}
valid_from: 2026-04-24
ai_autonomy: human_gated
superseded_by: null
supersedes: null
truth_sources:
  - "模块候选池/系统终局全貌审计/vibe-coding-audit-merged.md §Opus 五 M-02 双门协议"
related_rationale: R72
related_open_questions: []
tags: [architecture, governance, phase-transition, dod, gate-protocol, vibe-coding-2.0]
ttl: permanent
---

# Phase Transition Protocol
# 阶段过渡双门协议

---

## 0. 读者指南

| 章节 | 内容 | 主要读者 |
|------|------|----------|
| §1 | 双门协议的设计动机 | 项目经理、架构师 |
| §2 | 双门定义：exit_criteria + next_phase_entry_criteria | 任务卡作者、Agent |
| §3 | Phase 0 → 1 → 2 → 3 → 4 的具体双门内容 | 项目经理、架构师 |
| §4 | 任务卡 frontmatter schema 扩展 | 任务卡作者 |
| §5 | 自动化校验接口（validate_phase_transition.py）| 开发者 |
| §6 | 人工审核流程（HiL 必须节点）| 用户（个人量化一人团队）|

### 0.2 本文档不是

- ❌ 任务卡的总规划文档 → 见 `模块候选池/开发流程/任务卡/README.md`
- ❌ 具体 Phase 任务清单 → 见 `phase-0-taskbook.md` / `phase-1-taskbook.md` 等
- ❌ SSoT Validator 的实现 → 见 `scripts/governance/validate_ssot.py`（Phase 0 产出）
- ❌ 架构总览 → 见 `vibe-coding-infrastructure-architecture.md`

---

## 1. 设计动机

### 1.1 当前问题

在 vibe-coding-audit-merged.md §Opus §五 M-02 中识别的 Phase 管理漏洞：

1. **单门漂移**：只有 "本 Phase 完成标志"（DoD），没有 "下一 Phase 可启动标志"，导致未准备好就启动下一 Phase
2. **跨 Phase 偷跑**：Agent/用户在 Phase N 未完成时就开始 Phase N+1 任务，产生返工
3. **隐性依赖漂移**：Phase N+1 依赖 Phase N 的某产物，但 DoD 没列入，导致后期发现缺失

### 1.2 双门协议的解决方案

```
 Phase N                  Phase Transition Gate                Phase N+1
 ─────────               ────────────────────────              ─────────

 执行中 ─── DoD ───▶ [ exit_criteria 门 ]                      ────▶
                    │  （本 Phase 产物完整性）│
                    ▼
                 validate_phase_exit.py      ← 自动化校验
                    │
                    ▼
              [ next_phase_entry_criteria 门 ]
              │ （下 Phase 启动前置验证）│
                    ▼
                validate_phase_entry.py      ← 自动化校验
                    │
                    ▼
               HiL 人工审核点                ← 用户点头
                    │
                    ▼
              Phase N+1 启动                 ────▶ 执行中
```

### 1.3 核心原则

| 原则 | 说明 |
|------|------|
| **双门同时声明** | 每个 Phase 必须在 frontmatter 同时声明 `exit_criteria` + `next_phase_entry_criteria` |
| **机器可验证优先** | 每条 criterion 必须能被 `validate_phase_*.py` 自动校验；不可机器验证的标注 `manual: true` |
| **HiL 强制节点** | Phase 过渡必须有用户显式点头（不可跳过）|
| **回滚协议配套** | 每个 Phase 都有 `rollback_snapshot_path`，过渡失败可回退 |
| **零暗门**：next_phase_entry_criteria 必须是 Phase N-1 的 exit_criteria 子集 | 避免"下一 Phase 引入 Phase N-1 没提到的依赖" |

---

## 2. 双门定义

### 2.1 exit_criteria（Phase 退出门）

**定义**：本 Phase 结束时必须同时成立的所有条件。

**格式（frontmatter yaml）**：

```yaml
exit_criteria:
  - id: EXIT-N-01
    description: "SSoT Validator (scripts/governance/validate_ssot.py) 对全仓库执行返回 0 (无 P0 违规)"
    validator: "scripts/governance/validate_ssot.py --phase 0 --check exit"
    machine_verifiable: true
    blocking: true

  - id: EXIT-N-02
    description: "所有 Phase 任务卡的 status 字段为 completed"
    validator: "scripts/governance/validate_phase_exit.py --phase 0"
    machine_verifiable: true
    blocking: true

  - id: EXIT-N-03
    description: "用户验收会议纪要已写入 docs/09_audit/phase-N-acceptance.md"
    machine_verifiable: false
    manual: true
    blocking: true
```

**约束**：

| 字段 | 说明 |
|------|------|
| `id` | 格式 `EXIT-<phase>-<seq>`，全仓库唯一 |
| `description` | 中文描述，≤ 200 字 |
| `validator` | 如果 `machine_verifiable: true` 必填，指向可执行脚本 |
| `machine_verifiable` | 布尔值，默认 true |
| `manual` | 如果 `machine_verifiable: false` 必须为 true |
| `blocking` | 布尔值，默认 true；false 表示"警告但不阻塞"（非 P0 项）|

### 2.2 next_phase_entry_criteria（Phase 准入门）

**定义**：进入下一 Phase 前必须同时成立的所有前置条件。

**格式（frontmatter yaml）**：

```yaml
next_phase_entry_criteria:
  - id: ENTRY-N+1-01
    description: "Phase 0 的所有 exit_criteria 已通过"
    validator: "scripts/governance/validate_phase_exit.py --phase 0"
    references_exit: [EXIT-0-01, EXIT-0-02, EXIT-0-03]
    machine_verifiable: true
    blocking: true

  - id: ENTRY-N+1-02
    description: "Phase 1 任务卡已创建且 status=draft 的任务 ≥ N 张"
    validator: "scripts/governance/validate_phase_entry.py --phase 1"
    machine_verifiable: true
    blocking: true

  - id: ENTRY-N+1-03
    description: "影子快照 _reorg_snapshots/snapshot-phase-0-post/ 已创建"
    validator: "scripts/governance/validate_snapshot.py --label phase-0-post"
    machine_verifiable: true
    blocking: true
```

**约束（最严苛的一条）**：

```
  ⚠️ 零暗门原则：
     next_phase_entry_criteria 中的每一项，要么：
       (a) references_exit 指向 Phase N-1 的某个 EXIT 条目；
       (b) 或者是"准入专属"条目（如创建快照），不能引入新依赖；
     不允许在 ENTRY 中出现 Phase N-1 的 EXIT 没有覆盖的新依赖。
```

这条由 `validate_phase_transition.py --check zero-backdoor` 自动校验。

---

## 3. Phase 0-4 具体双门内容

### 3.1 Phase 0 → Phase 1

#### Phase 0 exit_criteria

| ID | 描述 | 校验方式 |
|----|------|---------|
| EXIT-0-01 | SSoT Validator 实现完成，对仓库执行返回 0 违规 | `scripts/governance/validate_ssot.py --all` |
| EXIT-0-02 | 11 处 SSoT 矛盾（Kimi #7 根因）已全部修复 | `scripts/governance/validate_ssot.py --check conflicts` |
| EXIT-0-03 | `ssot-authority-map.md` 已写入权威路径，无指向老树的链接 | `grep-scan` for `docs/02_ARCHITECTURE/` |
| EXIT-0-04 | B-E 阶段的原子事务 change_log 已完整归档到 `reference-remap-table.yaml` | 人工审核 |
| EXIT-0-05 | Phase 0 验收会议纪要已写入 `docs/09_audit/phase-0-acceptance.md` | 文件存在性 |

#### Phase 1 entry_criteria

| ID | 描述 | 前置 EXIT |
|----|------|----------|
| ENTRY-1-01 | Phase 0 全部 EXIT 通过 | EXIT-0-01~05 |
| ENTRY-1-02 | 影子快照 `_reorg_snapshots/snapshot-phase-0-post/` 已创建 | - |
| ENTRY-1-03 | Phase 1 骨架任务卡 T-1-01 ~ T-1-20 已创建且 status=queued | - |
| ENTRY-1-04 | 5 份服务接口规范的 ADR-0015~0020 全部 status=accepted | - |

### 3.2 Phase 1 → Phase 2

#### Phase 1 exit_criteria

| ID | 描述 | 校验方式 |
|----|------|---------|
| EXIT-1-01 | 5 大服务的 InProcess* 实现全部落地，进程内库形态 | `pytest tests/integration/services/` |
| EXIT-1-02 | 5 大服务的 `protocol.py` 抽象基类全部就位 | `grep Protocol src/zephyr/*/protocol.py` |
| EXIT-1-03 | `bootstrap.py` wiring 完成，依赖注入跑通 | `pytest tests/integration/bootstrap/` |
| EXIT-1-04 | 单元测试覆盖率 ≥ 70% | `pytest --cov=src/zephyr --cov-fail-under=70` |
| EXIT-1-05 | 冷启动 SLO 达标（VMS bootstrap 200 份 < 60s）| 性能基准测试 |

#### Phase 2 entry_criteria

| ID | 描述 | 前置 EXIT |
|----|------|----------|
| ENTRY-2-01 | Phase 1 全部 EXIT 通过 | EXIT-1-01~05 |
| ENTRY-2-02 | 影子快照 `_reorg_snapshots/snapshot-phase-1-post/` 已创建 | - |
| ENTRY-2-03 | Phase 2 骨架完善任务卡已创建 | - |

### 3.3 Phase 2 → Phase 3

#### Phase 2 exit_criteria

| ID | 描述 | 校验方式 |
|----|------|---------|
| EXIT-2-01 | CE 三级压缩回退链（LLM → 规则基 → 截断）全部实现 | 单元测试 |
| EXIT-2-02 | VMS 的 `multi_search()` RRF + `bulk_bootstrap()` 断点续传落地 | 集成测试 |
| EXIT-2-03 | Orc 的幻觉检测 4 条规则全部触发过测试用例 | 单元测试 |
| EXIT-2-04 | FLE 的 13 项 P0 指标 + 8 种异常 + 6 种动作全部落地 | 集成测试 |
| EXIT-2-05 | LSG 的红队语料库 ≥ 150 条，绕过率 ≤ 5% | 专项评估 |
| EXIT-2-06 | 所有 P0 DEGRADE-* 路径 100% 覆盖测试用例 | `pytest tests/degradation/` |

#### Phase 3 entry_criteria

| ID | 描述 | 前置 EXIT |
|----|------|----------|
| ENTRY-3-01 | Phase 2 全部 EXIT 通过 | EXIT-2-01~06 |
| ENTRY-3-02 | 升级触发条件至少一项达成 | 看板 `technology-landscape.yaml::upgrade_watchboard` |
| ENTRY-3-03 | 影子快照 `_reorg_snapshots/snapshot-phase-2-post/` 已创建 | - |
| ENTRY-3-04 | 服务化迁移任务卡 T-3-XX 已创建 | - |

### 3.4 Phase 3 → Phase 4

#### Phase 3 exit_criteria

| ID | 描述 | 校验方式 |
|----|------|---------|
| EXIT-3-01 | 至少一个服务（VMS / Orc）已切到 Remote* 实现，原 Protocol 不变 | `pytest tests/integration/remote/` |
| EXIT-3-02 | HTTP / NATS 通信层的重试 + 超时 + 熔断配置就位 | 混沌测试 |
| EXIT-3-03 | 端到端性能回归测试通过（稳态延迟不劣化 > 20%）| 性能基准测试 |

#### Phase 4 entry_criteria

| ID | 描述 | 前置 EXIT |
|----|------|----------|
| ENTRY-4-01 | Phase 3 全部 EXIT 通过 | EXIT-3-01~03 |
| ENTRY-4-02 | 影子快照 `_reorg_snapshots/snapshot-phase-3-post/` 已创建 | - |
| ENTRY-4-03 | Phase 4 实盘生产任务卡已创建 | - |

### 3.5 Phase 4（无下一 Phase）

Phase 4 是持续运营阶段，无 "下一 Phase"，但仍需定义 `exit_criteria` 作为"稳定态 DoD"：

| ID | 描述 | 校验方式 |
|----|------|---------|
| EXIT-4-01 | OpenTelemetry 全量集成，5 项 SLI/SLO 达标 | 可观测性 dashboard |
| EXIT-4-02 | Agent 健康度 SLO ≥ 99.5% 持续 30 天 | FLE 统计 |
| EXIT-4-03 | LSG 红队语料库 ≥ 500 条，绕过率 ≤ 2% | 季度红队演练 |

---

## 4. 任务卡 frontmatter schema 扩展

### 4.1 每个 Phase taskbook 的 frontmatter 新增字段

```yaml
---
# ... 既有字段 ...

# === Phase Transition Protocol 扩展字段（强制）===
phase: 0                              # 本 Phase 编号（0-4）
phase_name: "治理地基"                # 人类可读名称

exit_criteria:
  - id: EXIT-0-01
    description: "..."
    validator: "..."
    machine_verifiable: true
    blocking: true
  # ... （见 §3 具体内容）

next_phase_entry_criteria:
  - id: ENTRY-1-01
    description: "..."
    validator: "..."
    references_exit: [EXIT-0-01]   # 零暗门原则的追溯字段
    machine_verifiable: true
    blocking: true
  # ... （见 §3 具体内容）

rollback_snapshot_path: "_reorg_snapshots/snapshot-phase-0-post/"
phase_acceptance_doc: "docs/09_audit/phase-0-acceptance.md"
---
```

### 4.2 schema 校验（Phase 0 必须落地）

`scripts/governance/validate_ssot.py` 扩展规则：

```python
# 检查每个 Phase taskbook 必须有双门
def validate_phase_transition_schema(taskbook_path: str) -> list[Violation]:
    violations = []
    frontmatter = parse_frontmatter(taskbook_path)

    if "phase" not in frontmatter:
        violations.append(P0("missing 'phase' field"))

    if "exit_criteria" not in frontmatter or not frontmatter["exit_criteria"]:
        violations.append(P0("missing or empty 'exit_criteria'"))

    # Phase 4 例外：无 next_phase_entry_criteria
    if frontmatter["phase"] < 4:
        if "next_phase_entry_criteria" not in frontmatter:
            violations.append(P0("missing 'next_phase_entry_criteria'"))

    # 零暗门原则校验
    entry_items = frontmatter.get("next_phase_entry_criteria", [])
    for item in entry_items:
        if "references_exit" not in item and not is_entry_exclusive(item):
            violations.append(P0(
                f"ENTRY {item['id']} violates zero-backdoor principle: "
                f"no references_exit and not entry-exclusive"
            ))

    return violations
```

---

## 5. 自动化校验接口

### 5.1 核心脚本

| 脚本 | 职责 | 产出 |
|------|------|------|
| `scripts/governance/validate_phase_exit.py` | 校验 Phase N 的 exit_criteria | 0 = 通过 / 非 0 = 违规数 |
| `scripts/governance/validate_phase_entry.py` | 校验 Phase N+1 的 entry_criteria | 同上 |
| `scripts/governance/validate_phase_transition.py` | 双门综合（exit + entry + snapshot + HiL 标记）| 同上 |
| `scripts/governance/validate_ssot.py` | 扩展 `--check phase_schema` 校验 frontmatter schema | 同上 |

### 5.2 CLI 约定

```bash
# 校验 Phase 0 退出门
python scripts/governance/validate_phase_exit.py --phase 0

# 校验 Phase 1 准入门（会连带校验 Phase 0 退出门）
python scripts/governance/validate_phase_entry.py --phase 1

# 综合校验（推荐 Phase 过渡前跑）
python scripts/governance/validate_phase_transition.py --from 0 --to 1

# 校验所有 Phase 的双门 schema
python scripts/governance/validate_ssot.py --check phase_schema
```

### 5.3 输出格式（JSON lines）

```json
{"level": "P0", "phase": 0, "criterion": "EXIT-0-01", "status": "FAIL",
 "reason": "validate_ssot.py returned 3 violations",
 "remediation": "Fix violations in tasks/T-0-01/ before proceeding."}

{"level": "INFO", "phase": 0, "criterion": "EXIT-0-05", "status": "PASS",
 "evidence": "docs/09_audit/phase-0-acceptance.md exists"}
```

---

## 6. 人工审核流程（HiL 强制节点）

### 6.1 HiL 触发点

每个 Phase 过渡**必须**有一次人工审核，无法跳过：

```
自动校验全绿 ─── 必须 ───▶  HiL 审核会议 ─── 批准 ───▶  启动下一 Phase
                              │
                              ▼
                       产出：phase-N-acceptance.md
                              │
                              ▼
                        包含：
                          - 退出门校验结果摘要
                          - 准入门校验结果摘要
                          - 用户签字（文本格式：已审核，批准进入 Phase N+1）
                          - 日期
                          - 已知风险清单
```

### 6.2 验收文档模板

`docs/09_audit/phase-N-acceptance.md`：

```markdown
---
module_id: PHASE-N-ACCEPTANCE
phase: N
transition_to: N+1
date: 2026-XX-XX
reviewer: ZephyrAlpha-Owner
status: approved
---

# Phase N 验收记录

## 退出门校验结果
- EXIT-N-01: PASS (evidence: ...)
- EXIT-N-02: PASS (evidence: ...)
- ...

## 准入门校验结果
- ENTRY-(N+1)-01: PASS (references: EXIT-N-01)
- ...

## 已知风险与后续行动
- ...

## 用户签字
已审核本 Phase N 的全部产出，批准进入 Phase N+1。

签字：ZephyrAlpha-Owner
日期：2026-XX-XX
```
```

### 6.3 个人量化一人团队的特殊性

虽然是一人团队，HiL 步骤**仍然不跳过**，理由：

1. **强制自检**：签字前会自己复核一遍，避免 Agent 代劳漂移
2. **审计追溯**：未来回看时有清晰的决策记录
3. **风险记录**：已知风险清单强制归档，防止遗忘
4. **Phase 边界可见**：形成明确的"阶段完成"信号

---

## 7. 与既有审计系统的关系

### 7.1 与 SSoT Validator 的关系

`validate_ssot.py`（Phase 0 产出）是 `validate_phase_*.py` 的底层工具：

```
validate_phase_transition.py
  ├── 内部调用 validate_ssot.py --check conflicts  （SSoT 矛盾检测）
  ├── 内部调用 validate_ssot.py --check phase_schema （frontmatter schema 检测）
  └── 独立实现的 criterion 评估器（runner for validator 字段）
```

### 7.2 与 `reorganization-master-plan.md` 的关系

重组阶段（B-F）的 6 个子阶段**不是 Phase 过渡**，是 Phase 0 内部的架构治理动作。Phase 过渡门在 Phase 0 整体结束（即 F 阶段结束）时才首次触发。

---

## 8. 修订记录

| 日期 | 版本 | 作者 | 说明 |
|------|------|------|------|
| 2026-05-01 | 1.1.0 | AI Architect | **目录迁移**：从 `02_enterprise_architecture/target-architecture/` 移至 `01_policies_and_standards/governance/architecture/`，`reference` 类文档按 PS-STD-001 §3.4 规定归入治理目录。 |
| 2026-04-24 | 1.0.0 | opus47_architect | 初版。基于 vibe-coding-audit-merged.md §Opus §五 M-02 "双门协议"建议落地。Phase 0-4 全部双门内容 + validate_phase_*.py 接口规范 + HiL 流程。|
