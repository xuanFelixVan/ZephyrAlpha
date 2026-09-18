---
ttl: task_bound
completes_when: 六向台账可疑件全部完成单跑实证或转交 CI 车道
---

# 测试仪器完整性车道 · 接力单（撞轮数预算，如实归档断点）

车道 = `st-ff-testint-20260918` · 总包 = `st-fullflow-20260918` · 断点时间 = 2026-09-18 21:3x
本件**只记断点**，数字与判据以 `lanes/testint_census.md`（生成器产出）与
`lanes/testint_ci_prereq.md` 为准，勿在此重复计数。

## 1. 已扫（覆盖面声明，别把模式命中当确证）

- 主扫描器 `.runtime/tmp/ff-testint/scan_test_selfcontain.py`：`tests/**/test_*.py` 全量 AST 扫，
  七类形态命中落 `.runtime/tmp/ff-testint/census_hits.jsonl`。
- 漏报界定器 `probe_fn.py`（更宽口径）独立复扫同一面。
- **未做**单跑实证的部分 = 命中文件里除去已实证 33 件之外的**全部**（603 件）
  → 它们是"可疑/假阳未分"，**不得被引用为"已证明自包含"**。

## 2. 已证 / 已修

| 项 | 证据 | commit |
|---|---|---|
| `tests/rule/test_rule_red_blue.py` 报告测试不自包含（账本 R-035 实锤件） | 修前单跑 `got 0` → 修后单跑/整文件/倒序全 passed；反向变异（注释夹具记录步）→ 红 | `087b01609e` |
| 同件在 `-n 2` 下的**并行假红**（探针 I/O 预算，不是判定口径） | `-n 2` 修前 `1 failed, 9 passed`（`detection_rate=0.8889`）→ 修后 `10 passed` | `4fb7bc1622` |
| 132 个 nodeid 单跑（33 个高命中文件）全部自包含 | `proof_results.jsonl` → census §6 | `4fb7bc1622` |

## 3. 断点（接手者按此顺序做，性价比最高）

1. **补齐可疑件实证**：把 `prove_isolated.py --limit` 从 33 提到全量候选
   （候选生成器 `build_candidates.py` 已按分值排序，改 `--per-file`/`--limit` 即可续跑；
   产物 JSONL 是 append 模式，重跑前先备份旧文件以免重复行）。
   预期收益集中在两类：形4（时钟作窗口）与形3（数字前缀命名 —— 形3 命中 383 条，
   其中 `test_<数字>_` 型 121 条，但粗口径计数含 `test_500_is_emergency` 这类**非序数噪声**，
   故 121 本身不可当判据，仍须逐件单跑）。
2. **跨零点复跑**：形4 的"跨日漂移假红"只有零点后才现形 —— 本车道未做（需 00:00 窗口），
   交 CI 车道或下轮。判据：同一 nodeid 在 23:5x 与 00:1x 各跑一次，结果差 = 缺陷。
3. **测试隔离欠账清单（P4）**：`testint_ci_prereq.md` §3 的 M2 巡检脚本未逐件读码，
   244 件提及 `data/` 的粗口径命中需人工分诊（区分"读生产只读"与"写生产"）。
   宪法 §9.6：测试禁写 `data/` 业务目录 → 命中"写"的必须夹具化，不能夹具化的**登记不硬修**。
4. **红蓝仪器三项判据变更** = `adjudications/req_testint_01.md`（待总包裁，本车道未动判据）。

## 4. 禁越界自律记录（本车道实际避开的件）

- `tests/ex_core/**`（z-land3 幂等面，4 红归因中）、`tests/governance/commit_gates/**`（z-silent 在动，
  本车道只跑不改）、`tests/automation/test_flowthrough_verifier.py`（z-verifier3 独占）
  → **均只读/只跑，零改动**。
- `tests/plan_engine/test_judgment_ledger.py`：形1 弱信号命中，但工作区有他人 unstaged 改动
  → 按宪法 §3.4 只登记（census §5），未改。
- 新建件仅 3 个 md（census / ci_prereq / req_testint_01）+ 1 个测试件改动；
  `src/zephyr/**` 与 `scripts/**` **零改动**（测试仪器问题全部在 tests 侧解）。

## 5. 本车道工具链（未入库，落 `.runtime/tmp/ff-testint/`，有 TTL）

`scan_test_selfcontain.py`（主扫描）· `probe_fn.py`（漏报界定）· `build_candidates.py`（候选）
· `prove_isolated.py`（单跑实证，含"收集失败不作证据"分类）· `render_census.py`（普查表生成器）
· `revorder_plugin.py`（倒序实证插件）
→ **若下轮还要用，须在 TTL 清理前搬进 `scripts/` 并走新建件三件套**（本车道按任务书要求只落 tmp 区）。
