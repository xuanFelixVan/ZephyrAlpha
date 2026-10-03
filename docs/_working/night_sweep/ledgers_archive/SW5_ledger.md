---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# SW5_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# SW5 全流通业务链车道 · 夜战台账（sid=st-nightsweep-sw5-20260929）
# 总筹=st-nightsweep-chief-20260929 · 生成 2026-09-29 夜班
session: st-nightsweep-sw5-20260929
coldstart:
  path_python: "3.12.8 OK"
  lock_files_cleanup: "CLEAN"
  reaper: "alive (last_run 2026-09-29 03:47, killed=0)"
  session_registry: "registered pid=0 (逻辑session, TTL 心跳续期)"
cards:
  - id: C09-M1-f125
    card: "卡1 M1封矿第一批 · F125 data_governance"
    verdict: DONE-LANED
    disposition: "三选一=能接线（有消费者缺装配）→ 接线+测试"
    evidence: >
      alt_source_bootstrap.build_governance_triple 新增 lineage_tracker 参，缺省内建 LineageTracker
      并以 tracker.add_edge 注入 AltDataCatalog.lineage_sink——attach_lineage 由 Fail-Closed 抛错转
      真实血缘落边；zephyr.data_governance 生产 import 0→1（AST 口径首条真实 PROD 消费边）。
      红样 3 测（注入落边+上下游贯通/缺省自建不抛/直构不注入仍 Fail-Closed）；
      tests/zephyr/data/test_alt_sources.py 29 passed；tests/alt_data/+lineage_tracker 回归 455 passed。
      queue=q-20260929-st-nightsweep-sw5-20260929-0001
  - id: C09-M1-f127
    card: "卡1 M1封矿第一批 · F127 data_eng"
    verdict: DONE-LANED
    disposition: "纯装饰环/零消费 → 退役标记（deprecated+successor 注记）；物理净删=OWNER-GATE"
    evidence: >
      包 __init__ 落 [DEPRECATED]（AST PROD=0+零触发+cold_data_archive_manager 与 F08
      scripts/ch/archiver.py 双实现）；successor=scripts/ch/archiver.py（F08 现役冷储链）。
      OWNER-GATE 登记 99_skipped_for_owner.md #42（safe_write_text CAS）。
  - id: C09-M1-f128
    card: "卡1 M1封矿第一批 · F128 data_security"
    verdict: DONE-LANED
    disposition: "纯装饰环 → 退役标记；无直接继任（F88/F105 异域不并）→ 空缺转 known-gap 语义"
    evidence: >
      [DEPRECATED] 落包 __init__（PROD=0 且无 TC 腿/零挂载/零任务；M1 SourceType 消费腿=同名假阳性）。
      OWNER-GATE #43（净删或补接线二选一待裁）。
  - id: C09-M1-f130
    card: "卡1 M1封矿第一批 · F130 ml_serve"
    verdict: DONE-LANED
    disposition: "纯装饰环 → 退役标记；successor=F129 ml_train serve 腿"
    evidence: >
      [DEPRECATED] 落包 __init__（PROD=0/TC=0/无反射装配；serve 现役=F129 default_inference_engine
      被 intelligence/model_evaluation 实消费）。model_drift_monitor 双同名件（gov_drift 68 行 vs
      ml_serve 269 行）=登记不裁（裁-6 分母活边）。OWNER-GATE #44（净删+clone 判定待裁）。
  - id: G16-F62
    card: "卡2 F62 SettlementReconciler 违宪整改"
    verdict: DONE-LANED
    disposition: "违宪链定位（计划任务周时钟）→ 仓内事件触发腿+幂等日终 sweep+测试；任务退役=OWNER-GATE"
    evidence: >
      违宪链=ZephyrAlpha_PostSettlement（-Weekly Mon-Fri 15:30）→run_post_settlement.py→SettlementReconciler
      （本体无时钟，违宪在装配层）。事件腿：post_settlement_pipeline 新增 TOPIC
      post_settlement.recon.requested/.swept + subscribe_eventbus（幂等，共享总线单例，premarket 同款）
      + run_daily_end_sweep（同 trade_date 进程内去重，重放零副作用；force 逃生）+
      register_sweep_deps（未装配=UNWIRED 不伪跑）+ boot_hooks 消费方挂载。测试 6 新例
      （事件注入两次同日 emit→下游一次+回执 OK/REPLAYED；幂等重放零副作用；UNWIRED；
      订阅幂等；退订隔离），文件 14 passed；settlement 族回归 58 passed+boot_hooks 2 passed。
      过渡安全=时钟腿与事件腿并存（CLI 数据级幂等+sweep 进程级去重）。OWNER-GATE #45
      （schtasks 任务退役+AutoRuntime 重启运维窗）。gov_audit/writer.py 零接触（无依赖，grep 证）。
      queue=q-0002
  - id: C50-F34
    card: "卡3 F34 DDL#21 三步验证决策"
    verdict: DONE-LANED
    disposition: "DDL 形态=纯 CREATE IF NOT EXISTS 幂等加法 → 路径①执行（备份面验证→apply→首跑）；pf_alloc 消费=案卷自处方二期"
    evidence: >
      apply_l9_readiness_ddl.py dry-run 自校验 exit 0（无 DROP/ALTER/TRUNCATE）；
      三步验证：必要性=表不存在实证 / 真实性=CH 26.6.1.1193 活 / 可逆性=纯建空表；
      备份面=G:/backup/ch_vm_backup/data.vhdx mtime 09-28 01:39 在。
      --apply 建成 c1_market.l9_readiness_daily（ReplacingMergeTree 10 列，DateTime64(3)+显式时区）。
      首跑：dry-run 39 行（本夜无超时，前账疑虑未复现）；写跑 action=throttled=幂等闸实证；
      表内 234 行（09-15/24/28）。pf_alloc 消费=零接线→按 05_f34 卷缺3 处方归二期
      （allocation_inputs readiness 检查仿 anchored_cap），已入 phase2 挖矿卡体系。
      另：apply_market_tables_ddl.py（1336L）判读=纯幂等（108 ADD COLUMN IF NOT EXISTS+
      10 CREATE IF NOT EXISTS，0 破坏性）但非 F34 范围未执行，留属主车道自验。
      留痕：scripts/ch/apply_market_tables_ddl.py.tmp.22232.2a300814c75d 中断残留 tmp 件在盘
      （Wave 3 清理项登记）。
  - id: C31-recon
    card: "卡4 intake_ledger_recon rebuild 对账"
    verdict: DONE-LANED
    disposition: "check=drift 如实报；rebuild 全台账预演=0 候选，无需 --apply"
    evidence: >
      check：lane_b missing_in_csv=[CAND-x]（1 行）；three_high 14 行 missing_in_ch（未审=正常态）
      +CSV 31 重复（CSV 侧卫生）；lane_chain ok。rebuild 预演（lane_b/three_high/lane_chain）：
      rebuild_candidates=0——lane_b 唯一缺行 CAND-x 被内容寻址校验拒收（"CH 行 id 与假说原文不符"，
      CH 侧占位脏行；拒收机制按设计工作）。零写盘。CAND-x 脏行处置=只登记不删（RULE-DATA-OPS）。
  - id: C29-EC3
    card: "卡5 EC3 复测 CH 活体六项"
    verdict: DONE-LANED
    disposition: "六项读数全落 ec3_water_health_ledger.md §六（claim+CAS）；2 条新 known_data_gaps"
    evidence: >
      ①tilib 绿：stock_indicator/technical_indicator max(trade_date)=09-28（02:30 夜批效果首证）。
      ②ollama 演进红：进程不存在（tasklist rc=1）+11434 不通（前账"进程活API死"→"进程消失"），
      禁杀禁拉起（99 #4 在案）；nightly_sentiment_llm.enabled 旗仍开，LLM 不可达走 llm_fallback。
      ③kline_sector_intraday 红维持：max=09-22 15:00 未涨（tdx 断供未愈）。
      ④三空表 0 维持：account_nav_daily→新登记 known_data_gaps（writer 零调用方=从未接线，
      无腿可开禁新建源）；edb_data=既有条目在案（iFind 配额退役；卡面 etb_data 系前账本表笔误，
      CH 无 etb_data 表，已注记）；etf_benchmark=zc9-lane-d 换源域让路零触碰。
      ⑤NightlySentiment 黄：规则单源兜底成立；09-28 08:20 槽位缺跑一日→新登记
      nightly_sentiment_batch_missed_20260928（根因未定位不妄断；调度器本体两日 2902 条活跃）。
      ⑥EvaporationBlackbox 绿：blackbox.jsonl mtime 09-29 04:21 在飞（前账僵尸观察维持）。
      落账：docs/_working/chain_circulation_campaign/ec3_water_health_ledger.md §六 + 
      src/zephyr/data/config/known_data_gaps.yaml 追加 2 条（YAML 校验+CAS）。
      queue=q-0003
  - id: I2-21-F26
    card: "卡6 F26 E7 前哨四缺收尾"
    verdict: DONE-LANED
    disposition: "①提交②注册表原已在位；③事件接线④首跑=本夜补齐（含 schema 漂移修复）"
    evidence: >
      ①提交=HEAD 88f62e893e0 在位；②注册表=module_translation_registry:61493+creation token 双册。
      ③事件接线：pipeline_events OPTIONAL_DUE_KINDS+paper_outpost_due（契约体 run_paper_outpost_due）
      +maybe_emit_monthly 月度档（4 周窗≈30 天 marker 线，零新机制）+handler 成功才触 marker+
      CLI emit choices。④首跑（--dry-run 安全面）：暴露真缺陷=前哨 SQL equity_change 列在
      sim_pocket_daily schema 真源不存在（Code 47×20 日，fail-visible not_evaluable=契约正确）；
      修 argMax(daily_pnl, ingest_ts)（schema:38 当日盈亏=sim_paper_ledger:207 同口径）；
      修复后 coverage=1.0 verdict=pass continue_sim（2 幸存者账实相符）。测试 4 新例（22 passed）
      +pipeline_events 回归 42 passed。queue=q-0004。
      登记不代修：tests/strategy_pipeline/test_daily_gate_snapshot_l5.py=未跟踪在途件（导入
      _read_external_kill_switch_state 不存在于 HEAD），他会话 WIP 零触碰。
  - id: PHASE2
    card: "卡7 二期序列只挖不干"
    verdict: ADVANCED
    disposition: "7 张挖矿卡落盘+token 七件已登记；commit 被 R5-DIGIT-SUFFIX 结构性阻断→登记+跳过（§四.8）"
    evidence: >
      产出：docs/_working/night_sweep_20260929/phase2_{F53,F04,F73,F75,F92,F30,F05-F06}.md
      （各卡=六向台账快照转抄真源案卷+Wave2 施工处方可干/Owner 门分列+工量合计约 10-15 人日）。
      CREATE-GUARD token 七件登记 capability_canonical_file_registry（ASCII slug+
      merge-evaluation 按 裁#375）。BLOCKED 原因：R5-DIGIT-SUFFIX fail-closed 拦
      docs/_working/night_sweep_20260929/ 目录名（_\d+$ 后缀）——总筹 00_orchestration §一指定路径
      与门禁结构性冲突（目录未入 HEAD=新违规必拦；既定豁免只认 HEAD 已存在目录=先有鸡先有蛋；
      SW1 同目录件同样 staged 未落）。处置：禁 --skip-preflight 硬闯；文件安全在盘+token 在册，
      落地解法归总筹/SW1 目录属主（规则修订或目录更名或豁免登记），我方文件随其决议同车。
      next: 总筹裁目录名后 git_commit 正门直落（文件零改动）。
queue:
  enqueued: ["q-0001(6 files)", "q-0002(4 files)", "q-0003(2 files)", "q-0004(3 files)"]
  status_at_handover: "4 项 pending 排队（他队 16-34 项在前），快照零丢失，serializer 自动消化"
  post_commit_verify: "落地区须按宪法 §2.5 git log -1 --name-only 核实归属（本轮 4 袋均为显式 --files 清单）"
handoffs:
  - "OWNER-GATE #42/43/44/45 已入 99_skipped_for_owner.md（F127/F128/F130 净删候选+F62 任务退役）"
  - "known_data_gaps +2 条（account_nav_daily/nightly_sentiment 09-28 缺跑）"
  - "EC3 六项读数段已追加（交接 ②ollama 演进态/③tdx 断供未愈/⑤09-28 缺跑根因 日班接手）"
  - "Wave2 七卡待总筹派发（F34 缺3 pf_alloc 消费随卡体系）"
  - "R5-DIGIT-SUFFIX × 总筹指定目录名冲突待裁（卡7 落地前置）"
  - "scripts/ch/apply_market_tables_ddl.py.tmp.* 中断残留件（Wave 3 清理）"
```
