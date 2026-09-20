---
ttl: task_bound
session: st-dataqa-20260920
audit: dataqa_20260920
---

# R3 · 测试健康度报告（2026-09-20）

> 执行：st-dataqa-20260920（通宵总令·分包B）。只跑测试+编目，**零修码**。
> 跑法：tests/ 全仓 129 个目录域+根级散件=131 个域、3,523 个 test 文件，按文件数配平 3 批
> 并发（批内串行、域内 xdist -n4、每域墙钟 40 分钟时间盒）；tests/governance（636 文件）超时后
> 按子目录拆 90 个子域单独跑齐。逐域日志与计数：`.runtime/tmp/dataqa/pytest/<域slug>.{log,json}`。
> 命令：`python -m pytest <域> -q --tb=short -rEf -n 4`（仓库 pyproject 配置原样生效）。
> 证据等级：本报告数字全部 **[亲验]**（探针实跑）；失败根因逐条开日志核对。

## 0. 一页结论（TL;DR）

1. **总量**：131 域全跑完（含 governance 拆分），**65,311 passed / 68 failed / 16 errors /
   231 skipped / 395 xfailed / 76 xpassed**——失败错误合计 84 条，占 0.13%。
2. **84 条失败错分五类**（逐条开日志编目+flaky 复跑修正，非按名猜测）：
   - **A. 治理门抓到账面漂移 ≈32 条（稳定复现真账）**：D38 未登记库 k 系列+R24 因子欠账+catalogs 门 6 条、
     battle_map 拓扑 3 条、blueprint 陈旧引用 3 条、cron/生成器断言过期 4 条、zephyr SCD2 4 条等；
   - **B. 环境/资源型 ≈35 条**：infrastructure 11e+1f 全部 `WinError 1455 页面文件太小`
     （复跑两轮全部清零实锤）、drift/f_lifecycle/f14/gpu 8 条 worker 崩溃（复跑清零）、
     **trading decision_map 校验 7 条+blind_spot 1 条+path 1 条=测试污染类假红**（独立复跑全绿）、
     shared redis 2 条等；
   - **C. 疑似真 bug/回归 14 条**（见 §3/§2. C 编目，含 f18 子进程挂起 C14）；
   - **D. 并发会话漂移 5 条**：technical_indicators 105≠101——st-tilib-clear 会话新增指标，
     **复跑中该 5 条已消失（基线已同步），自证闭合**；
   - **E. 性能回归 1 条**：L09 回测 P99=1910ms（阈值 300ms；两轮复跑均超，负载相关待空载复测）。
3. **flaky 判定**（失败域同配置复跑 2 轮）：环境资源型复跑全绿（drift 323p/0f ×2 轮、
   governance gate_chain 9p/0f ×2 轮等）；治理账面类全部稳定复现（stable_fail）=真账。
4. **首批意外废案（如实披露）**：首轮跑批命令带 `-p no:cacheprovider`，与仓库 pyproject 的
   `cache_dir` 配置冲突→pytest INTERNALERROR，90 个域 10 秒内假"完成"。发现后停批、修命令、
   清结果、重发——本报告全部数字来自修复后第二轮，首轮废案零数据引用。

## 1. 全域总表

| 指标 | 数值 |
|------|------|
| 域数（tests/ 目录+根散件） | 131（governance 单域 636 文件超时后拆 90 子域跑齐，计入 1 域） |
| 测试文件 | 3,523 |
| passed | 65,311 |
| failed / errors | 68 / 16（合计 84，0.13%） |
| skipped / xfailed / xpassed | 231 / 395 / 76 |
| 40 分钟时间盒超时 | 1（tests/governance 整域，已拆分重跑覆盖） |
| 失败域数 | 19 |

governance 拆分批子域级结果（passed TOP 与失败子域）：

| 子域 | passed | 失败 |
|------|--------|------|
| commit_gates | 2,584 | 0 |
| audit | 1,821 | 1（gate_chain_multiproc 复跑全绿=资源型） |
| rule_enforcement | 511 | 0 |
| rule_bridge | 556 | 2（worktree_pool，复跑=stable_fail，git 分支生命周期类） |
| security | 337 | 2（exit_code 常量门，stable_fail=真账） |
| scripts_governance | 306 | 1（依赖图无环，stable_fail） |
| resilience | 403 / persistence 59 / observability 等 | 0 |
| test_battle_map_research_incubation | 43 | 3（33 步拓扑断言，stable_fail=真账） |
| test_commit_queue_integration | 27 | 1f+1e（worktree/落地集成，环境敏感） |
| 其余 ~80 子域 | 全绿 | 0 |

## 2. 失败编目（84 条逐条，按类归组）

### A 类 · 治理门抓到账面漂移（≈40 条，门=正常工作，修账不修门）

| 域 | 条数 | 失败点 | 真因（日志核对） |
|----|------|--------|------------------|
| tests/trading | 12 | test_decision_map.py（r1_bad_enum/r2_dangling_edge/r3_unknown_strategy_ref/r6×2/R41×2/catalogs gate 等）+ test_decision_map_adversarial（**R24 因子欠账复发**：挂策略节点 factor_refs 又空了） | **flaky 修正**：decision_map.py 校验 7 条+blind_spot 独立复跑全绿=测试污染假红（改 B 类）；稳定真账=R24+D38 k 系列+catalogs 门 6 条 |
| tests/trading | 5 | test_decision_map_d38_adversarial k1/k4/k5/k6 + test_blind_spot_closure | **三个未登记新库**：domain_responsibility_layer_mapping.yaml / fail_open_register.yaml / standard_family_registry.yaml（D38 铁律要求二选一登记） |
| tests/blueprint | 3 | scripts/src 陈旧 "AGENTS.md §编号" 引用（validate_intel_registry.py:10 等） | #355 同族债：§编号引用未改规则名/路径锚 |
| tests/scripts | 2 | resource profile registry 生成器断言（task 名覆盖/21 slots cron 逐字） | tasks.yaml/schedule.yaml 演进后生成器测试基线未更新 |
| tests/frontend | 2 | api_server cron 单源（15 slots 断言） | 同上，schedule 槽位变了 |
| tests/industry_graph | 1 | field dictionary required fields 缺 good/bad examples | 字段字典登记不全 |
| tests/db | 1 | 目录树与文件系统对齐 | 账面漂移 |
| tests/path | 1 | path tree 生成器设计保护 | 账面漂移 |
| tests/autonomy | 1 | G04 三策略注册表与组件 | 账面漂移 |
| tests/governance（子域） | 10 | battle_map 33 步拓扑×3、alert_threshold 总数×1、error_code 注册×1、reconcile_generators×1、externalize_algo_flow×1、vocab_domain_convergence×1、security exit_code×2 | 各治理登记册与设计文档数数对不上（stable_fail=真账） |

### B 类 · 环境/资源型（≈26 条，复跑多消失，不算账）

| 域 | 条数 | 真因 | 复跑判定 |
|----|------|------|---------|
| tests/infrastructure | 12 | **`OSError: [WinError 1455] 页面文件太小`**——conftest psutil 枚举进程/子进程时系统页面文件耗尽（12 xdist worker+CH 回填并发所致） | **独立复跑两轮 2051p/0f 全清零**（每轮仅 1 条轮换偶发错），资源型实锤 |
| tests/drift | 3 | xdist worker 崩溃（gw4/gw5） | **flaky_env**：两轮 323p/0f 全绿 ✓ |
| tests/f_lifecycle | 3 | worker 崩溃 2 条复跑清零；`test_run_idempotent_3_times` 文件级两轮同败=phase_check_registry 子进程挂起（升 C14） | flaky_partial |
| tests/shared | 2 | `[redis]` 参数用例（本地 redis 实例依赖） | flaky_partial（第 2 轮转绿） |
| tests/trading | 2 | worker crash（MemoryError，gpu_consensus/extreme） | 复跑清零 |
| tests/governance | 2 | gate_chain_multiproc（多进程重叠链）+commit_queue_integration 1e | gate_chain 复跑**全绿** ✓（flaky_env）；commit_queue r2 转绿 |
| tests/path+tests/git | 2 | path 设计保护断言/git 8 会话并发 | **两域独立复跑全绿**=顺序敏感假红（改 B 类） |

### C 类 · 疑似真 bug/回归（13 条，逐条已开日志，留证据待工单）

| # | 测试 | 现象（亲验日志） | 初步定性 |
|---|------|------------------|---------|
| C1-C4 | tests/zephyr/data/test_index_constituent_scd2.py ×4 | SCD2 闭行行为变化：新快照行**携带 valid_to 列**（应 NULL=开新）、同日重跑**闭旧批**、空快照闭行、闭行查询失败未保新行 | 数据正确性边缘回归（index_constituent 恰是 R2 在案 monitoring 表），建议数据线优先认领 |
| C5 | tests/zephyr/data/test_prevention_bells_20260914.py | warn_if_table_missing 告警一次语义 | 疑似回归 |
| C6 | tests/zephyr/data/test_silent_latch_before_delivery.py | `data/source_health_check.py` 行尾被整篇改写（LF 652 行 vs CRLF 0） | 卫生违规实锤（谁改的谁修） |
| C7 | tests/context/test_context_guard.py（collection error） | `cannot import name 'circuit_breaker' from partially initialized module 'zephyr.infrastructure.reliability'`（循环导入） | 真 bug（import 图成环） |
| C8 | tests/trading/integration/test_agent_e2e.py（error） | `No module named 'zephyr.orchestrator.agent_health_monitor'` | 模块缺失/重构遗留 |
| C9-C11 | tests/ex_sor/test_rl_exec_env.py ×3 | 撮合成交价 Decimal('10.01379379') ≠ 预期 10.011001（买/卖/市价三断言同因） | 撮合价格口径变更未同步 or 定价 bug，需 ex_sor owner 判 |
| C12 | tests/position/test_position_recipe_compiler.py | estimate_max_z(2)=0.847 vs 官方计算器 0.520 | 网格公式与官方口径劈叉 |
| C13 | tests/git/test_git_commit_extreme.py | 8 会话并发同文件极端场景 | **复跑两轮全绿**——改判 B 类（负载敏感假红），从 C 类移除 |
| C14 | tests/f_lifecycle/test_f18_redblue.py::test_run_idempotent_3_times | phase_check_registry 子进程 `run_subprocess_hidden` 挂起超时（线程 join 卡死），文件级两轮同败+单跑复现 | 疑似真问题（挂起根因待查：子脚本等锁/等 CH/等 git 均可能） |

### D 类 · 并发会话漂移（5 条，非 bug）

tests/zephyr/factor/technical_indicators/test_indicator_base.py ×4+DDL cross-check×1：
注册表实测 105 个指标 vs 测试预期 101——**st-tilib-clear-20260920 会话正在新增 4 个指标**
（本班跑批期间 live 观察到注册表从 101→105），测试基线待该会话随批更新。禁本班代修（避让）。

### E 类 · 性能（1 条）

tests/trading/pipeline/test_phase_g_perf.py：L09 backtest P99=1910ms > 300ms 阈值（均值 1484ms）。
满载跑批环境测得，建议空载复测定性后再立工单。

## 3. flaky 判定终表（18 域×2 轮 + governance 11 失败文件×2 轮，全部完成）

**governance 文件级**：

| 判定 | 文件 |
|------|------|
| flaky_env（复跑全绿） | audit/test_gate_chain_multiproc_append.py |
| flaky_partial | test_commit_queue_integration.py（r2 转绿） |
| stable_fail（真账） | worktree_pool（文件级 3f）、test_check_vocab_domain_convergence、test_externalize_algo_flow_mirror、test_dependency_graph_acyclic、security exit_code×2、test_alert_threshold_consistency、test_battle_map×3、test_error_code_consistency、test_reconcile_generators |

**主队列 18 域**：

| 判定 | 域 |
|------|----|
| flaky_env（两轮全绿） | drift、path、git |
| flaky_partial（部分转绿） | trading、shared、llm_security、infrastructure、f_lifecycle |
| stable_fail（两轮同败） | autonomy、blueprint、context、db、ex_sor、zephyr、position、scripts、frontend、industry_graph |

**flaky 修正后的分类迁移（对 §2 的三处修正）**：

1. **trading 拆账**：decision_map.py 校验失败 7 条+blind_spot 1 条在独立复跑中消失→改判
   **B 类·测试污染/顺序敏感假红**（某用例残留状态）；稳定真账=D38 k1/k4/k5/k6+R24+catalogs 门 6 条。
2. **path 1 条改判 B 类**（独立复跑两轮全绿，原 A 类"设计保护断言"实为顺序敏感）。
3. **f_lifecycle 拆账**：2 条 worker 崩溃复跑清零（B 类）；残留 `test_run_idempotent_3_times`
   文件级两轮同败+单跑复现=**phase_check_registry 子进程挂起超时**（run_subprocess_hidden
   线程 join 卡死）→升 C14 疑似真问题（挂起原因待查，不排除环境锁）。

**D 类闭合证据**：zephyr technical_indicators 5 条（105≠101）在复跑中消失——st-tilib-clear
会话已同步测试基线（并发漂移自证闭合）。

（原始逐域两轮明细：`.runtime/tmp/dataqa/out/ 下的 r3_flaky*.json 全家族。互核结论不变：崩溃/依赖类转绿，账面断言类两轮同败。）

## 4. 方法与纪律备注

- 时间盒：每域 40 分钟（总令 §5.4）；governance 整域超时即拆，未硬闯。
- 环境依赖类（redis/网络/生产凭据）标记后不计入失败账（shared/redis 2 条按此处理）。
- 首轮废案教训已写进 a1_progress.md 断点指引（**禁加 -p no:cacheprovider**）。
- 后台运行器累计 7 次被外部 SIGTERM 杀死（含脱离进程方案），靠"每域 json+增量落盘+幂等续跑"
  全部续齐；终改分片独占+脱离进程组合跑完——对后续长批次班的机械建议：重活拆片、每片独立
  输出文件、断点续跑为默认形态。

## 5. 复验命令示例

```bash
# 任一域复跑（应复现 §1 数字，±并发敏感项）
python -m pytest tests/blueprint -q --tb=short -rEf -n 4     # 278p/3f
python -m pytest tests/governance/security -q --tb=short -rEf -n 4   # 337p/2f
# 全量重放：分批清单在 .runtime/tmp/dataqa/batch{1,2,3}.txt + govbatch{1..4}.txt
```

## 6. 未覆盖与原因

- tests/ 内 6 个非 test_*.py 辅助文件未单独执行（conftest/fixture 由 pytest 自动加载）。
- slow/e2e 标记用例未 deselect（仓库默认全跑），但 40 分钟时间盒可能截断个别超长用例——
  本批仅 governance 整域触发过截断（已拆分补齐）。
- 未做失败修复（总令红线）；D 类并发漂移 5 条留归属会话自清。
