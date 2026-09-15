---
ttl: task_bound
session: st-btfix-p15-20260915
date: 2026-09-15
---

# P2-1 ALGO_FLOW 逐域出仓 批8 报告：trading 域（st-btfix-p15-20260915）

## 概要

| 项 | 值 |
|----|----|
| 域 | trading → `docs/03_modules/_domain_trading/algo_flow/` |
| 出仓文件 | 88 src（内联块 → 单行 external 锚点），3320 行机器块外迁 |
| yaml 产物 | 88 本批新建 |
| 测试 | tests/trading = **1621 passed / 6 failed / 1 skipped**（4 分片串行策略） |
| 提交 | `57ce69d6`（178 文件，零吸收已核实） |
| 幂等 | 复扫 0 待出仓（92 skipped + 6 already） |

## 配套登记

- **创建令牌**：+98 条（capability `btfix_p1p2`，created_by st-btfix-p15-20260915）——**已由他会话吸收落库**：kimi 挖矿会话提交（`cbd9bb40cc` / `bf7a8283cd`）落库注册表时连带吸收我方 98 条 token，批8 主提交不含注册表（同批7 REGISTRY-MASS-DELETION 处置口径）。token 均已入库，无重复义务。
- **TDM 注解**：2 节点（TDM-E-L4-13 三方对账 / TDM-X-S1-06 策略异常退出编排，note_confirmed 2026-09-15 紧贴 node_id + algo_note_zh 出仓注记）。
- **CloneGuard**：6 对既有同构暴露（boot_hooks 钩子姊妹函数 / eod 与 post_settlement `_alert` / registry property 三文件三角 / kill_switch 触发复位镜像），全部核实 HEAD 既有，echo-guard.yml acknowledged（**25→31 条累计**）——主提交因此含 echo-guard（178 文件）。

## 测试策略与发现

1. **80MB 审计日志致测试挂死（根因链确诊）**：多会话风暴把 `data/audit_trail/events.jsonl` 撑到 80MB / 105,882 行 → feedback_loop/scheduler.py 审计检查 → gov_audit/integrity.py `verify_chain` 逐行读全程 >120s → pytest-timeout 杀进程。整目录单跑两次挂死（0% 挂起 / 45% 被杀）。
2. **4 分片串行策略（pytest @file 语法）**：76 个测试文件分 4 片（`pytest @chunk0..3`），逐片跑完 → 1621 passed / 6 failed / 1 skipped，零超时。
3. **6 个失败全部他会话所致**：均为 NewRegistryGate（test_catalogs_no_unregistered_new_library 及 k1/k4/k5/k6 对抗变体、test_f4_repo_map_full_gates_still_green）——他会话新落 `trial_ledger_registry.yaml` 未按 D38 规则注册，与本批无关（git show HEAD 取证）。TDM 结构测试 60/60 通过。

## IMPORT-INTEGRITY noqa 逃生实录（本批最大教训）

HEAD 既有 3 处误报悬空 import（`__main__.py:44 import resource` Unix-only try/except 守护；`boot_hooks.py:260/588 from zephyr.governance.event_hook import` 经 governance/__init__.py sys.modules shim 注册、无实体文件）。

- 第一次修复方向错误：把 `# noqa: import-integrity` 从续行移到 import 首行 → gate 仍拦，同行号 3 findings 原样复现。
- **真根因**：`_make_noqa_pattern`（_diff_helpers.py:354）的正则要求 gate_id 后 **2+ 空格** 再接 reason（`\s{2,}`），原标记 `# noqa: import-integrity — ...` 仅 1 空格，标记从未被识别——行位置从来不是问题。
- 修复：三处标记补成 2 空格 → gate 放行。**教训：noqa 逃生标记格式先读 `_make_noqa_pattern` 再写，位置排查是白绕。**

## 过程发现（多会话并发高峰实录）

1. **daemon auto-stage 二次吸尘**：提交前暂存集再次被吸进 66 个外来文件（pipeline-research intake 报告等），纯化（git reset 仅 index）后复验纯净——提交前最后一步必须再纯化一次（批7 已记录，本批复现）。
2. **提交四度过闸**：①全局锁超时 → ②IMPORT-INTEGRITY noqa 空格格式 → ③CloneGuard 6 对既有克隆 → ④成功（`--wait 1800` + 逐门修复后）。多会话风暴下（同窗 3+ 活跃会话）门禁逐层串行暴露，每重试一次才见下一道门。

## 战役进度

- 已出仓累计：批1-2（72）+ 批3 regime（42）+ 批4 ex_core（59）+ 批5 ml_train（43）+ 批6 risk（76）+ 批7 factor（82）+ 批8 trading（88）= **462 文件（14.0% / 3302）**
- 剩余大域：feedback_loop(340) / infrastructure(336) / governance(296) / shared(243) / gov_enforcement(188) / security(188) 需独立立项；中小域：autonomy_core(138) / signal_ashare(128) / data(116) / orchestrator(75) 等可继续逐批。
- 遗留（非本批义务）：pytest_min.ini markers bug；TDM note 归因窗口重设计；GATE-PANORAMA-ALIGNMENT 检测器失效；events.jsonl 80MB 瘦身（审计日志轮转/归档）。
