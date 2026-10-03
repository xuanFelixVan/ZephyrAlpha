---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# ND_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# ND D+E 组安全执行车道台账 sid=st-nightsweep2-nd-20260930 chief=st-nightsweep-chief-20260929
# Owner 2026-09-30 裁定：D 组/E 组按建议执行，每条先挖矿确认安全（六向台账+安全评估）；E6 只评估绝不执行
session:
  sid: st-nightsweep2-nd-20260930
  cold_start: RULE-ENV py3.12.8 OK / RULE-GUARDIAN reaper alive last_run=2026-09-30 06:11:33 / RULE-WORKTREE=降级直改主区（总筹卡面明令直提+热文件 claim+CAS；登记原因：D1 宪法两行为工作树在途内容，隔离工作树不含该 diff；GW 计数留痕）
  registered_session_registry: true

cards: {}

cards:
  D1_宪法两行落HEAD:
    verdict: DONE-LANED
    hash: 81ddc98b
    evidence: |
      §7 三行实测对齐（提交队列+cleanup/health、数据集成器 8 子命令、仪表盘 api_server.py）
      落地后 git show HEAD:AGENTS.md 验证通过（行 105/110/111）；行数 140 守恒。
      安全处置：工作树原基为陈旧快照（缺 F88 setup_dev_env 子句=cd0a0bc730 今晨落地），
      以 HEAD 为基重建防回退，F88 子句原样保留（diff 零该区变动）。
      卡面 #ARCH-362 marker 不可用（议题册查无=防伪拒），实走 [ARCH-APPROVAL:#ARCH-360]
      （先例 375a0cb91e 同为 §7 修改）+裁定#441 实质授权（706752aa）。
  D2_裁定册注册_420_421_裁13:
    verdict: CROSSCHECK
    evidence: st-nightclean 袋 q-20260929-...-sw2? no=q-20260930-st-nightclean-20260929-0050
      已落地 HEAD（#420 decision_timestamp 15→16/#421 UTC 列型/裁-13 补登注记全在册，
      行 5830/5843/5862），本车道不重复登记；死袋 sw2-0001/sw12-0004 前案一并核销口径。
  D3_宪法入口唯一化:
    verdict: DONE-LANED
    hash: 81ddc98b
    evidence: 头部"规则细节正式真源"行去散文计数（"86 个 trae_*.yaml"违 §4.4），
      发现唯一入口改指 docs/registry_of_registries.yaml（ROOR），随 D1 同袋。
  D4_GATE-SELFDOC_立法:
    verdict: DONE-LANED（立法面）/ 产品件残
    hash: 81ddc98b（宪法条款）+ 706752aa（立法文本=裁定#441③）
    evidence: 三态豁免+统一拆写规范入宪法补充铁律一行；立法文本入裁定#441。
      契约单测已在 HEAD（test_detect_git_dangerous_selfdoc.py）实测 4 红/3 绿=
      产品件（detect_git_dangerous.py 豁免实现=SW19 残件 c72c8e59）未落地，
      死信 sw19-0003 族待重投——立法先行注记"不构成行为承诺"已入册。
  D5_考卷判定书纳版本控制:
    verdict: DONE-LANED
    hash: d1906d43（162 件 verdict.md）+ 97cff66bec（token=exam_verdict_docs 162 条，
      gate-rationalize 吸收携带落地）
    evidence: add -f 强制追踪（零 .gitignore 改动=零 PROTECTED-PATHS 面）；
      EQUIVALENCE_VERDICT_T0_200.md+HANDOVER.md 经核已在 HEAD 不重做。
      障碍留痕：队列 prestage 拒收忽略区路径（袋 nd-0002 死信在案）→
      队列通道对忽略区白名单件结构性不可用；后续自动入库需 .gitignore 否定模式
      （保护路径，须 ARCH-APPROVAL）+prestage 白名单，两处留后续批。
  D6_working新件created门:
    verdict: DEFERRED（登记缓办）
    evidence: 挖矿完成=照 library_hygiene created 轴模式（SW6）建 own-scope 只查新增门
      +测试+三件套（translation/depgraph/token）。缓办因=今夜提交链持续竞态
      （TRACKED-DRIFT 瞬态×2/全局锁超时×2/他会话循环暂存），新门三件套
      （新 .py+测试+token+翻译+depgraph）过闸成本超窗口；处方已明，
      建议日班专项 30 分钟落地。非静默跳过。
  E1_410续期:
    verdict: DONE-LANED
    hash: 706752aa
    evidence: #410 expires_at '2026-10-08'→'2027-10-08'（同 commit 原子）+
      续期裁定#442（93册 12条#1 回法"1 续到 2027-10-08"；X-49 空转史实保留：
      三袋仍 dead 授权面存活待重执行；2027 前未消费不自动再延）。
  E2_10-05_F盘摘除排窗:
    verdict: DONE-LANED（只排班不执行）
    hash: 706752aa（裁定#445）
    evidence: 三段式执行单落册（假日窗 2026-10-05 时点+点停 VM 步骤+716G 回收验证法，
      引 INFRA-STORE-003+#414②+93册 补-10）；乙丙未批=禁不可逆；执行仍待 Owner 点名。
  E3_D盘应急清理:
    verdict: PARTIAL（2.49G/8G，余量被并发写吃平）
    evidence: |
      实腾: done 回执 26 件归档 G 核验删源 + quarantine drift_20260923 218 目录
      （20.4MB，manifest 在 G）+ blobs_archive 7051 件 1.17G 迁 G（manifest 留原地）+
      blob_gc --archive 孤儿 8794 块 1.30G 并入 G（content-addressed 抽验 6/6，
      restore manifest=manifest.jsonl 随迁 G 侧）≈2.49GB。
      df: 前后均 45G（并发车道写吃掉净差）。
      SKIP: .aidrafts 39 树清理——chief4_diskrescue 镜像（G:/zephyr_cold/90_tmp/
      chief4_diskrescue_20260927/）全盘三深度搜索无踪且 90_tmp 空=镜像不可证实，
      按禁毁唯一字节铁律 SKIP； chief4 台账止于"镜像近完成+82 目录未释放"，
      镜像去向成谜=移交总筹核查（可能镜像先行被清而源未释放=字节风险敞口）。
      .runtime/tmp（910 项）与 session staging 按卡面禁碰未动。
  E5_flags轮转:
    verdict: DONE-CROSSCHECK（治本他队已落）+ 归档执行
    evidence: 写侧自愈轮转（_AUDIT_ROTATE_BYTES=32MB 翻代 .1，注记"2.1GB 无轮转事故
      2026-09-30 治本"）已在他队工作树落地（16 行未提交件=SW11 系在途，未代提）；
      07:08 已自动翻代实证。本车道执行=2.11GB .1 rename→rotated-20260930→
      copy G:/backup/feature_flags（75s，字节+首尾行 JSON 抽验）→删源，
      留 90 天（manifest 注 delete_after=2026-12-29）；写方活跃实证
      （active file mtime 07:18:42 持续增长）。
  E6_VM_root两件残留:
    verdict: EVALUATED（评估卡；已核销态）
    evidence: |
      两件=①/root/macro_data_broken_parts_bak_20260925（760K，188 个 0 字节空壳目录，
      macro_data gc 施工残留）②/root/macro_data.sql.bak_metaqgc_20260925（4.0K 表结构
      元数据备份）。出处=st-metaq-gc-20260924 交接（93册 F 案卷 X-45/95 册§九 B）。
      09-27 01:3x-02:0x 实测 ch_vm_ssh.py 通道 CHANNEL_OK+BOTH_ABSENT=两件已不在盘，
      95 册记核销（卡面前提过期）。矛盾调解：X-45 时点（更早）在盘，95 册（更晚）
      BOTH_ABSENT——以晚测为准=已删。
      压缩窗后核验步骤（待 VM 可达窗，禁今夜执行）：
      python scripts/backup/ch_vm_ssh.py --cmd "sudo -n ls -d /root/macro_data_broken_parts_bak_20260925 /root/macro_data.sql.bak_metaqgc_20260925"
      预期 BOTH_ABSENT；若镜像恢复旧态复活，删除命令=同通道
      "sudo -n rm -rf <两件>"，且须先复核 CH 数据完整性（销证权在 Owner 口径，
      dossier_F §89）。禁 SSH 禁重启已遵守（本卡零 VM 操作）。
  E7_landing_base_blob漂移requeue:
    verdict: YIELD（让路登记）
    evidence: st-zc9-lane-r1 在飞 scripts/commit_queue.py+test_commit_queue_landing.py
      （袋 0008 pending+已落地 9d5548a336 死信封印机制），总筹明令"zc9 系在改则让路"。
      实测 r1 现内容 drift 面=preflight_face_drift（E-4 增信）非 FIND-3 base_blob
      强制 requeue——FIND-3 未被其实现，处方仍开；本车道今夜三次 landing 实证
      base_blob 漂移实际后果=三向合并死信（nd-0001 #436 同键异容），危害坐实。
      移交：r1 落地窗后由总筹派发（landing 侧插入点=registry 三向合并器 ours 侧
      身份键去重前置校验）。
  E9_旗标名对齐:
    verdict: DONE-LANED
    hash: b192fa39
    evidence: gateway _PRECOMMIT_RUN_FLAG→'gate_precommit_run'（对齐 flags.yaml:109）；
      旧值指向不存在键=is_enabled 恒 default=True=Owner 回滚通道坏死，对齐后复活；
      同批重生成图11 dev_delivery_map（diff=code_key 对齐面，D11-G02 对账尺翻绿）；
      flags.yaml 零改动（改码不改册）；capability_lookup.find 记账 4 次。
  E11_灾备裁定+g_mirror锚:
    verdict: DONE-LANED
    hash: 706752aa（裁定#443）
    evidence: 93册③建议全收入册（排除 .worktrees+P95 派生时限生成器算+轻量灾备+
      免死名单影子账 3 天）；g_mirror 防回退锚=配置锚声明（backup_config.yaml
      ch_vm_backup 目标 2026-09-24 配置级移除+tests/dr 双测试面在案；改回=Owner 门位）。
      ①②③执行属运维面另窗（本裁定=授权与锚声明）。
  E12_ConfigCheck三件批注:
    verdict: DONE-LANED
    hash: 706752aa（裁定#444）
    evidence: 99_skipped #41 三件批注落册（①任务 action 变更=Owner 门位只登记不执行
      ②宿主挂靠待安全窗③日红根因 reload 缺路径=已知限界）；未夜改生产调度器。
  E13_三小裁:
    verdict: DONE-LANED
    hash: 706752aa（裁定#441④）
    evidence: 三小裁=93册 补-17/补-20/补-12，全部本车道执行完毕落册注记
      （补-17=D1 治愈/补-20=E3 磁盘/补-12=E5 轮转）。

handoffs:
  - approval_resolver 绝对路径 bug：resolve_approval 不归一化绝对路径
    （'D:/ZephyrAlpha/AGENTS.md'→source=none，相对路径→approved）=裁定授权通道
    对 gate 实参（绝对路径）结构性失效，此前人人走 marker 故未暴露。
    治本处方=入口 os.path.relpath 归一化+双形态测试；本车道以 #ARCH-360 marker
    先例通道完成 D1 后留档移交（维护班/治理批）。
  - SW19 残件：detect_git_dangerous.py 豁免实现（c72c8e59）+99_delivery_report
    未随投=三态契约红面，待重投（立法已先行，#441③ 注记）。
  - chief4_diskrescue 镜像去向核查（E3 SKIP 依据）。
  - 死信核销单：nd-0001（三向合并 #436 撞号，已由 nc 治愈后直提吸收）/
    nd-0002（prestage 拒收忽略区）——留维护班核销。

commits_tonight:
  - 706752aa 裁定册 #441-445+#410 续期+nc 撞号治愈吸收（直提）
  - 81ddc98b AGENTS.md D1+D3+D4（直提，140 行守恒，F88 保留）
  - d1906d43 D5 判定书 162 件（直提）
  - b192fa39 E9 旗标对齐+图11 重生成（直提）
  - （他袋携带）97cff66bec token=exam_verdict_docs 162 条吸收落地
```
