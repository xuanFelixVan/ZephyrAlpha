---
module_id: PLAYBOOK-SEC-001
title: "GitHub Branch Protection Rules 配置指南"
version: "1.0.0"
status: Active
layer: L11
owner: ZephyrAlpha-Owner
created_date: "2026-04-16"
priority: P0
description: "手动配置 GitHub main 分支保护规则，确保 CI 检查为 required（blocking）而非 advisory"
---

# GitHub Branch Protection Rules 配置指南

> **背景（GAP-2）**：评估发现项目有 7 个 GitHub Actions CI 工作流，但无法确认 main 分支是否启用了 Branch Protection。如果没有开启，所有 CI 检查即使失败也无法阻止代码推送到 main，治理链路的最后一公里存在断口。

---

## 一、配置步骤（5 分钟）

### Step 1：打开仓库设置

访问：`https://github.com/fanzi/ZephyrAlpha/settings/branches`

（或者：GitHub 仓库页面 → Settings → Branches）

### Step 2：添加分支规则

点击 **"Add branch ruleset"** 或 **"Add rule"**（取决于 GitHub 版本）。

**规则名称**：`main-protection`
**目标分支**：`main`（精确匹配，Fnmatch: `main`）

### Step 3：启用以下保护选项

| 选项 | 启用 | 说明 |
|------|------|------|
| ✅ Require a pull request before merging | 推荐开启 | 防止直接 push 到 main |
| ✅ Require status checks to pass before merging | **必须开启** | 核心保护 |
| ↳ Require branches to be up to date before merging | 推荐开启 | 防止过期分支合并 |
| ✅ Do not allow bypassing the above settings | **必须开启** | 防止管理员绕过 |

### Step 4：配置 Required Status Checks

在 "Require status checks" 下，搜索并添加以下 CI Job 名称：

**必须设为 Required（阻塞性）：**
```
governance-audit / governance-audit
code-quality / code-quality
永恒索引验证 (Eternal Index Validation) / 验证索引完整性
```

**可选（建议设为 Required）：**
```
version-validation / version-validation
document-quality-check / document-quality-check
```

> **如何找到 Job 名称**：在 GitHub Actions 页面，查看每个 workflow 的 job 名称（`.github/workflows/*.yml` 中 `jobs:` 下的 key）。

### Step 5：保存规则

点击 **"Create"** 或 **"Save changes"**。

---

## 二、验证方法

配置完成后，验证保护是否生效：

```bash
# 尝试直接推送到 main（应该被拒绝）
git checkout main
git commit --allow-empty -m "test: branch protection test"
git push origin main
# 预期结果：ERROR: push declined due to repository rule violations
```

---

## 三、当前 CI 工作流汇总（Required Checks 参考）

| 工作流文件 | Job 名称 | 触发条件 | 建议级别 |
|-----------|---------|---------|---------|
| `governance-audit.yml` | `governance-audit` | push/PR + docs/scripts 变更 | **Required** |
| `code-quality.yml` | `code-quality` | push/PR + src/tests/scripts 变更 | **Required** |
| `eternal-index-validation.yml` | key: `validate-indexes` / display: `验证索引完整性` | push/docs + 每小时 cron | **Required** |
| `version-validation.yml` | `version-validation` | push/PR + 周一 cron | Recommended |
| `document_quality_check.yml` | `document-quality-check` | push/PR + docs/**.md 变更 | Recommended |
| `periodic-audit.yml` | 三个 job | 定时 cron | Optional |
| `document_audit.yml` | 三个 job | push/PR + 定时 | Optional |

---

## 四、完成后更新

配置完成后，在本文件追加验证记录：

```yaml
verification:
  configured_date: "{YYYY-MM-DD}"
  configured_by: "ZephyrAlpha-Owner"
  required_checks:
    - "governance-audit / governance-audit"
    - "code-quality / code-quality"
    - "永恒索引验证 (Eternal Index Validation) / 验证索引完整性"
  test_result: "pass"  # 直接 push 被拒绝
```

并在 `docs/09_AUDIT/STATE/elimination-pipeline-tracker.yaml` 的 `health_check.blockers` 中移除此项（如有）。

---

*此 Playbook 由 ZephyrAlpha Owner 手动执行，完成后归档。*
