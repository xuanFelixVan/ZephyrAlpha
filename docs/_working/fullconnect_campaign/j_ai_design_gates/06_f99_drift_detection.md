---
ttl: task_bound
title: F99 漂移检测——挖干案卷
session: zc-l10-20260927
---

# F99 · 漂移检测（30 检测器+基线/级联/金丝雀+双 watchdog）

> 总册行（00_全环节总册.md:174）：built｜上游 F98｜下游 告警｜P1｜G3
> 第一证据源：fullflow_mining/m3_governance/02_reconcilers.md（漂移对账互补模式）＋src/zephyr/gov_drift/

## 一、六向台账（实证锚点）

| 向 | 实测证据（本日复核） |
|---|---|
| 上游输入 | F98 门禁执行面结果＋全仓架构面（depgraph/blueprint/manifest 校验器脚本产出，_detector_registry.yaml detectors.existing[].script 实证指 d5_architecture/validators/*） |
| 下游消费 | alert_router.py/events.py→告警；dashboard.py 投影；M3 04 分册"gate 防蔓延+reconciler 清存量互补"消费面 |
| 自动化触发 | 检测器为登记制（registry→dispatcher 派发）；运行时常驻面=worktree_drift_watchdog（60s 全量+10s 热文件双频，M10 豁免在案，M3 02 §3.5——属 rule_bridge 非本包，见 §三勘误） |
| 真源与注册表 | src/zephyr/gov_drift/_detector_registry.yaml（MOD-INF-011；**本日 grep -cE "^\s+- id:" = 30，与总册 30 检测器一致**）；blueprint 锚=docs/03_modules/_cross_layer/behavioral-auditor/blueprint.md |
| 门禁与质量尺 | baseline_poisoning_guard.py（基线投毒防护）＋drift_hotfix_bypass.py＋scan_mutex.py（扫描互斥+TTL watchdog） |
| 当前运行状态 | built（检测器登记与件全在；测试面分散：tests/gov_drift 1 件+tests/drift 17 件） |

## 二、子模块三级枚举（本日 ls 实测，包内 60+ 件按族收敛）

1. **检测器登记与派发**：_detector_registry.yaml（30 检测器，字段 id/script/drift_dimension/check_dims/severity/category）｜detector_dispatcher.py｜detector_core/｜drift_detector.py｜drift_engine.py｜_drift.py/_analysis.py/_core.py/_scanners.py/_infrastructure.py。
2. **基线/级联/金丝雀三件套（总册点名，全实存）**：baseline_manager.py＋baseline_poisoning_guard.py｜cascade_detector.py｜canary_controller.py＋canary 相关（bootstrapping_calibrator.py/cold_start.py）。
3. **检测器族（30 登记外的分析器面）**：ai_construction_detectors.py｜agent_stability_index.py｜autonomy_regressor.py｜backcompat_checker.py｜contract_drift_detector.py｜config_consistency.py｜correlation_engine.py｜credibility_engine.py｜cross_module_score.py｜file_attr_checker.py｜gitignore_auditor.py｜artifact_scanner.py 等。
4. **对抗与取证**：chaos_injector.py｜forensics_engine.py｜git_bisector.py｜baseline_poisoning_guard.py｜drift_hotfix_bypass.py。
5. **输出与运维**：alert_router.py｜events.py｜dashboard.py｜gate_persistence.py｜handoff_manager.py｜incremental_scanner.py/headless_scanner.py｜scan_mutex.py（:300 TTL 自动续期 watchdog）｜migration_plan.yaml｜__main__.py CLI。
6. **互锁面**：brain_integration.py（与 AI 层）｜absence_manager.py｜steady_state 相关与 F100 共享面（validator_event_bridge 在 F100 包）。

## 三、接线四态独立复核

- 总册判 **built**：主体成立（30 检测器登记复算一致＋三件套全实存＋CLI/告警路由在产）。
- **骨架勘误**："双 watchdog"在 gov_drift 包内**仅一处实证**=scan_mutex.py:300"TTL 自动续期 watchdog"。若总册指 worktree_drift_watchdog 的 60s+10s 双频节拍（M3 02 §3.5"双频"），则该件在 src/zephyr/gov_enforcement/rule_bridge/（commit 链面，M10 豁免），不属 gov_drift 包——总册表述归属需勘正或 Owner 裁定"双 watchdog"另有所指（进待裁）。
- 测试接线弱面：tests/gov_drift 仅 1 件 vs 包内 60+ 模块；主测试网在 tests/drift（17 件）——测试与模块不同目录树，CI 收敛面需 Owner 确认是否有意分层。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| G1 | "双 watchdog"表述与包内实证不符（仅 scan_mutex 1 处） | 待裁：勘正为"扫描互斥 TTL watchdog"或指认第二只真身 | P2 |
| G2 | 30 登记检测器与包内 60+ 分析器两套面无对账说明 | 注册表补"登记 vs 库内分析器"关系段（生成器产出） | P2 |
| G3 | tests/gov_drift 覆盖 1 件（薄） | 高风险件（baseline_poisoning_guard/scan_mutex）配对测试 | P1 |
| G4 | 检测器告警下游闭环（alert_router→告警消费）无本卷实证 | 交叉 M5 接线普查卷宗核对 | P2 |

## 五、自审闸三态

**检测器登记与三件套=挖干可施工**（30 复算+全件 ls 实证）；**"双 watchdog"归属=待裁**；**告警下游闭环=挂起**（待 M5 普查卷交叉）。

## 六、复跑命令

```bash
grep -cE "^\s+- id:" src/zephyr/gov_drift/_detector_registry.yaml   # 30
ls src/zephyr/gov_drift/ | grep -E "baseline|cascade|canary"        # 三件套
grep -n "watchdog" src/zephyr/gov_drift/scan_mutex.py               # 唯一 watchdog 实证
find tests/gov_drift tests/drift -name "test_*.py" | wc -l          # 18（1+17）
python -m zephyr.gov_drift --help 2>&1 | head -5                    # CLI 入口
```
