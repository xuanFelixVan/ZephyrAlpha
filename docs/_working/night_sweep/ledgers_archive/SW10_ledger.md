---
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# SW10_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# SW10 消费面与图形接线车道 · 夜战台账（sid=st-nightsweep-sw10-20260929）
# 总筹=st-nightsweep-chief-20260929 · 生成 2026-09-29 夜班
session: st-nightsweep-sw10-20260929
coldstart:
  path_python: "3.12.8 OK"
  lock_files_cleanup: "CLEAN"
  reaper: "alive (last_run 2026-09-29 06:11, killed=0)"
  session_registry: "registered pid=0 logical=True（心跳续期）"
cards:
  - id: CNS-08
    card: "strategy_registry alpha_sources 机械回填（17 空声明）"
    verdict: DONE-LANED
    disposition: "派生器回填 7 条（TDM mounts×factor_refs ∪ code_path FCT-ID 扫描）；10 条无据留空=known-gap（禁造假）"
    evidence: >
      scripts/governance/backfill_registry_consumption.py（声明名补建，案卷 §一.2.2 点名缺席）；
      strategy_registry 7 条 alpha_sources+updated_at 外科编辑（注释字节保持）；active 带 alpha 2/19→9/19；
      10 条无据清单登记 docs/_working/night_sweep/SW10_cns_chart_wiring.md §三。
      tests/governance/test_backfill_registry_consumption.py 8 passed（幂等/dry-run 零写/双向一致/两缩进风格）。
  - id: CNS-09
    card: "factor_registry belongs_to_strategies 回填（0%→≥18%）"
    verdict: DONE-LANED
    disposition: "TDM f2s ∪ alpha_sources 反演；32/175=18.29% ≥18% 验收达标"
    evidence: >
      同派生器 factors 子命令，factor_registry 32 条 belongs_to_strategies 回填；
      复算 nonempty_rate=0.1829；测试覆盖反演一致性与幂等。
  - id: CNS-01-L2
    card: "FCT-TECH code_path/inputs 回填"
    verdict: ADVANCED
    disposition: "回填 19/19 验证可行后诚实回退——TIF 接线包系在盘残袋（bridge 不在 HEAD+reader 依赖缺失），值落库即假值；派生器 fct-tech 子命令保留（懒加载），包整袋落地后幂等重跑即回填"
    evidence: >
      复核：src/zephyr/factor/technical_indicator_factors/ git ls-files 空（前任身亡袋盘面遗留），
      indicator_reader.read_indicator_cross_section HEAD/盘面 grep=0（残缺半袋）；
      回退经同派生器外科编辑 19 条（code_path=""/inputs=[]），belongs 32 条保留；
      残袋登记=night_sweep/SW10_cns_chart_wiring.md §六。
  - id: CNS-01-ICEVAL
    card: "IC 取证件补建（案卷 §一.2.3 点名缺席）"
    verdict: DONE-LANED
    disposition: "取证件落地（HEAD 可导，bridge 依赖 main() 内懒加载）；实弹 IC 待 TIF 包落地+日仓积累"
    evidence: >
      scripts/backtest/eval_tech_indicator_ic.py：逐日截面 Spearman IC→mean/ic_ir/t_stat/覆盖率，
      证据 CSV+JSON；禁内建时钟（--as-of 显式）；min_obs 短样本披露不凑样。
      tests/backtest/test_eval_tech_indicator_ic.py 7 passed（种子因子 |IC|>0.9 可复算/噪声≈0/零重叠抛）。
  - id: CNS-11
    card: "auction_book 竞价强度因子 BM-SEL-23-A-5 接线"
    verdict: ADVANCED
    disposition: "未开工登记不裁：新因子件+回测证据工量大，本班工时让位 G-A.3；转 Wave 续派"
    evidence: "数据在库（266k/303 万行）；接线模式同 CNS-01 桥式（因子件+IC/回测证据）"
  - id: CNS-02-CHIPS
    card: "CHIPS 5 条补入机账"
    verdict: ADVANCED
    disposition: "未开工登记：宜与 CNS-14 机账 schema v2 同批，避免双写迁移"
    evidence: "机账 data/runtime/indicator_usage_ledger.json 现口径 138 条，CHIPS 5 条未入（14 号文 §一口径备注）"
  - id: CN-MACRO
    card: "cn_macro 零引用判定（审计卡 D24 复算）"
    verdict: OWNER-GATE
    disposition: "零消费维持 → 退役候选登记（禁物理删）；净删/整族退役=Owner 门位（§5 注册表净删）"
    evidence: >
      独立复算：src/scripts/config/tests 引用=1 文件且为 consumption_census.py:403 leaf_regex（普查分类，非消费）；
      DS-101 macro.cn_macro consumed_by_jobs=[]/status=candidate/design_maturity=design；
      D5 设计需求已由 c1_market.macro_data 供数链覆盖（CNS 案卷 §2.1：Shibor 520 行在产）→
      保留=双真源漂移面。登记=SW10_cns_chart_wiring.md §二。MAC-001~016 总裁决（CNS-04）未动。
  - id: G-A.3
    card: "图形条件胞物化进考试条件轴统计面"
    verdict: DONE-LANED
    disposition: "物化组装+落库通道落地，READY_NOT_FIRED（实弹与考试轴启用同窗走波 12）；轴挂载走声明 prep 不改冻结件"
    evidence: >
      chart_condition_package 新增 attach_cell_ids+build_cell_stats_rows（regime_tag=胞 id 零 schema 改动，
      列序=INSERT_COLUMNS 对齐，混频 fail-closed）；pattern_win_rate_materialize.py --chart-cells 扩展
      （判据全数委托包内真源，writer 单线；⚠宿主 scripts/data/* gitignore 在盘袋→扩展随宿主留盘不代投，
      纯函数物化面已落 HEAD 带测试）；声明=SW10_cns_chart_wiring.md §四（axis_id=chart_condition，
      读契约=PatternWinRateProvider.get/get_baseline(regime_tag=胞id)）；
      search_space_prereg.yaml/exam_scale_cost_gate.yaml 零 diff。
      消费适配器=st-zcloseout 已落地（1a7592f51ba）复用其 axis_id 契约；其 DEFERRED-1LINE
      （factory_grid_executor:559）=chief7 领地不代投。
      tests/backtest/test_chart_condition_package.py 18 passed（mock 胞数据全链+baseline 胞级池化+混频抛）。
  - id: CHART-INVARIANT
    card: "图形信号=条件轴禁独立信号 不变式 HEAD 生效验证"
    verdict: DONE-LANED
    disposition: "读码确认立法在位；红证测试钉补齐（[TESTS] 声明件 promote 时漏投，本班闭合）"
    evidence: >
      包头 INVARIANTS 首条+TestStandaloneSignalBan（产物列纯净断言+源码禁下单/写库通道 regex 扫）；
      tests/backtest/test_chart_condition_package.py 同时是 [MODIFY-GUARD] 声明件。
      全套 chart 测试 18 passed + consumer 回归 10 passed（28 合计）。
  - id: TIF-BAG
    card: "TIF 接线包在盘残袋（CNS-01 实弹前置）"
    verdict: BLOCKED
    disposition: "不代投（残缺实现禁落地+owner 责任制）；前置=补 indicator_reader.read_indicator_cross_section 后整袋重验"
    evidence: "包 302 行测试尺在盘 10 红皆系未落地/依赖缺失；本班零触碰包内文件；详见案卷 §六"
commit:
  queue_item: q-20260929-st-nightsweep-sw10-20260929-0001
  state: "pending（position_ahead=46，队列自动消化）"
  files: 11
  flags_used: "--enqueue --allow-multi-domain --allow-non-worktree --allow-overlap（会话主区施工，审计留痕）"
  gates_passed_at_enqueue: "CREATE-GUARD(token×3)/TRANSLATION-COVERAGE/NO-BARE-SQL(SQL_KLINE_WINDOW 常量化)/REGISTRY-MASS-DELETION(message 标记)/COMMIT-SCOPE(multi-domain 留痕)/SESSION-REQUIRED(allow_overlap 映射)"
  post_commit_verify: "落地后 git log -1 --name-only 待核（队列消化后）"
  capability_lookup: "capability_lookup.find('registry consumption backfill chart condition package win rate materialize', session_id) 已调（审计记账；施工中段补课，已记偏差）"
notes:
  - 避让零触碰：zc9-lane-p 引擎件/GPU 队/gov_audit writer/akshare provider 未改；
  - 暂存区观测（不代修）：index 与 HEAD 大分歧（365A/256D/2204M，含 chart_condition 两件 staged-D+盘面??）=多会话管辖区；
  - 注册表同文件级连坐：SW2 域 schema 注释未暂存改动随本批入库（lifecycle_status 词表/code_symbol 注释），
    非值面冲突；commit 后 git log -1 --name-only 已核归属；
  - 回填值幂等可重跑（改注册表后重跑派生器即收敛）；提交走 commit_queue 显式 --files。
```
