---
ttl: task_bound
---

施工会话 AI-GOVA-001。任务：治理批 A 包（Owner 2026-08-17 裁定派单，与 AI-RFIX-001 文件级零交集实证——你域=governance/scripts/tests/governance+regime 单文件，禁碰 risk/pf_alloc/ex_core/position 域 RFIX 施工面）。
worktree 已由统筹创建：D:\ZephyrAlpha\.worktrees\AI-GOVA-001（分支 ai/AI-GOVA-001/task-governance-batch-a，自 dev aaa570ea70 切出）。进入后 `. .\activate_env.ps1`。

范围（六项，逐项真源引用）：
1. **Z1+Z2 退役脏工作区强制 patch 存证+派生活水三分类器**（CAND-WORKTREE-001）：
   - 真源=docs/01_policies_and_standards/_registry/catalogs/candidate_module_registry.yaml L6384-6409（条目全文含验收标准）
   - 背景裁定书=docs/_working/audit/architecture-reviews/2026-08-16-test-debt-leftover-adjudication.md（Z1/Z2 节）+ 140 WIP 调查 commit 558fb2ee4b
   - 要点：session_worktree abort/退役时若工作区脏，强制 git diff 生成 patch 存证 refs/quarantine/；派生活水（depgraph 统计块/CRLF 幻影/实质 WIP）三分类器辅助统筹甄别——先例：AI-VCFIX-001 实证 CRLF 幻影 stash 复活（存证无效），分类器应把"git diff 等行互换+EOL 警告"判为幻影零价值
2. **Z3 heartbeat daemon 失锚自退**（CAND-DAEMON-001）：
   - 真源=candidate_module_registry.yaml L6410 起条目
   - 要点：daemon 定期检查锚（worktree 目录/session registry 记录），失锚（worktree 已删/registry 无记录）自动退出——防 #99 类僵尸 daemon 堆积（实证：Z4 已杀 2 个两天残留 daemon）
   - 施工面=src/zephyr/gov_enforcement/rule_bridge/heartbeat_daemon.py（或同等 daemon 实现文件，先 Grep 定位）
3. **#ARCH-114 治理脚本命名前缀/EXIT 常量治本**：
   - 真源=architecture_issue_registry.yaml L16997-17005（#ARCH-114 条目全文含违例清单）
   - 违例实证=tests/governance/security/test_security_scripts.py 2 项 xfail 标记项（validate_script_naming ~20 脚本缺 LEGAL_PREFIXES / validate_exit_codes 17 处裸 return 0/1）
   - 裁定路径三选一（先出对比分析随 commit 说明）：批量改名合法化 / 常量替换 / EXCEPTIONS 豁免登记——命名前缀改动须同步 capability registry + script_manifest + 引用方（Grep 全仓）
4. **tracker #102 regime_detector 文件头顺手修**：
   - src/zephyr/regime/core/regime_detector.py L7 `# [MATURITY] design` → `production`
   - 依据=蓝图 docs/03_modules/_domain_regime/regime_detector/blueprint.md L7 design_maturity=production（C1/Phase 2 均已通过且检测器数据流实际运行，以蓝图为准）
5. **#ARCH-115/116 xfail 标记清除顺手项**（OBE 已转正，标记已无存在意义）：
   - tests/governance/data_layer/test_database_service.py L53/79/89 三处装饰器
   - tests/governance/test_sel_unreachable_5_linkage.py L55-61 fixture 内 pytest.xfail 段
   - tests/governance/depgraph/test_depgraph_generator_design_protection.py L165 装饰器
   - tests/governance/rule_bridge/test_worktree_pool.py 三处装饰器
   - 清除后复跑四文件须 36 项全 passed（零 xpassed 零 xfailed）
6. **watchdog RestartOnFailure 退避**（#99 ②③ 遗留）：
   - 背景=#99 内存耗尽事故：Task Scheduler 的 worktree_drift_watchdog 任务 RestartOnFailure 无退避连环拉起 50 实例
   - 施工：Task Scheduler 任务 XML/注册加退避间隔（RestartCount+RestartInterval 或等效机制），实证 trigger 后不连环拉起
   - fail-open 敞口分析（**只出方案不施工**）：PG 离线时 depgraph 类门禁静默放行（fail-open）是设计内降级还是敞口——出分析报告随 commit（docs/_working/reports/2026-08-17-fail-open-analysis.md），列现状清单（哪些 gate PG 依赖+fail-open 行为）+三选项对比（保持/告警升级/fail-closed）+推荐，供 Owner 裁定

避让：
- AI-RFIX-001 施工面（risk/core/var_calculator.py+tail_risk_monitor.py / position/core/drawdown_controller.py / ex_core/order_manager.py / pf_alloc/core/regime_meta_allocator.py + 对应 4 测试文件 + memo 31/36 + CAND registry + var_calculator blueprint）——零触碰
- AI-LVL3-001（37 号流动性域）/AI-REDIS-001（shared/state_store.py）并发施工中——各自域不碰
- #87 阈值统读（drawdown 域）/ERRCODE-001 改号 不在本包，等 RFIX merge

验收：①Z1-Z3 新增测试 2 轮全绿+既有 governance 套件不回归 ②#114 处置后 test_security_scripts.py 2 项去 xfail 转正 ③#115/116 四文件 36 项全 passed ④#102 一行修零测试影响 ⑤RestartOnFailure 退避实证 ⑥fail-open 分析报告落盘 ⑦Step 1+Step 6（14 节版）双 PASS ⑧全走 GitCommitGateway（[GW:AI-GOVA-001]）
完工反馈六要素：commit hash/Step 1/Step 6/测试轮次/改动清单/遗留项。worktree 保留待统筹统一 merge。
