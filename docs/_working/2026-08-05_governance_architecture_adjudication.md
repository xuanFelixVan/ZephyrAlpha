---
ttl: task_bound
---

# 治理架构裁定与治本施工方案

> **日期**：2026-08-05
> **性质**：架构师客观裁定（非 AI 提议，依据第一性原理 + 项目实测数据）
> **状态**：待用户确认后执行
> **关联**：#ARCH-REGEN-NONIDEMPOTENT-001 / #ARCH-REGEN-CONCURRENCY-001 / #ARCH-REGEN-CASCADE-001

---

## 一、调研发现（事实层，不含评价）

### 1.1 项目规模实测

| 维度 | 实测值 |
|---|---|
| AGENTS.md（AI 必读元规则） | 1,234 行 |
| `scripts/governance/` | 483 文件 / 130,344 行 |
| `src/zephyr/governance/` | 52,710 行 |
| `src/zephyr/gov_enforcement/` | 41,805 行 |
| 治理类代码合计（governance + gov_enforcement + gov_drift + gov_audit + gov_code_quality + gov_rule + data_governance） | **~131,000 行** |
| 交易业务代码合计（trading + risk + position + factor + signal + market_data + backtest + reporting + sell_decision + pf_core + pf_alloc + orchestrator + execution_simulation） | **~75,000 行** |
| pre-commit hooks | 54 |
| reconciliation_registry 中注册的 reconciler | 121 |
| rules YAML | 83 |
| architecture_issue_registry 条目 | 319（P0×14 / P1×133 / P2×139 / P3×28） |
| issue 按类别 | architecture_governance 62 / data_architecture 21 / governance 17 / governance_mechanism_gap 16（治理自身相关 ≈ 95 条，占 30%） |

**关键反差**：治理代码（~131K 行）≈ 交易业务代码（~75K 行）的 1.75 倍。

### 1.2 非收敛循环当前状态

- P0 止血 skip 仍在 [reconciliation_registry.py](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py) L2258-2266（path_tree）与 L6582-6591（domain_doc）**未移除**。
- P1 治本提交 97c77a9c8a 已落地（6 生成器去 `datetime.now()` + SQL `ORDER BY` + `newline="\n"`），但 stopgap 未同步移除 → reconciler 当前**完全停摆**，43 个域文档处于"上次非幂等生成后冻结"状态。
- 未提交变更 99 个：32 个在 `docs/_working/`（工作草稿）、20 个在 `docs/02_enterprise_architecture/`（派生文档）、其余散落。
- `.gitignore` 已部分承认派生产物不入库原则（`*.generated.md`、`_zoomable_html/`、`generated/`），但 **73 个域文档本体仍在库**。

### 1.3 三条 ARCH-REGEN 裁定的关系（实测）

- `#ARCH-REGEN-CONCURRENCY-001`：并发互斥（filelock drop-not-queue）— 已完成
- `#ARCH-REGEN-CASCADE-001`：worker 内级联截断（env 标志）— 已完成
- `#ARCH-REGEN-NONIDEMPOTENT-001`：生成器输出非确定性 — P1 治本进行中

三者治的是同一个反馈系统的三个症状，**根因未消**：见下文。

---

## 二、第一性原理分析

### 2.1 "100% AI 开发"的真实约束

AI session 的本质特征：(a) 跨会话无长期记忆；(b) 高幻觉率；(c) 倾向复制粘贴与预防性扩展；(d) 对隐式约定不敏感。项目用规则/门禁/reconciler 补偿这些特征——这是合理的起点。

但补偿层本身**也是 AI 写的**，具有完全相同的失败模式。这就引入了**反身性**：治理层的 bug 与业务层的 bug 同分布，但治理层 bug 的影响面是全局的。

### 2.2 治理层的失稳机制（正反馈）

观察 319 条 issue 的演化轨迹：每次治理失败 → 加一个 reconciler/gate 修复 → 新 reconciler 引入新失败面 → 再加 gate 修复 → ……。这是**正反馈**：治理失败 → 治理增多 → 治理面更大 → 更多失败机会。

实证：
- CONCURRENCY + CASCADE + NONIDEMPOTENT 三个 issue 都是 reconciler 自身的失败
- `dead_public_wrapper_reconciler` 用来检测 AI 预防性公共化——但该 reconciler 本身就是 AI 写的，需要另一个 gate 来验证它没有死代码
- P0 stopgap 里有 `TODO(P1 治本后移除本 skip)`——这个 TODO 本身需要人工记得执行，没有任何机制保证

### 2.3 非收敛循环的根因（第一性）

reconciler 是一个**反馈控制系统**。控制论要求闭环系统**有界且负反馈**才能稳定。当前架构违反两条：

**违反有界**：派生产物（43 域文档 + 项目树）被 git 跟踪。派生产物 = f(DB, 生成器代码, 环境)。任一输入的非确定性（时间戳/排序/换行符）→ 输出 diff → auto-commit → 触发下一次 reconciler → 再 diff。**只要派生产物在库里，非收敛是数学必然，不是 bug。**

**违反负反馈**：reconciler 的 `action="commit"` 会**自动提交**，等同于反馈控制器能自己改设定值。控制系统能改设定值 = 失稳。

CONCURRENCY/CASCADE/NONIDEMPOTENT 是在补偿这两条违反，但只要派生产物在库 + auto-commit 存在，补偿永无止境。

### 2.4 元问题：治理预算无上限

319 条 issue、54 gate、121 reconciler、83 rules、1234 行 AGENTS.md——**没有任何机制限制治理本身的规模**。每个新问题默认加新 gate，从不退役旧 gate。AI 必读的元规则已超过 1200 行，本身成为 AI 幻觉与遗忘的温床（AGENTS.md 卷首语提示 AI "全读完再开工"，但 1234 行 + 83 个 rules YAML 在单 session 内不可能真正内化）。

### 2.5 反身性的数学表达

设业务复杂度 B，治理复杂度 G。AI 失败率 p 随 B 线性上升，随 G 下降（治理有效性）。但 G 本身由 AI 维护，G 的 bug 率随 G 线性上升。系统总失败率：

> F(B, G) = p·B·(1 - q·G) + r·G

对 G 求最优：G* = (p·B·q - 1) / (2·r·q)。**当 G > G* 时，加治理反而增加总失败率**。当前 G ≈ 1.75B，已远超任何合理 G* 估计。这是"治理越多越不稳"的数学根据。

---

## 三、裁定结果

### 3.1 战术裁定（#ARCH-REGEN-NONIDEMPOTENT-001 本身）

**裁定**：P1 治本方案（去 datetime.now + ORDER BY + newline=\n + 门禁）**正确且必要**，但**不充分**。当前 stopgap 未移除属执行遗漏，必须补齐。

但即便 P1 全部完成，**非收敛类问题必然复发**，因为派生产物仍在库 + auto-commit 仍存在。NONIDEMPOTENT 只是让"单次生成"幂等，无法保证"跨环境/跨 PostgreSQL 版本/跨 Python 版本"幂等——任何 DB 升级或生成器逻辑变更都会再次触发循环。

### 3.2 战略裁定（元层级，本次新增）

**裁定 #ARCH-GOV-BUDGET-001（新）**：治理架构已跨过复杂度阈值，进入"加治理=加不稳定"区间。需结构性瘦身，禁止再加同类型治理。

**三条不变量**（后续所有治理决策必须满足）：

- **I-GOV-1（派生产物离库）**：凡可由 DB/源码/YAML 经生成器重现的文档，**禁止入 git**。源真源已跟踪，派生产物是构建产物。
- **I-GOV-2（reconciler 无写权）**：reconciler 只允许 `warn`/`skip`/`fix-in-place-without-commit`，**禁止 `action="commit"`**。auto-commit 是失稳原语，从 reconciler 词汇表删除。
- **I-GOV-3（治理预算硬上限）**：pre-commit gate ≤ 54（当前值，冻结）、reconciler ≤ 121（冻结）、AGENTS.md ≤ 1234 行（冻结）。新增必须等量退役。

### 3.3 关于"100% AI 开发"的根本立场

100% AI 开发不是"无限加规则让 AI 不犯错"的理由，恰恰相反——AI 的上下文容量是有限的，**治理面越大，AI 越无法内化，犯错率越高**。正确的方向是**减少 AI 需要理解的面**，而非增加。本项目已出现"治理复杂度 > 业务复杂度"的倒挂，这是架构级别的高利贷，必须还本。

---

## 四、治本施工方案（分阶段，全方案授权执行）

### Phase 1：当务之急（本会话完成，~1 小时）

**目标**：让非收敛循环物理停止，stopgap 合规移除。

| 步骤 | 操作 | 文件 |
|---|---|---|
| 1.1 | 移除 path_tree P0 skip（L2258-2266） | [reconciliation_registry.py](file:///d:/ZephyrAlpha/src/zephyr/governance/audit/reconciliation_registry.py) |
| 1.2 | 移除 domain_doc P0 skip（L6582-6591） | 同上 |
| 1.3 | 注册 `gate-generator-no-realtime-time` 到 pre-commit | [.pre-commit-config.yaml](file:///d:/ZephyrAlpha/.pre-commit-config.yaml) |
| 1.4 | 手动跑一次 path_tree + domain_doc 生成器，验证输出幂等（连跑两次 diff 为空） | 验证 |
| 1.5 | 提交 43 个域文档的"最终幂等版本"一次性 clean 提交 | git |
| 1.6 | 升级 AGENTS.md §11.1.1 检测条款：从手工 Select-String 升级为"pre-commit 硬阻断" | [AGENTS.md](file:///d:/ZephyrAlpha/AGENTS.md) |

**验收**：连续两次 commit 后 `git status` 在派生文档目录下为空。

### Phase 2：结构性止血（1-2 会话，治本）

**目标**：落实 I-GOV-1，派生产物离库。这一步**单独消灭整个非收敛问题类**。

| 步骤 | 操作 |
|---|---|
| 2.1 | `.gitignore` 新增：`docs/02_enterprise_architecture/02_domain_architecture_docs/*.md`、`docs/02_enterprise_architecture/01_global_architecture_diagram/full_project_tree_*.md` |
| 2.2 | `git rm --cached` 73 个域文档 + 项目树文件（保留磁盘文件） |
| 2.3 | 新增 `scripts/serve_docs.py`：本地 HTTP 服务 + 按需重生成（已有 `serve_docs_http.bat` 雏形） |
| 2.4 | 新增 gate `GATE-NO-COMMIT-DERIVED`：阻断对派生产物目录的 `git add`（防 AI 误重新跟踪） |
| 2.5 | reconciler 调整：path_tree / domain_doc reconciler 改为 `action="warn"`（提示"派生产物已离库，请本地跑 serve_docs.py 查看"），不再 auto-commit |
| 2.6 | AGENTS.md 新增 §11.1.4：派生产物离库原则 + `serve_docs.py` 使用方式 |

**验收**：派生产物目录在 `git status` 中永久消失；reconciler 跑后无 diff。

### Phase 3：治理预算冻结（1 会话）

**目标**：落实 I-GOV-3，给治理面设硬上限。

| 步骤 | 操作 |
|---|---|
| 3.1 | issue registry 三角化：P2/P3 已 resolved > 30 天 → 归档到 `_archive/`（从 319 降到 ~150 活跃） |
| 3.2 | 新增 gate `GATE-GOV-BUDGET`：统计 `.pre-commit-config.yaml` hook 数 / `reconciliation_registry.py` 中 `ReconcilerSpec(` 数 / AGENTS.md 行数，超上限阻断 |
| 3.3 | AGENTS.md 拆分：§1-9（核心铁律，冻结 ≤ 500 行）+ §10+（变更日志，append-only） |
| 3.4 | rules YAML 审计：83 个中识别已废弃/被覆盖的，归档 |

**验收**：`GATE-GOV-BUDGET` 在 CI 跑通；AGENTS.md 核心段 ≤ 500 行。

### Phase 4：reconciler 语义改革（长期，1-2 会话）

**目标**：落实 I-GOV-2，从机制上消灭失稳原语。

| 步骤 | 操作 |
|---|---|
| 4.1 | `ReconcileResult.action` 枚举收敛为 `{warn, skip, fix-in-place}`，删除 `commit` |
| 4.2 | 全量扫描 121 个 reconciler，将所有 `action="commit"` 改为 `fix-in-place`（写文件但不 commit）+ `warn`（提示用户手动 commit） |
| 4.3 | 新增显式命令 `python scripts/governance/commit_derived.py`：用户主动跑，把 fix-in-place 的产物一次性提交 |
| 4.4 | 文档：reconciler 是"检测器+修复器"，不是"提交器"。提交权回到用户 |

**验收**：grep `action="commit"` 在 reconciliation_registry.py 返回 0 匹配。

### Phase 5（可选，长期）：业务/治理比例回归

**目标**：把治理/业务代码比从 1.75 降到 < 0.5。

- 治理代码审计：131K 行中识别可合并/可删的（如 121 reconciler 中重复模式抽象为基类）
- 这一步不在本次授权范围，作为长期方向记录

---

## 五、风险与权衡

| 风险 | 缓解 |
|---|---|
| Phase 2 派生产物离库后，CI 中无法直接看架构文档 | `serve_docs.py` + CI artifact 上传生成产物（不入库但可下载） |
| Phase 4 移除 auto-commit 后，派生产物可能长期过时 | boot_hooks 已有 mtime 对比兜底；新增 `make sync` 提示 |
| Phase 3 治理预算冻结可能阻碍必要的新治理 | 退役机制保证：新 gate 必须等量退役旧 gate，倒逼合并 |
| 100% AI 开发下，AI 可能绕过 gate | 现有 GitCommitGateway 路径已覆盖；`--no-verify` 由 reconciler 兜底（保留） |

---

## 六、执行顺序与依赖

```
Phase 1（必做，立即） ──► Phase 2（治本核心） ──► Phase 3（预算）
                                                      │
                                                      ▼
                                                  Phase 4（语义改革）
                                                      │
                                                      ▼
                                                  Phase 5（长期比例回归，可选）
```

Phase 1 是 Phase 2 的前置（先让系统稳定，再改架构）。Phase 3/4 可并行。Phase 2 完成后非收敛类问题物理消失，是最高 ROI 的一步。

---

## 七、与现有裁定的关系

- **不推翻** #ARCH-REGEN-CONCURRENCY-001 / CASCADE-001 / NONIDEMPOTENT-001：三者作为战术补丁保留
- **升级** NONIDEMPOTENT-001：从"修生成器幂等"升级为"派生产物离库 + reconciler 无写权"——治本层级提升一阶
- **新增** #ARCH-GOV-BUDGET-001（本裁定）
- **不冲突** AGENTS.md §11.1.1：时间戳约定保留，但检测条款升级为 pre-commit 硬阻断

---

## 八、待用户确认

1. 是否授权按 Phase 1 → Phase 2 → Phase 3 → Phase 4 顺序执行？
2. Phase 2 派生产物离库涉及 `git rm --cached` 73 个文件（保留磁盘），是否确认？
3. Phase 3 AGENTS.md 拆分核心段 ≤ 500 行，是否接受核心段缩编？
4. Phase 4 reconciler 移除 auto-commit 权，改为用户主动 `commit_derived.py`，是否接受工作流变更？
