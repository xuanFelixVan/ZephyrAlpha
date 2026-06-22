---
module_id: KE-126
status: active
title: 10.2 Phase 门禁（不可越级）
category: documentation
---

# 10.2 Phase 门禁（不可越级）

10.2 Phase 门禁（不可越级）

**scaffold → experimental 出口门禁**（必须 ALL PASS）：

- [ ] `scripts/hooks/git-secrets-setup.sh` 已部署，所有 commit 必须过检
- [ ] 历史 git 全库 trufflehog 扫描 0 finding
- [ ] SQLite audit.db schema 定稿 + 写入一条测试事件
- [ ] 本视图 `status: active` + 被 `overview.md §5` 引用

**experimental → beta 出口门禁**：

- [ ] LSG 部署 + 红队评估漏拦率 < 5%
- [ ] Agent Sandbox 部署 + 30 天 0 逃逸事件
- [ ] D6 审计 ≥ 5.5/10
- [ ] Secret Leak Weekly Scan 连续 4 周 0 finding

---
