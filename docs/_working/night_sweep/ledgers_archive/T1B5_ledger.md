---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# T1B5_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# T1-B5 宏观指标复活车道台账（st-menu-t1b5-20260930，总筹 st-nightsweep-chief-20260929）
# Owner 本夜批复：CN-MAC 整族不退役，按 R1-R5 处方复活接入（挖矿底稿=nb1_b5_cn_macro_family.md）
session: st-menu-t1b5-20260930
date: 2026-09-30
worktree: D:/ZephyrAlpha/.worktrees/st-menu-t1b5-20260930

verdict: DONE-LANED
commits:
  token_batch: 9ec1ae0f6e   # CREATE-GUARD token 2 枚独立批（macro-indicator-series-map + macro-regime-sensor，带 merge_evaluation）
  main_batch: q-20260930-st-menu-t1b5-20260930-0002  # 6 文件袋（映射表+传感件+测试+TDM+指标册+翻译册），入队时点已过全预检，落地哈希见 done/q-...-0002.json

deliverables:
  R1_map:
    file: config/macro_indicator_series_map.yaml
    verdict: DONE-LANED
    evidence: >-
      MAP-MAC-SERIES-001 v1.0：16 条逐条映射 c1_market.macro_data 实有序列码；
      12 wired（CH 实测新鲜度快照 2026-09-30 入册）+3 missing（CN-002/008/010）
      +1 meta（CN-016）；组声明真源（四组+权重）随表。
  R2_pit_read:
    file: src/zephyr/regime/features/macro_regime_sensor.py::read_macro_indicators
    verdict: DONE-LANED
    evidence: >-
      as_of=None 走现值表 FINAL（live 3040 行实测）；as_of 给定走 macro_vintage.PIT_LATEST_SQL
      （pub_ts<=as_of；vintage 覆盖外序列如实缺席=回补终值不参与 PIT 的设计语义，实测零抛错）。
  R3_consumer:
    file: src/zephyr/regime/features/macro_regime_sensor.py
    verdict: DONE-LANED
    evidence: >-
      MOD-REGIME-MAC；四组信号→滚动分位(36月窗)→方向修正→组内均值缺员降权→加权天气分 0-100
      →caution_factor 确定性阶梯；月/周采样同一 read 视图（月线定 regime/周线确认，不另建管线）；
      TDM-E-L1-S0 module_ref 改指本件；live 实测 weather=41.2/neutral、月聚 1644 行、周聚 2926 行、
      214 月天气史（末段 2026-06=47.1 neutral → 2026-07=34.5 cautious → 2026-08=58.3 neutral）。
  R4_fred:
    verdict: DONE-CROSSCHECK
    evidence: >-
      R4 处方四序列（FEDFUNDS/DGS10/PAYEMS/VIXCLS）经既有 macro_fred_incremental+fred_provider
      全覆盖（21 序列在产，实测新鲜至 2026-09-29），零新管线零新表——处方目标已被既有腿满足。
  R5_registry:
    verdict: DONE-LANED
    evidence: >-
      macro_indicator_registry.yaml v1.2.0→v1.3.0：entry_count 15→16（NB1 漂移①销口，
      实核=CN-001..011+US-001..004+CN-016 共 16 条，CN-012..015 空号）；12 条 wired 转 active
      （used_by+=macro_regime_sensor）；CN-002/008/010 源缺保 candidate+核验结论；
      CN-016 meta 保 candidate。safe_write_text CAS（base_sha+allow_mass_edit 显式）+进程外复核。

data_source_verification:  # R1 车道令：16 条逐条核验
  MAC-CN-001: {source: akshare, series: "全国-同比增长", status: 源活, freshness: "2026-08-31"}
  MAC-CN-002: {source: akshare, series: null, status: 源缺（PPI 未挂 job，lane-d 领地让路）, transfer: T1B6}
  MAC-CN-003: {source: akshare, series: "制造业-指数", status: 源活, freshness: "2026-09-30"}
  MAC-CN-004: {source: akshare, series: "GDP_同比", status: 源活, freshness: "2026-06-30"}
  MAC-CN-005: {source: akshare, series: "社会融资规模增量", status: 源活但源端截断, freshness: "2026-04-30（ingest 09-30 仍成功=上游 akshare 仅供到 4 月，非我方腿断，如实登记）"}
  MAC-CN-006: {source: akshare, series: "货币和准货币(M2)-同比增长+M1 aux 剪刀差", status: 源活, freshness: "2026-08-31"}
  MAC-CN-007: {source: akshare, series: "LPR_1年", status: 源活, freshness: "2026-09-20"}
  MAC-CN-008: {source: akshare, series: null, status: 源缺（MLF 未挂 job；TDM 挂载 8 条唯一缺数据条目，传感件缺员降权）, transfer: T1B6}
  MAC-CN-009: {source: akshare, series: "国债_10年", status: 源活, freshness: "2026-09-30"}
  MAC-CN-010: {source: akshare, series: null, status: 源缺（贸易差额未挂 job）, transfer: T1B6}
  MAC-CN-011: {source: fred, series: "FRED_USDCNY(DEXCHUS)", status: 源活, freshness: "2026-09-25"}
  MAC-US-001: {source: fred, series: "FRED_FEDFUNDS_US", status: 源活, freshness: "2026-07-01（美联储利率 akshare 腿 2025-10 停更=FRED 侧接管）"}
  MAC-US-002: {source: fred, series: "FRED_DGS10_US", status: 源活, freshness: "2026-09-28（备胎 akshare 美国国债收益率10年 至 09-30）"}
  MAC-US-003: {source: fred, series: "FRED_PAYEMS_US", status: 源活, freshness: "2026-07-01"}
  MAC-US-004: {source: fred, series: "FRED_VIX(VIXCLS)", status: 源活, freshness: "2026-09-28"}
  MAC-CN-016: {source: registry_meta, status: meta 条目不映射数值}
  edb_data_结论: >-
    表恒 0 行=iFind EDB 配额耗尽 2026-08-14 整体退役（#ARCH-DATA-IFIND-RETIRE-001 在案；
    车道令中"FRED 源恒 0"假设不成立——edb_data 从非 FRED 源）。源死不可修（需重订阅 iFind），
    空壳表处置归 T1B6（本车道只登记，未动其注册表条目）。
  fred_结论: >-
    FRED 腿活着且新鲜（macro_fred_incremental/macro_fred_full_refresh 在 tasks.yaml:3107/3124，
    fred_provider 22 序列定义、21 序列在产，FRED_API_KEY 在配）。NB1 底稿"SRC-FRED-001 无活 fetcher"
    系底稿时点后已建（本车道 crosscheck 修正）。

yield_register:  # 让路登记（夜战避让图）
  - file: src/zephyr/data/implementations/akshare_provider.py
    reason: st-zc9-lane-d 领地；3 条缺序列（PPI/MLF/贸易差额）补 job 需改其 _fetch_macro_data
    handoff: 后继班次按映射表 status=missing 三条的 reliability_note 补采腿，产出名回填 series_code
  - file: src/zephyr/data/config/tasks.yaml
    reason: 同上领地；本车道零改动需求（既有 macro_data/macro_fred 任务面已足）
  - 社融源端截断/回购腿 2025-12 停更/央行_* 日期解析疑似异常/美联储利率 akshare 腿 2025-10 停更:
    reason: 均 akshare_provider 内部腿问题=lane-d 领地，让路登记不移交 T1B6（属数据腿维修非分层处置）

tests: {count: 18, result: 全绿, path: tests/regime/features/test_macro_regime_sensor.py, mode: mock 数据路径零 CH}
lint: {ruff_format: 过, ruff_check: 过}
registrations:
  translation: module_translation_registry.yaml +macro_regime_sensor（主仓+worktree 同步入册）
  depgraph: apply_depgraph.py --add-design-node MOD-REGIME-MAC（node_id=15758387，架构库直写）
  creation_token: 2 枚（9ec1ae0f6e 先行独立批落地）

incidents_and_fixes:
  - 会话活性三坑：裸 register 记录当前进程 PID→进程退即判死；heartbeat daemon 被=reaper 误杀（keep 册补登 heartbeat_daemon st-menu-t1b5-20260930）；SESSION-REQUIRED 需 pid=0+daemon 双齐
  - 令牌提交入队后 CLI 挂起 25 分钟空转+重复死袋一封（CAS 竞态 q-…-0001 死信=落地后重复落地尝试，非内容丢失）——已终止失控进程；改用预检全过后再入队的节奏
  - CREATE-GUARD 落地仿真态从分支 HEAD 读册→worktree 分支基点早于 token 落地=假红；merge dev 后消除
  - NO-BARE-SQL/TRANSLATION-COVERAGE 均为真问题真修（SQL 常量化+翻译条目 worktree 册补写）
  - safe_write_text 批量转正触发 mass-edit 防呆→R5 处方授权显式 allow_mass_edit 留痕

cross_lane_notes:
  - TDM 仅动 TDM-E-L1-S0 节点 module_ref/module_id 两行+注释（claim+safe_write 纪律）
  - 主仓 module_translation_registry.yaml 有他会话 staged/unstaged 在途内容——本车道未触碰未提交，按 owner 责任制留原状；本车道翻译条目经本袋落地
```
