---
ttl: task_bound
completes_when: 清单内问题全部施工完成、或 Owner 叫停、或清单整体被替代时
title: "08 · TDM 决策地图"
---

# 08 · TDM 决策地图

> 取数时间：2026-10-14 20:5x & 20:56（CST）　HEAD：`f300c3d02f`　分支：dev
> 原样底稿：`_raw/08_TDM_决策地图.md`（348KB + 第二遍补抽 136 段）
> 本域来源文档：182 个（第一查）+ 77 个（第二查）
> 取证：`git show HEAD:` / `git ls-tree -r HEAD` / `grep -c`；**未改任何文件、未提交**
> **本卷为两轮并集**：首轮粗查 + gp-6 深度复核。冲突处以 gp-6 实测为准并保留首轮读数备查

---

## §0 一句话结论

**TDM 挂载的口径被纠正了：不是 41 处空，是 63 处**（`module_ref: null` 41 + **裸空写法 `module_ref:` 22**，后者历史计数一直漏掉）。
63 全部为红节点，且 `DECISION-MAP` 子台 R1 warn **精确 63 条**互证 ⇒ **挂载手术一个都没做**。
更关键的是：**挂载义务门禁当前是空转的**——`config/tdm_mount_exemption_registry.yaml`（55 条豁免）是 **?? 未跟踪**，
按 gate INVARIANTS 第 4 条「豁免册缺席=前置未落自锁 skip 非拦」⇒ **TDM-MOUNT-COVERAGE 永远 skip，不会拦任何人**。

---

## §1 现状实测

| 指标 | 读数 |
|---|---|
| `config/trading_decision_map.yaml` | **8,019 行** |
| **`module_ref` 空值总数** | **63** = `grep -c "module_ref: null"` **41** + `grep -cE "^\s*module_ref:\s*$"` **22**（裸空写法） |
| `module_ref` 节点总数 | **186** ⇒ 挂载率 **123/186 = 66.1%** |
| 空值分层 | FLOW-E/P/X/F 各 1；E-L2 2、E-L3 5、E-L4 1、**E-L9 38**、F-C1 3、F-C2 1、F-C3 1、P-P2 1、P-P3 1、X-S1 1、X-S2 1、C-L1~L4 各 1 |
| red_reason 分布（63 全为红节点） | by_ref_design 20 / structural 18 / not_built 19 / terminal 4 / pending_gate 2 |
| 重点三件仍空 | `:6033`(A01)、`:6209`(A06)、**:6314**(A09) |
| 号位可用性 | **`MOD-SIG-155…160` 六个号位全仓零命中**（TDM 已用最大 = MOD-SIG-154）⇒ **补挂可零撞号执行** |
| 交叉验证 | `DECISION-MAP` 子台 **R1 warn = 63 条**，与 63 精确互证 |
| `module_mounts` 数 | **77**（f 规格 §2 期望 ≥180） |
| 覆盖账本 | `generate_map_coverage_ledger.py --check` → population **317** / mounted **67** / **unmounted_orphan 250**（期望 55） |

---

## §2 确认仍成立（A 类）

| ID | 问题 | 现状证据 | 建议处置 | 优先级 |
|---|---|---|---|---|
| **TDM-1** | **挂载口径纠正：63 处空（不是 41），且 63 全为红节点** | 41 + 22 裸空；分层见 §1；R1 warn=63 互证；A01/A06/A09 三件仍空 | **先把口径从 41 改 63 再排施工**；六节点行级手术（ruamel 保注释）：A01→MOD-SIG-155…A09→160，**号位全空闲可零撞号** | **P0** |
| **TDM-2** | **🔴 挂载义务门禁空转（f 两前置闸未满足 → 施工闸死）** | ①`module_mounts`=**77**（期望 ≥180）；②orphan=**250**（期望 55）；③`config/tdm_mount_exemption_registry.yaml`（55 条豁免，updated 10-05）为 **?? 未跟踪**，而 gate(`commit_gates/tdm_mount_coverage_gate.py`) 与 reconciler(`governance/audit/tdm_mount_coverage_reconciler.py`) 已在 HEAD ⇒ 按 INVARIANTS 第 4 条**自锁 skip 非拦** | 工单A apply 批把 `module_mounts` 推到 ≥180 + 豁免册 staged；否则该门禁永远 skip | **P0** |
| **TDM-3** | **🚨 A-6 相位判别器（`phase_discriminator`）：原结论「零施工」方向性错误，已完全颠倒 —— 实际已建成，属「P0 失落件找回」** | **四方面证据都指向已建成**：<br>①**隔离区三件套齐全**（`.runtime/quarantine/finalclean2_safety/inflight_20261010/`）：`src/zephyr/ex_core/phase_discriminator.py` **10,511 B** + `tests/trade/ex_core/test_phase_discriminator.py` **9,101 B** + `docs/03_modules/_domain_execution_core/algo_flow/phase_discriminator.yaml` **2,350 B**<br>②**遗留 `.pyc` 可反解出完整规格**（`__pycache__/phase_discriminator.cpython-312.pyc` 10,311 B，mtime 10-09）：`__all__=("TradingPhase","PhaseVerdict","PhaseDiscriminator","HALT_KEYWORDS")`；`TradingPhase` 枚举含 `CALL_AUCTION_OPEN [09:15,09:25)`、`CALL_AUCTION_BREAK [09:25,09:30)`；`PhaseVerdict` frozen dataclass 含 `phase/determined/reason/red_flags` + `is_red()`；`HALT_KEYWORDS=("临时停牌","盘中停牌","停牌核查","紧急停牌","停牌")`<br>③**registry 三方在册**：`MOD-EX-065` + capability 册 + translation 册<br>④**语义已按裁定#488 落地**（判不出=记红不拒单）<br>**原判错因**：只查 `src/` 与 `scripts/` 活树（且未覆盖 `.runtime/quarantine` 与 `.pyc`），把失落判成未施工 | **①先从隔离区取回三件套（不是从零施工）**，用 `.pyc` 反解规格做逐项验收；②再补 C445 的「记红」可审计留痕面 | **P0** |
| **TDM-4** | **TDM 文件有他会话在途** | porcelain 中 `config/trading_decision_map.yaml` 处于 **M** 状态 | 改前 **claim**，禁并发写 | P1 |
| **TDM-5** | **覆盖账本 v2（裁定#481 分母）填充班欠账** | 宇宙 **5272** / 直接挂载 2273 / 闭包归属 1266 / **孤儿 2057** / 悬空键 **1**（`MOD-BT-081`，FACTORY）。report-only **恒 exit 0** | 填充班排产；report-only 恒绿是"假绿"风险点 | P2 |

---

## §3 已过时 / 已消化

| 原条目 | 判定 | 依据 |
|---|---|---|
| "TDM 全图 41 处 null" | **口径偏小，实为 63** | 裸空写法 22 处历史漏计 |
| TDM 测试缺失 | 已消化；并附**取数坑** | `tests/trade/trading/test_decision_map.py` collect **77 items**。⚠ **直接调 `validate_decision_map(dm, rd)` 不传 `known_strategy_ids` 会得到假红 29 error（R3 strategy_ref）**，必须走 `check_decision_map.run_checks()` 包 AST 集合 → **FAILS=0 / WARNS=393 / NODES=186**（warn 分布 R43 194 / R39 70 / **R1 63** / R11 31 / R22 19 / R25 9 / R24 3 / R21·R23·R12·R16 各 1）。另 `check_decision_map.py` **无 `__main__`**，直接 `python <file>` 静默 RC=0 是**假象** |

---

## §4 Owner 门位

| # | 事项 |
|---|---|
| **O-TDM-1** | **挂载义务前置闸**：是否批准工单A apply 批（`module_mounts` 77→≥180）；或改认新基线（77 / orphan 250）并改写 f 规格 §2 判据 |
| **O-TDM-2** | **豁免册 55 条**（`config/tdm_mount_exemption_registry.yaml` untracked）：是"有意排队"还是"漏落"，需定性 |
| **O-TDM-3** | **C445 相位判别器**：立项施工 vs 认"判不出=记红不拒单"为终态、把 C-4 降级为"补记红留痕" |
| **O-TDM-4** | 实盘拒单翻转（#490 单项裁定）— 与 17 卷 A-11 同源 |

## §5 无法判断（C 类）

| 事项 | 阻塞点 |
|---|---|
| `tests/trade/trading/test_decision_map.py` 是否全绿 | 实跑 25 passed / **52 errors**，但 52 个 error **全部**为 `SystemExit: 1`，来自 IDE safe-delete 批量守卫拦截 `tests/conftest.py:434`/`:696` 的临时目录回收（`{"count":50,"threshold":50}`）。**0 条真实断言失败**（前 25 条真跑全绿）。换 `--basetemp` 亦被同一守卫拦截 ⇒ **会话环境 artifact，非代码缺陷** |
| 图14 gap 编号跳过 D14-G10 | 当前 gap 为 G01–G09、G11、G12；counts `total_nodes: 28 / total_gaps: 11 / total_steps: 17` 自洽（17+11=28）。是否应为 29/12 需 Owner 一句判言 |

> **副作用披露（未回滚，纪律禁删）**：为绕开上述 artifact 使用了 `--basetemp=tmp/ptbase_tdm`，pytest 自建该目录（**65KB / 24 文件，untracked**）。**请 chore 车道清理**（已并入 15 卷待清项）。

## §6 可复现取证命令

```bash
grep -c "module_ref: null" config/trading_decision_map.yaml          # 41
grep -cE "^\s*module_ref:\s*$" config/trading_decision_map.yaml      # 22  ← 别漏这个
git grep -c module_mounts HEAD -- config/trading_decision_map.yaml   # 77（期望 ≥180）
python scripts/governance/d5_architecture/generators/generate_map_coverage_ledger.py --check
# 校验器正确打开方式（勿直调 validate_decision_map）
python -c "from ... import check_decision_map; check_decision_map.run_checks()"
```
