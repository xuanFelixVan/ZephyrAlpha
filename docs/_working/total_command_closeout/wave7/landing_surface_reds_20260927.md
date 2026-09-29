---
ttl: task_bound
completes_when: "本表 5 簇红件每簇都被复跑定性为『已修』或『判定为预期变化并同步测试』，落地面同面复跑零失败"
measured_at: "2026-09-27 10:36-10:53（本地钟）"
authored_by: "st-final-build-20260926（总筹本班，测量者非肇事者）"
---

# 落地面现网 14 件红：五簇定性与复跑命令（非本班产物，逐条可查）

取数：主区（落地面，非车道）跑 `python -m pytest tests/governance/commit_gates tests/scripts --no-header -q`
⇒ **14 failed / 3351 passed in 1000.63s**，日志 `.runtime/tmp/hookreg.log`。
对照组：本班同仓 04:47 与 05:08 两轮跑 `tests/gov_enforcement + tests/backup + tests/data + tests/governance/commit_gates`
均为 **3328 passed / 0 failed** ⇒ 这 14 件红出现在 05:08–10:36 之间的**他人落地**，与本班的钩子改动无关
（14 条失败里 **0 条**命中 guard/gw/hook/reference_transaction 关键字；本班改的是 `reference_transaction_guard.sh`，
其红队件同窗 23 passed）。

| # | 簇（文件） | 件数 | 实测症状（断言原文摘录） | 定性 | 建议第一动作 |
|---|---|---|---|---|---|
| 1 | `tests/governance/commit_gates/test_resource_schedule_gate.py::test_production_registry_clean` | 1 | `sched_mem_ceiling/block：data_slot_consensus_crosscheck+…共 5 槽同窗并发内存和 11.5GB > mem_ceiling_gb=10.0（at=2026-09-16T23:35:00+08:00）` | **注册表数据与上限互斥**：注记还是 9-16 的旧值，槽位/内存实测已涨 | 要么调并发槽位、要么经 Owner 门位调上限；**不得改断言消红** |
| 2 | `tests/scripts/governance/d8_doc_sync/test_algo_flow_reverse_orphan_reconciler.py` | 7 | 整文件全红（retire 回收镜像/二次退役拒绝/回滚注册表/提交说明带因/变异授权与写后检查等） | **本体被改而测试没跟**（或本体被删/改名） | 先跑 `git log --oneline -5 -- <本体路径>` 定位改动，再判"测试过期"还是"回归" |
| 3 | `tests/scripts/test_ch_archiver.py::TestVerifySampleFieldComparison` | 2 | `verify_partition('c1_market.kline_1min','202101',…) == True`，而用例要求"样本值不符/幻影行必须判失败" | **判据真被削弱**（该函数现在对坏数据返回通过）——本簇是本表最危险的一条 | 立刻按"抽样核验"口径复查 `verify_partition` 的比对分支；这是会让"归档完整性"假绿的类型 |
| 4 | `tests/scripts/test_deadman_dashboard_channel.py` | 2 | `_alert_log(...) == ''`（该告警时零告警：listening+stale alive pid / dead pid 两态） | 死信看板告警通道未触发（判据或通道漂移） | 复查告警触发条件与看板 promotion 通道是否被改 |
| 5 | `tests/scripts/test_generate_resource_profile_registry.py` | 2 | `len(解析出的槽位) == 32/33` 与期望不等；`test_parse_ps1_entities_covers_all_task_names` 同红 | **生成器解析面与 .ps1/排产册漂移**（条目数变了） | 跑生成器看 diff，判定是 .ps1 加了任务还是解析器漏了 |

## 为什么单独成册（不留在这次的交付报告里）
1. 落地面"全绿"是波 12 点火的五条件之一。这 14 件不在本班件面上，但**照样挡住点火**——
   点火判据不分"红是谁造的"。
2. 本仓已有多起"别人的红被下一个会话顺手改断言消掉"的在案事故；把簇、症状、定性、第一动作写死，
   是为了让接管者**先定性再动手**，而不是先消红。
3. 第 3 簇（`verify_partition` 对坏样本返回通过）性质上属于"判据失效"而不是"测试过期"，
   按 Owner 既有裁定应判"疑似判据失效"而非"可删/可跳"。

## 复跑命令（原样可贴）
```bash
cd /d/ZephyrAlpha
python -m pytest tests/governance/commit_gates/test_resource_schedule_gate.py   tests/scripts/governance/d8_doc_sync/test_algo_flow_reverse_orphan_reconciler.py   tests/scripts/test_ch_archiver.py tests/scripts/test_deadman_dashboard_channel.py   tests/scripts/test_generate_resource_profile_registry.py --no-header -q --tb=short   --basetemp=.runtime/tmp/bt_reds_triage
python -c "import shutil;shutil.rmtree(r'D:/ZephyrAlpha/.runtime/tmp/bt_reds_triage',ignore_errors=True)"
```
