---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# SW15_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# SW15 门禁定性小件打包车道台账
# sid=st-nightsweep-sw15-20260929，总筹=st-nightsweep-chief-20260929
# 生成：2026-09-29 夜战；verdict 纪律=铁律7（id/verdict/evidence）
session: st-nightsweep-sw15-20260929
cards:
  - id: 卡1·15门逐台定性（实数以现册为准=22台）
    verdict: DONE-LANED(q-20260929-st-nightsweep-sw15-20260929-0001 入队待落地)
    distribution: "退役登记 22 / 装载 0 / 存根 0（G-81 时点 15 台；现差集 22 台，新增 7 台为 P4 合并后新现形）"
    evidence: >-
      G-81 尺复跑：磁盘声明 123 − 名册装载 104 = 22 台差集（f08 记录 15 为 09-28 时点）。
      逐台定性=全部 22 台均系 2026-09-23 st-gslim P4 七簇合并吸收台（gate_audit_report_v1 §C2，
      Owner 全批 E 既批=退役登记在案）：REFERENCE-INTEGRITY←{DANGLING/ARCH/RULING-REFERENCE}、
      PERMANENT-SYSTEM-TRIGGER←{PERM-TRIGGER/MANUAL-ONLY-PERMANENT}、GATE-VOCAB←{VOCAB-HARDCODE/VOCAB-CHAIN}、
      DEPGRAPH-ENFORCEMENT←{PRE-REGISTRATION/NEW-FILE/RENAME-SYNC/WRITE-PATH}、
      MAP-ALIGNMENT←{PANORAMA/BATTLE-MAP/DECISION/FRONTEND/INDUSTRY-CHAIN/FACTORY}、
      BLUEPRINT-HEADER←{AMODULE-CONSISTENCY/AMODULE-CROSS-CHECK}、COMPLEXITY-GUARD←{HIGH-COMPLEXITY/GOD-CLASS/LONG-PARAM}。
      七聚合器子判据接线逐台读源验证（REFERENCE-INTEGRITY._union_check 实调 ruling_reference_gate._check 等，
      subs 元组 3+2+2+4+6+2+3=22 全数在册）⇒ 执法无真空，"无人装载"系册面假象非执法缺口。
      假象复活根因=generate_gate_registry.extract_commit_gates 每文件只取首个 gate_id：
      独立薄工厂文件首匹配=自身 id 时 MANUAL_GATES 墓碑被遮蔽→统一册恒假 active（15 台），
      合并宿主文件首匹配=聚合 id 时墓碑生效（7 台）——同一机制两种命运的分流水实测。
      治本=三源合并改墓碑覆盖优先（id 未回装名册时墓碑胜出，已回装者让位防误墓活门）：
      统一册 15 台 active→deprecated+redirect_to，悬空镜头 16→1（残 1=COMMIT-CRITICAL-SECTION-LOCK
      系裁定#347 _GlobalCommitLock 机制实名登记 active 设计态，镜头不可见非真悬空）。
      红证=HEAD 态机械复放 15 违例（新旧测试同款断言对 HEAD 册数据全红）→修后绿；
      回归测试 test_manual_tombstones_override_disk_shadowed_entries 新增；
      生成器套件 34 绿+face_reconciliation 9 绿+sys_master_compliance 12 绿；total_gates=183 不变。
      观察留档：GATE-VOCAB/PERMANENT-SYSTEM-TRIGGER 两聚合台 enabled=false（Owner B 方案临时禁用，
      名册注"187 件落地后恢复"）⇒ 其下 4 子台执法暂空窗=既批状态非新缺口；
      in_process 名册仍挂 BLUEPRINT-FORMAT enabled=true 薄工厂（T8 簇2 域，与统一册 deprecated 撞=双执法疑点，
      属 st-commitspeed 域未代修）。

  - id: 卡2·W-133..136 四件回流骨架
    verdict: ADVANCED(W-133 CROSSCHECK/W-134 部分落地 q-0002/W-135 DONE-LANED q-0003/W-136 DONE-ADJUDICATED)
    evidence: >-
      W-133（candidate 007 同袋序）=CROSSCHECK 让路：SW3 袋 q-…-sw3-0004 在队已验（007 重编号完整、
      外部引用经 HEAD grep 证=撞号案卷描述面非 ID 消费，单文件袋成立）。
      W-134（snapself/EV 红测转绿）=四腿走三：snapself 7 绿+_DESTRUCTIVE_GIT_VERBS 有实体+黑匣子 EV-01
      强化 3 绿（他会话/先前袋已落，crosscheck）；EV CLI 腿=我落地 q-0002（ops_guard 补 sh_rm_recurse
      原语：rm -rf 误入 PS 别名分支致 targets=[] 判"非保护区"放行=案根命令 rc=0 失守实证；修后 rc=1 拦截，
      red_team 102 绿）；EV-02 三件（_git_wt 钉死/TOCTOU/fail-closed 审计）=BLOCKED-让路：
      commit_queue_landing.py 有他会话在途暂存（B0/M1·P3 integrity 58 行），宪法 §3.4 不代修已登记。
      W-135（密钥门触发面改型）=DONE-LANED q-0003：BARE-SUBPROCESS/NO-BARE-GETENV/NO-SECRET-HARDCODE
      三台 files_trigger 死触发（password/api_key 路径子串 0+0 命中，dossier_F 9-R4b）→空触发面（无条件）
      +门内新增行内容判定（三门均只扫 added 行+tests 豁免）；红证 _files_trigger_hit 修前 False/修后 True，
      三门测试 98 绿；名册 CAS safe_write 落盘；SW11 同册三袋已落无基底漂移。
      W-136（dead_archive 89 件入库定策）=DONE-ADJUDICATED 不入库：
      .runtime/commit_queue/dead_archive_metaq_gc_20260926/ 89 件 JSON 996K 系 runtime 死信取证态
      （.gitignore 设计内；代码零引用；知识已提馏入 dossier_F X-42/X-44/9-R4）；
      与 X-44 先例同型"保留盘面仅供回读"；入库反而违 .runtime 生命周期隔离设计。可随时逆。

  - id: 卡3·10_d_data.md 行数引用核验
    verdict: DONE-LANED(q-20260929-st-nightsweep-sw15-20260929-0004 入队待落地)
    evidence: >-
      文件在=docs/02_enterprise_architecture/02_domain_architecture_docs/10_d_data.md 实际 19,364 行
      （引用 19,037→+327 漂移，今晨 08:24 仍被写=活文件；gitignored by .gitignore:541 该域整体未跟踪
      =X-52 口径成立，Z-37"入库"支仍开放）。六处引用中五处未决面（93 册菜单项8/00 册 W-59/
      01 册 Z-37 两处/_MASTER_INDEX W-59）已补带日期复测注记〔SW15 2026-09-29 复测 19,364〕不篡改历史实测；
      02 册 X-52 与 dossier_F 为当时证据记录不动。Z-37 入库工程（19k 行拆册避 FOLDER-CAPACITY 120 限）
      不在本卡范围，留终报。

  - id: 卡4·H35 波2 C 类复核（#417 12 项已批项）
    verdict: DONE-VERIFIED(12 项逐件复核查 HEAD；销账 8/OWNER-GATE 4/工程开放 2)
    evidence: >-
      吸收源=裁定#417（AI 层 12 项补批文，09-28 补票）；#414=tick 保留期与 12 项无交集（无销账来自 #414）。
      逐件（键路径已按实际落位修正报告旧路径）：①C6 八轨=半落地缺口——washer.py:164 消费端在 HEAD，
      但 model_routing_policy.yaml 全史（git log -S 全 refs）从未含 ai_layer_routes 段→八轨静默走默认，
      且该文件现被 st-c9-purify 在途锁定→让路登记（工程待办=补配置段，非 OWNER-GATE）；
      ②口径 0.7 销账（HEAD switch_criteria.yaml:92）；③外扫宿主销账+启用=OWNER-GATE（ps1 在 HEAD 未注册任务）；
      ④L7 design_final 销账；⑤confirm_gate.py+tests 在 HEAD 销账，接线禁令（W6-C 三雷修前）=工程开放；
      ⑥tool_sandbox_profile.yaml 在 HEAD 销账；⑦双真源已收敛销账，红四类目残余=工程开放；
      ⑧ai_secret_exposure.py+tests 销账，get_secret 断言通电=OWNER-GATE；⑨墓碑 TTL 销账；
      ⑩S3 普查器在 HEAD 销账；⑪白名单首批销账（94_chief_rulings_wave2 AI-2 认可+test_kpi 消费），扩面=OWNER-GATE；
      ⑫FSM 销账（语义项禁区）。

  - id: 卡5·R-1..R-7 移交清单复核
    verdict: DONE-VERIFIED(销账 3/未覆盖列入终报 4)
    evidence: >-
      R-1 叶子册=ADVANCED 未完：leaf_books 现 9 件（f02/f04/f05+f06/f08/f09/f10/f11），
      原 7 缺口补齐 5（06/08/09/10/11），仍缺 f07/f13/f14（列入终报）。
      R-2 d5 五图=销账：scripts/governance/d5_architecture/ 模块族+config 六本 *_map.yaml 在 HEAD。
      R-3 热册增量=基本销账：translation 册已净；残余=capability_canonical_file_registry.yaml 有一会话
      worktree 改动在途（他道领地让路）。R-4 死信处方扩面=销账（96 册 L77 实录 63 处方族 100% 覆盖）。
      R-5 旗标名不匹配=仍开放（HEAD 实测 flags.yaml:109 gate_precommit_run vs gateway:382
      gate_precommit_run_enabled；d5 图已带"未注册×default=True⇒恒 ON"实录注记；真修=改 gateway 常量
      对齐在册键+同批改 d5 生成器叙事+重生成图——跨面施工列终报配方）。
      R-6 越界清单=未覆盖（原 5 件明细不在 96 册内、322 处 miniQMT 提及无法机械对判，列终报需原清单）。
      R-7 磁盘=OPEN 恶化：D 盘现余 23.1G（记录时 ~35G），commit_queue 7.2G→8.1G；
      减压涉删除面=OWNER-GATE（终报标红）。

session_meta:
  cold_start: "Python 3.12.8 PATH 修正/reaper 存活(07:47:29)/lock cleanup CLEAN/session_worktree_start 注册+worktree .aidrafts/st-nightsweep-sw15-20260929"
  queue_bags: "q-…-0001(3件 卡1)/0002(1件 W-134 CLI)/0003(1件 W-135)/0004(4件 卡3) 全部 pending 在队（正门快照零丢失，传送带消化）"
  avoidance_respected:
    - "commit_queue_landing.py（他会话 B0/M1·P3 在途暂存 58 行）未碰"
    - "config/model_routing_policy.yaml（st-c9-purify 锁）未碰"
    - "capability_canonical_file_registry.yaml（他道 worktree 改动）未碰"
    - "GPU 队/st-zc9 各领地零接触"
```
