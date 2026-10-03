---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# NB2_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# NB2 B组确定件执行车道台账
# sid=st-nightsweep2-nb2-20260930 | 总筹=st-nightsweep-chief-20260929
# worktree=D:\ZephyrAlpha\.worktrees\st-nightsweep2-nb2-20260930 | 分支=ai/st-nightsweep2-nb2-20260930/nightsweep2-nb2
# 基线 commit=d2446aff07 | 日期=2026-09-30

lane: NB2-B-determined
session: st-nightsweep2-nb2-20260930
baseline_commit: d2446aff076a797e75939f20dee3ea93e7fbd101

items:
  B4_postsettlement_clock_leg_retire:
    verdict: DONE-LANED
    evidence:
      - 事件腿在库实证：35ca1d69cd8（14 测绿，boot_hooks 挂载 post_settlement_pipeline 消费方）
      - 取证：schtasks LIST/V + XML 双导出 .runtime/tmp/st-nightsweep-20260929/NB2_evidence/postsettlement_task_{detail,def}_20260930.{txt,xml}（Weekly Mon-Fri 15:30 → run_post_settlement.py）
      - 执行：schtasks /delete 成功；复查 schtasks /query = 系统找不到指定的文件（已消）
      - 事件腿独立验证：注入 post_settlement.recon.requested 一次 → 回执 swept status=UNWIRED（显式落状态零副作用），脚本=NB2_evidence/b4_event_leg_inject_verify.py
      - Owner 批：B4（夜总攻批文）

  B9_restartminiqmt_retire:
    verdict: DONE-LANED
    evidence:
      - 取证：restartminiqmt_task_{detail,def}_20260930.{txt,xml}（已禁用态、指向 E:\XtQuant SDK程序化交易\scripts\restart_minimqmt.ps1，E 盘脚本本体在盘未动——非仓内资产）
      - 残壳定性佐证：Owner 2026-08-21 裁定 disable 先例（QMT 无法自动登录，pre_expiry_full_backlog_roadmap.md:39）
      - 执行：schtasks /delete 成功；复查=任务不存在
      - Owner 批：B9

  B7_roor_8_registries_net_deletion:
    verdict: BLOCKED
    reason: 源清单灭失——S4_registry_machine_governance 簿从未入 git（全历史 pickaxe "S4_registry_machine_governance"=0 命中；fms_overhaul 目录仅 S2/S3/S5/S7/S8 在树，S1/S4/S6/S9 缺）；Owner 批的是该簿 §4.4 点名的 8 候选，名单不可复得，按"只动册面列名件绝不扩大化"禁自由发挥代选
    mechanical_recheck: ROOR 81 条 physical_path 存活性实测=79 存活+2 条 PG 连接串（非文件）；非 active 态 11 条（archived×2/draft×8/deprecated×1 REG-MIGRATION-001 归 B10）
    next: 需 Owner 或归档通道重出 8 候选名单（死会话 st-zc8-s4 / fms 簿作者处或有副本）后按原处方执行

  B8_translation_registry_wo001_003:
    verdict: DONE-LANED
    hash: 8954523b7f
    evidence:
      - 三 module_path 指 scripts/governance/meta_question/wo001_003/*，目标目录 ls ENOENT；R5-DIGIT-SUFFIX 门杀件实录 dead_triage_r2.yaml:1406
      - 8925→8922 条目（-24 行）；lock claim+safe_write_text CAS（before=584f3492/after=d4e4f0c1）+allow_mass_edit；[allow-mass-deletion] 正门
      - YAML safe_load 复验过

  B10_migration_registry_retirement_schedule:
    verdict: DONE-LANED
    hash: b7c3aa0a81
    evidence:
      - 13 条 pending 逐条核实：12 条 old_path 消失+new_path 存活（gate_engine 族 8+rule_engine 族 4=迁移事实完成账面漂移）；1 条 rule_watcher 双亡（new 从未创建，src 树零命中=作废）
      - retirement_schedule 顶层块追加（执行窗=下个注册表维护窗；A 组 12 条 status→done，B 组 1 条→superseded），零条目删改，entries=37 不变
      - claim+CAS（after=6956164d）+YAML 复验

  B11_windows_service_deprecated:
    verdict: DONE-LANED
    hash: ae952d32
    evidence:
      - 双实证（NB1 复核未出，按批文兜底口径）：sc query ZephyrAlpha→1060 服务未装；零 import 消费（仅 __init__:45/speed_baseline_checker:43 字符串清单+process_supervisor:22/runtime_config:5 注释头）
      - "[DEPRECATED]+successor 注记（successor=ZephyrAlpha_* 计划任务群+桌面壳自启动）；物理删除留 NB3 波"
      - capability_lookup 反查留审计；判据=99_skipped #37 全文

  B12_final_cleanup_true_deletion:
    verdict: BLOCKED
    reason: "'96 册清单'（勾选真删件的源册）不可定位——total_command_closeout/final_delivery/fms/qoder 四个 96_*.md 均无清盘勾选清单；C410 乙方案与补-14 删链的枚举面未在 HEAD/夜战 tmp 复得"
    evidence: "补-14 只批'标记+隔离'两段（recovered_final_reconciliation_checklist:210）；零字节对拍即删=违纪，宁缺勿滥"
    next: "需清单源（finaldel 系车道产物或 G 盘归档索引）落位后按'确定缓存/临时'类+sha256 双证执行"

  B13_f56_three_way_closure:
    verdict: DONE-LANED
    hash: 7bdf98e8
    evidence:
      - 裁定#438 落册（选 c 葬：B7 超集 78982c4c81 事实终态，kernel 字节封存死袋 blob q-20260927-st-c7-f56-20260927-0001）
      - 事实链核验：edf0788dfb 墓碑收编+dd3b17f9fd 断腿重建已在库；capability_canonical_file_registry merge_evaluation 同口径注记
      - 99_skipped #36 状态改"已裁销账（裁定#438）"
      - 取号 claim_438 原子占号；[ARCH-APPROVAL:#ARCH-361] 先例通道；双册 claim+CAS+YAML 复验

  B14_final_menu_four_items:
    verdict: ADVANCED
    sub_items:
      fms_hygiene_block_flip:
        state: 未达翻档线，登记差额
        evidence: 判据已改写（连零 20 笔机读 .runtime/gate_audit/fms_hygiene.jsonl；原"存量清偿过半"实测 554/3702=15% 机械不可达已废）；现 trailing clean streak=16/20，差 4 笔；block_flip_eligible(main root)=False；FMS_HYGIENE_GATE_MODE 保持 warn（翻档本身=OWNER-GATE 常量）
      eight_registry_deletion:
        state: 已含 B7 → BLOCKED（同 B7 S4 簿灭失）
      mirror_tree_migration_w0:
        state: 未开工，处方定位
        evidence: C28 卡（workorders_docs_misc.md:87）=备料簿 M3_mirror_tree_migration 盘面不存在需重建 docs/_working 新件后分目录迁移（裁定不整体迁移、先写者改造 W0）；W0 的 R0 即日规（新文件一律新规）已由 FMS-HYGIENE 门执法在岗=零存量动作部分已生效；备料簿重建=独立施工波
      gib165_archive_exemption:
        state: 只登记等处方（按批文口径）；归档处方未出，不执行
        evidence: recovered menu B14"165GiB 需先出归档处方再批"

  B15_empty_shell_tables:
    verdict: DONE-LANED
    hash: f3030556
    evidence:
      - CH 实读 12 表：suspend=36 行/etf_benchmark=7114 行已活出列；余 10 张 0 行
      - 挖矿去重：edb_data 已有 accepted 条目（iFind 退役裁定在案）；F06 卷（2026-09-29）已挂 6 张 *_empty_table_no_leg——防重复挂账，净新增仅 2 张
      - 净新增：index_valuation_daily_v2_no_collector + reconciliation_differences_dual_empty_disease（W-36/X-40 病根，dual_source_guard.py:28 实锚）；gaps 71→73，追加式
      - 让路：realtime_snapshot=st-zc9-lane-d #19 域领地（避让图），不挂账不建腿
      - 建腿面：9 张全无现成采集腿（src/zephyr/data 树 grep 0 provider/0 task config）→ 全部归挂账路径，无 tasks.yaml 改动（lane-d 领地零接触）

  B17_severity_variants_and_w163_menu:
    verdict: DONE-LANED
    hash: a8697815
    evidence:
      - "'7+2'解码=93_owner_menu D.1'A 组 9 项=7 项完全查无+2 项已呈缺详版'（补-1..9）"
      - 裁定#439 打包 8 项照册建议（补-1 乙/补-2 甲/补-4 甲/补-5 甲/补-6 甲/补-7 甲/补-8 甲/补-9 甲）；补-3 已被裁定#431 十六项授权覆盖，条目内 DONE-CROSSCHECK 不重复立案
      - 裁定#440 severity 22 条变体定性：纯展示面机械归一（Z-36 同向）+中文量级字优先映射 canon 表（P1中→P2中×9/P0高→P1高×4/P0紧急→P0致命×3/P1严重→P1高×2/medium→P2中/P2低→P3低/P0阻断→P0致命/P4低→P3低），收口判据=余量 0
      - 取号 claim_439/claim_440 原子占号；[ARCH-APPROVAL:#ARCH-361] 通道；claim+CAS（after=5d8482d5）+YAML 复验 253 entries

  B18_164_staged_deletions_triage:
    verdict: DONE-CROSSCHECK
    evidence:
      - 对象已消解：主区 git diff --cached --diff-filter=D 实测=0（B18 卡书写时的 164 枚暂存删除已被后续 finaldel 系袋处理完）
      - Owner 09-28 已批 O-6"批（归档式）：字节全在 HEAD 可回取"（recovered_final_reconciliation_checklist:174）
      - 事件链在库：e8999a1593b（O-6 登记 171→164，自家 7 枚已 restore）+ad7111b1379（O-1..O-6 四栏呈批）
      - C461/C462（_working 10 件/全仓 175 件在册被删定性）枚举面未复得，登记缓议不执行

  B13_attached_f51_crypto_retirement:
    verdict: DONE-CROSSCHECK
    evidence:
      - 核现状：F51 币圈退役=挂起等 Owner 通知（99_owner_gate.md §挂起表 #2，2026-09-30 st-finaldel-retire 登记"不代裁"）——裁定#431 批的是"六件非币圈退役先归档后删"，币圈面刻意排除，批文前提与本卡"已批"表述不符，以在册更严口径为准
      - 落登记已由 st-finaldel-retire 完成（挂起表+表头通知清单 11 处），无需重复动作

commits:
  - 8954523b7f B8 翻译册三条悬空净删
  - b7c3aa0a81 B10 退役排班落册
  - ae952d32 B11 windows_service deprecated 标记
  - 7bdf98e8 B13 裁定#438+99#36 已裁
  - f3030556 B15 空壳表挂账 2 张
  - a8697815 B17 裁定#439/#440

merge_state:
  status: DEFERRED-拥堵登记
  branch: ai/st-nightsweep2-nb2-20260930/nightsweep2-nb2（worktree= .worktrees/st-nightsweep2-nb2-20260930，禁 abort——6 commits 未落 dev）
  diff_surface: 恰 6 文件（merge-base=d2446aff07 实测），与 dev tip 零内容冲突
  blocker: 主区 407 脏面中 13 件他会话在飞件（config/flags.yaml、e0z_commit_chain 族、pg_probe.py 族等）被 git merge 安全拒写——两会话重试均同果；非本车道内容问题，禁代 stash/checkout 他会话文件
  next: 主区脏面清偿后由总筹/收尾班执行 session_worktree.py merge st-nightsweep2-nb2-20260930 --yes 单动作即落

lock_release:
  lock_files: CLEAN（release-all 完成，无残留）
  ruling_claims: claim_438/claim_439/claim_440 全部同 commit 原子登记消费（#438/#439/#440 在册分支）
  next_ruling_check_branch: 分支册 256 entries 最大 #440 无悬空（dev 侧合并后同步）

evidence_dir: .runtime/tmp/st-nightsweep-20260929/NB2_evidence/
  # schtasks_all_20260930.csv（430 任务全量）/postsettlement_task_{detail,def}/restartminiqmt_task_{detail,def}/双删除回执/事件腿注入验证脚本及输出/B8 删条脚本/B10 排班脚本/B13 裁定脚本/B15 挂账脚本/B17 裁定脚本

yielded_lanes:
  - realtime_snapshot 表（B15）→ st-zc9-lane-d #19 域（避让图领地，未挂账未建腿）
  - data/config/tasks.yaml 全程零接触（lane-d 领地；9 表均无现成采集腿，无建腿需求）

blocked_registered:
  - B7：S4 簿灭失（源名单不可复得，禁代选）
  - B12：96 册清盘清单不可定位（零字节对拍不删）
  - B14/镜像树：备料簿重建独立施工波（R0 部分已在岗）
  - B14/165GiB：等归档处方
  - B18/C461-C462：定性枚举面未复得
```
