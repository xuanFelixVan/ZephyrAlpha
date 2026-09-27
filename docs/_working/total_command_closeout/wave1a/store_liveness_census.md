---
ttl: task_bound
completes_when: 本役案卷已在落地面复跑并逐条附命令原文
---

<!-- 本表由 scripts/governance/wave1a/store_liveness_probe.py 机生，禁手改（重跑覆盖） -->
<!-- generated_at=2026-09-26 20:36:49 -->

| 库（rel path） | 字节数 | mtime | .py 引用数（带路径真指针数） | 真实消费者数 | 规则册指向数 | 规则册样例 | 活替代（同 stem 最大件） | 共现后继（同行点名） | 三态建议 | 判据 |
|---|---|---|---|---|---|---|---|---|---|---|
| `data/databases/depgraph.db` | 0 | 2026-07-20 09:26 | 31（11） | 4 | 0 | 无 | 无 | `governance.db` | **repoint** | 4 个真实消费者 + 存在活替代/共现后继 `governance.db` ⇒ 改指活库 |
| `data/databases/integrator_progress.db` | 0 | 2026-07-24 02:38 | 1（0） | 1 | 0 | 无 | data/integrator_progress.db (37,003,264B @2026-09-26 20:15) | 无 | **repoint** | 1 个真实消费者 + 存在活替代/共现后继 `data/integrator_progress.db` ⇒ 改指活库 |
| `data/databases/progress.db` | 0 | 2026-07-24 14:03 | 1（0） | 1 | 0 | 无 | 无 | `integrator_progress.db` | **repoint** | 1 个真实消费者 + 存在活替代/共现后继 `integrator_progress.db` ⇒ 改指活库 |
| `data/databases/scheduler_progress.db` | 0 | 2026-08-14 07:15 | 0（0） | 0 | 0 | 无 | 无 | 无 | **retire** | 零消费者 + 零规则指向（声明面与消费面双空）⇒ 内收判据'零触发零消费→退役' |
| `data/depgraph.db` | 0 | 2026-08-04 00:59 | 31（0） | 4 | 0 | 无 | 无 | `governance.db` | **repoint** | 4 个真实消费者 + 存在活替代/共现后继 `governance.db` ⇒ 改指活库 |
| `data/runtime/progress.db` | 0 | 2026-09-15 23:50 | 1（0） | 1 | 0 | 无 | 无 | `integrator_progress.db` | **repoint** | 1 个真实消费者 + 存在活替代/共现后继 `integrator_progress.db` ⇒ 改指活库 |
| `data/zalpha_metadata.db` | 0 | 2026-09-10 00:44 | 5（1） | 1 | 1 | trae_034_task_card_standard.yaml | 无 | `governance.db` | **repoint** | 1 个真实消费者 + 存在活替代/共现后继 `governance.db` ⇒ 改指活库；规则册亦指向本库 ⇒ 规则与代码同批 |

合计可疑库 7 个；其中 0 字节 7 个。