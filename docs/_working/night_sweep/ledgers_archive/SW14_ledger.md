---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# SW14_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# SW14 CNS 第二批与图形 writer 车道 · 夜战台账（sid=st-nightsweep-sw14-20260929）
# 总筹=st-nightsweep-chief-20260929 · 生成 2026-09-29 夜班
session: st-nightsweep-sw14-20260929
coldstart:
  path_python: "3.12.8 OK"
  lock_files_cleanup: "CLEANED（2 死锁清理）"
  reaper: "alive (last_run 2026-09-29 07:41:28, killed=0)"
  session_registry: "registered pid=0 logical=True（心跳）"
  capability_lookup: "CapabilityLookup.find ×4 已调（chart condition package / pattern win rate / indicator usage ledger / 综合关键词），全部 0 命中=施工面无既有能力卡，审计已记账"
cards:
  - id: G-A.3-WRITER
    card: "writer 宿主裁定执行：物化 writer 并入 tracked 区（总筹预裁定）"
    verdict: DONE-LANED
    disposition: >
      库函数+CLI 落 src/zephyr/backtest/regime_validation/chart_cell_materializer.py（tracked），
      scripts/data/pattern_win_rate_materialize.py 降薄壳委托（盘面件 gitignore 保持，CLI 面兼容）。
      修正 SW10 盘面版三颗在盘雷（READY_NOT_FIRED 未实弹故未爆）：
      ① load_condition_pack 两轴包误引喂 attach_cell_ids（实弹必 KeyError family）→改
      ChartPackRequest 真源；② stack() MultiIndex 级序 (trade_date,symbol) 误按
      (symbol,trade_date) 解包；③ INSERT_COLUMNS 系 SQL 字符串片段被当列名元组迭代。
    evidence: >
      证尺 tests/backtest/test_chart_cell_materializer.py 7 passed（mock conn/base_pack/
      fake insert 零 CH 全链+INSERT 定序+错误契约+禁内建时钟）；包既有证尺回归通过；
      包 __init__ 单行 import 挂 ORPHAN；新 .py 三件套齐（token[随 q-0001]/翻译/depgraph
      节点 15387765）。批次：token 独立批 q-…-sw14-0001（在队）；内容批 A2 待 sw10-0002
      落地后重投（依赖其 attach_cell_ids/build_cell_stats_rows/_STATS_COLUMNS 真源——
      HEAD 现版 chart_condition_package=st-c7-resc lineage B，无 G-A.3 函数集）。
  - id: CNS-14
    card: "机账口径升级 schema v2（代码引用 vs 文档引用分列）"
    verdict: DONE-LANED
    disposition: >
      indicator_usage_audit 降薄壳委托 consumption_census 族①（census 头注/reconciler
      自述"旧模块降为薄壳"的承诺落地，内收 w5_1 同真源必并）；机账 schema /3：
      consumer_files 分列 code_refs（扫描面代码消费者计客）+doc_refs（文档提及只作证据位）。
      病根复盘：旧实现 registry_path.parents[3] 只取到 docs/（catalogs 下第 4 级父）——
      生产机账只扫过 docs/ 树，旧账 26 active 全是对文档/注册表 yaml 的提及
      （扫描根错位=第一病根，文档计客=第二病根，IND-REV-001 同案）。
    evidence: >
      真跑实测：143 全覆盖 counts=active 27/zero 115/retired 1（与 census 族①直跑逐位
      一致）；CHIPS 5 条诚实重判全 zero（旧账 CHIPS-001/002 active=文档假阳性）；
      IND-REV-001 retired+12 处 doc_refs 证据位。证尺 3 passed（三态+doc-only 红证+
      签名契约）。批次 q-…-sw14-0002（在队；注：其快照为 parents[4] 修前一版，落地后
      需补差批——工作区当前版=parents[4] 修正+注释复盘版）。census 本体缺陷（默认
      repo_root 推导差一级取到 src/）已绕开未代修（属主=其他车道），披露于终账 §五。
  - id: CNS-02-CHIPS
    card: "CHIPS 5 条补入机账（消费活性听证）"
    verdict: DONE-CROSSCHECK
    disposition: >
      入册面=st-zcloseout 批已落（机账 143 条含 IND-CHIPS-001~005，updated_at 2026-09-29）
      ——交叉验证不重做；本班补其诚实重判：v3 口径下五条全 zero（零代码消费），
      retire_candidate 登记禁删（转绿路径=D21 获利盘接线后幂等重跑）。
    evidence: "data/runtime/indicator_usage_ledger.json v3：CHIPS-001~005 state=zero，doc_refs 4/3/0/0/0；SW10 台账'CHIPS 5 条未入'已被 zcloseout 批消化（时序交叉验证）"
  - id: CNS-11
    card: "auction_book 竞价强度因子 BM-SEL-23-A-5 接线"
    verdict: DONE-LANED
    disposition: >
      查询装配件 src/zephyr/factor/auction_strength.py（装配/查询路径，打分委托 youzi
      引擎 score_auction_strength 真源，禁造新指标；PIT 严格前序日基线；缺昨收/基线=
      None 禁拍中性值——daban_load_producer 不可产字段清单之竞价条补源）；IC 取证件
      scripts/backtest/eval_auction_strength_ic.py；实弹 IC 证据产出（不显著=如实，
      FCT-INTRADAY-031 维持 candidate 不晋级）。
    evidence: >
      实弹（CH 只读）：窗 2026-07-21~2026-09-26，25 日中 15 有效日（>=30 截面，10 日短
      截面如实弃），120,549 行打分/81,015 行有效（缺昨收/基线=None 不凑样）；
      IC=-0.0219/ICIR=-0.266/t=-1.03（5% 水平不显著）。证据=
      docs/_working/night_sweep/sw14_auction_ic_evidence/（daily_ic.csv+summary.json）。
      证尺 8 passed。三件套齐（token×2+翻译+depgraph 15387770/15387771）。
      factor_registry 注册条目 FCT-INTRADAY-031 编辑已备
      （.runtime/tmp/st-nightsweep-20260929/sw14_apply_fct_intraday_031.py，幂等补丁），
      受 sw10-0002 袋 factor_registry blob 序约束，待其落地后执行+随 B2 批提交。
      daban 决策链 T 日竞价喂入=声明接线点（策略侧盘中通道，非 T-1 负载批产字段——
      PIT 语义裁定留模块头 CONSUMERS）。
    commit: "q-…-sw14-0003（在队，6 件含两注册表纯追加）"
  - id: CNS-CLOSEOUT
    card: "CNS 消化度终账"
    verdict: DONE-LANED
    disposition: >
      全九族 census 重跑（2026-09-29，production ledger 落 data/runtime/
      consumption_census_ledger.json）：grand active 287/zero 473/retired 5；
      族① 143=27/115/1（对照 14 号文基数 24/114→26/117：口径修正非漂移，
      病根=扫描根错位+文档计客）。CNS 14 条逐条对账：已接线 5/登记让路 5/
      OWNER-GATE 3/BLOCKED 1（CNS-01 残袋前置）。
    evidence: "docs/_working/night_sweep/cns_closeout_ledger.md（token 随内容批）；退役候选全部只登记禁删（CN-MACRO 维持 SW10 §二登记+CHIPS 5 条+族⑩ residual 61+族⑤ macro zero 15 等，净删=Owner 门位）"
  - id: CN-MACRO
    card: "cn_macro 零引用维持性复核（SW10 OWNER-GATE 项）"
    verdict: CROSSCHECK
    disposition: "重跑维持 zero（11 处文档提及不计客）——SW10 退役候选登记维持，净删待 Owner；不重裁"
    evidence: "census ⑤族 macro zero=15；cn_macro census 行 state=zero doc_mentions=11"
  - id: SW10-BAG-RESCUE
    card: "SW10 死袋代维（q-…-sw10-0001 cascade_stale）"
    verdict: DONE-LANED
    disposition: >
      死因=cascade_stale（stale-by sw8-0003 后已 done=死因消）；按宪法 §2.6 requeue
      --from-bag 从死信 blob 快照重放（新 qid=q-…-sw10-0002，FIFO 队尾）——11 件含
      chart_condition_package G-A.3 函数集/18 测证尺/回填器/IC 取证件/CNS-08/09
      注册表回填值。工作区缺失的 4 件（backfill/eval_tech 等）内容在袋零丢失。
    evidence: "commit_queue requeue 输出 REQUEUED -> q-20260929-st-nightsweep-sw10-20260929-0002；死因与快照 blob 清单见 dead/q-…-0001.json"
commit_queue:
  items:
    - "q-…-sw14-0001 token 独立批（capability_canonical_file_registry，1 件）— 已出队未见落地 commit（疑 C1 合批吸收），token 条目已重追加随 A2 批兜底"
    - "q-…-sw14-0002 CNS-14 机账薄壳（2 件）— pending（快照=修前版）"
    - "q-…-sw14-0003 CNS-11 接线批（6 件）— pending"
    - "q-…-sw14-0004 消化度终账（2 件）— pending"
    - "q-…-sw14-0005 CNS-14 parents[4] 增量修正（1 件）— pending（紧跟 0002 后回正）"
    - "q-…-sw10-0002 SW10 死袋重放（11 件）— pending（本班代维 requeue）"
  post_commit_verify: "全部落地后逐袋 git log -1 --name-only 核归属（维护班/后续班次续做）"
handoff_followups:
  - id: FOLLOWUP-A2
    when: "q-…-sw10-0002 落地后（attach_cell_ids/build_cell_stats_rows/_STATS_COLUMNS 进 HEAD）"
    do: >
      入队 A2 内容批：src/zephyr/backtest/regime_validation/chart_cell_materializer.py +
      __init__.py + tests/backtest/test_chart_cell_materializer.py + 两注册表（token/
      translation 条目已在工作区，pure-append 姿势；若被他袋落地卷走则 checkout HEAD--
      两册后重放 batch_creation_tokens/add_module_translation 再投）。
      git_commit.py --session st-nightsweep-sw14-20260929 --files <上述清单> --enqueue
      --allow-multi-domain --allow-non-worktree --allow-overlap。
      落地前先 python -m pytest tests/backtest/test_chart_cell_materializer.py（7 测）。
  - id: FOLLOWUP-FCT031
    when: "q-…-sw10-0002 落地后（factor_registry blob 先行防回卷）"
    do: >
      python .runtime/tmp/st-nightsweep-20260929/sw14_apply_fct_intraday_031.py（幂等补丁，
      插 FCT-INTRADAY-031 于 INTRADAY 族尾）→ 与 factor_registry.yaml 单件批提交
      （同 session --files docs/01_policies_and_standards/_registry/catalogs/factor_registry.yaml）。
  - id: FOLLOWUP-VERIFY
    do: "全部落地后：git log --grep=sw14 逐袋 git show --name-only 核归属；pytest 三套（chart_cell_materializer/indicator_usage_audit/auction_strength×2）复跑连绿"
notes:
  - 避让零触碰：zc9 各车道/gov_audit writer/GPU 队/akshare provider 未改；
  - 多会话工作区曾两度回卷本车道 tracked 修改（队列 stash 隔离/他袋落地波）——新建未跟踪
    件幸存，tracked 修改靠队列快照零丢失，重投后全数恢复；
  - 注册表提交姿势改用 HEAD 基线+纯追加（git checkout HEAD -- 后重放 token/翻译），
    采纳 92b3256fd01/sw6/sw8 吸收先例，REGISTRY-MASS-DELETION 门拦截验证有效；
  - 临时补丁 sw14_apply_fct_intraday_031.py 存 .runtime/tmp/st-nightsweep-20260929/
    （临时区合规），执行后可清理；
  - pytest 长批零启动（全部单测秒级，无 reaper keep 需要）。
```
