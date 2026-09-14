---
ttl: task_bound
---

> ## 结案报告（2026-09-15 由 st-fullchain-20260914 核验）
> **总结论：报告/清单/记录类（既成事实记载，无待办）。处置=**软归档**。**
>
> **✅ 已完成**：无显式完成信号
>
> **⚠️ 未完成**：无待办信号
>
> **核验方式**：全文扫描完成/待办信号 + 引用文件存在性核验（引用 4 个，其中判废弃 0、路径漂移 0）+ commit 提及 0 处。
>
> **处置建议**：软归档。（本报告由清理批自动生成，判定依据=文档自身信号 + 代码侧核验）




# 回测修复外审遗留批（P1-4 + P2×3 + tick 语义 docstring）交付报告

> 2026-09-14 st-btfix-p14-20260914 班｜交接自 st-btfix-20260914（P0×4+P1×3 主批已落库）
> 审查报告原件：`.runtime/tmp/zephyr_external_review_2026-09-14.md`

## 1. 一页结论

| 任务 | 状态 | 落地物 |
|---|---|---|
| P1-4 xdist 并行 flaky | ✅ 并行跑绿双证 | `-n4` 两轮 1171 passed / exit 0（精简配置+默认配置各一轮）；pyproject 注记留痕 |
| P2-1 契约头过载 | ✅ 设计稿（先方案后动手） | `docs/_working/p21_contract_header_slimming_proposal.md`——ALGO_FLOW 块出仓方案，试点零删除 |
| P2-2 运行时产物堆积 | ✅ 根因修复+存量清扫 | watchdog 空壳竞态治本 + 空壳/对账清扫 + 4 新测试；存量 10,571 空壳待门禁落库后清理（见 §3） |
| P2-3 双 Python 运行时 | ✅ 检测固化 | env_check.py 门槛升 3.12 + PATH 影子检测（advisory） |
| tick 同 tick 成交 docstring | ✅ | event_driven_engine.py 约束段补语义说明（防审查再误报前视） |
| 基线回归 | ⏳ 后台在跑 | tests/backtest + tests/ex_core 单进程（上批基线 0 failed 不回退） |

## 2. P1-4 复现与结论（关键事实）

- 复现环境：项目 Python 3.12.8，`tests/backtest -n4`。
- **第 1 轮**（`-c .runtime/tmp/pytest_min.ini` 精简配置）：1171 passed，exit 0。
- **第 2 轮**（pyproject 默认配置，含 `--max-worker-restart=5`）：1171 passed，exit 0，8:54。
- 审查报告观测的"2 失败"未复现；与 `#ARCH-XDIST-WORKER-CRASH-001` 四层治本
  （PID-unique basetemp / 退出自清理 / 空目录回收 / max-worker-restart）已在库一致。
- **附带发现（已写进 pyproject 注记）**：`-p no:cacheprovider` 与 pyproject `cache_dir`
  组合会触发 INTERNALERROR（Unknown config option）——外审/交接文档的跑法踩的就是这个
  陷阱；禁 cacheprovider 必须同时 `-c` 精简 ini。审查报告的"并行失败"存在被此配置
  问题污染的可能（其 -n4 跑法未说明用哪种配置）。

## 3. P2-2：从"没清理"改判"产量病 + 空壳病"（根因修复）

### 3.1 实况颠覆审查判断

- `.runtime/quarantine/` 实测 **11,843 个 drift_* 目录（385MB，1,522 个文件）**；
- 其中**空壳目录 10,571 个（89%）**；
- 30 天 TTL **早已生效**：超 30 天目录 = 0，daemon（PID 35220）存活、`quarantine_last_sweep=2026-09-14`；
- 产量 ~395 目录/天（24h 内新增 116）。

审查报告"TTL 机制未严格落实"不成立——真问题两个：
1. **空壳竞态**：`_snapshot()` 旧实现 `mkdir(parents=True)` 先行，源文件在"scan 判
   dirty → 读字节"竞态窗内被会话正常落地时，留下纯目录（无任何文件）；
2. **高产量**：shared 机 7×24 多会话，每轮扫描告警事件都新建秒级时间戳目录。

### 3.2 修复（src/zephyr/gov_enforcement/rule_bridge/worktree_drift_watchdog.py）

- `_snapshot()`：**先验证源文件存在再建目录**——源消失即返回空串，不再出生空壳；
- 新增 `_dir_has_files()`：OSError 按非空处理（保守不删）；
- `_sweep_quarantine()`：新增空壳清理分支（60 秒在飞宽限期防误删刚建快照），
  审计记录带 `kind=empty_shell|expired`；返回 `removed_names`；
- `_maybe_sweep_quarantine()`：按 `removed_names` **对账 `known_quarantine`**，
  自家清扫的目录同步摘除登记——修掉"自清扫被下轮 tamper 检查误判带外删除"的
  潜在误报（tamper 4,263 条史里混有此类噪声）。

### 3.3 测试（tests/governance/rule_bridge/test_worktree_drift_watchdog.py）

新增 4 例（40→44，全绿）：
`test_snapshot_source_vanished_no_dir` / `test_sweep_removes_empty_shells_after_grace` /
`test_sweep_keeps_fresh_empty_shell_inflight` / `test_maybe_sweep_reconciles_known_quarantine`。

### 3.4 存量清理时序（刻意安排）

10,571 个存量空壳**待本批代码落库后由清扫器处置**：quarantine 在 ops_guard 保护区，
带外裸删=tamper 审计噪声；正确的清法是"落库→调用 `_sweep_quarantine`（授权通道
safe_rmtree）→逐条审计留痕"。落地步骤见 §6。

## 4. P2-3：检测固化（scripts/governance/meta/env_check.py）

- `MIN_PYTHON (3,10)→(3,12)`，SSoT 对齐 pyproject `requires-python>=3.12`
  （旧门槛会放行 3.11——系统 PATH 实存 3.11/3.12 并存，实测 `where python` 还有
  第三重：E:\AutoClaw 托管 Python 排首位）；
- 新增 `_check_python_path()`：`shutil.which("python")` 首位非项目 Python（Python312
  安装前缀）→ 告警+打印 RULE-ENV 修正命令（advisory 不阻断，JSON 带
  `python.path_ok/path_first` 供 CI/上层消费）；
- 实测双路径：干净 PATH 无告警；影子 PATH（托管 Python 首位）正确告警。

## 5. P2-1：先方案后动手（合规动作）

实查修正审查口径：回测域 53 文件 48 个带 [BLUEPRINT]（90.6%），注释率 18.2%，
头部负担均值 ~115 行（含 docstring 内嵌 ALGO_FLOW 机器块）——比报告的"17 行"更重。
逐标记消费方 grep 实证：`[ALGO_FLOW]` 块是 AST 可再生成物，是唯一可出仓迁移面；
其余标记全是门禁/生成器消费面，删行=断链。设计稿交付：
`docs/_working/p21_contract_header_slimming_proposal.md`（试点 1 文件零删除验证 +
净零增长对账，Owner 批准后才进实施序）。

## 6. 遗留与后续班建议

1. 存量空壳清理：落库后跑一次性清扫（授权通道），预计移除 ~10.5K 目录/385MB；
2. P2-1 设计稿裁定：若批 ALGO_FLOW 出仓，按 §3.3 实施序走；
3. `pytest_min.ini` 精简配置缺 `--strict-markers`/timeout，长期建议与 pyproject 对齐
   或在交接文档改用默认配置跑法；
4. 审查报告 §4 第 2 点（模拟盘不复用 `_SYNTHETIC_DEPTH`）属回测/模拟盘桥梁验证，
   超出本批范围，建议排进模拟盘前检查单。
