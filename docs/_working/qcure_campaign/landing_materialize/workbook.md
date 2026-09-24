---
ttl: task_bound
title: QCure作业簿·landing_materialize
session: st-qcure-20260925
---
# landing_materialize 作业簿
## 1 环节定义与边界
队列项（bag manifest+blobs）→ serializer worktree 物化 → staged → gateway.commit 全门禁 → dev ref CAS → 主工作区收敛。真源=scripts/governance/commit_queue_landing.py（2730 行，WorktreeLanding）。边界：不含 enqueue 侧装袋（M1 预检归他环节）、不含门禁链内部（gate_chain 环节）、含 _pool_cas_replay 落地重放段。
## 2 六向台账
### ①上游输入
- drain_queue 调 landing_fn：scripts/commit_queue.py:1282；pool 版 _pool_process_item：commit_queue_landing.py:2419（路径锁 LAND:2410）。
- item 契约：files[{path,action,blob_ref,blob_sha256,base_blob}]（CQ:702 写入 blob_sha256，delete=null CQ:720）、base_head、message、meta.stale/depends_on。
- blobs 根 `.runtime/commit_queue/blobs/`；构造参数 serializer_branch/target_branch/_max_cas_retries/_lock_wait_seconds（LAND:1701,1765）。
### ②下游消费
- LandingResult(ok,landed_id,reason)→done//dead/ 落盘（CQ:1307-1322）；dead_reason 原样入库。
- _advance_dev：`git update-ref` CAS（LAND:1469，双锁统一 L1450-1467）；_converge_main_workspace 快进留痕 main_workspace_sync.jsonl（LAND:1565 fail-open）。
- _mark_cascade_stale 级联（CQ:1025-1074）；_notify_task_board_dead_letter（CQ:1322）；phase 计时 _timed_phase（sync/conflict/snapshot/prestage/cas）。
### ③机制现状（业界参照）
- 物化=「读回校验的 rsync」：写后读回逐文件 checksum 是 rsync -c 语义（https://download.samba.org/pub/rsync/rsync.html ）；门禁前移=GitLab merged results/merge train（https://docs.gitlab.com/ee/ci/pipelines/merged_results_pipelines.html ）、GitHub merge queue。M5.1 即把 rsync 式 checksum 引进 _apply_snapshot。
- 主流程六步已成型：sync→conflict→claim→apply→prestage→commit→CAS；W2 注册表三向合并（LAND:197-217 is_registry_mergeable=catalogs/ 前缀+.yaml）。
### ④代码面（实现/测试/调用方全集）
- _sync_worktree LAND:1050-1077（reset --hard:1065；clean -fd:1067 失败重试一次:1070 降级 warning:1073-1077）。
- _already_landed LAND:1082-1099（is-ancestor:1090+marker grep:1094；noop 前缀剥离:1087）。
- _conflict_reason LAND:1114-1153：注册表族豁免 path 级死信（mergeable:1131,1143）；base==dev:1138；base 无效死信:1140-1141；noop 字节同 blob 短接:1146→_noop_overwrite_paths:1155-1176；无 base_head 走时间基底 _legacy_base_drift_reason:1185-1229。
- _merge_registry_file LAND:1273-1323：ours=old_dev:1282；ours==theirs→None noop:1285；base 取 base_head:1287-1290，否则袋内 base_blob:1300-1311，两无→RuntimeError"基底不可知":1302-1307（=BASE-UNKNOWN 死因）；合并 conflict→RuntimeError:1319-1320（=3WAY 死因）；merged==ours→None:1321。
- 身份键：委托 registry_mass_deletion_gate.entry_identity_key（src/zephyr/gov_enforcement/commit_gates/registry_mass_deletion_gate.py:339；LAND:312-325 import 失败→None fail-closed）；复合键 `首标量|token=` LAND:328-349；翻译册族真键 LAND:361-390；**同侧键重复/判不了判定代码=_index_family_blocks LAND:470-473**（"存在身份判不了的条目":471；"同侧身份键重复":473）。
- _apply_snapshot LAND:1326-1364：_validate_relpath:1337；delete:1341；blob 读取失败:1352-1353；注册表走三向合并:1354-1357；合并 noop 跳过:1358-1359；write_bytes:1362。
- _prestage_snapshot LAND:1370-1428：check-ignore 拒绝 gitignored adds:1392-1400；add --pathspec-from-file:1404；dels 走 rm --cached:1416（**无 check-ignore**）。
- __call__ LAND:1666-1913：幂等:1677；ensure_worktree/gateway 异常→LandingEnvironmentError 包裹:1690-1698；CAS 循环:1701；sync 瞬态→env:1715-1716（_TRANSIENT_GIT_MARKERS:174-181）；conflict→死信:1720-1721；claim:1725；apply+prestage:1727-1733；全 noop→哨兵 landed_id:1738；gateway.commit 逃生旗组:1745-1766；pathspec 丢 staging 自愈重放:1772-1805；LOCK_TIMEOUT→env:1821-1825；NOTHING_TO_COMMIT 假落地防线逐 blob sha256 对比:1830-1877；非 OK→"网关落盘失败（status）":1878-1887；CasConflict 同路径死信/重试/pool replay:1889-1913。
- 测试：tests/governance/test_commit_queue_landing.py（70 例：幂等/冲突/主区收敛/假落地/pathspec 自愈/瞬态锁 L1003-1077）、test_commit_queue_landing_nightfix.py（9 例：三向合并/族键/多插顺序 L59-161）、test_commit_queue_pool.py（15）、test_commit_queue_base_head.py、test_commit_queue_integration.py。跑法：`python -m pytest tests/governance/test_commit_queue_landing.py tests/governance/test_commit_queue_landing_nightfix.py -x`。
### ⑤运维/呈现面
- gate_execution_stats.jsonl（.runtime/audit/）由 gateway 落；死因三分类 classify_dead_reason CQ:1797-1803（env/item 标记表 CQ:218-271）；queue_health+dead_burst 告警 CQ:1806/1900+。
- daemon 吃启动时刻代码（plan §1.3#6）：landing 侧改动须 daemon 纪元换血/重启才生效。
### ⑥失败态与数据面
- 死因链精确分支：**_apply_snapshot/_prestage 的 RuntimeError 无 except 包裹**（内层 try 仅 finally LAND:1806,1811）→ 逸出 __call__ → drain 泛化 except（CQ:1299）→ dead "landing 异常: RuntimeError: 注册表三向合并失败…"。sync 瞬态/LOCK_TIMEOUT/ensure_worktree 三路才转 env 退 pending。
- 实测死信（.runtime/commit_queue/dead/）：3WAY 族 dead_reason="注册表三向合并失败（死信回退人工）: docs/01_…/catalogs/…"；BASE-UNKNOWN=“基底不可知”×5；同侧键重复样本 step_id=BM-BUY-05×7、ruling_id=裁定#404×3、module_path=scripts/backtest/sim_daily×3、capability_id×3——横跨 battle_map/ruling/translation/capability 多册。
- blobs 19941 个只增不减（cleanup 不清，CQ:1553）。
## 3 缺陷与矿脉清单
已知→QCure 映射：M5.1（SNAPSHOT-NOT-APPLIED 31，现有防线=NOTHING_TO_COMMIT 逐 sha 对比 LAND:1838-1877，但在 gate 链**之后**才死）；M5.3（3WAY 64 笔，本包只登记）。
新矿脉：
1. M5.1 最佳插点=_apply_snapshot 的 write_bytes（LAND:1362）后读回比对：期望值来源=entry.blob_sha256（CQ:702，与 --from-bag 自校验 CQ:1495 同哈希）。**契约细节**：注册表族 content 已被合并重写（LAND:1357），sha 基准必须用合并后 in-memory content 而非 blob_sha256；delete 项 blob_sha256=null 需豁免；noop 跳过项（:1359）不计。次优插点=_prestage 后 `git hash-object` 复核 staged（可兼抓 Mode B index 丢失，与 LAND:1772 自愈互补）。
2. 死因分类失真：3WAY/BASE-UNKNOWN/路径校验拒绝均落 "landing 异常:" 前缀但 classify_dead_reason 归 other（标记表 CQ:218-271 无这些串）→ 58 笔最大死因族进不了 item/env 统计，对消审计失真（observability 环节接手）。
3. prestage dels 无 check-ignore（LAND:1412-1423）：删除 gitignored 路径静默 rm --cached，低危不对齐 adds 口径。
4. _conflict_reason 注册表族豁免（LAND:1143）把全部同路径漂移压力转移给合并器；复合键已救 token 族，battle_map step_id/ruling_id 等单键册仍会"同侧键重复"死（见⑥样本）——M5.3 专包的精确病灶点=LAND:470-473 + 各册键规范。
5. pool 重放 _pool_cas_replay（LAND:1889-1913 分派）不重跑门禁，重放若再遇合并冲突走向需专测（夜班测试未覆盖 pool replay×合并冲突组合）。
## 4 自审闸三态裁定
施工——M5.1 插点/判据/豁免面全部落点明确（LAND:1362+CQ:702），纯增量自验不改合并语义；3WAY 族维持方案封矿（M5.3 另开专包）。
## 5 长尾清单
- classify_dead_reason 标记表补 3WAY/BASE-UNKNOWN/快照路径校验（归 observability）。
- blobs 退役通道=M5.4（低优）。
- _legacy_base_drift_reason 存量兜底（LAND:1185）待装表前旧袋清零后退役。
- prestage dels check-ignore 对齐（P3）。
- pool replay 与三向合并冲突组合缺红蓝例。
