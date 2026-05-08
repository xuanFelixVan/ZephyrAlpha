---
module_id: KE-documentat-7_4-002
title: 7.4 版本化与回滚
category: documentation
---

# 7.4 版本化与回滚

7.4 版本化与回滚

- **Platform** 版本与 Apps / Packages 解耦；以 `platform@major.minor.patch` 发布
- **Apps** 每个独立版本号，Module Federation 引用 `remoteEntry.js?version=X` 固定版本
- **Packages** 走 semver + Changeset，apps 升级前先评估 breaking change
- 回滚策略：CDN 层保留最近 10 个版本静态文件，`/platform?version=X` 查询参数可强制回退
