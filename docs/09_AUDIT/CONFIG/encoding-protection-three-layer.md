---
module_id: AUDIT_CONFIG_ENCODING_PROTECTION_THREE_LAYER
version: '1.0.0'
status: Active
created_date: '2026-04-16'
last_updated: '2026-04-16'
owner: Project Owner
layer: cross_layer
---

# 编码防护三层确认（UTF-8 / 乱码 / 双编辑器）

> **目标**：对齐 LL-002（双编辑器编码损坏）与 LL-007（GBK 归档不可读）的防护要求，
> 在 **pre-commit（本地）**、**CI（远程）**、**每日检查（定时）** 三层形成闭环。

---

## 第一层：Pre-commit（本地门禁）

| 项 | 内容 |
|----|------|
| **配置文件** | [`.pre-commit-config.yaml`](../../../.pre-commit-config.yaml) |
| **钩子 ID** | `doc-guard-pre-commit` |
| **命令** | `python scripts/hooks/doc_guard_pre_commit.py --check staged` |
| **编码检查** | **D-05 编码损坏**：对**暂存区**内 `docs/**/*.md` 执行 `check_encoding()`（无法用 UTF-8 解码或命中乱码模式则阻止提交） |
| **手动全量** | `python scripts/hooks/doc_guard_pre_commit.py --scan-encoding` |
| **验证是否启用** | 仓库根执行 `pre-commit run doc-guard-pre-commit --all-files`（需已 `pre-commit install`） |

**结论**：第一层在 **每次提交** 对已暂存文档生效；`--check staged` 已包含 D-05，**无需**单独再挂一条 `--scan-encoding`（全量扫描留给 CI/定时任务）。

---

## 第二层：CI Workflow（GitHub Actions）

| 项 | 内容 |
|----|------|
| **工作流** | [`.github/workflows/governance-audit.yml`](../../../.github/workflows/governance-audit.yml) |
| **步骤名** | `UTF-8 / 编码一致性全量扫描（D-05）` |
| **命令** | `python scripts/hooks/doc_guard_pre_commit.py --scan-encoding` |
| **触发** | `push`/`pull_request` 且路径包含 `docs/**`、`scripts/**` 等（见 workflow `on.paths`） |

**结论**：第二层在远端对 **全库 `docs/**/*.md`** 做 D-05 全量扫描，与本地 pre-commit 互补（本地只检暂存，CI 检全量）。

---

## 第三层：每日检查（`daily_check.py`）

| 项 | 内容 |
|----|------|
| **脚本** | [`docs/09_AUDIT/AUTOMATION/daily_check.py`](../AUTOMATION/daily_check.py) |
| **行为** | 在原有 YAML/职责/死链占位统计基础上，**调用** `doc_guard_pre_commit.py --scan-encoding`，将 `encoding_scan_exit_code` 与 `encoding_ok` 写入当日 JSON 报告 |
| **产出** | `docs/09_AUDIT/STATE/daily_check_YYYYMMDD.json` |
| **建议调度** | Windows 任务计划 / cron 每日运行（参见 [`periodic-audit-config.md`](periodic-audit-config.md)） |

**结论**：第三层保证**即使未提交**，定时任务仍能发现全库编码回归（与 pre-commit 触发条件解耦）。

---

## 快速自检清单

1. **Pre-commit**：`pre-commit run doc-guard-pre-commit --all-files`  exit 0
2. **CI**：推送含 `docs/` 的 commit，检查 `Governance audit` workflow 中编码步骤通过
3. **Daily**：`python docs/09_AUDIT/AUTOMATION/daily_check.py`，查看生成的 JSON 中 `encoding_ok: true`

---

## 变更历史

| 版本 | 日期 | 说明 |
|------|------|------|
| 1.0.0 | 2026-04-16 | 初始成文，三层与仓库实现对齐 |
