---
ttl: task_bound
---

# T14 门禁名册三方对账摘要

- 生成器: `scripts/governance/d3_metadata/reconcile_gate_rosters.py`（只读取证，不改两册）
- 对账根: `D:\ZephyrAlpha\.runtime\tmp\csx_t14_wt`
- 模块面: 116 个 .py，其中 GateSpec 门 114、辅助模块 2
- in_process 名册: 99 条（标量 99 / 列表 99）
- 统一册: 180 条（标量 180 / 列表 180）
- own_scope 分布: {'false': 133, 'true': 33, 'missing': 12, 'null': 2}

## 漂移类型分布

| 类型 | 条数 |
|---|---|
| MODULE_NOT_IN_IN_PROCESS | 15 |
| OWN_SCOPE_MISSING | 12 |
| PRECOMMIT_SCRIPT_MISSING | 2 |

## own_scope 待 Owner（不可机械判定）

- `BLUEPRINT-AMODULE-CONSISTENCY`（manual）：manual 源（重定向锚点/机制实名登记），无执行体可机械判定
- `COMMIT-CRITICAL-SECTION-LOCK`（manual）：manual 源（重定向锚点/机制实名登记），无执行体可机械判定
- `DANGLING-REFERENCE`（manual）：manual 源（重定向锚点/机制实名登记），无执行体可机械判定
- `DATA-TASK-COMPLETENESS`（manual）：manual 源（重定向锚点/机制实名登记），无执行体可机械判定
- `DEPGRAPH-PRE-REGISTRATION`（manual）：manual 源（重定向锚点/机制实名登记），无执行体可机械判定
- `GATE-DRIFT`（pre-commit）：显式 null：无可定位执行体源码，不可机械判定
- `GATE-PANORAMA-ALIGNMENT`（manual）：manual 源（重定向锚点/机制实名登记），无执行体可机械判定
- `GATE-SCHEMA-HEALTH`（manual）：manual 源（重定向锚点/机制实名登记），无执行体可机械判定
- `GATE-ZR`（pre-commit）：显式 null：无可定位执行体源码，不可机械判定
- `ISSUE-RESOLVED-INTEGRITY`（manual）：manual 源（重定向锚点/机制实名登记），无执行体可机械判定
- `LIBRARY-COVERAGE`（manual）：manual 源（重定向锚点/机制实名登记），无执行体可机械判定
- `NO-HIGH-COMPLEXITY`（manual）：manual 源（重定向锚点/机制实名登记），无执行体可机械判定
- `PERM-TRIGGER`（manual）：manual 源（重定向锚点/机制实名登记），无执行体可机械判定
- `VOCAB-HARDCODE`（manual）：manual 源（重定向锚点/机制实名登记），无执行体可机械判定

## 附注

- 对账基线=scratch worktree @ dev HEAD c0724304456（Max 取批基准）；主区在途态见证据附录 csx_t14_main_run.txt（in_process 102 vs 本基线 99，其中 3 条名册条目暂无模块文件=跨 commit 原子性在途形态）
- 15 门 MODULE_NOT_IN_IN_PROCESS 全部为 st-gslim-20260923 P4 合并家族（map/depgraph/complexity/vocab/reference 五簇）：模块文件留档+统一册 deprecated 重定向锚+名册条目已除——三方三种说法，净形态处置（删模块或改标注）属 Owner 门位
- ms 盲区红转绿证据见附录：修前 2 failed（0.5ms/0.0ms 门在 ms 字典蒸发）→ 修后 2 passed；total_ms 语义不变
- own_scope 补全 53 条（pre-commit 通道可定位脚本者，全部 False=该通道零 own-diff 覆盖的直接证据）；显式 null 2 条+manual 12 条待 Owner；统一册标量 174→180 随重生成归位（L4 丢标量形态自愈）
- 本批不含 apply_depgraph 触发的 blueprint 派生文档搅拌（已在 scratch 回滚，非本车道变更集）

## 证据附录: csx_t14_ms_red.txt

```
============================= test session starts =============================
platform win32 -- Python 3.12.8, pytest-8.4.2, pluggy-1.6.0 -- C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe
rootdir: D:\ZephyrAlpha\.runtime\tmp\csx_t14_wt
configfile: pyproject.toml
plugins: anyio-4.13.0, dash-4.4.1, asyncio-0.26.0, cov-6.3.0, timeout-2.4.0, xdist-3.8.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
timeout: 120.0s
timeout method: thread
timeout func_only: False
collecting ... collected 2 items

tests/governance/test_gate_registry_ms_visibility.py::test_sub_ms_gate_visible_in_ms_dict FAILED [ 50%]
tests/governance/test_gate_registry_ms_visibility.py::test_zero_ms_reused_state_visible FAILED [100%]

================================== FAILURES ===================================
_____________________ test_sub_ms_gate_visible_in_ms_dict _____________________
tests\governance\test_gate_registry_ms_visibility.py:45: in test_sub_ms_gate_visible_in_ms_dict
    assert "FAKE-SUBMS-GATE" in rec["ms"], "0.5ms 门被 >=1.0 过滤蒸发——计时盲区"
E   AssertionError: 0.5ms 门被 >=1.0 过滤蒸发——计时盲区
E   assert 'FAKE-SUBMS-GATE' in {'FAKE-SUPRA-MS-GATE': 12.3}
______________________ test_zero_ms_reused_state_visible ______________________
tests\governance\test_gate_registry_ms_visibility.py:57: in test_zero_ms_reused_state_visible
    assert "FAKE-ZERO-MS-GATE" in rec["ms"]
E   AssertionError: assert 'FAKE-ZERO-MS-GATE' in {}
=========================== short test summary info ===========================
FAILED tests/governance/test_gate_registry_ms_visibility.py::test_sub_ms_gate_visible_in_ms_dict - AssertionError: 0.5ms 门被 >=1.0 过滤蒸发——计时盲区
assert 'FAKE-SUBMS-GATE' in {'FAKE-SUPRA-MS-GATE': 12.3}
FAILED tests/governance/test_gate_registry_ms_visibility.py::test_zero_ms_reused_state_visible - AssertionError: assert 'FAKE-ZERO-MS-GATE' in {}
============================== 2 failed in 1.95s ==============================
```

## 证据附录: csx_t14_ms_green.txt

```
============================= test session starts =============================
platform win32 -- Python 3.12.8, pytest-8.4.2, pluggy-1.6.0 -- C:\Users\fanzi\AppData\Local\Programs\Python\Python312\python.exe
rootdir: D:\ZephyrAlpha\.runtime\tmp\csx_t14_wt
configfile: pyproject.toml
plugins: anyio-4.13.0, dash-4.4.1, asyncio-0.26.0, cov-6.3.0, timeout-2.4.0, xdist-3.8.0
asyncio: mode=Mode.STRICT, asyncio_default_fixture_loop_scope=None, asyncio_default_test_loop_scope=function
timeout: 120.0s
timeout method: thread
timeout func_only: False
collecting ... collected 2 items

tests/governance/test_gate_registry_ms_visibility.py::test_sub_ms_gate_visible_in_ms_dict PASSED [ 50%]
tests/governance/test_gate_registry_ms_visibility.py::test_zero_ms_reused_state_visible PASSED [100%]

============================== 2 passed in 0.73s ==============================
```

## 证据附录: csx_t14_main_run.txt

```
模块面 114 门（117 py / 3 辅助） | in_process 102 | 统一册 180
own_scope: {'false': 80, 'true': 33, 'missing': 67} | 待 Owner: 14
DRIFT IN_PROCESS_MODULE_MISSING: 3
DRIFT MODULE_NOT_IN_IN_PROCESS: 15
DRIFT OWN_SCOPE_MISSING: 67
DRIFT PRECOMMIT_SCRIPT_MISSING: 2
```
