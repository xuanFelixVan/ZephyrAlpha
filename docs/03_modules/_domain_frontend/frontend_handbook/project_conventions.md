---
ttl: permanent
doc_type: architecture_view
title: 前端技术手册·项目约定（PC）
owner: ZephyrAlpha-Owner
language: zh
status: active
version: "1.0.0"
date: 2026-08-31
topic: frontend_handbook_project_conventions
scope: frontend
---

# 前端技术手册·项目约定（PC）

> 本册收录 ZephyrAlpha 项目自有的前端约定（overlay 分组/commit 门禁/文件认领/验收纪律）。
> 条目四段式：触发词 → 想做什么 → 内置能否 → 坑 → 正确做法+代码锚点。编号永久稳定不回收。

---

### FEH-PC-001｜K 线标注层 overlay 分组管理

- **触发词**：overlay 分组 / marks / trades / cost / draw / 标注层
- **想做什么**：在 K 线图上同时管理多类标注（量化信号/真实成交/成本线/画线工具）且互不干扰
- **内置能否**：✅ 库支持 groupId，但分组方案是项目自定义
- **坑**：不分组会互相覆盖/误删（关一个开关全没了）；分组名乱起会无法对齐治理
- **正确做法**：固定四组——`marks`（量化买卖点灰框）/ `trades`（真实成交红B绿S）/ `cost`（黄色成本线）/ `draw`（画线工具）；开关按组控显隐
- **代码锚点**：开关逻辑 `src/zephyr/frontend/dashboard/web/core/app1.js#L6147`（klpRefreshMarks）；成本线组 `app1.js#L6229`
- **来源**：KLineChart 集成交接文档 · 2026-08-31

### FEH-PC-002｜前端 commit 必须走 GitCommitGateway

- **触发词**：commit / 提交 / 网关 / git_commit / 裸 commit
- **想做什么**：提交前端代码/文档改动
- **内置能否**：❌ 裸 `git commit` 被禁（pre-commit 全树 stash 会冲掉其他会话暂存）
- **坑**：禁裸 commit、禁 `--no-verify`；受保护路径（AGENTS.md/architecture_model/rules/）需 message 带 `[ARCH-APPROVAL:ISSUE_ID]`；新文件入永久区需 `--allow-promote`；先改后提触发 FOREIGN_CHANGE 需 `--adopt-prior-work`
- **正确做法**：`python scripts/git_commit.py --session <id> --files <逗号分隔> --message-file <utf8文件> --allow-non-worktree [--adopt-prior-work 跨session续作时] [--allow-promote 永久区新文件] [--allow-multi-domain 多域]`
- **代码锚点**：——（流程纪律）；网关 `scripts/git_commit.py`
- **来源**：项目硬约束（project_memory） · 2026-08-31

### FEH-PC-003｜编辑被追踪文档前先 claim_files

- **触发词**：claim / 文件锁 / 回滚 / watchdog / 认领文件
- **想做什么**：修改已被治理追踪的文档/文件
- **内置能否**：✅ 有机制但必须主动用
- **坑**：不 claim 直接改会被 watchdog 回滚或触发 FOREIGN_CHANGE 阻断（"改了被冲掉"）
- **正确做法**：编辑前先 claim（gateway 的 `--adopt-prior-work` 可认领前序未提交变更）；热文件（注册表/AGENTS.md/tracker）用 `safe_write_text`（base-hash CAS+回读校验）
- **代码锚点**：`src/zephyr/shared/io/file_utils.py`（safe_write_text）
- **来源**：项目系统性问题（topic 记忆 2026-08-31） · 2026-08-31

### FEH-PC-004｜前端验收纪律（验收单+截图目检）

- **触发词**：验收 / 截图目检 / 回归 / 图标消失
- **想做什么**：改完 UI 确认没改坏、没回归
- **内置能否**：❌ 前端无自动化测试（Playwright 冒烟待建=四件套第 5 步）
- **坑**：AI 改完 UI 只看代码不看效果——"图标消失"类回归全靠人眼事后发现
- **正确做法**：任何 UI 改动 commit 前：起本地服务 → 截图 → 逐条对验收单（`docs/03_modules/_domain_frontend/acceptance/`，待建）→ 全绿才提交；过渡期"机断"条款由人工/AI 在浏览器控制台手动执行等价断言
- **代码锚点**：验收单目录 `docs/03_modules/_domain_frontend/acceptance/`（待建）
- **来源**：四件套草案 v0.4 §二 · 2026-08-31

### FEH-PC-005｜Playwright 冒烟测试三实证坑

- **触发词**：冒烟测试 / Playwright / wait_for_selector 超时 / 测试导航不生效 / 改动被回拨
- **想做什么**：用 Playwright 给仪表盘写结构断言测试
- **内置能否**：✅（playwright 1.62+chromium 已装；chromium 下载走镜像 `PLAYWRIGHT_DOWNLOAD_HOST=https://cdn.npmmirror.com/binaries/playwright`，官方源国内会卡死零字节）
- **坑**：①`wait_for_selector` 默认等"可见"，但页面 section 默认隐藏（导航才显示）——必须用 `state="attached"`；②测试里改 `location.hash` 不触发页面初始化（应用无 hashchange 监听）——必须调全局 `go('<page>')`；③Edit 工具改完文件可能被 IDE 脏缓冲区回拨（实证：test_dashboard_smoke.py 第一处改动被静默回退）——改后必须进程外核实（Select-String/git diff）
- **正确做法**：见坑①②③；冒烟网真源 `tests/frontend/test_dashboard_smoke.py`（自起 http.server，无需外部服务）
- **代码锚点**：`tests/frontend/test_dashboard_smoke.py`
- **来源**：冒烟网建设实证（3 次失败→3 修复→4/4 绿） · 2026-08-31

---

# FEH-PC-008｜组件拆分铁律（数据源边界 + 单一功能）
- 触发词：组件拆分 / 模块拆分 / 什么时候拆组件 / 自选和持仓 / 数据源边界 / 单一功能
- 想做什么：判断两个功能块该不该拆成独立组件
- 内置能否：无内置，项目自约定（Owner 2026-09-01 裁定铁律）
- 坑：①数据源不同的功能块糊在一起 = 改 A 数据源要测 B 功能，回滚互相牵连（自选列表 vs 持仓列表实证）②功能语义不同但数据源相同的功能块糊在一起 = 改标题样式要测五档挂单，回归爆炸
- 正确做法：
  - **数据源边界判据（最高优先）**：两个功能块数据源不同，必须拆成两个组件。即使视觉相邻、同页面、同模块组，数据源不同 = 独立组件。例：自选列表（localStorage）vs 持仓列表（QMT）必须拆；股票标题（daily_valuation）vs 五档挂单（l2_tick）必须拆
  - **单一功能判据**：一个视觉区块 + 一种交互行为 + 一个功能语义 = 一个组件。即使数据源相同，功能不同也必须拆。例：右栏"股票标题"和"关键数据表"都读 daily_valuation，但功能语义不同 = 独立组件
  - **积木思维**：组件拆到最细 = 任何页面直接引用 = 改 A 页面不影响 B 页面 = 未来加新功能只需在页面做入口
- 反例（禁止）：把"自选+持仓"写成一个"侧边栏组件"（数据源不同）；把"股票标题+关键数据+五档挂单+简介"糊成一个"资料面板组件"（功能语义不同）
- 关联：TRAE-086（前端拆件铁律）· DS-11（设计规范）· stockq 拆分清单 v2
- 来源：Owner 2026-09-01 裁定（数据源边界+单一功能双判据）

---

# FEH-PC-007｜depgraph 新增字段四步铁律（防重建丢值）
- 触发词：depgraph 加字段 / migration / nodes_metadata / 重建器 / generate_project_depgraph / PRODUCTION_PROTECTED_FIELDS
- 想做什么：给 depgraph 的 nodes 表新增业务字段（如前端覆盖三字段 has_frontend/no_frontend_reason/frontend_ref）
- 内置能否：无内置保护，必须人工走四步
- 坑：**generate_project_depgraph 重建运营态时会整表 DELETE+INSERT，新字段不在保护字段清单里 = 全部重置为默认值**。夜战实证：20 个模块的前端覆盖数据一次重建后全丢，回填工作白费
- 正确做法（四步缺一不可）：
  1. **nodes 表加列**：`ALTER TABLE nodes ADD COLUMN IF NOT EXISTS xxx`（migration SQL 脚本，如 `12_add_frontend_coverage_fields.sql`）
  2. **nodes_metadata 保险柜表同步加列**：同脚本里给 metadata 表也加同一列——metadata 是重建前的"保险柜"，存盘时把值暂存于此
  3. **重建器"重建前存档"（UPSERT）登记新列**：在 `generate_project_depgraph.py` 的 Stage 2 UPSERT 语句里，把新列加进 INSERT 字段清单和 ON CONFLICT DO UPDATE SET 清单——否则存档时漏存新列
  4. **重建器"重建后恢复"（UPDATE）登记新列**：在同一文件的 Stage 2 UPDATE 语句里，把新列加进恢复清单——COALESCE(NULLIF(nodes.xxx, ''), nm.xxx, nodes.xxx)。**注意空哨兵**：如果字段默认值是非空字符串（如 has_frontend 默认 'no'），不能直接用 COALESCE，必须用 `CASE WHEN nodes.xxx = 'no' AND nm.xxx <> 'no' THEN nm.xxx ELSE nodes.xxx END`，否则重建默认值会回灌覆盖真值
- 验证：四步做完后，必须完整跑一次 `generate_project_depgraph.py`，然后查 `SELECT count(*) FROM nodes WHERE xxx != 默认值` 确认值存活
- 代码锚点：migration `12_add_frontend_coverage_fields.sql` · `generate_project_depgraph.py` Stage 2 UPSERT (~3680) / UPDATE (~4210)
- 关联：depgraph_schema.py `_DDL_NODES_METADATA`
- 来源：2026-09-01 夜战实证（20 模块值重建丢值 → 四步根治 → 端到端重建验证存活）

---

# FEH-PC-006｜数据源状态灯四态约定（DS-12）
- 触发词：状态灯 / 真源角标 / 数据断线 / klpDataMode / ● 真源
- 想做什么：给数据功能标题行加数据源状态指示
- 内置能否：无内置，项目自约定（DS-12，2026-09-01 Owner 裁定四态不二元）
- 坑：①二元（绿/红）会误判"数据旧但接口通"（归绿=静默放行旧数据=交易大忌；归红=狼来了，真断线时脱敏）②"未启动"（从未取数）≠"断线"（取过但失败），必须分开——灰留给前者
- 正确做法：四态——绿 真源（取数成功+数据在新鲜窗口内）/ 黄 延迟（取到但过期）/ 红 断线（回退演示数据，诚实纪律红色明示不可信）/ 灰 未启动（服务从未响应）；新鲜窗口随 update_frequency（日级 4 天 / 分钟级 30 分钟）
- 代码锚点：app1.js klpDataMode + dataLoader finish 分支（~5980）· 样式 .klp-datamode.dm-*（main.css ~254）
- 关联：DS-12（design.html）· modlib #52 · ACC-F-STOCKQ-KLINE-DATA
- 来源：commit 53bdb4b6 打样 + 2026-09-01 Owner 四态裁定

---

## 修订记录

| 日期 | 版本 | 改动 | 为什么改 |
|---|---|---|---|
| 2026-08-31 | 1.0.0 | 建册，首批 4 条（PC-001~004） | 四件套施工第 1 步；项目自有约定是弱模型最易踩的坑 |
| 2026-08-31 | 1.1.0 | +PC-005 Playwright 冒烟测试三实证坑 | 冒烟网建设 3 失败→3 修复实证 |
| 2026-09-01 | 1.2.0 | +PC-006 数据源状态灯四态约定（DS-12） | Owner 四态裁定（绿/黄/红/灰）成文 |
| 2026-09-01 | 1.3.0 | +PC-007 depgraph 新增字段四步铁律 | 夜战实证：重建器静默重置新字段（20 模块值全丢）→ 根治后重建验证存活 |
| 2026-09-01 | 1.4.0 | +PC-008 组件拆分铁律（数据源边界+单一功能） | Owner 2026-09-01 裁定：数据源不同必拆；功能语义不同必拆 |
