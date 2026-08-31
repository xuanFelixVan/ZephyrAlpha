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

---

## 修订记录

| 日期 | 版本 | 改动 | 为什么改 |
|---|---|---|---|
| 2026-08-31 | 1.0.0 | 建册，首批 4 条（PC-001~004） | 四件套施工第 1 步；项目自有约定是弱模型最易踩的坑 |
