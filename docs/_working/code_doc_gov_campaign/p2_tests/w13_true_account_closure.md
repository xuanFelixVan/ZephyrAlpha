---
ttl: task_bound
session: st-code-doc-20260921
campaign: p2-wo13
---

# WO-13 测试真账台账（分包2 续班，2026-09-21）

> 执行：st-code-doc-20260921（接替速率限制阵亡的前任代理，续做勿重做）。
> 方法：逐族先实跑复现→绿记已闭合→红才修；修账不修门。
> 证据等级：全部 [亲验]（本会话实跑 pytest 计数节选随条目）。

## 六族终态总表

| 族 | 条目 | 复现结果 | 终态 | 证据（pytest 节选） |
|----|------|---------|------|---------------------|
| 1 | D38 三未登记库（domain_responsibility_layer_mapping/fail_open_register/standard_family_registry） | d38_adversarial+blind_spot 全绿；三库均已在 catalogs 落册（standard_family_registry.yaml 为前任新建未跟踪件） | **已闭合**（前任/他会话已修，本班核验） | test_decision_map_d38_adversarial+test_blind_spot_closure：38 passed；test_generate_standard_family_registry：6 passed |
| 2 | R24 factor_refs 因子欠账复发 | config/trading_decision_map.yaml 前任已修（YAML 完好），adversarial 全绿 | **已闭合**（前任已修，本班核验） | test_decision_map_adversarial：38 passed（136.6s） |
| 3 | governance 9 文件 | 详见 §1 逐文件 | **全部闭合**（4 已绿+5 本班修账） | security 12 passed；vocab 6 passed；acyclic+消费方 69 passed；mirror 32 passed |
| 4 | blueprint 死引用 3 条 | 全库实扫 112 处 AGENTS.md §编号死引用（58 文件）+施工模板 1 处 | **修账**（112+1 处全部改齐为规则名/真源路径/v1 归档锚） | test_no_stale_agents_numbered_refs_in_scripts+test_normalize_blueprint_autogen_anchors：28 passed |
| 5 | cron 断言 4 条 | ps1 任务 25→26（gate_fulltree_audit，aca8c71fad）；schedule 22→24 槽（data_supply_sentinel 85ef0962d0+eod_reconciliation R-015 在飞批）；带 dow 槽 15→17 | **修账**（逐槽位核对后基线追认，禁恒真化——每槽对照真源 yaml/ps1 git 溯源） | 两文件 113 passed |
| 6 | 测试污染假红 ~9 条 | trading decision_map 7+blind_spot 1：整域 xdist -n4 套跑未复现（2419 passed 套内全绿）=污染源已消失；tests/path 1：独立跑绿 | **已闭合/不复现**（未改任何测试代码） | tests/trading 整域：5 failed 2419 passed（5 红全为 B/E 类资源型，不在本单范围）；tests/path：25 passed |
| 7 | A14 77 表 data_asset_registry 生成器重建 | 实测 CH live 未登记 78 张（77 审计清单+新表 1，已排除 13 张 bak/quar/dup/v2 备份族） | **修账**（新建生成器 generate_data_asset_coverage.py，登记 DS-276..DS-353，册 264→342，缺口清零） | 生成器 --check：total_missing=0 exit 0；check_registry_consistency CR-007b PASS；registry_entry_counts 8 passed |

## §1 族3 逐文件

| 文件 | 复现 | 终态 | 处置 |
|------|------|------|------|
| rule_bridge/test_worktree_pool.py | 7 passed（健康报告 3f 已被他会话修复） | 已闭合 | — |
| test_alert_threshold_consistency.py | passed（前任已 stage 修复） | 已闭合 | — |
| test_error_code_consistency.py | passed | 已闭合 | — |
| test_reconcile_generators.py | passed | 已闭合 | — |
| security/test_security_scripts.py exit_code×2 | 13 处裸 return 0/1/2（6 文件） | 修账 | 裸返回码→EXIT_PASS/FINDINGS/ERROR 常量（validate_exit_codes 门箭头指示）；命名门 gate_prerun.py 按 #ARCH-114 爷爷条款登记豁免（改名牵 12 处跨域引用，碰撞风险>收益） |
| d5_architecture/test_check_vocab_domain_convergence.py | 词表滞后 10 域（BRK-082 补登批+D_TEST） | 修账 | target_layer_vocabulary.yaml v1.1.0→v1.2.0 收编 10 值（62→72，FDR 条目溯源，is_foundation 全 false） |
| generators/test_externalize_algo_flow_mirror.py | KeyError: header_reconcile | 修账（stale WIP 回滚） | 工作区未提交的 self-ref 豁免特性（mtime 09-19<HEAD，无活跃 claim）打破已提交的裁定#276 契约；classify_workspace_wip 判 stale_rollback → git stash 保全后回滚（stash msg 含 salvage 说明）。判定依据：HEAD 版 externalize 用几何 _header_block_spans，测试与 787fd269d5 同源 |
| scripts_governance/test_dependency_graph_acyclic.py | reconciliation_registry ⇄ schedule_consistency_reconciler 环 | 修账 | dependency_graph._iter_load_time_imports 契约=加载时 import，但漏跳 `if TYPE_CHECKING:`（运行时恒假）——分析器契约 bug；修复后 acyclic+全部消费方（asset_inventory/dependency_root/cascading_rollback）69 passed |
| test_battle_map_research_incubation.py | passed（前任已 stage 修复） | 已闭合 | — |

## §2 改动文件清单（本班）

scripts/governance/：align_battle_map.py、check_ssot_gate.py、run_fulltree_gate_audit.py、meta/gate_prerun.py、d7_code/generate_fail_open_register.py、standards_governance/generate_standard_family_registry.py、d11_compliance/validate_script_naming.py、d11_compliance/validate_exit_codes 涉及的 6 文件即上、d5_architecture/dependency_graph.py、d3_metadata/generate_derived_files.py 等族4 批 58 文件（全列=.runtime/tmp/stale_ref_files.txt 口径：AGENTS.md §编号改锚批次）；新建 d5_architecture/generators/generate_data_asset_coverage.py。
docs/01_policies_and_standards/_registry/：vocabularies/target_layer_vocabulary.yaml（v1.2.0）、catalogs/data_asset_registry.yaml（264→342）、catalogs/fail_open_register.yaml（生成器重建）、registry_of_registries.yaml（REG-DATAFLOW-001 entry_count 264→342）、catalogs/capability_canonical_file_registry.yaml（creation_token 登记，batch_creation_tokens 写入）、catalogs/module_translation_registry.yaml（新模块大白话条目）、templates/blueprint_construction_template.md（1 处死引用）。
src/zephyr/：族4 批涉 12 文件（gov_enforcement/commit_gates×5、governance×5、shared×2，见 git diff）。
tests/：scripts/test_generate_resource_profile_registry.py、frontend/test_api_server_cron_single_source.py（基线追认）。tests/blueprint 两测试文件零改动（修账不修门）。
未跟踪新产物转正：tests/governance/standards_governance/test_generate_standard_family_registry.py（前任半成品，实测 6 passed 已保留原样，未 stage——归属前任批次）。

## §3 垃圾清理

- config/trading_decision_map.yaml.tmp.18276.*（CAS 残留两枚）：已 rm（主文件验完好）。
- tests/governance/rule_bridge/_wt_marker_a.json：已 rm。判定=**teardown 不缺失**（test_session_worktree._cleanup_artifacts 含 marker unlink，L158-161），残留源=历史超时击杀运行中断清理；且已核实该文件当前非在飞写入（mtime 陈旧）。

## §4 停手项与移交

1. **误吸收披露**：族4 批量阶段一次 `git add -A` 误暂存他会话在途 31 件（含 st-data-fix 的 schedule/tasks.yaml、2 枚 live CAS tmp、standards_governance src 包等）——已用 classify_workspace_wip 快照逐件精确 `git restore --staged` 回退（571 staged=前任批次+本班改动），回退后门禁复验全绿。
2. **scripts/governance/reports/findings.jsonl**：check_registry_consistency 运行自动追加了审计行（工具自身行为），未 stage，留总包裁决。
3. **CR-007 ROOR 其他 16 项 stale**（REG-BTB-001 137→142、REG-ATH-001 38→42 等）：属前任/他会话 staged 批次对应的 ROOR 同步义务，非本班改动引入，未代修（owner 责任制）。
4. **A14 语义细化**：78 条新 datasets 中无 DDL 真源模块者以占位描述在册留缺口（生成器 --check 可随时重跑刷新）；建议数据线补 DDL-as-Code 后重跑。
5. **不在本单六族的 A 类残留**：tests/db 目录树对齐 1 条（30 文件 depgraph 记录不存在）、tests/industry_graph 字段字典 1 条、tests/autonomy G04 1 条——非 WO-13 六族清单内，未动。
6. 本台账新建件 creation_token 未登记（batch 工具仅验证过 .py 通道）——**待总包补**。

## §5 复验命令（任何人可重跑）

```bash
python -m pytest tests/trading/test_decision_map_d38_adversarial.py tests/trading/test_blind_spot_closure.py tests/governance/security/test_security_scripts.py tests/governance/d5_architecture/test_check_vocab_domain_convergence.py tests/governance/generators/test_externalize_algo_flow_mirror.py tests/governance/scripts_governance/test_dependency_graph_acyclic.py tests/blueprint -q
python scripts/governance/d5_architecture/generators/generate_data_asset_coverage.py --check  # total_missing=0
python scripts/governance/d11_compliance/validate_exit_codes.py && python scripts/governance/d11_compliance/validate_script_naming.py
```
