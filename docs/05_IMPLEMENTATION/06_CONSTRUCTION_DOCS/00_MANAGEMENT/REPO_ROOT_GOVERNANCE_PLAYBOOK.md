---
module_id: REPO_ROOT_GOVERNANCE_PLAYBOOK_001
version: 1.0.0
status: Active
created_date: 2026-04-10
last_updated: '2026-04-10'
owner: 仓库 Owner
responsibility:
  - 仓库根目录卫生、误提交与敏感配置的处置口径（与分层治理 R1/R4 衔接）
standard_type: 治理 Playbook
applicable_scope: 仓库根 `ZephyrAlpha/` 下文件与 Git 跟踪边界
---

# 仓库根治理 Playbook（根目录卫生 · 密钥 · 误生成文件）

> **用途**：把「根目录出现怪文件、敏感配置进库、运行时数据进库」时的**机构式处理方式**写成可执行口径；与 [蓝图交付标准](./BLUEPRINT_DELIVERY_STANDARD_INSTITUTIONAL_LITE.md) **§1.5**（R1、R4）及 [任务清单](./BLUEPRINT_PHASE_CLOSURE_TASK_LIST.md) **W2 / W4** 对照。  
> **不替代**：全局文档孤儿/重复仍以 [孤儿与重复 Playbook](../../../09_AUDIT/STANDARDS/DOC_ORPHAN_AND_DUPLICATE_GOVERNANCE_PLAYBOOK.md) 为准。

---

## 1. 仓库根「正常该有什么」（摘要）

- **常见且合理**：`docs/`、`src/`、`tests/`、`scripts/`、`config/`、`tools/`、`notebooks/`、`pyproject.toml`、`README.md`、`requirements*.txt`、`.gitignore`、`.editorconfig`、`.pre-commit-config.yaml`、`.github/`、`.env.example` 及**不含密钥**的 `*.example` 环境模板。  
- **仅本机、一般不进库**：`.venv/`、`.pytest_cache/`、`.audit_cache/`、IDE 工作区目录（如 `.trae/`，以 `.gitignore` 为准）。  
- **数据/日志**：`data/`、`logs/`、`reports/` 等是否进库以 **`.gitignore` + 项目约定** 为准；大文件与密钥**不得**入库。

---

## 2. 三类问题怎么区分（先分类再动手）

| 类型 | 典型迹象 | 处理方式 |
|------|-----------|----------|
| **A. 误生成「垃圾文件名」** | 文件名像半句命令、半句代码（如以 `= [`、`Where-Object`、`subprocess.run(` 片段为名）、或与路径拼接无分隔的乱串 | **从 Git 移除跟踪并删除工作区文件**；**不必**当正式文档归档。 |
| **B. 敏感配置误入库** | `.env`、`.env.qmt` 等含账号口令的文件曾被 `git add` | **`git rm --cached` 停止跟踪**；确保 `.gitignore` 已覆盖；**轮换已暴露凭证**；若仓库曾推送共享，评估 **历史记录清除**（如 `git filter-repo`）或接受风险并仍轮换密钥。 |
| **C. 运行时/交易端数据** | 根下出现以资金账号命名的目录、`down_queue_*` 等队列文件 | **从版本库删除**；在 `.gitignore` 增加对应目录/通配（若模式稳定）；真源数据留在本机或由业务程序管理。 |

---

## 3. 误放在根下的「正式内容」

若审计报告、设计稿等**应属于** `docs/` 下 canonical 树（例如 `docs/05_IMPLEMENTATION/...`），应 **迁移到约定路径** 后再从错误位置删除，并在 commit 说明中写一句「归位 + 删除误路径」，便于追溯。

---

## 4. 与任务清单的挂钩

- **W2（R1）**：根门面、`.gitignore`、密钥不进库 → 本节 **§1～2** 为操作细则。  
- **W4（R4）**：排除层验证 → 本节 **§1** 与 `.gitignore`/CI 一致即可。

---

## 5. 版本记录

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-10 | 首版：根目录分类处置 + 与交付标准 §1.5 / W2 W4 互指 |
