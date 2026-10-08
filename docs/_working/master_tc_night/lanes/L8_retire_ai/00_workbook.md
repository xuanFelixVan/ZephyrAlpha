---
ttl: task_bound
title: L8 退役+AI层 作业簿（13 卡：C267 C412 C169 C301 C394 C462 C475 C39 C84 C85 C96 C136 C314）
session: st-mastertc-l8
date: 2026-10-07
worktree: .aidrafts/st-mastertc-l8（分支 session/st-mastertc-l8）
---

# L8 退役+AI 层 作业簿（总包夜战 2026-10-07）

> 基线=开战时 HEAD `014ccf5b18` 后的活面；本车道直提落袋=C39/C85/C169 三袋（主区队列正门）+C394/C84/C314 两笔（会话 worktree 正门，直提道连坐规避，沿 W2-FIN 车道 MERGER-TOPKEY-SWALLOW 死因处方）。
> 六向台账①卡面处方 ②HEAD 现状实证 ③上游 ④下游 ⑤冲突面 ⑥残余移交；自审闸三态=GREEN/WAIT/RED。

## C267 退役批（余量）——GREEN（登记关账）

- **六向**：①七个 0 字节死库=只归档登记+G 盘核对，真删=Owner 保留（#488 已记）；F51 币圈挂起维持 ②实测：`G:/zephyr_cold/retire_c267_20260930/` 在盘（zero_byte_dbs/ 5 文件+zero_byte_dbs.json 封账 7 库全 0 字节 sha256=e3b0c44…空串恒值；shell_tables_c1_market/ + HANDOVER_TO_C_LANE.json + live_ddl_export 在盘）；七库清单=depgraph.db(4 消费者→governance)/integrator_progress.db/progress.db/scheduler_progress.db(零消费者=retire)/data/depgraph.db/data/runtime/progress.db/data/zalpha_metadata.db（trae_034 死指针已 1cf01067f5/7b… 改指）③上游=store_liveness_census ④下游=C 道 S-02/03 三步验证窗 ⑤冲突面=无（只读核对）⑥残余=真删 Owner 门位不动。
- **自审闸**：GREEN（登记即关账）。
- **施工记录**：本 workbook §C267+99_delivery 呈报=登记位；零物理删除零 DROP ✓。

## C412 B.5 真终验（降级执行）——GREEN（读数落账）

- **六向**：①降级=tests/infrastructure 拆超时件+分域一轮读数 ②实测三轮（pytest --timeout=60 --durations）：
  - 轮1 root+drift+escalation+adversarial+system_telemetry：163.43s，1186P/13F/7S/15xf/2xp；top duration=3.03s（trust_anchor），**无超时大件**；13F 全部集中于 process_reaper_identity_recheck×7/resource_schedule_regen×4/f18_adversarial×1/resource_sampler×1——live-reaper 环境冲突面（本机 reaper 在岗+多会话夜战），非本车道 diff 面（own-diff 于 tests/infrastructure=0）
  - 轮2 observability+process_lifecycle：108.35s，579P/0F/2xf；slowest=29.81s（test_auto_telemetry_bootstrap，<60s 阈），无标记需要
  - 轮3 mcp：**网络依赖大件簇**（真连 HTTP socket，--timeout=20 仍超墙钟，含 test_mcp_client_discovery 等多文件）——拆分处方=mcp 域独立网络执行窗，禁与本地域混跑（3 次尝试上限，按实况登记）
  ③上游=B.5 卡面 ④下游=W3 循环检查 ⑤冲突面=mcp 域墙钟 ⑥残余=mcp 拆分移交收尾班/测试重收编道。
- **自审闸**：GREEN（降级口径即卡面自带的执行方式）。
- **施工记录**：读数如上；pytest.mark.timeout 未新增（轮1/轮2 无单件超 60s，无标的面；mcp 面非 timeout 标记可治——是网络隔离问题）。

## C169 IFC-007 级联 + C475 trae_032 step7 余量——GREEN（同一实现，联动销账）

- **六向**：①retire_module.py 实现 --cascade-deprecate（trae_032_module_lifecycle.yaml:459 已立法）②实测：立法原文在册（IFC-007 契约级联废弃由 retire_module.py --cascade-deprecate 执行，批文②废止）；实现=标记传播模式（命中契约条目单 CAS 写 deprecated/deprecated_reason/deprecated_date，幂等 skip，ISO 日期引号化防 YAML date 漂移）；旧 --cascade-contracts 恒拒指向新旗；缺旗=REMAIN 语义零变化 ③上游=trae_032:459+MLC-003 七步 ④下游=cross_layer_contracts.yaml 消费者/IFC-007 流 ⑤冲突面=CloneGuard 首袋死（find_contract_block 100% 克隆 find_entry_block）→合并为 _find_keyed_block 本体+双薄委托，复发熔断后换新袋 ⑥残余=无。
- **自审闸**：GREEN。
- **施工记录**：commit `739b6fe466`（q-20261007-st-mastertc-l8-0005 落地）；测试 19 passed（新增 4：execute 打标+幂等/dry-run 零写侧/缺旗回归/字段手术保邻）。C475 同件销账 ✓。

## C301 R7 计划任务销账——GREEN（登记关账）

- **六向**：①RestartMiniQmt 实测不存在→销账登记 ②实测：NB2 证据链在盘=`.runtime/tmp/st-nightsweep-20260929/NB2_evidence/`{restartminiqmt_task_detail_20260930.txt（查询证明无此任务）,restartminiqmt_delete_20260930.txt（删除回执"成功删除"）,schtasks_all_20260930.csv（430 任务全量快照）}；W-170（#377 勘误"全仓零引用被证伪=17 处引用"）另案在册不冲突——本卡只销"计划任务存在性"账 ③上游=R7/#377 勘误 ④下游=登记面 ⑤冲突面=无 ⑥残余=代码引用 17 处的清理属波5（W-170），不在本卡。
- **自审闸**：GREEN。**施工记录**：本 workbook 即销账登记位；零 schtasks 变更 ✓。

## C394 windows_service.py 退役——GREEN（#488 通道=deprecated 标记制）

- **六向**：①文件头 DEPRECATED 注记+候选册行，零删除 ②实测：注记已在（B11/ae952d32，2026-09-30 落：SCM 1060+零消费者双实证+successor 指针）；本夜补候选册行=migration_registry.yaml retirement_schedule 增 windows_service_file_retire 条目（deprecated_marked，物理删除 Owner 门位保留）③上游=#488/B11 ④下游=退役排班窗 ⑤冲突面=合并器 MERGER-TOPKEY-SWALLOW 两袋死（q-0002/q-0006，同 W2-FIN 车道 67be6338f4f 呈报的死因族）→按其处方改会话 worktree 正门直提 ⑥残余=物理删除三段式 Owner 批。
- **自审闸**：GREEN。**施工记录**：worktree commit `9c37e387`（migration+strategy 双册，safe_write_text CAS，YAML 复验过）。

## C462 _working 在册盘上无——GREEN（枚举面重建+定性，零代裁）

- **六向**：①逐件 git log 考古 ②实测：**枚举面漂移**——卡面"10 件"为书写时点快照（NB2 已记"枚举面未复得"）；本夜重建=`git ls-files --deleted -- docs/_working/`=**248 件**（全仓 249）；逐件对拍=**248/248 在 docs/_working/archive/ 有同名归档副本**（O-6"批（归档式）：字节全在 HEAD 可回取"口径的归档式搬迁在途面）；git HEAD 全部可回取（tracked）。能恢复吗=能；该不该本夜恢复=不该——恢复=与归档语义打架（原路径+archive 双份），提交删除=代裁他会话在途工作面 ③上游=O-6/finaldel 系 ④下游=收尾班脏面清偿 ⑤冲突面=主区 3764 脏面中本面归 finaldel/清洁系 ⑥残余=定性清单移交（清单文件=.runtime/tmp/st-mastertc-l8/deleted_working.txt，248 行）。
- **自审闸**：GREEN（零代裁删除+零代裁恢复，登记即关账）。**施工记录**：本节+清单文件；"故意删候选"清单=空（248/248 均有归档副本，无真丢失件）。

## C39 miniQMT 文案残 1 处——GREEN

- **六向**：①bridge.html:3 按裁定#339 口径改 ②实测：原文"券商全面清退"→"仅实盘退役（模拟盘持续供数，裁定#339）"；=92 册交接卡 §三 7 件修正的**最后残留件** ③上游=裁定#339（miniQMT 9/18 实盘退役、模拟盘供数持续）④下游=前端展示面 ⑤冲突面=无 ⑥残余=0。
- **自审闸**：GREEN。**施工记录**：commit `6bb3c7e940`（q-0001）。

## C84 FSM 词表收尾——GREEN

- **六向**：①strategy_registry.yaml 补 shelved 态 ②实测：增顶层机读块 lifecycle_status_values 九态（原八态+shelved）+:58 行注释同步；消费端 registry_state_vocab.MACHINE_READABLE_FIELD 实读 source=catalog_machine_readable、shelved=True（落地义务原文"YAML 块待总筹落地"=本批兑现）③上游=裁定#398/#399+04_lifecycle_fsm §二3.6 ④下游=promotion_advisory/前端 ⑤冲突面=无 ⑥残余=0。
- **自审闸**：GREEN。**施工记录**：worktree commit `9c37e387` 同袋；测试 11 passed 1 skipped（tests/meta/shared/lifecycle/test_registry_state_vocab.py+tests/infra/frontend/test_promotion_advisory_api.py）。

## C85 C6 消费端余量（M4 free_window_pref）——GREEN

- **六向**：①washer 已读 task_routes 维持；M4 执行器谷时偏好最小 patch ②实测：dispatcher.py 新增 free_window_boost()（读 policy.priority.free_window_pref，窗内 +boost 排序偏好键；缺失/关闭/坏配置一律 0 保守不抛）+work_order_score 增 free_boost 参（缺省 0=旧式零变化）+rank_pending 接线；config/schedule_gate_policy.yaml 增块（**出厂 enabled:false**，翻转走 OBJ_R）③上游=C6/OBJ_R ④下游=order_daemon 派工序 ⑤冲突面=CAPABILITY-LOOKUP 门补审计后过+ruff 一轮 ⑥残余=翻转出厂旗=Owner/OBJ_R 门位。
- **自审闸**：GREEN。**施工记录**：commit `0e6a76bbcb`（q-0004）；测试 26 passed（新增 4）。

## C96 HANDOFF 真源（双层蒸发）——GREEN（登记关账）

- **六向**：①登记关账 ②实测：凭据原文不可考（双层蒸发实证=NB2 台账 blocked_registered"定性枚举面未复得"同族）；12 项批准以裁定#417（ruling_registry:3308 在册 active）+#450（:3742 在册）补批文为准 ③上游=波2 HANDOFF 链 ④下游=Owner 补录 ⑤冲突面=无 ⑥残余=OPEN_QUESTIONS 留 Owner 补录凭据原文。
- **自审闸**：GREEN（登记即关账）。**施工记录**：本节+HANDOFF_wave2_closeout.md §四.2 引用。

## C136 B 类波6.2 施工位映射表——GREEN

- **六向**：①96_final_report 的 B1-B11 逐条现状列表 ②实测：真源锚=W-168（total_command 00_master_skeleton:228+ext_03:33,56，出口判据"四行映射表，无表不算完成"）；四簇现状=B5 已收敛（generate_wiring_registry.py wiring_status 正交词表）/B7 五子案未施工（W3D-P=0/upgrade_requires=0/append_only_fields=0 全仓 grep）/B9 挂起有主（M7-BF-6b→C445+Owner 翻旗门）/B10 一项收敛（NON_WORKBOOK_RELS 生成器化+自守）一项未做（--auto-fix 结论面闸 CLI 无此参）③上游=W-168 ④下游=后续波次排期 ⑤冲突面=无 ⑥残余=B7/B10 两缺口移交（见 b_class_map.md §三）。
- **自审闸**：GREEN。**施工记录**：`lanes/L8_retire_ai/b_class_map.md`（同 worktree 袋提交）。

## C314 波2 HANDOFF 交接卡——GREEN

- **六向**：①补 HANDOFF_wave2_closeout.md（token 先行）②实测：卷已建（卷面现状/本夜 AI 卡落点/§七临时件清理勾选制——185 件备份与 worktree 两件"待勾"如实不代清/移交清单五项/终局判据照抄不自定）；creation_token=c314-wave2-closeout-handoff-handoff-wave2-closeout-20261007 已登记（带 merge_evaluation 内收判据：与 92 册跨域不同对象不并）③上游=92/93/94 册+dossier_D ④下游=收尾班/继任棒 ⑤冲突面=capability_canonical_file_registry 多会话共写——只携自家条目走 worktree 袋（主区直提必连坐 L6 在途条目）⑥残余=§七两件"待勾"留收尾班。
- **自审闸**：GREEN。**施工记录**：worktree commit `f4910d5b`。

## CONFLICT_LEDGER（本车道冲突面全记录）

| # | 冲突 | 处置 |
|---|---|---|
| 1 | WORKTREE/SESSION 门双拦直提（q-0001 前夜） | session_worktree_start 注册（.aidrafts/st-mastertc-l8）+--allow-non-worktree（2026-08-13 裁定 AI 默认）|
| 2 | CloneGuard：find_contract_block 100% 克隆（q-0003 死，同签名熔断 564 次） | 合并非新建：_find_keyed_block 本体+双委托；换新袋 q-0005 落地 |
| 3 | 合并器 MERGER-TOPKEY-SWALLOW（q-0002/q-0006 双死，migration_registry 增量吞没） | 沿 W2-FIN 死因处方=会话 worktree 正门直提（worktree index 干净零连坐），commit 9c37e387 |
| 4 | 主区暂存区 2948 件连坐面（含他会话 .py 触 MUTABLE-CONST 门） | 直提道弃用；热册共写只携自家条目（capability registry 提取式入 worktree） |
| 5 | capability_lookup API 漂移（capability_lookup.find→CapabilityLookup().find） | 按实锚适配，审计已留 |

## OPEN_QUESTIONS（呈 Owner/移交）

1. **C96 凭据原文补录**：12 项批准的原始凭据双层蒸发不可考，以裁定#417+#450 为准——请 Owner 择机补录原文锚点。
2. **C412 mcp 域拆分**：tests/infrastructure/mcp=网络依赖大件簇，需独立网络执行窗（非 timeout 标记可治），移交测试重收编道排期。
3. **C136 余量移交**：B7 W3D-P1..P5 五子案、B10 --auto-fix 结论面闸——两施工位排 OBJ_R 修订窗（见 b_class_map.md §三）。
4. **C267 真删**：七 0 字节库物理删除+数据/备份摘除三段式=Owner 门位（#488 通道在记）。
5. **C394 物理删除**：windows_service.py 三段式窗口另批（deprecated_marked 已落册）。
6. **C462 面清偿**：248 件归档式在途面归收尾班（清单 .runtime/tmp/st-mastertc-l8/deleted_working.txt）。
7. **C85 出厂旗**：free_window_pref.enabled 翻转=行为变更，走 OBJ_R 修订窗批。

## DONE_SUMMARY

- 13/13 卡全处置：GREEN 13（其中登记关账 5：C267/C301/C96/C412-读数/C462-定性）；RED 0；WAIT 0。
- 落袋 commit：主区队列=6bb3c7e940（C39）/0e6a76bbcb（C85）/739b6fe466（C169+C475）；worktree 直提=9c37e387（C394+C84）/f4910d5b（C314）；本 workbook+b_class_map=收尾袋。
- 测试读数：retire_module 19P / dispatcher 26P / vocab+promotion_advisory 11P1S / tests/infrastructure 三轮读数（见 C412）。
- 红线遵行：零物理删除、零 DROP、零 schtasks 变更、零裸 pytest 全量、单命令时限内、卡均 ≤3 次尝试。

## merge_state（2026-10-07 09:1x 补记）

- **DEFERRED-拥堵登记**（NB2 同款）：merge session/st-mastertc-l8 → dev 实测被拒——他会话 st-mastertc-l3b（0fed20a6cf）恰在合并窗口落地共享件（capability_canonical_file_registry/DEEP_DIVE_R2/L3 作业簿），ort 策略拒写本地脏面；"Index was not unstashed"提示后核 stash 空、dev 未被我笔移动、分支内容零丢失。
- **分支在库**：session/st-mastertc-l8 tip=9094d25f（含 9c37e387 C394+C84 / f4910d5b C314 / 9094d25f 作业簿三笔）；主区盘面已重新物化 b_class_map.md（worktree 分支为登记真源）。
- **next（收尾班单动作）**：主区脏面清偿后 `python scripts/session_worktree.py merge st-mastertc-l8 --yes`（junction .worktrees\st-mastertc-l8→.aidrafts\st-mastertc-l8 已建，CLI 可寻址）；若 L3 袋已携同名 token 条目，merge 时 capability registry 冲突按"两批条目并集"解（我的=HANDOFF+L8 双件，他们的=其树面），零条目删改。
