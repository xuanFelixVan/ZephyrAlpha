---
module_id: KE-module_blu-3_9__47__git-000
title: 3.9 #47: Git仓库健康监控
category: module_blueprint
---

# 3.9 #47: Git仓库健康监控

3.9 #47: Git仓库健康监控

在 `capacity_slo.yaml` 中新增 git_repo_health 节：
- CAP-015-git-repo-size-mb 指标
- weekly git gc --aggressive
- >50MB文件跟踪+建议LFS
- git操作性能：status/diff耗时基线监控
