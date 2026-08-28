---
ttl: permanent
---

# AI-NIGHT-001 顺手实证小包核查报告

- 日期：2026-08-19
- 范围：#210 指标注册数口径 / 阶段4 防白跑六项（#69/#70/#72/#73/#80/#82）/ #172 plain_zh 缺口
- 性质：全部只读实证；任务1 裁定为幽灵注册（登记待裁定，未擅动注册表）；无 git commit；未改 src/；未改 tracker。

---

## 任务1 · #210 指标注册数口径（41 vs 40）

**结论：差项真身 = IND-COMP-001 一目均衡表（Ichimoku Kinko Hyo），属"幽灵注册"（注册表有、代码无），且为已知设计态登记——非注册滞后、非计数口径差。按预案登记待裁定，不擅自删、不补登。**

### 实证链

**注册表侧**（`docs/01_policies_and_standards/_registry/catalogs/technical_indicator_registry.yaml`）：

- L40 `entry_count: 41`，物理条目实数 41 条 = trend 10（L78-397）+ momentum 10（L400-719）+ volatility 8（L722-977）+ volume 7（L980-1203）+ reversal 5（L1207-1366）+ **composite 1（L1368-1401）**。
- 第 41 条 IND-COMP-001（L1368）：`status: candidate`（L1383）、`code_symbol: null`（L1400）、`algorithm_status: "pending_backtest"`（L1398），条目内自带 2026-08-17 AI-AUDIT08 审计注释（L1396-1397）："trend.py 实际无一目均衡表实现（code_symbol=null 设计态），algorithm_status 由机械推导的 quantized 更正为 pending_backtest"。
- 头部 description（L23-24）仍写"5 大类 40 指标 58 输出列"——叙述口径只数已实现的 5 类 40 个，entry_count 含设计态第 41 条，两者并存即"41 vs 40"差异来源。

**代码侧**（`src/zephyr/factor/technical_indicators/`，以 `@TechnicalIndicatorRegistry.register` 装饰器实证）：

| 文件 | 实有注册类（行号） | 数 |
|---|---|---|
| trend.py | MA L197 / EMA L222 / WMA L247 / DEMA L271 / MACD L298 / ADX L326 / DMI L353 / CCI L378 / SAR L407 / TRIX L474 | 10 |
| momentum.py | KDJ L160 / RSI L190 / WR L215 / ROC L242 / MTM L267 / CMF L293 / UOS L323 / AO L357 / CMO L383 / StochRSI L413 | 10 |
| volatility.py | ATR L160 / BOLL L186 / Keltner L213 / Donchian L245 / STDDEV L271 / BandWidth L296 / PercentB L321 / HistVol L346 | 8 |
| volume.py | OBV L132 / MFI L157 / VWAP L190 / VR L223 / AD L256 / PVT L282 / WVAD L307 | 7 |
| reversal.py | CandlestickPattern L139 / RSIDivergence L202 / MACDDivergence L235 / BOLLBreakout L269 / VolumePriceDivergence L297 | 5 |
| **合计** | | **40** |

- 全仓 grep（src/ + tests/）`ichimoku|一目均衡|tenkan|kijun|senkou|chikou` **零命中**——一目均衡表无任何代码落地，排除"注册滞后（代码有注册表缺）"与"code_path 指错位置"两种情形。
- 包 `__init__.py` L17-24 docstring 亦只列五类 ~40 个，无 composite。

### 裁定建议（登记待裁定，本批不动）

- 该条目为 2026-08-14 有意补登的**设计态**条目（schema v2.1 规则：代码未落地=库管设计态，L13），且已被 AI-AUDIT08 标注纠偏，信息自洽。是否保留设计态条目 / 何时施工 Ichimoku 实现，归治理裁定。
- 可选小修（留给裁定方）：description L23 "5 大类 40 指标" 与 entry_count 41 的叙述-元数据张力，可在下次条目维护时顺手注明"含 1 条设计态 composite"。

---

## 任务2 · 阶段4 防白跑实证（对照 AI-FIX-001 merge commit a539c1fcb6）

commit a539c1fcb6（2026-08-16 merge ai/AI-FIX-001 → dev）自述治理范围：#69/#70/#73/#80/#82/#85（7 施工 commit），改动文件 12 个。**逐项代码实证如下：5 项已吸收，1 项（#72）未吸收。**

| # | 遗留项 | 结论 | 实证 |
|---|---|---|---|
| 69 | d6 三 hook argparse 兼容 positional files | ✅ **已吸收** | `scripts/governance/d6_security/detect_git_dangerous.py` L202 `add_argument("files", nargs="*")` + L207 `scan_files(args.files) if args.files else scan_repo(...)`；`detect_shell_dangerous.py` L187-192 同款；`detect_permanent_file_deletion.py` L129-131 同款（三处注释均留"#69 兼容修复/#69 兼容"字样）。三 hook 现均可被 pre-commit 喂文件名参数，不再 exit 2。 |
| 70 | reconciliation_registry.py I001 import 排序 | ✅ **已吸收** | `src/zephyr/governance/audit/reconciliation_registry.py` import 块（L182-191）排序合规；实测 `ruff check` 该文件：I001 已消，仅余 L8903 UP015 1 个——与 tracker #70 登记的"dev base 1 error（UP015 存量）"吻合，增量瑕疵已清偿。 |
| 72 | git_safety_wrapper -d/-D 区分 | ❌ **未吸收** | `scripts/git_safety_wrapper.ps1` L148 仍为 `($fullArgs -match '-D|--delete-force')`——PowerShell `-match` 默认大小写不敏感，`git branch -d <merged>` 依旧命中被拦。a539c1fcb6 改动文件清单不含本脚本；git log 实证最近触碰为 c79de22c0d（#58 收口），AI-FIX-001 未染指。**缺陷仍在，仍需治理批修（建议 `-cmatch` 或参数级甄别），不白跑。** |
| 73 | TTL 质保链（post-commit 增量校验 + 每日全量 rejudge） | ✅ **已吸收** | ① `scripts/governance/d3_metadata/backfill_ttl_metadata.py` L6 头注"#73 起自动触发"，L360 `--check`（隐含 dry-run 零写入）、L362 `--rejudge`；② `src/zephyr/governance/audit/reconciliation_registry.py` L4914/4937/5074 `GATE-TTL-DRIFT-INCREMENTAL` post-commit reconciler（priority=285）在册；③ 计划任务实证：`schtasks /query /tn ZephyrAlpha_TTLRejudgeDaily` → Ready，下次运行 2026-08-20 18:05——每日全量 rejudge 常态化已落地。 |
| 80 | session_worktree --to 默认 main→dev | ✅ **已吸收** | `scripts/session_worktree.py` L628 `p_merge.add_argument("--to", default="dev", ...)`，注释明示"2026-08-15 前误默认 main，#ARCH-WORKTREE-WRITE-INTEGRITY-001 P1-2② 修正"（merge 冲突裁决取 WDOG 版文案）。 |
| 82 | data_source_operation_manual.md 路径双重过期 | ✅ **已吸收** | `docs/03_modules/_domain_data/data_source_operation_manual.md` L120 主线环境已定为"模拟盘 `E:\国金QMT交易端模拟`（全项目模拟盘化主线）"；L122/208/219/228/240/244/256/304/306/648-649 全部示例路径均为 E 盘模拟端。残余 `d:\ZephyrAlpha` 引用（L30/33/36）为本仓仓库路径——项目实体就在 D 盘，非过期。双重过期（D→E 搬迁 + 实盘→模拟主线）均已修复。 |

**防白跑总结**：阶段4 只需安排 #72 一项（git_safety_wrapper.ps1 L148 大小写不敏感误拦 `-d`）；其余五项已被 a539c1fcb6 吸收，勿重复立项。

---

## 任务3 · #172 翻译注册表 plain_zh 缺口规模

**结论：缺口 4450 条（占 75.1%），>50 条 → 登记排期，不可本批补。**

实证（`docs/01_policies_and_standards/_registry/catalogs/module_translation_registry.yaml`，PyYAML 解析）：

- 总条目数：**5928**（tracker #172 登记时口径 5927，现 +1，吻合）
- plain_zh 字段缺失（无该 key）：**0**
- plain_zh 空值/空白：**4450**
- 缺口合计：**4450**（与 tracker #172 "4450/5927 plain_zh 待覆盖"登记数完全一致，无漂移）

前 20 条缺口样本（unique_key = module_path）：

1. src/zephyr/infrastructure/asset_inventory/telemetry.py
2. tests/feedback/test_teacher_transfer.py
3. src/zephyr/shared/infra/process_pool.py
4. tests/feedback/test_training_data_gov.py
5. tests/feedback/test_cognitive_load.py
6. scripts/governance/d7_code/detect_silent_degradation.py
7. schemas/categories/market_hog_spot_index.py
8. scripts/governance/meta/pre_op_check.py
9. tests/audit/test_value_added_baseline.py
10. tests/governance/orchestrator/test_objective_tracker.py
11. tests/test_tick_replay_data_handler.py
12. tests/asset_inventory/test_classifier_asset_inventory.py
13. src/zephyr/infrastructure/a2a_protocol/layer2_communication/a2a_state.py
14. tests/trading/test_finalizer.py
15. scripts/governance/d5_architecture/detect_constraint_violations.py
16. tests/agent_rbac/test_derive_rbac.py
17. tests/safety/test_injection_engine.py
18. src/zephyr/gov_enforcement/rule_bridge/commit_gate_registry.py
19. src/zephyr/governance/ops_governance/budget_tracker.py
20. tests/trading/unit/test_design_decisions_unit.py

样本形态观察：缺口遍布 src/ 与 tests/（tests/ 占比目测过半），tests 条目大白话价值密度低——建议排期时按"src 优先、tests 靠后/从简"分档，或裁定 tests 条目豁免 plain_zh 以缩减有效缺口规模。

---

## 汇总

| 任务 | 结论 |
|---|---|
| #210 | 差项 = IND-COMP-001 一目均衡表，幽灵注册（已知设计态，AI-AUDIT08 已标注），登记待裁定，本批未动注册表 |
| 防白跑 | #69/#70/#73/#80/#82 已吸收；**#72 未吸收**（git_safety_wrapper.ps1 L148 仍误拦 `git branch -d`） |
| #172 | plain_zh 缺口 4450/5928，>50 → 登记排期 |

本批改动：仅新增本报告文件；无 commit；src/、tracker、注册表均未触碰。无阻塞。
