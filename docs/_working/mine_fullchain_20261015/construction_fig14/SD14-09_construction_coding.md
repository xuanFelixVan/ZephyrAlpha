---
ttl: task_bound
doc_type: mining_segment
campaign: mine_fullchain_20261015
segment_id: D14-09
figure: fig14 施工升级流（construction_workflow_map）
created: 2026-10-15
ssot: docs/01_policies_and_standards/sop/construction_sop/construction_workflow_policy.md#step-4-施工编码 + 附录 D 锚块
---

# SD14-09 施工编码（policy Step 4）

## 1. 定义

Step 3 对齐通过后触发：按设计备忘伪代码/接口签名/状态机落码。执行要点七件套：蓝图创建（仅新建模块）→scaffold.py+锁协议建文件→路径多维审查（≤150 拆分）→文件头 15 字段锚定→启动方式事件驱动（⚡hook_registry/event_bus，禁 CircadianScheduler/Timer/cron）→多注册表同步（MRS-001~003）→git 调用预算（GitCommandBatcher 批量化，禁循环内 subprocess git）。配套：任务卡系统（33 字段+八指标机械门）、并行原子事务、防幻觉四件套、代码组织（≤300 行）、DB 破坏性三步验证、RunCommand 纯洁性、Symbol 约定。verified_scope=production（骨架 ✅），wiring=partial。

## 2. 六向台账

| 向 | 内容 | 路径证据 |
|---|---|---|
| 输入面 | 定稿设计备忘（Step 1.9 方案挖矿产物）；depgraph planned 登记+对齐干净 | 政策 L360-410；图 rollback_to=D14-02（算法缺失回补文档） |
| 输出面 | 代码文件（含 15 字段文件头）+蓝图+任务卡（可选） | `docs/01_policies_and_standards/rules/trae_047_engineering_file_header.yaml#A_full`（15 字段真源）；`docs/03_modules/template_registry.yaml` |
| SSOT 真源 | trae_056（phase_4~9）/trae_047（文件头）/trae_053（双轨）/trae_064（git 预算）/trae_047+trae_055（容量）/trae_063（数据三步验证）/trae_066（RunCommand）/trae_082（Symbol）等 | `docs/01_policies_and_standards/rules/` 对应册 |
| 代码模块 | `src/zephyr/gov_enforcement/commit_gates/create_guard.py`（module_id=MOD-GATE_ENGINE；a_full 字段集动态读规则 L757 实证）+`scripts/git_guard.py`（L1 止血/L2 治本，危险子命令清单 :90）+`scripts/scaffold.py` | 三件在盘实证 |
| 门禁约束 | 六台 gate 双册全命中（本批 grep 实证）：`BLUEPRINT-FORMAT`/`BLUEPRINT-HEADER`/`GIT-CALL-BUDGET`/`FOLDER-CAPACITY-HARD-LIMIT`/`COMPLEXITY-GUARD`/`CREATE-GUARD`；另 RULE-CLONEGUARD（clone_guard.check_before_write）/TRANSLATION-COVERAGE/新增 .py 登记大白话简介 | 两册+`AGENTS.md` §1 补充铁律 |
| 自动化触发 | 提交期六台 gate（新建路径执法）+pre-commit 通道兜底+git_guard 实时防自伤；启动方式=boot_hooks 注册（`src/zephyr/trading/boot_hooks.py`） | 图 exec_source=gate:CREATE-GUARD |

## 3. 自审闸三态

| 向 | 态 | 依据 |
|---|---|---|
| 输入面 | pass | 方案+登记双前置链闭合（Step 1.9→D14-06→D14-07） |
| 输出面 | pass | 文件头/蓝图产出有 gate 拦格式 |
| SSOT 真源 | pass | 规则册族在册，锚块在册 |
| 代码模块 | pass | create_guard/git_guard/scaffold 三件实证在盘 |
| 门禁约束 | warn | 六台在册且新建路径执法；但"启动方式事件驱动"与"存量修改的字段齐全"两判据零执法面（图 note 原文）；容量口径分三对象（文件/函数/文件夹）不可压一列 |
| 自动化触发 | pass | 提交期+实时防自伤双层 |

## 4. 缺口与建议

- 缺口1：两判据零执法面——启动方式合规（禁 cron/Timer）与存量修改的文件头字段同步。建议：前者可由静态扫描（grep CircadianScheduler/Timer import 于 own-diff）低成本落 gate；后者已在 BLUEPRINT-HEADER 语义邻域，可扩其 own-scope 规则。
- 缺口2（D14-G12 关联）：本段判据部分指向已归档 design_memos 体系（R-11 十二处链接）——见 SD14-04/11/12/14 合并建议。
- 缺口3：政策 Step 4 引用密集（15+ 规则册），本段是全图最重段。建议：capability_cards 渐进披露给一张"Step 4 施工编码速查卡"，降低每次进上下文的检索成本。
