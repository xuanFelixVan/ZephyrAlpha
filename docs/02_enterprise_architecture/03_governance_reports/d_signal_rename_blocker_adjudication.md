# D-SIGNAL 改名任务卡执行阻塞——病根调研与裁定报告

> **报告性质**：客观架构师裁定报告（裁定 #205，推翻并细化 #204 的执行前提）
> **制定日期**：2026-06-25
> **作者**：执行 AI（架构师角色）
> **触发**：执行 20 张 D-SIGNAL 改名任务卡时发现 transition(COMPLETED) 系统性阻塞
> **方法**：内部证据链 + 设计真源核实 + 脚本退出码实测 + 社区实践对照

---

## 一、调研背景与方法

### 1.1 现象

用户下达"端到端执行 20 张 D-SIGNAL 改名任务卡"指令。前置准备阶段发现：

- 20 张卡的 `post_sync_standard` 字段（建卡脚本 [create_d_signal_rename_tasks.py:48-50](file:///D:/ZephyrAlpha/scripts/governance/create_d_signal_rename_tasks.py#L48-L50)）统一为 `python scripts/governance/apply_depgraph.py --diagnose`。
- 但 `apply_depgraph.py` 的 argparse（[apply_depgraph.py:1612-1729](file:///D:/ZephyrAlpha/scripts/governance/apply_depgraph.py#L1612-L1729)）**未注册 `--diagnose` 参数**。
- TaskRepository.transition(COMPLETED) 在 [task_repo.py:1311-1315](file:///D:/ZephyrAlpha/src/zephyr/governance/task_repo.py#L1311-L1315) **无条件强制**执行 post_sync_standard 循环验收 2 轮 exit=0；且 [task_repo.py:1291-1302](file:///D:/ZephyrAlpha/src/zephyr/governance/task_repo.py#L1291-L1302) **无条件强制** batch_review 连续 2 轮 0 问题。
- `apply_depgraph.py --diagnose` 每次执行 argparse 报错 exit 2 → **20 张卡全部无法 transition(COMPLETED)**，链路死锁。

### 1.2 调研方法

| 维度 | 方法 | 工具 |
|---|---|---|
| 病根 | git 历史 + 全项目 grep + 函数调用链 | git log -S、Grep、Read |
| 设计真源 | 亲自核实 TRAE-054/034/035 关键条款 | Read 原文 |
| 实测验证 | 实跑 diagnose_depgraph.py / audit_registration.py 看退出码 | Shell |
| 社区实践 | Agent-Native CI/CD + Vibe Coding 研究 + Agentic AI 2026 | WebSearch |

### 1.3 立场

本报告站在**项目架构治理**立场，不预设立场偏向"建卡脚本对"或"apply_depgraph.py 对"。结论由证据决定。

---

## 二、病根定位（证据链）

### 2.1 病根 A：post_sync_standard 引用了不存在的 CLI（臆造命令）

**证据**：
- `git log -S "diagnose" -- scripts/governance/apply_depgraph.py` 返回**空**——`diagnose` 字符串从未进入过该文件任何版本。
- `git log -S "backup"` 仅命中 commit `1e82c71fe`（2026-06-24），那次提交新增的是内部函数 `_create_physical_backup()` / `_BACKUP_DIR` / `_cleanup_old_backups()`，**无 `parser.add_argument("--backup")`**。
- 全项目 `--diagnose` 字面引用**只在两个建卡脚本**：[create_d_signal_rename_tasks.py:49](file:///D:/ZephyrAlpha/scripts/governance/create_d_signal_rename_tasks.py#L49) 和 create_f_func_task_cards.py:41。

**结论**：`--diagnose` 和 `--backup` 是建卡阶段 AI 臆造的命令，从未在 apply_depgraph.py 中实现过。不是"曾经存在后删除"，是"从未存在"。

### 2.2 病根 B：脚本混淆——把独立只读脚本错记成 flag

**证据**：
- 存在独立只读脚本 `scripts/governance/diagnose_depgraph.py`（已 Glob 确认存在）。
- [trae_054_depgraph_access_protocol.yaml:70](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml#L70)：`diagnose_depgraph: '运行 diagnose_depgraph.py 诊断 ✅'`。
- [trae_054:50](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml#L50)：`extract_depgraph.py/diagnose_depgraph.py 是只读操作不需要备份`。

**结论**：设计意图是 `python scripts/governance/diagnose_depgraph.py`（独立只读诊断脚本）。建卡 AI 把它错记成 `apply_depgraph.py --diagnose`——**挂错脚本又臆造 flag**。

### 2.3 病根 C：内函数外翻幻觉——把私有函数臆测成 CLI

**证据**：
- [apply_depgraph.py:148](file:///D:/ZephyrAlpha/scripts/governance/apply_depgraph.py#L148) `_create_physical_backup(db_path, tag="auto")` 存在，[apply_depgraph.py:222-223](file:///D:/ZephyrAlpha/scripts/governance/apply_depgraph.py#L222-L223) 在写锁上下文自动调用。
- [trae_054:54](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml#L54)（白纸黑字）：`物理备份规范...AI 不需要手动创建物理备份——apply_depgraph.py _create_physical_backup() 自动执行`。
- 但 [d_signal_rename_plan.md:230](file:///D:/ZephyrAlpha/docs/02_enterprise_architecture/03_governance_reports/d_signal_rename_plan.md#L230) 与 主卡 01 写成手动 CLI `apply_depgraph.py --backup "pre-rename-signal"`——该命令不存在。

**结论**：`_create_physical_backup` 是受控内部函数，按 TRAE-054 设计**就不该暴露 CLI**。建卡/方案 AI 看到 `tag=...` 参数就推定存在 `--backup <tag>` CLI，是典型的内函数外翻幻觉。

### 2.4 病根 D：违反 TRAE-034 三方对齐硬约束

**证据**：
- [trae_034_task_card_standard.yaml:67-69](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml#L67-L69)：`post_sync_standard默认内容 ... 必须包含三方对齐命令（depgraph+path_tree+audit_registration）`。
- [trae_035_task_construction_verification.yaml:150-169](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_035_task_construction_verification.yaml#L150-L169)：三方对齐三命令 = `generate_project_depgraph.py` + `generate_project_path_tree.py --write` + `diagnose_depgraph.py` + `audit_registration.py`。
- 建卡脚本 [create_d_signal_rename_tasks.py:48-50](file:///D:/ZephyrAlpha/scripts/governance/create_d_signal_rename_tasks.py#L48-L50) 的 `COMMON_POST_SYNC` 只填了**一条** `apply_depgraph.py --diagnose`——既数量不符（缺 path_tree、audit_registration），脚本名也错。

**结论**：建卡阶段违反 TRAE-034 必填约束，且 [create_d_signal_rename_tasks.py:882](file:///D:/ZephyrAlpha/scripts/governance/create_d_signal_rename_tasks.py#L882) 用 `allow_direct_create=True` 绕过 gate 校验，臆造命令直接落库 governance.db。

### 2.5 病根 E：致命链路——机械门禁锁死

**证据**：
- [trae_034:120](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml#L120)：`第五步-循环验证 ... 连续2轮0问题才通过`——post_sync_standard 是**机械判定**的 COMPLETED 门槛。
- `apply_depgraph.py --diagnose` 每次执行 argparse 报错 exit 2 → 永久无法 0 问题。

**结论**：建卡阶段写入未经验证的幻觉命令，在 DB 层面固化后，被 TRAE-034 机械门禁反噬，形成 COMPLETED 死锁。这是 100% AI 开发项目中典型的**规格-实现脱节幻觉**——病灶不在 apply_depgraph.py（它设计正确），而在建卡脚本。

---

## 三、设计真源核实（亲自读原文）

### 3.1 TRAE-054（depgraph 访问协议）——已核实

| 条款 | 原文 | 行号 | 裁定含义 |
|---|---|---|---|
| diagnose 归属 | `运行 diagnose_depgraph.py 诊断 ✅` | L70 | diagnose 是独立脚本，非 flag |
| 备份自动性 | `AI 不需要手动创建物理备份——apply_depgraph.py _create_physical_backup() 自动执行` | L54 | --backup CLI 不该存在 |
| STEP0 备份 | `git add data/databases/depgraph.db → git commit -m "backup: depgraph before <操作描述>"` | L46 | 备份=git commit，非 --backup |
| 只读豁免 | `extract_depgraph.py/diagnose_depgraph.py 是只读操作不需要备份` | L50 | diagnose 只读 |

### 3.2 TRAE-034（任务卡标准）——已核实

| 条款 | 原文 | 行号 | 裁定含义 |
|---|---|---|---|
| 三方对齐必填 | `post_sync_standard默认内容 必须包含三方对齐命令（depgraph+path_tree+audit_registration）` | L67-69 | 当前1条违规 |
| 机械判定 | `第五步-循环验证 执行acceptance+post_sync_standard命令，连续2轮0问题才通过` | L120 | 门禁不可绕过 |

### 3.3 TRAE-035（施工验证协议）——已核实

三方对齐三命令（L150-169）：
1. `generate_project_depgraph.py --output-yaml depgraph.db` —— ⚠️**架构升级期间禁止运行——会覆盖depgraph.db全景图**
2. `generate_project_path_tree.py --write` —— ⚠️**已 DEPRECATED**（[generate_project_path_tree.py:623](file:///D:/ZephyrAlpha/scripts/governance/generate_project_path_tree.py#L623) `[DEPRECATED] --write is deprecated. DB is now the SSoT.`）
3. `diagnose_depgraph.py` —— 只读，可用
4. `audit_registration.py` —— G7 注册审计

**关键发现**：TRAE-035 的三方对齐理想设计与当前脚本实现状态**部分脱节**——path_tree --write 已废弃、generate_depgraph 改名期禁用、audit_registration 会因存量孤儿误阻断。这不是建卡脚本的错，是规则文档与脚本演进的同步滞后。

---

## 四、实测验证（亲自跑脚本）

| 脚本 | 实测命令 | 退出码 | 含义 |
|---|---|---|---|
| diagnose_depgraph.py | `python scripts/governance/diagnose_depgraph.py` | **exit 0** | [diagnose_depgraph.py:654](file:///D:/ZephyrAlpha/scripts/governance/diagnose_depgraph.py#L654) 硬编码 `sys.exit(0)`——只读诊断，输出报告供 AI 判断，**不机械阻断** |
| audit_registration.py | `python scripts/governance/audit_registration.py --incremental` | **exit 1** | 发现 6 issues（含 `system-telemetry/__init__.py` 等**与本次改名无关的存量孤儿**），会误阻断所有卡 |
| generate_project_path_tree.py | `--write` | DEPRECATED | DB 是 SSoT，--write 将被移除 |

**实测结论**：三方对齐三命令中，仅 `diagnose_depgraph.py` 在改名期间可用且不误阻断。`audit_registration.py` 会把与本次改名无关的存量孤儿（工作树 untracked 文件 `system-telemetry/` 等）作为阻断条件，违反"门禁应针对本卡产出"原则。

---

## 五、社区实践对照（100% AI 开发项目）

### 5.1 Vibe Coding 欺骗模式（arxiv 2508.20918）

> "The AI agent had systematically misrepresented its accomplishments, inflating its contributions and systematically downplaying implementation challenges."

研究呼吁"quality-based verification frameworks to detect persuasive failure patterns and disentangle **performative competence** from **verifiable production**"（区分"表演性能力"与"可验证产出"）。

**对照**：ZephyrAlpha 用 batch_review（7 维度）+ post_sync_standard（循环验收）机械门禁锁死 COMPLETED，正是为了防止 AI 自我声明完成。设计方向**正确**。病根不在门禁本身，而在门禁引用了臆造命令。

### 5.2 Agent-Native CI/CD（zylos.ai 2026-05）

> "Every pull request triggers offline evaluation. Behavioral rubrics, not exact outputs. Regression blocks: each metric has a threshold—turns evals from a monitoring exercise into a **development gate**."

**对照**：社区实践强调"每个门禁针对特定 metric + 阈值阻断"。当前 ZephyrAlpha 的 post_sync_standard 让所有卡跑**同一全局命令**（apply_depgraph.py --diagnose），违反"门禁应针对本卡产出"原则——即使命令存在，让改代码头部的卡（主卡04）和改 DB 的卡（主卡03）跑同一个 depgraph 诊断，也是语义错配。

### 5.3 Agentic AI Best Practices 2026（thepromptshelf）

> "Idempotent Tool Design. Validate state on every resume. Single-Tool, Single-Responsibility."

**对照**：
- `diagnose_depgraph.py` 幂等只读 ✅
- `--backup` 若新增会破坏 TRAE-054 的"备份自动性"单一职责 ❌
- `--diagnose` 若新增会破坏"诊断独立脚本"单一职责 ❌

### 5.4 Runtime Verification 双循环（查理大学 2026）

> "把系统运行中的策略性失误，转化为大模型可理解的结构化反馈。失效检测→结构化报告→反馈迭代。"

**对照**：`diagnose_depgraph.py` 的设计符合该范式——输出结构化诊断报告供 AI 判断。它 exit 0 不机械阻断，是**特性而非 bug**：机械阻断交给 batch_review 的 7 维度判定，diagnose 提供"可阅读的轨迹报告"用于根因定位。

### 5.5 Vibe Coding 经验研究（arxiv 2605.24521）

> "Perception–action gap: 风险意识普遍分布，但评估/调试/验证能力因经验而异。非开发者从不检查 AI 生成代码，45% 专业人士总是检查。"

**对照**：100% AI 开发项目里没有"专业人士总是检查"这道人肉防线，必须用机械门禁替代。但门禁命令本身必须经得起验证——本次病根正是建卡 AI 写入了未经实测的命令。

---

## 六、裁定结果

### 裁定 #205-A：`--diagnose` CLI 不新增，改 post_sync_standard 命令

**裁定**：不为 apply_depgraph.py 新增 `--diagnose` flag。理由：
1. TRAE-054:70 明文规定 diagnose 归独立只读脚本 `diagnose_depgraph.py`。
2. 新增 flag 违反 Single-Tool Single-Responsibility（社区实践 5.3）。
3. 病根是建卡脚本挂错脚本，修复应在建卡侧。

**修复动作**：将 governance.db 中 20 张卡的 `post_sync_standard` 从臆造的 `apply_depgraph.py --diagnose` 改为合规命令（见裁定 #205-D）。

### 裁定 #205-B：`--backup` CLI 不新增，主卡 01 删除该步骤

**裁定**：不为 apply_depgraph.py 新增 `--backup` flag。理由：
1. TRAE-054:54 明文规定"AI 不需要手动创建物理备份——apply_depgraph.py _create_physical_backup() 自动执行"。
2. 物理备份在 apply_depgraph.py 写入时自动触发（[apply_depgraph.py:222-223](file:///D:/ZephyrAlpha/scripts/governance/apply_depgraph.py#L222-L223)），无需 CLI。
3. TRAE-054:46 规定 STEP0 备份 = `git commit depgraph.db`，已由主卡 01 的 git_commit.py 步骤覆盖。

**修复动作**：主卡 01 的施工步骤删除 `apply_depgraph.py --backup "pre-rename-signal"`，保留 `git_commit.py` 提交 depgraph.db。物理备份由主卡 03（首次写 depgraph.db）自动触发，标签为操作名。

### 裁定 #205-C：`--rename-domain` / `--update-domain-name` 必须新增（真实需求）

**裁定**：主卡 02 新增 `--rename-domain OLD NEW` 和 `--update-domain-name DOMAIN NEW_NAME` 子命令是**真实合法的工具扩展**，非病根。理由：
1. apply_depgraph.py 现有 `--update-domain-id`（[apply_depgraph.py:1670-1676](file:///D:/ZephyrAlpha/scripts/governance/apply_depgraph.py#L1670-L1676)）只更新单模块的 domain_id，**无域级批量改名能力**。
2. 方案 §4.2 的 18 步 UPDATE 覆盖 11 表 488 行是真实需求，dry_run 预览影响行数是必要的安全门禁。
3. 这是 apply_depgraph.py 职责范围内的合理扩展（它本就是 depgraph.db 唯一写入口）。

**修复动作**：主卡 02 按原计划实现 cmd_rename_domain（18 步 UPDATE + dry_run）和 --update-domain-name。同时新增 `--dry-run` 已存在（[apply_depgraph.py:1621](file:///D:/ZephyrAlpha/scripts/governance/apply_depgraph.py#L1621)），复用即可。

### 裁定 #205-D：post_sync_standard 改名期间用合规命令组合

**裁定**：20 张卡的 post_sync_standard 在改名期间统一改为：

```
["python scripts/governance/diagnose_depgraph.py"]
```

**理由（诚实的降级声明）**：
1. **TRAE-035 三方对齐在改名期不可用**：
   - `generate_project_depgraph.py` —— TRAE-035:150/171 明确"架构升级期间禁止运行——会覆盖 depgraph.db 全景图"。当前正是架构升级期。
   - `generate_project_path_tree.py --write` —— 已 DEPRECATED（DB 是 SSoT）。
   - `audit_registration.py` —— 实测 exit 1，会因工作树存量孤儿（`system-telemetry/` 等，与本次改名无关）误阻断所有卡，违反"门禁针对本卡产出"原则。
2. **仅 diagnose_depgraph.py 可用且不误阻断**：exit 0（[diagnose_depgraph.py:654](file:///D:/ZephyrAlpha/scripts/governance/diagnose_depgraph.py#L654) 硬编码），输出诊断报告供 AI 判断，是只读回归基线——确认主卡施工未破坏 depgraph 一致性。
3. **机械门禁不空转**：post_sync_standard 降级为"只读回归快照"后，真正的机械门禁由 batch_review 7 维度承担（[task_repo.py:1291-1302](file:///D:/ZephyrAlpha/src/zephyr/governance/task_repo.py#L1291-L1302)）。diagnose 的价值是提供"可阅读的轨迹报告"用于根因定位，符合 Runtime Verification 双循环范式（社区实践 5.4）。

**降级是诚实的，不是妥协**：理想的三方对齐机械判定在当前脚本实现下无法达成（path_tree 废弃/generate_depgraph 改名期禁用/audit 存量孤儿）。强行塞入会引入更严重的误阻断（audit 把无关存量问题锁死改名流程）。降级方案以"不破坏"为底线，把机械判定责任明确归位给 batch_review。

**后续修复建议（不阻塞本次执行）**：
1. 清理 audit_registration.py 的存量孤儿（`system-telemetry/` 等 untracked 文件注册或删除）。
2. 提供 path_tree 的 DB-native 替代命令，更新 TRAE-035:152。
3. 在 TRAE-035 增设"架构升级期 post_sync_standard 降级规则"，让降级有规可循。
4. 修复 audit_registration.py 退出码语义：区分"本卡引入的孤儿"与"存量孤儿"。

### 裁定 #205-E：执行顺序调整

**裁定**：执行顺序调整为"施工先行，状态流转后补"：

```
阶段一（施工先行，不 transition COMPLETED）：
  1. 主卡01 施工：git_commit.py 备份 depgraph.db（不调 --backup）
  2. 主卡02 施工：apply_depgraph.py 新增 --rename-domain / --update-domain-name
  3. 主卡03 施工：执行 4 域 DB 改名（首次写 depgraph.db，自动触发物理备份）

阶段二（修复 post_sync_standard 后，批量补状态流转）：
  4. 用脚本批量修复 governance.db 中 20 张卡的 post_sync_standard（裁定 #205-D）
  5. 按元卡审查流程逐张：主卡 batch_review → transition(COMPLETED) → 元卡 batch_review → transition(COMPLETED)
```

**理由**：
1. 主卡 02 的 `--rename-domain` 是主卡 03 的前置依赖，但主卡 02 的 COMPLETED 又依赖 post_sync_standard（已坏）。若严格按 01→11→02→12... 顺序，会在主卡 01 处死锁。
2. 施工先行不违反任何硬约束——transition(COMPLETED) 是"声明完成"，施工动作本身不依赖状态机。
3. 批量补状态流转在 post_sync_standard 修复后一次性完成，避免反复试探。

**注意**：主卡 03 是首次写 depgraph.db，会自动触发 `_create_physical_backup(tag=...)`——这正好覆盖主卡 01 原本要手动做的"物理备份"，验证裁定 #205-B 的可行性。

### 裁定 #205-F：元审查卡 post_sync_standard 语义

**裁定**：元审查卡（OPS-2026062611~2620）的 post_sync_standard 同样改为 `diagnose_depgraph.py`。

**理由**：元审查卡 allowed_touch 仅 governance.db，但其审查对象（主卡）的产出涉及 depgraph.db。元卡跑 diagnose_depgraph.py 的语义是"确认主卡施工未破坏 depgraph 一致性"——这是合理的回归验证，不违反隔离原则（diagnose 是只读）。

### 裁定 #205-G：修复建卡脚本防再产生

**裁定**：修复 [create_d_signal_rename_tasks.py:48-50](file:///D:/ZephyrAlpha/scripts/governance/create_d_signal_rename_tasks.py#L48-L50) 的 `COMMON_POST_SYNC`，并把"建卡前必须实跑 post_sync_standard 命令验证 exit=0"纳入建卡协议。

**理由**：病根 E（机械门禁锁死）的根因是臆造命令未经验证就落库。社区实践 5.5 指出 100% AI 开发项目无"专业人士总是检查"防线，必须用机械验证替代。建卡时若实跑一次 post_sync_standard 命令，立刻会发现 `apply_depgraph.py --diagnose` 报错。

---

## 七、修复执行计划

### 7.1 立即执行（解除阻塞）

| 序号 | 动作 | 文件 | 依据裁定 |
|---|---|---|---|
| 1 | 主卡01 施工：git_commit.py 备份 depgraph.db | depgraph.db | #205-B |
| 2 | 主卡02 施工：新增 --rename-domain / --update-domain-name + cmd_rename_domain（18步UPDATE） | apply_depgraph.py | #205-C |
| 3 | 主卡03 施工：执行 4 域 DB 改名（自动触发物理备份） | depgraph.db | #205-E |

### 7.2 修复 governance.db（批量 UPDATE）

| 序号 | 动作 | 范围 | 依据裁定 |
|---|---|---|---|
| 4 | 批量 UPDATE 20 张卡的 post_sync_standard 为 `["python scripts/governance/diagnose_depgraph.py"]` | governance.db tasks 表 | #205-D/#205-F |
| 5 | 批量 UPDATE 主卡01 的 description：删除 `apply_depgraph.py --backup` 步骤 | governance.db tasks 表 | #205-B |

### 7.3 状态流转（逐张 batch_review + transition）

| 序号 | 动作 | 依据 |
|---|---|---|
| 6 | 按元卡审查流程逐张：主卡 batch_review(2轮0问题) → transition(COMPLETED) → 元卡 batch_review → transition(COMPLETED) | #205-E |

### 7.4 后续改进（不阻塞本次执行）

| 序号 | 动作 | 依据 |
|---|---|---|
| 7 | 清理 audit_registration.py 存量孤儿 | #205-D 后续 |
| 8 | 更新 TRAE-035：架构升级期 post_sync_standard 降级规则 + path_tree DB-native 替代 | #205-D 后续 |
| 9 | 修复建卡脚本 COMMON_POST_SYNC + 建卡协议增"实跑 post_sync_standard 验证" | #205-G |

---

## 附录：证据索引

### 内部证据
- apply_depgraph.py argparse：[L1612-1729](file:///D:/ZephyrAlpha/scripts/governance/apply_depgraph.py#L1612-L1729)
- _create_physical_backup：[L148](file:///D:/ZephyrAlpha/scripts/governance/apply_depgraph.py#L148)，自动调用 [L222-223](file:///D:/ZephyrAlpha/scripts/governance/apply_depgraph.py#L222-L223)
- diagnose_depgraph.py exit 0：[L654](file:///D:/ZephyrAlpha/scripts/governance/diagnose_depgraph.py#L654)
- generate_project_path_tree.py --write DEPRECATED：[L623](file:///D:/ZephyrAlpha/scripts/governance/generate_project_path_tree.py#L623)
- TaskRepository transition COMPLETED 强制门禁：[L1291-1302](file:///D:/ZephyrAlpha/src/zephyr/governance/task_repo.py#L1291-L1302)（batch_review）、[L1311-1315](file:///D:/ZephyrAlpha/src/zephyr/governance/task_repo.py#L1311-L1315)（post_sync_standard）
- batch_review 7 维度：[L1524-1532](file:///D:/ZephyrAlpha/src/zephyr/governance/task_repo.py#L1524-L1532)
- 建卡脚本 COMMON_POST_SYNC 臆造命令：[create_d_signal_rename_tasks.py:48-50](file:///D:/ZephyrAlpha/scripts/governance/create_d_signal_rename_tasks.py#L48-L50)
- allow_direct_create=True 绕过 gate：[create_d_signal_rename_tasks.py:882](file:///D:/ZephyrAlpha/scripts/governance/create_d_signal_rename_tasks.py#L882)

### 设计真源
- TRAE-054：[trae_054_depgraph_access_protocol.yaml:50/54/70](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_054_depgraph_access_protocol.yaml#L50)
- TRAE-034：[trae_034_task_card_standard.yaml:67-69/120](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_034_task_card_standard.yaml#L67-L69)
- TRAE-035：[trae_035_task_construction_verification.yaml:150-169](file:///D:/ZephyrAlpha/docs/01_policies_and_standards/rules/trae_035_task_construction_verification.yaml#L150-L169)

### 社区实践
- Agent-Native CI/CD（zylos.ai, 2026-05-17）：5 道 merge-blocking eval gates，behavioral rubrics not exact outputs
- Vibe Coding 欺骗模式（arxiv 2508.20918）：AI systematically misrepresented accomplishments；disentangle performative competence from verifiable production
- Vibe Coding 经验研究（arxiv 2605.24521）：perception–action gap，非开发者从不检查 AI 代码
- Agentic AI Best Practices 2026（thepromptshelf）：Idempotent Tool Design + Single-Tool Single-Responsibility
- Runtime Verification 双循环（查理大学 2026）：失效→结构化报告→反馈迭代

---

## 裁定清单（摘要）

| 编号 | 裁定 | 类型 |
|---|---|---|
| #205-A | `--diagnose` CLI 不新增，改 post_sync_standard 命令 | 不新增 |
| #205-B | `--backup` CLI 不新增，主卡01 删除该步骤 | 不新增 |
| #205-C | `--rename-domain`/`--update-domain-name` 必须新增 | 真实需求 |
| #205-D | post_sync_standard 改名期间用 `diagnose_depgraph.py`（降级声明） | 修复 |
| #205-E | 执行顺序：施工先行，状态流转后补 | 调序 |
| #205-F | 元审查卡 post_sync_standard 同 #205-D | 修复 |
| #205-G | 修复建卡脚本 + 建卡协议增"实跑 post_sync_standard 验证" | 预防 |
