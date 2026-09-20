---
ttl: task_bound
---

# 外审遗留批二期——三项遗留全施工报告（P2-1 实施 + pytest 配置对齐 + 模拟盘桥梁核验）

> 2026-09-15 st-btfix-p14-20260914 班｜Owner 裁定"全部施工"后的一期批（commit 59e5d875e3）续篇
> 前篇报告：docs/_working/archive/2026-09/btfix_p1p2_report.md（已被清理批软归档）

## 1. 一页结论

| 遗留项 | 状态 | 落地物 |
|---|---|---|
| ② pytest_min.ini 与 pyproject 漂移 | ✅ 对齐+看守 | ini 补 strict-markers/timeout/markers/norecursedirs；新校验器 compare_pytest_configs.py + 6 测 + pre-commit 挂点 |
| ③ 模拟盘不复用 _SYNTHETIC_DEPTH | ✅ 核验留证+检查单 | docs/_working/sim_bridge_checklist.md——结构性隔离证据链，非代码改动项 |
| ① P2-1 ALGO_FLOW 出仓实施 | ✅ extractor 支造+试点迁移 | external 锚机制 + event_driven_engine 首迁，round-trip 验证 nodes/edges 一致，30 测全绿 |

## 2. ② pytest 双配置对齐（治本"换配置就绿/红"）

- `pytest_min.ini` 补齐：`--strict-markers`、`timeout=120`、9 个 markers 注册（单行分号写法——pytest ini 不支持跨行数组，实测 unexpected ']'）、`norecursedirs` 收集卫生镜像（test_collection_hygiene 守卫抓漏，值与 pyproject 逐项一致）；
- 新校验器 `scripts/governance/d7_code/compare_pytest_configs.py`：markers 键集相等 / timeout 继承 / ini 禁 cache_dir 三类漂移看守，`--json` 供 CI；
- pre-commit 挂点 `gate-pytest-config-drift`（pyproject 或 ini 变更时触发）；
- 测试 6 例全绿（对齐通过/markers 漂移/timeout 漂移/cache_dir 拒入/ini 缺失/垃圾输入降级）。

## 3. ③ 模拟盘桥梁核验（审查 §4.2 承接）

全仓 grep 实证：`_SYNTHETIC_DEPTH` 仅存在于回测 `matching_engine.py`；SimulationBroker
import 图不含回测 matching_engine——**结构性隔离，无复用路径**。审查担心的
"模拟盘复用无限深度假设"不成立。留证+上线检查单（5 项，含 KillSwitch SIMULATION
运行态确认）见 docs/_working/sim_bridge_checklist.md。

## 4. ① P2-1 ALGO_FLOW 出仓（设计稿批准后实施）

### 4.1 机器链路取证（消费方全部收敛）

- `check_algo_flow.py`：只查 docstring 内标记**存在**（external 锚行满足）；
- `parse_algo_flow`：唯一真源解析器，被 extractor 内部调用（validate_rules_integrity 仅是保护清单 desc 文字）；
- 生成器（module_algorithm_overview/domain_doc）与 translation_reconciler：全部经
  `extract_algorithm_from_code` 消费——**改造面收敛到 extractor 一处**。

### 4.2 extractor 改造（scripts/governance/_shared/code_algorithm_extractor.py）

- `_load_external_algo_flow()`：解析锚行 `# [ALGO_FLOW] external: <path>` → 加载外部
  yaml 的 `algo_flow:` 块原文 → 走同一 `parse_algo_flow` 管线；护栏=docs/ 前缀+.yaml
  后缀（路径逃逸拒绝）；失败降级 None（生成器回退文字卡片，契约一致）；
- `_has_inline_algo_flow()`：真内联块判定——**实测坑：锚行本身含 `# [ALGO_FLOW]`
  字面量，简单字符串包含会误判内联导致解析落空**；
- `_strip_algo_flow_block()` 同步剥离锚行（不泄漏进概述）；
- 内联优先向后兼容存量 416 模块；无内联才走外部锚。

### 4.3 试点迁移 + round-trip 验证

- `docs/03_modules/_domain_backtest/algo_flow/event_driven_engine.yaml`（块逐字节副本，
  doc_type=architecture_view 过 DCR-001，目录契约允许 .yaml）+ creation_token 已登记；
- 源码 docstring `# [ALGO_FLOW]` 60 行块 → 1 行锚（文件头减 ~50 行）；
- round-trip：extractor 经锚加载解析出 nodes=[I1,I2,A1,O1] / edges=[I1→A1, I2→A1, A1→O1]，
  与迁移前内联块**逐项一致**；
- 测试 27→30 全绿（3 新例：锚加载/缺失降级/路径逃逸拒绝）+ overview 生成器实跑
  13 文件产出正常 + d8 translation 测试零回归（amber-orbit 1267 项中唯一失败是
  collection_hygiene 抓 ini 漏 norecursedirs，已修复复验）。

### 4.4 全景图卡片真源路由核对

旧版全景图 MOD-BT-001 卡片真源是 `backtest/__init__.py`（rich-docstring 路由），A1 卡
片内容为 `__init__` 聚合器——**event_driven_engine 的 A1 卡片在旧产物中本就不独立呈现**
（其块经 `__init__` 回退被覆盖）。迁移不改变路由结果，无全景图回归面。

## 5. 存量推广边界（后续班）

416 运营态模块全量出仓=逐域分批（出仓→round-trip→域测试→提交），非一簇完成；
本批交付机制+试点，推广节奏由 Owner 按域排期。宪法 §4 对账：机制侧新增 1 校验器+
3 测试+1 pre-commit 条目，试点侧净减 ~50 行/模块——存量推广完成后显著净减。

## 6. 验收对账

| 项 | 结论 |
|---|---|
| ini 对齐 | ✅ collection_hygiene + compare_pytest_configs 双守卫绿 |
| 校验器 | ✅ 6/6 测 + CLI 实跑 exit 0 + pre-commit 挂点 |
| 桥梁核验 | ✅ 隔离证据链 + 检查单落盘 |
| extractor | ✅ 30/30 测 + round-trip 一致 + 生成器实跑正常 |
| 提交归属 | 提交后 `git log -1 --name-only` 核实（见汇报） |
