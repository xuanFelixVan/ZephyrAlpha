---
module_id: MOD-GOV-pure_assertion_gate
title: "PURE-ASSERTION Gate 设计文档——纯陈述原则扩范围 + 注册制 gate 治本"
version: "1.0.0"
layer: L1_foundation
depends_on:
  - TRAE-030
  - TRAE-028
tags: [pure_assertion, GOV-DOC-016, commit_gate, design]
ttl: task_bound
completes_when: "PURE-ASSERTION gate 注册并通过 8+10 测试用例；check_pure_assertion.py --full-scan 验证 in-scope 文档 0 违规；AGENTS.md/trae_030/capability_registry/blueprint/onboarding 五处同步完成"
---

# PURE-ASSERTION Gate 设计文档

## 0 背景与目标

### 0.1 问题
项目已有规则 GOV-DOC-016「规则文档纯陈述原则」（`docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml` §gov_doc_016_pure_assertion L533），要求文档只写"现在是什么"不写"过去是什么后来改了"——历史是 git log 的职责。但现状有两个缺口：

1. **适用范围窄**：规则 scope 仅覆盖"规则文档"（`.trae/rules/` + `AGENTS.md`），蓝图/架构文档/模块文档/README 不在覆盖范围。
2. **强制力降级**：原 `_check_pure_assertion` 在 AD-001 阶段3（commit `cde1255c`，2026-06-30）随 12 个 ad-hoc `_check_*` 一起删除，**未迁移到注册制 gate**。现仅靠 `rules_integrity_reconciler`（post-commit，非阻断）+ code review。

### 0.2 目标
- 扩范围：纯陈述原则覆盖所有项目 `.md` 文档（豁免天然历史性文档）
- 治本强制力：注册新 commit gate `PURE-ASSERTION`（in-process，`--no-verify` 绕不过），incremental-only 阻断新增违规
- 清现存：一次性 `--full-scan` 扫描报告现存违规，按文件清理，gate 在清理过程防护不引入新违规

### 0.3 AD-001 病根规避
不"重挂"删掉的 ad-hoc `_check_pure_assertion` 方法（重挂=重蹈 AD-001 病根），而是**注册新的 `GateSpec`**（对标 `pure_shim_gate.py` 模式），符合向内收原则。

---

## 1 架构与范围

### 1.1 组件

| 组件 | 路径 | TTL | 职责 |
|------|------|-----|------|
| SSoT checker | `scripts/governance/d3_metadata/check_pure_assertion.py` | permanent | 6 条 regex + scope 过滤 + 结构区跳过 + 检测逻辑唯一真源；`--ci <files>` 供 gate 调用，`--full-scan` 供一次性审计 |
| Gate 薄壳 | `src/zephyr/gov_enforcement/commit_gates/pure_assertion_gate.py` | permanent | subprocess 调 checker，解析 exit code，fail-open/fail-closed |
| 测试 1 | `tests/governance/commit_gates/test_pure_assertion_gate.py` | permanent | gate 闭包 8 用例 |
| 测试 2 | `tests/governance/d3_metadata/test_check_pure_assertion.py` | permanent | checker 检测逻辑 10+ 用例 |

> **对原计划的微调**：不新建 `scan_pure_assertion_violations.py` (TTL=task_bound)。检测逻辑和 scope 列表已在 `check_pure_assertion.py` 内，再建扫描脚本=重复 scope 定义=漂移温床。改为 checker 内置 `--full-scan` 模式。该脚本 permanent，`--full-scan` 留给未来审计复用。比原计划更向内收。

### 1.2 Gate 检测范围（.md 文件 only）

**INCLUDE**（路径前缀匹配，且文件后缀 `.md`）：
- `.trae/rules/` — IDE 规则入口
- `AGENTS.md`（根）— 项目宪法
- `README.md`（根）— 项目首页
- `docs/01_policies_and_standards/`（**除** `rules/` 子目录）— 政策标准
- `docs/02_enterprise_architecture/`（**除** `architecture_debt_registry.md`）— 架构文档
- `docs/03_modules/` — 模块蓝图
- `docs/08_knowledge/` — 知识库

**EXCLUDE**（即使命中 INCLUDE 也跳过）：
- `docs/_archive/` — 归档区
- `docs/_working/` — 过程文档（允许过渡描述）
- `session_logs/` — 会话日志
- `**/CHANGELOG.md` — 变更日志本质是历史
- `docs/03_governance_reports/` — 审计报告
- `docs/02_enterprise_architecture/architecture_debt_registry.md` — 债务登记
- `docs/01_policies_and_standards/rules/` — YAML 规则定义 + MD companion 含结构性反例，**继续由 `rules_integrity_reconciler` 独立负责**（向内收，不重复实现）

### 1.3 关键设计决策
**gate 只检 `.md` 不检 `.yaml`**。理由：原作者已证明 YAML 规则的 `fail:`/`prohibitions:`/`change_history:` section 是结构性反例（如"prohibitions: 在正文中保留'已废止'标注"——这是禁止做的事的描述，不是真违规），正则无法区分反例与真违规。YAML 规则的纯陈述治理保持由 `rules_integrity_reconciler`（post-commit，结构感知）负责，gate 不越界。

---

## 2 数据流与检测逻辑

### 2.1 Commit-time 数据流

```
git commit
  → GitCommitGateway.commit()
  → registry.check_all() 按 priority 升序
  → PURE-ASSERTION gate (priority=69，紧邻 PURE-SHIM=68)
      _check(gateway, files):
        1. _get_staged_md_files(gateway) — staged added/modified .md 列表 (fail-open)
        2. _filter_scope(md_files) — 按 INCLUDE/EXCLUDE 路径前缀过滤
        3. _run_assertion_checker(in_scope_files, wt_root) — subprocess 调 checker --ci
        4. _parse_assertion_result(result):
             exit 0 → (True, "")          pass
             exit 1 → (False, detail)      硬阻断，detail 含 file:line:pattern
             exit 2 → (True, "")           fail-open + logger.warning (脚本异常)
             None   → (True, "")           fail-open (subprocess 缺失/超时)
```

### 2.2 检测逻辑（check_pure_assertion.py 内，SSoT）

```
对每个 in-scope .md 文件：
  1. 读 staged 内容 (gate --ci 模式由 gate 传入 added 行号) 或磁盘内容 (--full-scan 模式)
  2. 取 added 行号集合 (gate 模式增量；full-scan 模式=所有行)
  3. 逐行扫描，维护两个状态机：
       frontmatter_state: 文件首行是 --- → 进；遇到第二个 --- → 出
       code_block_state:  遇到 ``` 或 ~~~ → toggle
  4. 对每行判定：
       行号 ∉ added_set        → skip (增量检测，不误阻断现存)
       in frontmatter          → skip (YAML frontmatter 不检)
       in code_block           → skip (代码块示例不检，避免误报)
       否则匹配 6 条违规 regex
  5. 命中 → 记录 (file:line_no:pattern_name:line_content)
exit 1 + stderr 输出违规清单；exit 0 无违规
```

### 2.3 6 条违规 regex（从 `cde1255c^` 恢复，原版词表）

| # | Regex | 命中示例 |
|---|-------|---------|
| 1 | `已[废止弃]\w*` | 已废止 / 已废弃 / 已弃用 |
| 2 | `旧[定规]义?[则]?` | 旧定义 / 旧规则 |
| 3 | `之前是.{1,30}现在` | 之前是X现在改为Y |
| 4 | `已被取[代替]` | 已被取代 / 已被替代 |
| 5 | `P[0-9]迁移后` | P2迁移后 |
| 6 | `从.{1,30}迁移(至|到)` | 从X迁移到Y |

### 2.4 结构性反例跳过（避免误报的关键）

| 跳过区 | 判定方式 | 理由 |
|--------|---------|------|
| YAML frontmatter | 首行 `---` 到第二个 `---` | frontmatter 是元数据不是正文 |
| MD 代码块 | ` ``` ` / `~~~` toggle | 代码示例可能展示违规词作为反例 |
| 非 added 行 | 只检 `+` 前缀行 | 增量检测，不检历史 |

---

## 3 错误处理（ERROR_CONTRACT）

**gate `_check` 闭包永不抛异常**——所有异常路径降级：

| 异常路径 | 降级策略 | 理由 |
|---------|---------|------|
| `git diff --cached` 失败 | fail-open `(True, "")` + logger.warning | git 故障是环境异常，不阻断业务 commit |
| `check_pure_assertion.py` 缺失 | fail-open + warning | 检测器缺失不应阻断（对标 PURE-SHIM） |
| subprocess 超时 (60s) | fail-open + warning | 检测器卡死不阻断 |
| subprocess exit 2（脚本异常） | fail-open + warning | 脚本 bug 不阻断业务 |
| subprocess exit 1（检出违规） | **fail-closed** `(False, detail)` | 唯一阻断路径 |
| 文件不可读 | skip 该文件，不阻断 | 单文件故障不影响其他 |

### 3.1 复杂度控制
gate `_check` 闭包拆为模块级辅助函数（对标 `pure_shim_gate.py` 结构）：
- `_get_staged_md_files(gateway) -> list[str]`
- `_filter_scope(md_files, project_root) -> list[str]`
- `_run_assertion_checker(abs_files, wt_root) -> CompletedProcess | None`
- `_parse_assertion_result(result) -> tuple[bool, str]`

每个函数圈复杂度 ≤15。checker 主检测函数拆为：
- `_init_state_machines() -> dict`
- `_is_skippable_line(line_no, added_set, states) -> bool`
- `_match_violations(line_content) -> list[tuple[str, str]]`
- `_check_file(content, added_lines) -> list[str]`

每个 ≤15。

---

## 4 测试

### 4.1 `test_pure_assertion_gate.py`（gate 闭包，8 用例）

| 用例 | 场景 | 期望 |
|------|------|------|
| `test_pass_no_staged_md` | 无 staged .md | pass |
| `test_pass_all_excluded` | staged .md 全在 EXCLUDE 路径 | pass |
| `test_block_added_violation` | added 行含"已废止" | block |
| `test_pass_violation_in_unchanged_line` | 违规在非 added 行 | pass（增量检测） |
| `test_pass_violation_in_code_block` | 违规在 ``` 内 | pass |
| `test_pass_violation_in_frontmatter` | 违规在 frontmatter | pass |
| `test_failopen_subprocess_exit2` | checker exit 2 | fail-open |
| `test_failopen_git_diff_error` | git diff 失败 | fail-open |

### 4.2 `test_check_pure_assertion.py`（SSoT 检测逻辑，10+ 用例）
- 6 条 regex 各 1 命中用例
- frontmatter 跳过用例
- code block 跳过用例
- 增量模式（added 行号集合）vs 全量模式
- scope INCLUDE/EXCLUDE 路径边界用例

---

## 5 同步与登记

| 同步项 | 文件 | 改动 |
|--------|------|------|
| AGENTS.md L381 | `AGENTS.md` L381 | "已废弃，未迁移"→"已迁移到注册制 gate PURE-ASSERTION (priority=69)，检测范围扩到所有 .md 文档（豁免历史性文档）" |
| trae_030 §gov_doc_016 | `docs/01_policies_and_standards/rules/trae_030_doc_numbering_metadata.yaml` §gov_doc_016 L533 | scope 描述从"规则文档"扩到"所有 .md 项目文档（豁免 CHANGELOG/session_logs/_archive/audit/debt_registry）"；change_history v1.1.3→v1.1.4 |
| capability registry | `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml` | 登记 2 新能力：`check_pure_assertion`（SSoT checker）+ `PURE-ASSERTION`（commit gate）+ creation_tokens |
| blueprint gate inventory | `docs/03_modules/_cross_layer/gate_engine/blueprint.md` §0.1 | 补 PURE-ASSERTION 条目 |
| onboarding_detail.md L416 | `.trae/rules/onboarding_detail.md` L416 | 触发表加一行："修改任何 .md 项目文档 → Read trae_030 §gov_doc_016" |

**不需要改**：`gate_registry.yaml`（in-process gate 是代码注册，非声明式）；`directory_contract.yaml`（无新目录）。

---

## 6 一次性清理闭环

```
1. python scripts/governance/d3_metadata/check_pure_assertion.py --full-scan
   → 输出现存违规清单 (file:line:pattern:content)
2. AI 读清单，按文件逐个清理（gate 在每步清理时确保不引入新违规）
3. 清理完成后再跑 --full-scan 验证 0 违规
4. 永诀后患验证：现存清零 + gate 永久阻断新违规
```

`--full-scan` 模式 permanent 保留，供未来审计复用。

---

## 7 实施顺序（供 writing-plans 拆解）

1. 写 `check_pure_assertion.py`（SSoT checker，含 `--ci` + `--full-scan` 双模式）+ 测试
2. 写 `pure_assertion_gate.py`（薄壳 gate）+ 测试
3. 在 `git_commit_gateway.__init__` 注册 `make_pure_assertion_gate()`
4. 跑 `--full-scan`，按清单清理现存违规
5. 验证清理后 0 违规 + gate 测试全过
6. 同步 5 处文档（AGENTS.md / trae_030 / capability_registry / blueprint / onboarding）
7. commit + merge
