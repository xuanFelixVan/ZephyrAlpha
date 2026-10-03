---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# SW19_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# SW19 第三轮死账救援车道台账（sid=st-nightsweep-sw19-20260929，总筹=st-nightsweep-chief-20260929）
# 开工：2026-09-30 02:40 前后；冷启动三件套过（py3.12.8/reaper alive last_run=2026-09-30 02:47 killed=0/SessionRegistry 已注册 depends_on=chief）
lane: SW19-deadbag-rescue-r3
session: st-nightsweep-sw19-20260929
date: 2026-09-30

bags:
  bag1_w178:
    original: q-20260929-st-nightsweep-sw18-20260929-0027 (7件)
    death: COMPLEXITY-GUARD ch_read_shape_ruler.py:106 scan_text complexity 19>15
    verdict: DONE-LANED(e8bfd3490b)
    net_landed:
      - scripts/governance/wave1a/ch_read_shape_ruler.py（scan_text 拆四helper：_reader_match/_record_reader_hit/_check_var_uses/_attach_contexts；新旧实现对 HEAD 树136文件输出逐字节一致=行为零变化；复杂度 19→全文件峰值11）
      - scripts/governance/data_supply/ch_probe.py（取原袋blob修正版：parents[3]修深度病+金丝雀标记）
      - tests/governance/test_wave1a_query_shape_ruler.py（基线断言补 severity==JUDGMENT 过滤）
    crosscheck_absorbed:
      - src/zephyr/data/ch_writer.py + ch_reader.py：642b8886bb（st-finaldel-chief W-180补落）blob==HEAD 零差
      - tests/governance/test_wave1a_strict_read_canary.py + test_ch_probe_json_serialization_canary.py：0a90fc3904（q0213捞回）blob==HEAD 零差
    evidence: pytest 三件 27/27 绿；ruff check+format 双过；落地后 git log -1 核实 3 件归属精确；基线测试假红翻案=q0213 捞回件对 tests/ 豁免面病样本自trip（EXEMPT 软红≠硬违约，与尺 §退出码契约对齐）

  bag2_p3:
    original: q-20260929-st-nightsweep-sw18-20260929-0028 (9件)
    death: BARE-SUBPROCESS validate_rules_integrity.py:408/459（袋增行）
    verdict: DONE-LANED(228ce95188)
    disposition: 408/459 复核均已带 creationflags=CREATE_NO_WINDOW（SW18 死后已补刀未重投，本次复核合规重投）；gateway 件 blob==base 零增量跳过；ritual 件 blob==HEAD 已落地跳过；净投 7 件（validate/landing/recon_registry/flags.yaml/00_orchestration.md + 新件 derived_dirty_ledger.py token50690/翻译60934 在册 + test_orphan_same_bag_reference.py）
    evidence: 队列首投 q-…sw19-0001 二死于同门（根因=SW18 补刀只加 creationflags，门 AST 仅认行级 noqa: bare-subprocess+reason≥10字符）→补两处标准 noqa（沿 git_commit.py:81 先例）+derived_dirty_ledger 补内联 ALGO_FLOW 机器块（出仓 defer：capability/翻译热册被 nightclean claim）→直提落地；落地判据 git grep _MIN_DYNAMIC_GATES HEAD=4 达成；19/19 绿+ruff 双过；git log -1 归属 7 件精确

  bag3_f53_f04:
    original: q-20260929-st-nightsweep-sw18-20260929-0030 (13件)
    death: CREATE-GUARD 无token
    verdict: DONE-LANED(b985b1e35b)
    token_check: HEAD capability_canonical_file_registry 56633/56638/56643/56648 四条 file 路径与袋内四 .py 逐字符一致✓（0029 前置袋已落地）；四模块翻译册条目在册✓
    materialized: 5 modify 件 worktree==base 零漂移清洁应用+8 new 件纯新增；四测试 53/53 绿；ruff 双过
    blocker: TRANSLATION-COVERAGE 预检要求 plain_zh 合格简介——工作区翻译册已含四条合格 plain_zh（他会话所备），但该册被 st-nightclean-20260929 以 q-0045/q-0046 landing claim 锁定（HELD-OVERLAP 不硬闯，铁律3）；nightclean 的册 blob 不含此四条
    gate_ladder_all_cleared:
      - REGISTRY-MASS-DELETION：首版吸收工作区旧册净删他队条目被拦（正确）→册重排为 HEAD 版+仅 upsert 我4条 plain_zh（纯增 7937→7941）；他队孤儿词条留快照不代投
      - CREATE-GUARD 波13 关键词判重：saga_compensation_registry/quarantine_manifest 加逐字格式 create-guard-not-dup 标记（含具体理由）
      - BLUEPRINT-FORMAT：四测试件 MOD-EX-057-R1/R2、MOD-L00-004-R1/R2 改母模块 id（MOD-EX-057/MOD-L00-004）
      - ORPHAN-MODULE：三组合根/入口形态模块（facade/装配入口/清单桥，F53/F04 案卷 documented 零生产调用方挂 Owner 门）补最小诚实 __main__ 自检块（facade 打印 engines_status、manifest 转储默认隔离目录 16 条实测、sim_saga 装配冒烟）——入口豁免本义形态
      - PERMANENT-SYSTEM-TRIGGER：quarantine_manifest TTL=permanent+argparse=永久系统手动触发违规→改零参数只读账面转储（与"Owner 门审计面只读"定位一致）
      - NO-LONG-PARAM-LIST：build_sim_saga 9 参>7→SimSagaDeps 参数对象重构（门自荐法），测试 3 处调用面同步+import 补 SimSagaDeps
      - GATE-ANY-ABUSE：facade 三处裸 Any→pd.DataFrame/list[AnomalyFinding]/ValidationReport 具型（TYPE_CHECKING 惰性引用）
    landing_hash: b985b1e35b（14 件=13 内容+翻译册；1949+/14-；GW:multi-domain 留痕）
    window_race_note: 提交窗口期 st-c9-f42 的 library_new_module_reconciler 词条与我有一次瞬时竞争——终态核验=双方条目共存于 HEAD（我4条 plain_zh 42/43/58/46 + 对方富版 136 字符），零净丢失（git show b985b1e3^ 对比 HEAD 全量条目集核验）；commit message 中"吸收他会话7条"表述已过时（实际重排后仅纯增我4条），以本台账为准
    evidence: 四测试 53/53 绿全链复验；ruff check+format 全件双过；三 CLI 实跑 rc=0（facade 4 引擎台账/manifest 16 条实读/sim 装配冒烟）；翻译册纯增零删

  bag4_candidate_registry:
    original: q-20260929-st-nightsweep-sw18-20260929-0031 (4件)
    death: 三向合并拒绝——HEAD 侧 CAND-GOVTEST-005 同键异容双条（仓库态缺陷）
    verdict: DONE-LANED(635abae900)
    disposition: 工作区已带正确去重修复（005 唯一=promoted commit queue P1 条；测试泄漏条改号 CAND-GOVTEST-007+注释落账）；全册引用 grep 核 sync；YAML 623 entries 零重复 id；净差 2ins/2del
    evidence_post: 队列投 q-…sw19-0002 落地死=ours 侧(HEAD)重复键使三向合并结构性拒绝（合并器先索引 ours，HEAD 未修前任何袋必死；破鸡生蛋悖论实证）→按死因处方"合并器不可解改走 git_commit.py 直提"换正门通道（非同路硬闯；--heal-equal 对账器只治全等重复，同键异容不适用）直提落地；落地判据达成：^- id: CAND-GOVTEST-005$=1（promoted 条保留），007 条在册，YAML 623 条零重复；GR-ZR 钩子一次性修正后二跑过
    residual: 原袋另 3 件（detect_git_dangerous.py c72c8e59/test_detect_git_dangerous_selfdoc.py/99_delivery_report.md b47c8fc4）未随投——俟后续袋（本车道 claim 已释放，可由任一后续车道按同法直提）
    abort_clause: 未触发（直提一次过）

  bag5_e08_fsm:
    original: q-20260929-st-nightsweep-sw18-20260929-0032 (2件)
    death: strategy_registry.yaml 自证读回无法判别（ours 身份判不了条目）
    verdict: CROSSCHECK-DONE(原袋全部内容已被 HEAD 吸收/超越，零重投件)
    findings:
      - strategy_registry.yaml：袋 blob(430ac31d) strategies 161 条与 HEAD 逐条全等、头版本字段全等=增量已被他袋吸收；死因实为册头 unique_key 元数据族（流式 list 解析出字符串块'strategy_id'→identity None）在 base blob 已被清（b5be6ed2 missing）的陈旧三重态下触发，现行 HEAD/theirs 双侧代入合并均无错（base=theirs/base=ours 两仿真 err=NONE）
      - promotion_advisory.py：袋 blob==base 零增量；HEAD 已含 F74 晨报刷新（他道落地）
      - test_promotion_advisory.py：HEAD 比袋 blob 新（F74 monkeypatch+F75 from=sim 真边修正），17/17 绿
    orphan_tests_blocked:
      files: [tests/strategy_pipeline/test_daily_gate_snapshot_l5.py, tests/strategy_pipeline/test_daily_gate_snapshot_pool.py]
      reason: import 的 _read_external_kill_switch_state/_read_kill_switch_state 全仓（HEAD+工作区+src 全 grep）不存在；配套 src 仅存于无主 blob（cd586871/de525a1c/e81798fb，原袋已清无引用），且与 HEAD 分歧 327-865 行=重建级工程非机械修复
      prescription: 重建需以 HEAD 版 daily_gate_snapshot.py 为基重接 kill-switch 双函数+两测试改造，或裁定废弃两孤测试；属施工决策，登记让路，不硬投（同因禁第三次硬闯）

extras:
  done_drop_investigation:
    question: done 850→732 反常下降
    verdict: 良性（设计内 TTL 清理，非事故）
    mechanism: commit_queue.py cleanup_done（66号§12 Q3，done 7天 TTL，CAND-GOVTEST-005 P1 三件套功能）在每次 drain 排空收尾自动调用；118 件=landed 早于 2026-09-23 ~03:30 的 >7 天 cohort 被今晚首扫清除
    evidence: 剩 735 件中 730 件全在 7 天窗内且最老保留件=2026-09-23T03:47:12 恰贴边界；done/ 内 09-20/21/22 落地件=0；5 件边界残留（09-23 02:41-02:56）系移除瞬态竞争遗留待下轮；dead/ 永不自动清（TestDoneTtlCleanup 不变量）；done 记录仅回执，commit 本体在 git 史，blobs/（内容寻址共享存储）不在清理范围
  preexisting_defect_report:
    - tests/governance/test_commit_queue_landing.py::TestRegistryMergeCompoundIdentity::test_true_duplicate_compound_key_still_deadletters 在 HEAD 预存红：three_way_merge_registry_yaml 对同 file 同 token 真重复未死信（fail-closed 松动），HEAD 版函数级复跑实证；建议维护班核对复合键身份判定回归（涉 0031 类死信的对账器处方面）

monitoring:
  round_log:
    - r1(03:47): q-0001 ahead=6/q-0002 ahead=8；nightclean q-0045 processing
    - r2(03:51): ahead=3/5；q-0045 死（翻译册合并病同类）
    - r3(04:00): ahead=1/3
    - r4(04:09-04:21): q-0001/q-0002 相继落地死（BARE-SUBPROCESS 复发+ours 侧重复键结构性拒绝）
    - r5(04:2x-05:4x): 袋2 直提 228ce951✓、袋4 直提 635abae9✓、袋3 直提七门连闯后 b985b1e35b✓
  final_tally:
    - 五袋终态：袋1=落地 e8bfd349｜袋2=落地 228ce951｜袋3=落地 b985b1e35b｜袋4=落地 635abae9｜袋5=CROSSCHECK 全吸收（原袋零净差）+两孤测试 BLOCKED 登记
    - 本车道净落地 4 commit / 28 文件；allow_overlap 熔断一次（≥5 触发，此后全部 --no-auto-enqueue 无旗直提成功）
    - 会话收尾：claims 全释放（提交即释放+lock cleanup SALVAGED 复核）
extras_done_drop_investigation_verdict: 良性（详见上）
```
