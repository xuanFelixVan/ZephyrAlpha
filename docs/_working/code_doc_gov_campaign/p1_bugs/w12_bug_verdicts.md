---
ttl: task_bound
session: st-code-doc-20260921
---

# [BLUEPRINT] | docs/_working/code_doc_gov_campaign/p1_bugs/w12_bug_verdicts.md |
<!-- [MODULE]  -->
<!-- [STABILITY] evolving -->
<!-- [SAFETY] L -->

WO-12 疑似 bug 认领逐条裁定台账（现象/根因/终态/红绿证据/改动清单）

> 会话 sid=st-code-doc-20260921；HEAD=2d7308df1f；全部证据 [亲验]=本会话实跑。
> SCD2×4 已划数据线、C13 已改判 B 类，均不在本单（9 条 = C5/C6/C7/C8/C9/C10/C11/C12/C14）。

---

## C5 · test_prevention_bells_20260914.py — warn_if_table_missing "告警一次"

- **现象**：`tests/zephyr/data/test_prevention_bells_20260914.py::test_warn_if_table_missing_alerts_once`
  报 `AttributeError: '_FakeScheduler' object has no attribute '_deliver_alert_with_latch'`。
- **根因**：`src/zephyr/data/scheduler.py:1424` — BRK-049 收口把告警投递改经
  `_deliver_alert_with_latch`（投递成功才记 4h 去重戳，实现有意演进且语义更严），
  测试替身 `_FakeScheduler`（测试文件 :97-105）只绑了旧两个方法，未同步。
- **终态**：**修复**（测试域）。替身补绑 `_deliver_alert_with_latch.__get__(self)`；
  告警一次/4h 去重/表存在清账三段断言语义原样保留，全数成立。
- **红证** [亲验]：`AttributeError ... no attribute '_deliver_alert_with_latch'`（1 failed）。
- **绿证** [亲验]：`python -m pytest tests/zephyr/data/test_prevention_bells_20260914.py -q` → **8 passed**。
- **改动**：`tests/zephyr/data/test_prevention_bells_20260914.py`（+5 行）。

## C6 · test_silent_latch_before_delivery.py — source_health_check.py 行尾"整篇改写"

- **现象**：`test_patched_files_keep_line_endings` 断言 `LF 652 == CRLF 0` 失败（行尾被整篇改写）。
- **核查**：当前行尾实测 LF 652 / CRLF 0；`git ls-files --eol` = `i/lf w/lf`；
  `.gitattributes` 对 `*.py` 强制 `text eol=lf`；改写嫌疑提交 a9b3e039db 对该文件仅 +22/−4
  （git 侧从未整篇改写，CRLF 只是旧 autocrlf 工作区残留）。
- **根因**：**测试断言口径过时**——"全文件纯 CRLF"与 `.gitattributes eol=lf` 直接矛盾，
  任何规范检出必挂；文件现状（纯 LF）恰是仓库规范态。非源码 bug，无需移交数据线改文件。
- **终态**：**修复**（测试域）。反改雷语义保留：回归=有人把 CRLF 写回来 → 改断言为
  `raw.count(b"\r\n") == 0`，判据真源锚 .gitattributes。
- **红证** [亲验]：`AssertionError: data/source_health_check.py 行尾被整篇改写 / assert 652 == 0`。
- **绿证** [亲验]：同命令复跑 → **1 passed**。
- **改动**：`tests/zephyr/data/test_silent_latch_before_delivery.py`（断言+docstring）。

## C7 · test_context_guard.py — reliability 包 collection error

- **现象**：`ImportError: cannot import name 'circuit_breaker' from partially initialized module
  'zephyr.infrastructure.reliability'`（Python 3.12 对"子模块不存在"的误导性提示，非真循环导入）。
- **根因**：`src/zephyr/infrastructure/reliability/__init__.py:20` 残留幽灵引用
  `from . import circuit_breaker`——该模块已由 1ddcd089cf 作为死模块删除（144 行，ARCH-032
  迁 governance 后无存续引用，全仓零 importer），但 `__init__` 未同步 → 整包不可导入。
- **终态**：**修复**（src 域=可修域）。清除幽灵引用：`from . import context_guard`，
  `__all__` 同步收缩；非结构变更。
- **红证** [亲验]：collection error（collected 0 items / 1 error，见现象）。
- **绿证** [亲验]：`python -m pytest tests/context/test_context_guard.py -q` → **20 passed**。
- **改动**：`src/zephyr/infrastructure/reliability/__init__.py`（import/`__all__` 两行+注释）。

## C8 · test_agent_e2e.py — No module named 'zephyr.orchestrator.agent_health_monitor'

- **现象**：collection error `ModuleNotFoundError`（tests/trading/integration/test_agent_e2e.py:27）。
- **根因**：`src/zephyr/orchestrator/agent_health_monitor.py`（374 行）已由 8b7cb30893
  （A5-M1 补刀，2026-09-16）**有意删除**（前批 f5c82f742a 被并发复活后补齐磁盘删除），
  同批已删其专属测试两件；本 e2e 文件是该删法的漏网消费者。判"真缺/退役"，非改名
  （全仓无任何 agent_health_monitor 新路径；orchestrator/ 下亦无替代同名件）。
- **影响面**：仅 `TestHealthMonitorIntegration` 3 条测已退役对象（死测试）；其余 4 类
  11 条（AgentRouter/编排/幻觉钩子/通过率）不依赖该模块但被 collection 连坐。
- **终态**：**证伪（退役留痕）+ 回执登记**。未动文件——理由：该测试文件是 5 类复合件，
  删整文件会误杀 11 条活测试，删类+摘 import 属测试归档决策，超出本单"最小 diff"授权；
  建议后续由测试线做"摘 `TestHealthMonitorIntegration` 类 + 第 27 行 import"或整文件归档。
- **红证** [亲验]：2 轮复跑均 `ModuleNotFoundError: No module named 'zephyr.orchestrator.agent_health_monitor'`。
- **绿证**：不适用（终态=留痕，无改动）。
- **改动**：无。

## C9/C10/C11 · test_rl_exec_env.py 三条 — 撮合成交价 10.01379379 ≠ 10.011001

- **现象**：market/limit-BUY/SELL 三条同因失败：买 `10.01379379 ≠ 10.011001`、
  卖 `9.98621379 ≠ 9.989001`（差额恰 = ±3.79bp 与 ±1bp 之差）。
- **定谳**：**实现是对的，测试预期过时**。`src/zephyr/backtest/core/matching_logic.py`
  `_apply_slippage`→`slippage_bps_for`→`cost_model_calibration.resolve_slippage_bps`（:267-299）：
  无流动性信息时取 `SLIPPAGE_BPS_UNIVERSAL=3.79bp`（全市场名义加权实证值，台账 #23 H2；
  该件 docstring 明示"宁取实证加权，不回退到无出处的 1bp"、3/4 档"一律严于旧 1bp"）。
  10.01×(1+3.79/10000)=10.01379379、9.99×(1−0.000379)=9.98621379，逐位吻合 → 口径有意变更未同步测试。
- **终态**：**修复**（测试域）。三条被测对象是边界/撮合/IS 记账骨架而非滑点标定值，
  故用官方**固定口径覆写位** `MatchingConfig(slippage_bps=Decimal("1"))`（该字段文档自述
  用途=平口对照）钉住 1bp：断言与"ask1×1.0001"注释逐字保留、且不受
  `SLIPPAGE_TIERING_ENABLED` A/B 取证开关影响。
- **红证** [亲验]：3 条 `assert Decimal('10.01379379') == Decimal('10.011001')` 等（3 failed）。
- **绿证** [亲验]：`python -m pytest tests/ex_sor/test_rl_exec_env.py -q` → **15 passed**。
- **改动**：`tests/ex_sor/test_rl_exec_env.py`（import +1、`make_env` 钉口径+留痕注释）。

## C12 · test_position_recipe_compiler.py — estimate_max_z(2)=0.847 vs 官方 0.520

- **现象**：`test_estimate_max_z_matches_official_calculator` 差 0.3272：
  `estimate_max_z(2)=0.8469317055375386` vs `DeflatedSharpeCalculator...expected_max=0.5197553442805939`。
- **官方口径出处**：`src/zephyr/simulation/deflated_sharpe_calculator.py:242-275`
  `expected_max_sharpe_z`（自称"全仓唯一真源"）——已从 Euler–Maclaurin 渐近式（N=2 给
  0.8469=超折减 50%，恰为编译器现值）**有意切换**为 Bailey & López de Prado 2014 闭式
  `(1−γ)Φ⁻¹(1−1/N)+γΦ⁻¹(1−1/(N·e))`，并明令"禁止把断言改回钉在本函数自身输出上"。
  旧渐近式残留在 `src/zephyr/position/core/position_recipe_compiler.py:300`，与其自身
  docstring"与官方件同一公式"矛盾。
- **终态**：**修复**（src 域=可修域，实现侧）。`estimate_max_z` 按官方闭式逐位对齐
  （同一 stdlib `NormalDist().inv_cdf`、同运算次序 → 逐位相等），γ 常量数值真源锚官方件；
  保留"不拉模拟依赖的快速预览"设计意图（本地常量+注记，不 import simulation）。
- **红证** [亲验]：`assert 0.3271763612569447 < 1e-12`（1 failed）。
- **绿证** [亲验]：`python -m pytest tests/position/test_position_recipe_compiler.py -q` → **12 passed**。
- **改动**：`src/zephyr/position/core/position_recipe_compiler.py`（import +1、常量 +2、方法体重写、docstring）。

## C14 · test_f18_redblue.py::test_run_idempotent_3_times — run_subprocess_hidden 挂起超时

- **现象**：单跑可复现 120s pytest-timeout 击杀，栈停在 `run_subprocess_hidden` →
  `communicate` → `stdout_thread.join`。
- **诊断** [亲验]（三步，产物落盘 `.runtime/tmp/w12_c14_*`）：
  1. 子命令直跑 `generate_project_path_tree.py --check` → 秒级返回 exit=1（OUT OF SYNC，脚本健康）；
  2. 全 58 gate 计时扫一遍 → 总 61.1s（大头 vms_migration 16.8s / path_tree 14.2s / encoding 10.8s，
     均为真实仓扫描+PG 往返）；子进程超时链路（30~60s + TimeoutExpired 捕获→"TIMEOUT after Ns"）**工作正常，无死锁无卡死**；
  3. 按测试原样 3×`runner.run()` → 61/74/86s（审计日志逐轮增长故递增），三轮全绿
     （cleanup_done/audit_logged=True、total_gates=58 一致），**总 221s**。
- **根因**：**非挂起**——是测试真实成本（≈221s）超出 pyproject 全局 pytest-timeout 120s
  预算被误杀；timeout 栈 dump 恰落在某慢 gate 的正常 communicate 窗口内，造成"线程 join 卡死"假象。
  "子进程加超时+失败可见化"修复前提已被证伪（该机制本就存在且生效）。
- **终态**：**修复**（测试域，最小）。按测试真实成本给该测试加 `@pytest.mark.timeout(600)`
  +诊断留痕 docstring；不削弱任何断言、不动 gate 体系、不动全局 timeout 配置。
- **红证** [亲验]：`+++++++++++++++++++ Timeout ++++++++++++++++++`（120s 击杀，栈见现象）。
- **绿证** [亲验]：放宽后单跑 → **1 passed in 258.46s**（600s 本级预算内）。
- **改动**：`tests/f_lifecycle/test_f18_redblue.py`（+marker、+docstring）。

---

## 汇总

| 条目 | 终态 | 证据 |
|------|------|------|
| C5 | 修复（替身补绑） | 红 1F → 绿 8 passed [亲验] |
| C6 | 修复（测试过时口径改纯 LF 断言；**无需移交**） | 红 1F → 绿 1 passed [亲验] |
| C7 | 修复（删幽灵引用） | collection error → 绿 20 passed [亲验] |
| C8 | 证伪/退役留痕（模块有意删除；不擅自删测试文件） | 2 轮复现留痕 [亲验] |
| C9/C10/C11 | 修复（钉 1bp 平口径；实现=3.79bp 标定值是对的） | 红 3F → 绿 15 passed [亲验] |
| C12 | 修复（实现侧闭式对齐官方件） | 红 1F → 绿 12 passed [亲验] |
| C14 | 修复（测试真实成本 221s>120s 预算，放宽本级 timeout；无挂起） | 红 Timeout → 绿 1 passed [亲验] |

**改动文件清单**（全部已 git add）：
- `tests/zephyr/data/test_prevention_bells_20260914.py`
- `tests/zephyr/data/test_silent_latch_before_delivery.py`
- `src/zephyr/infrastructure/reliability/__init__.py`
- `tests/ex_sor/test_rl_exec_env.py`
- `src/zephyr/position/core/position_recipe_compiler.py`
- `tests/f_lifecycle/test_f18_redblue.py`
- `docs/_working/code_doc_gov_campaign/p1_bugs/w12_bug_verdicts.md`（本台账，新建）

**顺手发现（不在本单，移交登记）**：
- `phase_check_registry.check_dependency_audit` → `DependencyAuditor` 无 `audit` 方法
  （AttributeError，gate fail-closed=RED；链路可见于诊断 stderr，属 governance 域）。
- `generate_project_path_tree.py --check` 在本会话前后均报 OUT OF SYNC（HEAD 既有状态，
  非本单引入；refresh `--write` 属 depgraph 写域，未擅动）。

## 总包收口补记（st-code-doc-20260921 总包，C8 停手项收口）

C8 停手项"摘除 TestHealthMonitorIntegration 死测试类"已由总包执行（tests/** 本线写域内）：
- 摘除死类 3 条（import agent_health_monitor 连坐全文件 collection error）+ 两个仅死类使用的
  import 名（OrchestrationResult/RouteDecision）+ docstring 覆盖面与计数同步（14 条实测）。
- 修后 `pytest tests/trading/integration/test_agent_e2e.py` = **14 passed** [亲验]，
  collection error 清零，活测试全部复绿。
- 改动：tests/trading/integration/test_agent_e2e.py（+2/-65），已 git add，随分包1 批走正门。
- 至此 WO-12 九条全部终态：6 修复 + 3 证伪留痕（C6 证伪改断言/C8 证伪退役摘除/C14 证伪超时修正）。
