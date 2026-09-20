---
ttl: task_bound
completes_when: 原文 2.1 节编辑落地 HEAD 后本备份转 archived
---

# TC-03 步骤0——原文 2.1 节在盘唯一副本补丁备份

> 背景（tc_03 卡 2026-09-21 实测）：原备份目录 `.runtime/tmp/flash_speedup_workbook_backup/`
> 已无声消失（find 全仓零命中），在盘编辑成为全仓唯一副本。本文件由
> st-taskcards-exec-20260921 于 2026-09-21 夜从在盘实态重新导出生成（.md 载体），
> 防 tmp 清扫灭失。输入件 hash 快照见 `.runtime/sessions/` 会话 staging（临时）。

## 坐标与实测

- `src/zephyr/gov_enforcement/rule_bridge/session_worktree.py`：+8 行（`_wt_block_gate_id` 内
  `base_sync_failed` 归因 WORKTREE-BASE-CONFLICT，audit-only）
- `tests/governance/rule_bridge/test_session_worktree_audit_wrapper.py`：+26 行
  （新用例 test_base_sync_failed_audited_as_worktree_base_conflict）
- 盘上 grep WORKTREE-BASE-CONFLICT：码=2、测试=3；HEAD 版两文件均=0
- 与已入 HEAD 的 P1-2 直取治本（370ea4bc25）不冲突（tc_03 卡核验）

## 重放方法

从下方 fence 提取 diff 存为 .patch 后 `git apply <patch>`；落地前必须先完成
裁定 #369 的 CloneGuard merge 治本（X-5），禁 ack 白名单私开（tc_03 卡红线）。

```diff
diff --git a/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py b/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py
index 2a36cfc72a..8f1f32a1a4 100644
--- a/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py
+++ b/src/zephyr/gov_enforcement/rule_bridge/session_worktree.py
@@ -4534,6 +4534,14 @@ def _wt_block_gate_id(result: dict) -> str:
         return "DIRECTORY-CONTRACT"
     if result.get("cross_commit_dep_blocked"):
         return "CROSS-COMMIT-DEP"
+    if result.get("base_sync_failed"):
+        # 堵点本 §2.1 净新病灶残余治本（2026-09-18 st-flashspeed）：commit 路径 base
+        # 新鲜度/落地冲突失败返回 base_sync_failed=True 且无 gate_results（message 如
+        # 「worktree base 过期且 rebase 冲突」「worktree base 对齐阻断」既不匹配「门禁…
+        # 阻断」也无 _VIOLATION 后缀），此前恒落 UNKNOWN。归为伪门禁 WORKTREE-BASE-CONFLICT
+        # ——audit-only 零行为变更（阻断本身正确，仅补观测归因）。merge 路径已带
+        # gate_results=BASE-FRESHNESS-MERGE，直取分支先命中，不受此处影响。
+        return "WORKTREE-BASE-CONFLICT"
     import re as _re
 
     m = _re.search(r"门禁 ([A-Z][A-Z\-]+) 阻断", str(result.get("message", "")))
diff --git a/tests/governance/rule_bridge/test_session_worktree_audit_wrapper.py b/tests/governance/rule_bridge/test_session_worktree_audit_wrapper.py
index 0a88038942..f7307d8e9f 100644
--- a/tests/governance/rule_bridge/test_session_worktree_audit_wrapper.py
+++ b/tests/governance/rule_bridge/test_session_worktree_audit_wrapper.py
@@ -126,6 +126,20 @@ class TestBlockEventAudit:
             evs = _read_events(tmp_path)
             assert evs[-1]["gate_id"] == expected
 
+    def test_base_sync_failed_audited_as_worktree_base_conflict(self, mocked_impl, tmp_path):
+        """堵点本 §2.1 残余 UNKNOWN×26 治本：base 落地冲突阻断端到端落账归因精确（非 UNKNOWN）。"""
+        mocked_impl.result = {
+            "session_id": "s1", "status": "FAILED", "commit_hash": "",
+            "message": "worktree base 过期且 rebase 冲突（3 commits）. 手动处理: git rebase ...",
+            "base_sync_failed": True,
+        }
+        session_worktree_commit("s1", ["a.py"], "m", project_root=tmp_path)
+        evs = _read_events(tmp_path)
+        assert len(evs) == 1
+        assert evs[0]["event"] == "commit_blocked"
+        assert evs[0]["gate_id"] == "WORKTREE-BASE-CONFLICT", "base 冲突此前恒落 UNKNOWN"
+        assert evs[0]["source"] == "worktree_commit"
+
     def test_not_found_not_audited(self, mocked_impl, tmp_path):
         """worktree 不存在（not_found）=用法/环境前置错误，非门禁堵点 → 不记。"""
         mocked_impl.result = {
@@ -209,6 +223,18 @@ class TestPreMergeGateAudit:
         assert sw._wt_block_gate_id({"message": "门禁 CREATE-GUARD 阻断: 无 token"}) == "CREATE-GUARD"
         assert sw._wt_block_gate_id({"message": "FOREIGN_CHANGE_VIOLATION: xxx"}) == "FOREIGN-CHANGE"
         assert sw._wt_block_gate_id({"message": "奇怪的错误"}) == "UNKNOWN"
+        # 堵点本 §2.1 残余病灶治本：commit 路径 base 落地冲突（无 gate_results）此前落 UNKNOWN
+        assert sw._wt_block_gate_id(
+            {"status": "FAILED", "base_sync_failed": True, "message": "worktree base 过期且 rebase 冲突（3 commits）"}
+        ) == "WORKTREE-BASE-CONFLICT"
+        assert sw._wt_block_gate_id(
+            {"status": "FAILED", "base_sync_failed": True, "message": "worktree base 对齐阻断：worktree 有 5 个未提交改动"}
+        ) == "WORKTREE-BASE-CONFLICT"
+        # merge 路径优先级：带 gate_results=BASE-FRESHNESS-MERGE 时直取先命中，不受新标志分支影响
+        assert sw._wt_block_gate_id(
+            {"base_sync_failed": True, "message": "worktree base 过期",
+             "gate_results": [{"gate_id": "BASE-FRESHNESS-MERGE", "detail": "x"}]}
+        ) == "BASE-FRESHNESS-MERGE"
 
     def test_gate_results_direct_attribution(self, mocked_impl, tmp_path):
         """gate_results 直取归因（红蓝 v3 P1-2 治本）：拼接 message 正则失配不再落 UNKNOWN。"""
```
