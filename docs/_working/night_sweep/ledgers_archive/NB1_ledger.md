---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# NB1_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# NB1 B组退役候选价值挖矿车道 · 台账
# sid=st-nightsweep2-nb1-20260930  总筹=st-nightsweep-chief-20260929
# 卡源=Owner 本夜裁定（B组删东西不能只看全仓零引用，每条过三审：价值/真源唯一含全网/数据持续性）
# verdict 词汇: DONE-LANED(hash) / ADVANCED(状态+next) / BLOCKED(因) / OWNER-GATE(登记) / CROSSCHECK
# 本车道铁律：零删除零退役执行——只产出挖矿裁定卡（docs/_working/night_sweep/b_audit/ 六件）

lane: st-nightsweep2-nb1-20260930
worktree: D:\ZephyrAlpha\.worktrees\st-nightsweep2-nb1-20260930
started: '2026-09-30'
cards:
  - id: NB1-B3
    obj: ml_serve 四件+model_drift_monitor 双同名件
    verdict: CROSSCHECK
    evidence: 物理净删已被 st-finaldel-retire 先行执行（5ccc4c3cf1+42d286d116，8 件归档
      G:/zephyr_cold/retire_c267_20260930/F130_ml_serve/ 逐件 sha256）；本卡=终审追认：
      被删 269 行四维漂移监控（PSI/JS/性能/IC）设计价值高（全网 Evidently/alibi-detect/NannyML
      无四维合一现货），复活落点=ml_train 非 ml_serve；冷储已达成，零追加动作
    card: docs/_working/night_sweep/b_audit/nb1_b3_ml_serve_drift_monitor.md
  - id: NB1-B5
    obj: CN-MACRO 宏观指标整族 16 条（MAC-001~016）
    verdict: ADVANCED(保留+接线处方 R1-R5 交 NB2/数据道；entry_count 15≠16 漂移已记)
    evidence: 活源=c1_market.macro_data akshare 291K 行+macro_vintage.py PIT 通道在册；
      edb_data 断供≠族死；TDM-E-L1-S0 Owner 裁定背书四组信号全上；缺的是映射+消费两根线
    card: docs/_working/night_sweep/b_audit/nb1_b5_cn_macro_family.md
  - id: NB1-B6
    obj: CHIPS 5 条+族⑩ residual 61+族⑤ macro zero 15
    verdict: ADVANCED(三档分层交 NB2/C 道；CH 不可达故 DROP 全部挂 live 三步验证前置)
    evidence: CHIPS=已量化已验收零下游，转绿路径=D21（chips_winner 不依赖流通股本可先行）；
      macro zero 15 并入 B5 卡；residual 61=59 zero_ref+l2_tick+edb_data 推导口径，
      A 直接可退≈20/B 储备≈35/C 待 live 复核≈6（DS-002 ohlc_bar 疑似 kline_daily 前身）
    card: docs/_working/night_sweep/b_audit/nb1_b6_indicator_retirement_groups.md
  - id: NB1-B1
    obj: F127 data_eng 16 件 vs F08
    verdict: ADVANCED(件级处置单交 Owner 门 #42-44 裁定时并用；sla_breach_predictor 融合待批)
    evidence: 取代关系成立（F08 完胜，与 INFRA-STORE-003 一盘一责同向）；九件逐件头注级尽调：
      唯一融合建议=quality_sla_breach_predictor（迁 data/quality 给归档 SLA 做 burn-rate），
      其余 8 件删除(归档后)/储备；gpu_resource_manager 留 GPU 队备注
    card: docs/_working/night_sweep/b_audit/nb1_b1_f127_vs_f08.md
  - id: NB1-B2
    obj: F128 data_security 三件（脱敏引擎/访问审计/AI 脱敏管线）
    verdict: OWNER-GATE(建议翻案：known-gap→接线复活；两接点行号级方案已给)
    evidence: L1-L4 分级+purpose 查表+审计回调与全网 gateway 前脱敏最佳实践吻合；
      接点①=LSGSecurityGateway.scan_input(:214) 前包装层（零侵入）；接点②=dashboard
      api_server 响应序列化层+规则册 YAML 真源；若不接则净删+归档 G 盘
    card: docs/_working/night_sweep/b_audit/nb1_b2_f128_data_security_wiring.md
  - id: NB1-B11/B15/B16
    obj: windows_service/空壳表/blueprint 附带复核
    verdict: CROSSCHECK
    evidence: B11 保留（蓝图背书+M02/M10 豁免在案，服务路线废止归 Owner 门）；
      B15 维持先归档后 DROP+etf_benchmark 翻案移出净删名单；
      B16 整族保留（548 份蓝图=MODIFY-GUARD 真源链），空壳子集另立分诊卡
    card: docs/_working/night_sweep/b_audit/nb1_b11_b15_b16_quick_review.md
commit:
  hash: 1a5521db4f（worktree 分支 ai/st-nightsweep2-nb1-20260930/nightsweep2-B-lane-mining）
  files: 7（六卡+capability_canonical_file_registry token 6 条同袋）
  state: DONE-LANED(1a5521db)——git log -1 --name-only 归属核实无误
  route: 前手 q-0001/q-0002 两袋均死于 landing WinError 233（管道瞬断，与 r3 车道 q-0005/6/7
    同签名三连=今夜基建级已知病），按 3117cdd41d 载明的 66 号死信闭环处方改直提正门
    （--no-auto-enqueue，b985b1e35b/97046b15c3 先例）
  merge: DEFERRED——session_worktree merge 干净中止（主区 flags.yaml/commit_chain_fullflow/
    pg_probe 等=他会话在途 WIP，按宪法 §3.4 禁代碰）；分支留存，主区静后由总筹或本车道补 merge
  claims: 全部已 release（网关 finally+逐件确认）
deviations:
  - 文件名首版大写违反 N-13 snake_case，已改名+册内 6 条目 CAS 移除重登（before/after sha256 留 safe_write 审计）
  - capability_lookup 留审计（macro/masking/chips 0 命中，drift 1 命中）
  - CH VM 172.24.30.100:9000 本夜 SocketTimeout 不可达（与 C267b 记录一致），行数类判读全部降级为文档真源+live 复核前置
next: NB2 按 B5-R1-R5/B6 三档/B1 件级单/B2 两接点处方开工；Owner 门 #42-44 并用本卡 B1/B2 结论
```
