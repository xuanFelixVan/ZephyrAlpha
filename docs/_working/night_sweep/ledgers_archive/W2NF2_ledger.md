---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# W2NF2_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# W2-NF2 F组补完车道 · 台账
# sid=st-nightsweep2-nf2-20260930  总筹=st-nightsweep-chief-20260929
# verdict 词汇: DONE-LANED(hash) / ADVANCED(状态+next) / BLOCKED(因) / OWNER-GATE(登记) / CROSSCHECK

lane: st-nightsweep2-nf2-20260930
started: '2026-09-30'
avoid_faces: [0260526facc F3, 7194643e4b8 F5, 4cef321180 F6]  # 前棒 nf 三 commit 未进 HEAD，触面避让（ruling_registry 例外=F1/F8 卡面强制+diff 零外来已验证）

cards:
- id: F8_GATE-MUT退役
  verdict: DONE-LANED(0e39637418)
  evidence: |
    :84 SSoT 修 CROSSCHECK 已在 HEAD（2026-09-27 告别补丁）不重做；裁定#448=前棒浮游在途件采纳落地
    （内容与本卡一致+补执行披露行，同 commit 原子）；四件 deprecated+successor 注记（三 .py header
    [STATUS]/[SUCCESSOR]+cases.yaml 封存注）；顺带 ruff --fix 同件三处 F541（PRECLEAN 处方）；
    yaml 264 条零重复+py_compile 过+PROTECTED-PATHS 走 [ARCH-APPROVAL:#ARCH-369]。

- id: F1_L09-C01追认
  verdict: DONE-LANED(9938b2ed) + CROSSCHECK(裁定面)
  evidence: |
    裁定面 CROSSCHECK：追认已在册=裁定#437（2026-09-30 晨 Owner 全批落册载体 #ARCH-367，含 #421→#437
    撞号重排全史；nightclean 3f75191285 补录行经该批追认）——不另取新号防同源重复立法（宪法 §4.2）。
    SKEL 面（_20260924 现行版）：§三 MINING→SEALED（未挖清单 5 件 B9 批全读：blueprint 238 行 D1-D7
    对表/owner-vision §二.3/data-sufficiency L4 行/55 号=archive design_memos 55_monitoring_review
    合流关系结清/alert_threshold_registry 迁址实勘 THD-HEALTH 族+dloop 心跳面）；§四补 L09-C01 ✅
    裁定结果行引 #437；§六 B9 补录+封矿双联满足翻转；UNVERIFIED-SEAL 横幅=门机械态不手改（L01-L08 先例）。

- id: F7_两聚合台恢复
  verdict: DONE-CROSSCHECK + 验证回归绿（无码改零提交）
  evidence: |
    摘禁用标记 CROSSCHECK：已由裁定#431 第①项（终局交付战役批）翻回 enabled: true 在 HEAD
    （in_process_gate_registry GATE-VOCAB:208/PERMANENT-SYSTEM-TRIGGER:246，含"187 件落地已达成"注记）。
    装载验证：registry load→两门 enabled=True+factory 实例化 GateSpec(80/82)+check callable。
    证能红：违例样① permanent+while True+time.sleep 无订阅→[PERM-TRIGGER] 红；违例样②
    VALID_TTL_VALUES 字面量→[VOCAB-HARDCODE] 红（探针=假 gateway+tmp 样本，不碰真暂存区；
    首两轮全绿系 mock 失真：反斜杠绝对路径+wt_root 错位，修正为 git 真实形态后复现）。
    正常样不误伤：good_perm(有订阅)+neutral(task_bound)+clean 文件全 passed=True。
    4 子台执法面在岗：PERM-TRIGGER/MANUAL-ONLY-PERMANENT/VOCAB-HARDCODE/VOCAB-CHAIN
    （聚合失败清单只含预期源台=其余子台装载成功）。
    回归：tests/governance/commit_gates/ -k "vocab or perm or manual" = 99 passed（2517 deselected）。

- id: F9①_SW13整合批272件+撞号重编
  verdict: DONE-LANED(6ab478e326 队列落地实钉)
  evidence: |
    272 件=未落地（spec"禁碰待整合"维持；mapbuild 会话不在活跃册，不代落）；撞号让号重编登记面执行=
    主区 #414/#415（存储终裁/总包单写者 2026-09-28 落地）→战役两裁二次撞号作废，取号器重占
    #451（首波三图准入裁）/#452（收口总裁）（claim_451/452.json 在案，整合批落地须同 commit 原子登记）；
    两处登记面同步=map_build/99_pending_owner.md §已知会 10+night_sweep/fig14_fig15_spec.md §5.2。

- id: F9②_甲-2图15三迁移挂门
  verdict: DONE-LANED(q-20260930-...-nf2-0002 入队)
  evidence: risk_tier_registry D_FACTOR/D_BACKTEST 各补 human_gate 三行（D15-M11 封卡/M14 挂起/
    M17 跨实例复活，production 流转级=宪章 §5.2）；tier 维持 medium 不越权翻级；X-7 点名两域原件 hg 空。

- id: F9③_SKIP-4/5呈批落册
  verdict: DONE-LANED(q-20260930-...-nf2-0003 入队)
  evidence: pending_owner_items 补-15（INTRADAY paper 放宽 Warning=裁定值需新裁）+补-16（xtdata
    零新增数据源口径边界）；详版锚 chain_circulation 99_skipped SKIP-4/5（09-28 终态：清单闸写侧已治本/
    纪律闸两把已装余腿待源）。

- id: F9④_W-174宿主注记
  verdict: DONE-LANED(q-20260930-...-nf2-0003 同袋)
  evidence: 00_master_skeleton W-11 行尾追加"另有 245 件批文批次"（≠169 两数并存不混，指 93 册 ⚑ 补-9）。

- id: F9⑤_emoreplay交接确认
  verdict: DONE-LANED(f8198b8fc3 裁定#453)
  evidence: 补-6 采甲=历史"已批"判未批（裁定册 grep=0 实证）+处方①原文「骨架维持在途+注释挂接随情绪线
    复职批」+影响面一页纸捞回重呈=本条载体；动手面锁归 L02-C01/C9 复职批。PROTECTED-PATHS 走
    [ARCH-APPROVAL:#ARCH-369]+--allow-overlap（过期 claim 痕迹误伤 FOREIGN_CHANGE，diff 零外来双验证后放行）。

- id: F9⑥_账房单一写手裁定
  verdict: DONE-LANED(f8198b8fc3 裁定#454)
  evidence: gov_audit events.jsonl 写侧唯一=writer.py（跨进程锁+锁内重读尾哈希 GW-A+有界等待 cc730f6474；
    禁旁路写手；落地史三件+并发双测为判据载体；既成事实正式化零行为变更）。

- id: F10_F11_归口销账
  verdict: DONE-LANED(q-20260930-...-nf2-0004 入队)
  evidence: |
    99_skipped 高频 10 项逐行 [Owner 2026-09-30 夜批]（#8 批/#14 E10 维持/#19 zc9 3c01517bb2/
    #20 zc9 8479b8b7ce/#21 已落 082d4591e79+833af2d0220 DDL 残腿留痕/#25 批退役（币圈专项挂起窗不代执行）/
    #29 A2 沙箱批+实盘等通知/#34 D2 3f75191285/#35 销账 1cf01067f5/#36 B13 edf0788dfb）；
    93_owner_menu 追加"夜批回执"节（①-⑤+12条 #1/#3/#6/#7/#12/② + A 组 9 项 NB1/NB2 b17 结论 +
    B 组 5 项 ND 系）；无据项维持原状不代裁。销账计数=10 行（99_skipped）+21 行回执（93 册）。

- id: E6_VM_root两件评估卡
  verdict: ADVANCED(评估卡已落盘；token/commit 挂热册竞争处方)
  evidence: |
    CROSSCHECK：ND 车道 E6 已 EVALUATED（两件 09-27 实测 BOTH_ABSENT 已核销，压缩窗后复核义务在账）。
    本车道交付=评估卡文件化 docs/_working/night_sweep/e6_vm_assessment.md（ND 证据忠实转登+风险清单+
    压缩窗后核验命令+复活分支 Owner 门位前置）。token 登记三跑均被 capability_canonical_file_registry
    在飞基底 fail-safe 拦（st-finaldel-c83 持锁 8.3m+，worktree 缺 HEAD 条目 auction-backfill-...-20260916）——
    该册=本车道避让面（F6 触面）+他锁活跃，按"他会话在途不代修"不硬闯。
    处方已执行=其落地后第四次 batch_creation_tokens CAS 成功（落盘 True+已插入 1 条）+评估卡同批入队
    q-0006（--adopt-prior-work 认领在飞基底增量，diff 只增不减复核）。

- id: F2_t0甲位
  verdict: DONE-LANED(pending_owner 补-17 行；delta 待 q-0003 落地后随队/直提)
  evidence: 维持缓批（NB2 b17④ 采甲：diff 表齐后再呈圈定）；两硬前置登记=pending_owner_items 补-17
    （①三版本 diff 表出齐 W-166/167 门后施工位 ②Owner 圈定后执行位解封）。

queue_bags: [q-20260930-st-nightsweep2-nf2-20260930-0001..0004]  # 快照入袋零丢失，传送带自治消化
ruling_claims_held: {#451: mapbuild首波三图准入裁, #452: mapbuild收口总裁}  # 整合批落地同 commit 登记；#453/#454 已消费
```
