---
ttl: task_bound
completes_when: 总包夜战战役(master_tc_night)归档收尾
---

# L10 PENDING 移交册（st-mastertc-l10 → 收尾班，2026-10-07）

## P1 token 批代投（移交收尾班执行）

- **事项**：把 `docs/_working/master_tc_night/`（00_orchestration.md + lanes 下已存在
  workbook 等）登记进 `capability_canonical_file_registry.yaml`（CREATE-GUARD 批量
  creation_token 补登）。
- **处方命令**（原样执行即可）：
  ```
  python scripts/governance/d3_metadata/batch_creation_tokens.py --prefix docs/_working/master_tc_night --created-by st-mastertc-20261006 --capability master_tc --merge-evaluation "总包夜战施工文档,战役终了归档,无既有真源重复"
  ```
- **受阻原因**：目标册 `docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`
  在本台施工窗口被他会话 **st-matrix-20261006** 持锁（lock_files 在途活跃，MM 态）。
  按总包预案「该册仍被他会话占用→登记移交，留给收尾班」，本台未抢锁未等待。
- **移交要点**：①执行前先 `python scripts/lock_files.py status` 确认 st-matrix 已释放；
  ②该册同为热册，写侧走 safe_write_text CAS；③登记批与产出物同批或紧随提交；
  ④若战役终了归档（00_orchestration §一 W5），归档移动后路径以 archive 后实际路径为准重跑。

## P2 裁定#488 落地核验（收尾班复核项）

- 裁定#488 已入提交队列：qid=`q-20261007-st-mastertc-l10-0001`（袋=索引 staged 快照，
  对 HEAD 纯插入 +33/-0，含恢复被误 staged 删除的 #487 条目原文）。
- 队列终态快照（04:33）：pending=14/done=513/daemon 在排空，本项前约 13 袋、oldest 0.96h
  ——未落地属拥堵非死信；本台 release-all 已执行，不影响该袋落地（袋自带 blob 快照）。
- 收尾班核验：`git log --all -S "裁定#488" -- .../ruling_registry.yaml` 确认已落 HEAD；
  若队列项 dead，读 dead_reason 修正后 `python scripts/commit_queue.py requeue <qid>`。
- 占号凭据：`.runtime/ruling_claims/claim_488.json`（session=st-mastertc-l10）。

## 已关账项（非 pending，备查）

- Owner 保留七项（C63/C287/C109/C410/C36/C37/C45）+C267 真删部分补记：已登记关账于
  同目录 `00_workbook.md` §二，晨会呈 Owner，本夜零施工。
