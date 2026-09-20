---
ttl: task_bound
completes_when: 战役 st-vocabconsol-20260918 W8 封账提交后转 archived
---

# W7 修复登记（注入即挖，挖出即修，修完必证红）

## FIX-R8-1 merge_domain B1 兜底子串替换打穿 FK 列（P1，W7 R8 实跑挖出）

- 症状：`apply_depgraph.py --merge-domain D_DATA D_MKT_DATA` step2-17+step1 DELETE 全部
  报 OK 后，B1 `_scan_replace_all_text_columns` 对 `domain_events.source_domain`
  （domains 外键列）做 `%D_DATA%` 子串 REPLACE，把复合历史值 `D_DATA_ENG` 改成
  `D_MKT_DATA_ENG`（domains 无此域）→ 提交时 FK 违例，整笔 merge 回滚，RC=4。
- 根因：兜底扫描的设计意图=清描述性残留（tags/owner/description），但 FK 引用列的
  值域受 `domains` 主键约束，子串替换在结构上就非法；且 merge 的 step1 DELETE 早于
  B1，FK 列被 B1 触碰时旧域行已不存在，二次伤害面更大。
- 治本：B1 扫描经 `pg_constraint` 现查"引用 domains 的全部列"并动态排除（勿手工清单，
  防漂移）；这些列的迁移仍由 step2-17 专职精确处理（等值或受控 LIKE 的 JSON 列）。
- 证红：`tests/governance/test_merge_domain_fk_scan_guard.py`（假 cursor 脚本化）——
  删除守卫谓词后 test_fk_column_not_substring_replaced + total 计数双双变红，
  恢复守卫 3 passed；另真库 dry-run（D_ZZZ_NO_SUCH_DOMAIN）验证 FK 现查 SQL 可用。
- 幸运条款：本缺陷全程被 PG 事务回滚兜住（domains 73 不变、零 orphan），
  BACKUP-PG 快照+事件驱动 regenerate 正常收尾，生产库零污染（已复核）。
- 遗留观察（不阻断）：D_COMPLIANCE 在 DB 是"词表废弃但 domains 行仍在+有依赖"的幽灵域，
  真归并需按预检提示人工合并 edge_count 后走 merge——登记为 DB 侧 advisory 存量债，
  与收敛校验器 10 域 ADVISORY 同族，交 W8 汇总。

## FIX-R5-1（无修复，纯证真）

- R5 三护栏（ghost/dirty/excluded）+ audit 行数自校一次全中，无失明，无代码改动。

## FIX-R6-1 预检不读提交信息致净删门禁预检失明（已治本+钉死）

- 症状：run_preflight 调 spec.check 时不透传 commit_message，REGISTRY-MASS-DELETION
  的 `[allow-mass-deletion:…]` 逃生标记在预检阶段永远读不到=入队前必假红。
- 治本（随 0004 落地）：commit_preflight.py:266 透传 commit_message；
  _ESCAPE_HINTS 更新提示"预检已可读 message"。
- 钉死：新增 tests/governance/rule_bridge/test_commit_preflight_mass_deletion_message.py
  4 例（注册在列/透传/默认空串/提示文案）。红证：临时摘 kwarg→2 例红；还原→13 passed
  且源文件与 index 零差异。grep 证实既有测试对该透传零覆盖（失明为真，非臆断）。

## FIX-R10-1（无修复，纯证真）

- m11 豁免滥用检测链健在：短理由(≥10字红线)活注入即红、无标记基线红、合规长理由绿、
  9/10 字符边界精确；既有 30 例 noqa 测试全绿。无代码改动。
