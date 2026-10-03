---
gate_selfdoc: GIT-DANGEROUS
ttl: task_bound
completes_when: 夜巡台账抢救归档使命完成（c1核销与追溯证据已可查，随本战役归档保留）
---
# T1B6_ledger

> [等值证据封装] 原件为 .yaml 台账。2026-10-04 凌晨投影割接过渡期：新 .yaml 的 creation_token 无法落 HEAD（REGISTRY-YAML-PARSE 投影指纹门武装于未播种账本+意图API未接线，详见 full_circulation_closeout_20261004/99_delivery.md 呈报），故按目录契约以 .md 等值封装（yaml 原文逐字节内嵌于代码栅栏，可逆向提取）。全量188件原件冷库：F:/zephyr_cold/night_sweep_ledgers_raw_20261004/

```yaml
# T1-B6 三档指标处置车道 · 夜战台账（sid=st-menu-t1b6-20260930）
# 总筹=st-nightsweep-chief-20260929 · 菜单执行夜 · 生成 2026-09-30
session: st-menu-t1b6-20260930
coldstart:
  path_python: "3.12.8 OK"
  setup_dev_env_check: "usercustomize installed (points to D:/ZephyrAlpha)"
  lock_files_cleanup: "CLEANED（回收死会话 st-menu-t1b1/t1b5/t1f2 遗物）"
  reaper: "alive (last_run 2026-09-30 21:37:28, killed=0)"
  session_registry: "registered（worktree create 时自动登记，heartbeat daemon pid=31464）"
  worktree: "D:/ZephyrAlpha/.worktrees/st-menu-t1b6-20260930 branch ai/st-menu-t1b6-20260930/task-t1b6-indicator-disposal"
  capability_lookup: "CapabilityLookup.find ×3（指标退役 data asset registry/筹码 winner 获利盘/龙虎榜 采集 akshare）全 0 命中=施工面无既有能力卡，审计已记账（LOOKUP_AUDIT_DIR）"
owner_batch_留痕:
  原文: "①b 档（无持续数据源档）：先全网搜索有没有数据源，搜到就可以接入使用，搜不到才冷归档；②a 档批接线（CHIPS 5 条绑获利盘 D21）；③c 档批删（每条删前过实数据三步验证）。"
  落册: "docs/_working/night_sweep/99_nightsweep2_final_report.md B 组 NB1 行（本批同车）"
cards:
  - id: T1B6-A-CHIPS-D21
    card: "a 档：CHIPS 5 条绑获利盘 D21 接线现状核查"
    verdict: ADVANCED
    disposition: >
      D21 未就绪判实：获利盘接线面不存在（chip_distribution_engine.py 零 winner/获利/CYQ 命中，
      末次实质变更=3dcfe9dd079 裁定#257④ 回 trial；TDM-E-L3-12-3 算法注维持挂起；机账 v3
      CHIPS-001~005 state=zero）→ 按批文二分逻辑执行"保持 candidate+登记'绑 D21 批文已下待其就绪'"。
      新事实登记：stock_daily_basic.float_share 7,107,404 行（max trade_date=2026-09-30 当日）在产
      ——裁定#257④ 挂起前提"需流通股本数据工程"的数据腿已通；CYQ winner 本不依赖流通股本。
      就绪判据=chip_distribution_engine 增补 winner 剖面直调 chips.py::CYQ+TDM 注更新+机账幂等重跑
      回填（SW14 处方①②）。登记面=b6_source_search.md §6+99 报告 B6 行+本台账。
      零改 technical_indicator_registry（evidence 字段语义=回测证据 IC，不挪作批文登记，防语义污染）。
    evidence: "grep winner/chips/CYQ on chip_distribution_engine.py=0 命中；git log 末次=3dcfe9dd079；CH 只读实测 float_share>0 行=7,107,404/max=2026-09-30；机账 v3=SW14 台账 CNS-02-CHIPS 记录"
  - id: T1B6-B-SOURCE-SEARCH
    card: "b 档（无持续数据源档）逐族数据源全网搜索+处置"
    verdict: DONE-LANED
    disposition: >
      口径：b 档=residual-61 非死工具伴生 38 条（矿卡 B 档 32+C 档 6），macro 15 归 B5 车道零触碰。
      6 轮 WebSearch 实搜（财务三表/龙虎榜/股本股东/申万+ST/alpha 因子开源实现/图形族/业绩预告披露/daily_basic）。
      结论三态：有源 32 条（9 族；18 条真身已活=CH 活表继任 income_statement/balance_sheet/cashflow_statement/
      financial_indicator/disclosure_plan/earnings_forecast/express_report/restricted_shares/st_stock_list/
      sector_constituent_sw_history/stock_daily_basic 等；派生型 ashare 14+图形 3 开源公式参照；
      纯外源型 lhb_detail=akshare stock_lhb_detail_em）；无源 6 条冷归档（DS-002/040/056/057/070/075
      →deprecated+successor 注记，禁物理删；schema 枚举无 archived 故取 deprecated，已在册注记）。
      接入实施面核查：采集腿唯一注册点 src/zephyr/data/config/tasks.yaml+akshare_provider.py 均为
      st-zc9-lane-d 避让领地（#20 换源+#19 域在飞）→ 本夜出处方不施工（b6_source_search.md §5 四条处方，
      F5 lhb 优先），移交采集腿 owner 班次。
    evidence: "落卡 docs/_working/night_sweep/b_audit/b6_source_search.md（token 批 39af6551 先行）；WebSearch 6 轮记录在卡 §2（akshare/tushare/开源库来源全列）"
  - id: T1B6-C-RETIRE
    card: "c 档：19 条死工具伴生表批删（三步验证+注册表退役）"
    verdict: DONE-LANED
    disposition: >
      逐条三步验证全过：必要性=CH 五库 system.tables 全库精确扫描 19 表零命中+本地四 sqlite 库与
      data/ 文件树零命中（59 条零引用表物理上从未物化，全为 2026-08-13 设计态登记）；
      真实性=两通道独立读数一致为 0+producer 路径缺失（barra/data_eng services/factor/mine 等目录不存在）
      或 B12 判装饰（backtest services 代码在而 result 表从未落库）；
      可逆性=data_asset_registry.yaml git revert 整批可回滚+G 全条目原文快照双保险。
      执行：退役 19 datasets（DS-041~049,051~055,060~064）+19 companion jobs（JOB-040~048,050~054,059~063）
      +SRC-INTERNAL-001.provides_datasets 摘除 19 id+entry_counts 实数修正（293→275/122→103，293 系预存
      漂移）+version 1.9.9。[allow-mass-deletion] 正门，逐条清单进 message。
      零连坐核验：src/config/scripts/tests 对 19 DS id 零引用；PG depgraph dataflow_datasets 无 40~65 号行
      （从未同步）；panorama_alignment_gate 触发面不含 data_asset_registry.yaml。
      留观：JOB-049（输出 DS-050 本就不在册）、legacy dataflow_graph_registry.yaml（过渡保留件含同名
      19 datasets，其退役归引用迁移跟进项）、l2_tick（0 行）与 edb_data（已不在 CH）随 B15 通道。
    evidence: "census 快照 .runtime/tmp/st-nightsweep-20260929/t1b6_ch_census.json；G 留档 G:/zephyr_cold/retire_t1b6_20260930/（manifest+datasets_snapshot_19+jobs_snapshot_19）；提交袋 q-20260930-st-menu-t1b6-20260930-0001（3 件）"
  - id: T1B6-D-BATCHLOG
    card: "批复落册"
    verdict: DONE-LANED
    disposition: "Owner 本夜批复原文+执行终态回填 99_nightsweep2_final_report.md B 组 NB1 行（同袋落地）"
    evidence: "msg_t1b6_main.txt §四"
commit_queue:
  items:
    - "q-20260930-st-menu-t1b6-20260930-0003（4 件）— DONE→落地 commit 6186bcceb6（dev）：卡+token+99 报告行+注册表部分落地（provides 清理+6 deprecated）；⚠️19+19 删块被串行器丢弃（57 行 vs 袋快照 -1230 行）"
    - "q-20260930-st-menu-t1b6-20260930-0002（token 册基底重整）— DONE（noop@0c20042f，内容已含于 0003 同批）"
    - "q-20260930-st-menu-t1b6-20260930-0001（3 件初版）— dead（CREATE-GUARD：token 在 worktree 分支未进 dev）；已按 §2.6 修正重投"
    - "q-20260930-st-menu-t1b6-20260930-0004（删块补齐首投）— done 但落地=noop@56846cd7（bag base=worktree-HEAD blob 与 dev 漂移→串行器 fail-safe noop）"
    - "q-20260930-st-menu-t1b6-20260930-0005（dev-exact 基底重投）— dead：队列三路合并器吞没大删量内容（死因原文'合并结果与 dev 零变化，内容被合并器吞没'）——可复现串行器缺陷，已录维护班线索"
landing_终态:
  dev_已落: "6186bcceb6=b6_source_search.md（token b6-source-search-b6-source-search-20260930 在册）+99 报告 B6 行批复落册+data_asset_registry 部分（SRC-INTERNAL-001.provides_datasets 摘 19 id+6 条 deprecated+successor 注记）；dev 现_HEAD_=68fe30bd5f（他会话后续推进）"
  dev_待落_一键收尾: "git checkout -- docs/01_policies_and_standards/_registry/catalogs/data_asset_registry.yaml && git merge --ff-only session/st-menu-t1b6-20260930（等价=cherry-pick 7aea69ca13）；内容=19 datasets（DS-041~049,051~055,060~064）+19 jobs（JOB-040~048,050~054,059~063）退役+entry_counts 293→275/122→103+v1.9.9"
  待落_artifact_三重: "①session/st-menu-t1b6-20260930 分支 commit 7aea69ca13（=dev 68fe30bd5f 直接子代，ff 即落）②ai/...task-... 分支 c7628f15 ③袋 blob .runtime/commit_queue/blobs/9397ea88（q-0004 快照）+G:/zephyr_cold/retire_t1b6_20260930 快照"
  待落_阻塞因: "主区 .git/index.lock 持续被队列 drain 守护占用+主区工作树存该文件陈旧还原（f96e10c7=落地前原版，无独有信息，安全可 checkout 恢复）——跨车道环境阻塞，按铁律 8 登记+停"
infra_findings_维护班:
  - "IF-1 队列串行器对'大删量 hunk'袋两种坏行为：6186 部分施加（-1230 行袋只落 57 行）/q-0005 合并器吞没（'合并结果与 dev 零变化'）——建议 drain 侧对 blob 级快照袋改用 checkout-blob 而非 hunk 合并，或落地后按袋 blob sha256 自证读回"
  - "IF-2 主区工作树存在 data_asset_registry.yaml 陈旧还原（f96e10c7=6186 落地前原版）——疑 drift watchdog 快照回灌时序；已验证无独有信息"
  - "IF-3 session_worktree_start 重建登记会另创 .aidrafts/<sid> worktree+session/<sid> 分支（与首次 create 的 ai/... 分支命名不一致），merge 工具只认 session/<sid>——同会话双分支易致 merge 落空（本次实证）"
post_commit_verify: "6186bcceb6 已核（4 文件+注册表部分态逐项 yaml 断言）；待落块由收尾人按上面一键命令落地后同断言复核（275/103/v1.9.9/6 deprecated/provides 54 项）"
followups:
  - "【移交维护班·一键】落地 7aea69ca13（ff 或 cherry-pick）——内容已三步验证+G 快照，见 landing_终态.待落_一键收尾"
  - "采集腿接线（F5 lhb 优先）：tasks.yaml+akshare_provider 归 st-zc9-lane-d，避让期满后按 b6_source_search.md §5 处方施工"
  - "D21 就绪后：chip_distribution_engine winner 剖面（直调 chips.py::CYQ 禁第二实现）+TDM 注更新+机账幂等重跑回填转绿 CHIPS 5 条"
  - "legacy dataflow_graph_registry.yaml 19 同名 datasets 摘除=引用迁移跟进项"
  - "JOB-049 悬空（输出 DS-050 不在册）+DS-305=stock_daily_basic 已在册（b 档 DS-086 successor 佐证）：归下次 data_asset 册治理批"
notes:
  - "interpretation 留痕：任务 a/b/c 三档映射=a=CHIPS 5/b=residual-61 非死工具 38 条按族搜源/c=矿卡 A 档 19 条批删；macro 15 归 B5 车道零触碰（矿卡明文）"
  - "CH live 普查实证 59 表从未物化（非空表待 DROP 而是无表可 DROP）——c 档落地=注册表条目净删，无 CH DDL 动作，数据文件零存在"
  - "claims 已全释放（data_asset_registry RELEASED/99 报告 NOT FOUND=已过期自清/technical_indicator_registry 未改未占）"
notes:
  - "interpretation 留痕：任务 a/b/c 三档映射=A档(CHIPS)/B档+C档(residual-61 非死工具 38 条按族搜源)/矿卡 A 档 19 条(批删)，与矿卡三分层（CHIPS/residual61/macro15）及菜单 B6 行一致；macro 15=矿卡明文'归 NB1_B5 卡'且 B5 车道（st-menu-t1b5）存在，本车道零触碰"
  - "b 档'search 到源'分支=接入处方+登记（实施面被避让图阻断，零施工），'搜不到'分支=6 条冷归档——两条分支均有执行"
  - "矿卡'CH 复活后 DROP'语义升级说明：CH live 普查实证 59 表从未物化（非空表待 DROP 而是无表可 DROP），故 c 档落地=注册表条目净删（数据文件零存在，G 快照即全部留档），无 CH DDL 动作"
```
