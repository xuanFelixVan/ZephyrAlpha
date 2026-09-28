---
ttl: task_bound
title: L11 案卷 F110 — 契约冻结与错误码（freeze_manifest 38 契约+error_code 788 SSoT+GATE-ERRCODE 悬空）
session: zc-l11-20260927
---

# F110 契约冻结与错误码（K 段 G14，骨架态=built/P2）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | 契约面=src/zephyr/shared/contracts/ 全族（本日 ls：execution_report/execution_report_contract/compliance_rule/capital_allocation_result/experiment_result/ctr002 生产消费适配双件/backpressure/core/enums/errors 等）；SSoT 头注"cross_layer_contracts.yaml v3.0"（freeze_manifest.yaml 头注） |
| 下游消费 | 全链跨层调用面（冻结接口改动 MUST 过 ContractImpactAnalyzer，头注铁律）；错误码消费=errors/ 六错误类型件（execution_rejection/risk_limit_violation/data_quality/factor_computation/contract_violation/signal_degradation_warning） |
| 自动化触发 | GATE-ERRCODE（gate_registry.yaml:335，entry=pytest tests/governance/test_error_code_consistency.py）——**但 wiring_gap §1.6 判"悬空 4"之一：无钩子无启动器承接**+「半接线 2」之一（仅单一脚本顺带调）；另有 GATE-ERRCODE-CONSISTENCY（:1070） |
| 真源与注册表 | freeze_manifest.yaml：module_id=MOD-INF-016、freeze_version 1.0.0、frozen_date 2026-05-05、phase C；本日 grep contract_id=**38**（与总册"38 契约"精确吻合）；错误码 SSoT=architecture_model/contracts/error_code_registry.yaml（REG-ERRCODE-001，ROOR:467-469 锚），本日 yaml 实测 error_codes=**788**（与总册"788"精确吻合） |
| 门禁与质量尺 | 双 gate 在册（:335/:1070）但承载面悬空/半接线（wiring_gap §1.6 机判+本日 grep 复核在册）；冻结修改评估器 ContractImpactAnalyzer（头注引用） |
| 当前运行状态 | **黄**：两 SSoT 计数精确吻合（38/788）=账实相符；黄红点=GATE-ERRCODE 悬空（注册表↔代码双向对账无人跑）+errors/ 六类实件与 788 码的映射覆盖面未证 |

## 二、子模块三级枚举

1. **冻结清单层**：freeze_manifest.yaml（38 contract_id；MOD-INF-016；stability=evolving 治理锚头注）。
2. **契约实件层**：shared/contracts/ 根（execution_report_contract、execution_report、compliance_rule、approval_types、capital_allocation_result、experiment_result、contract_bus、escalation/、execution/、experiment/、backpressure/、core/、enums/、_frozen_signatures/、_codegen_snapshot.txt）。
3. **错误码层**：contracts/errors/ 六类型件（本日 ls）+SSoT=architecture_model/contracts/error_code_registry.yaml（788 码）。
4. **适配器层**：ctr002_producer_validator.py+ctr002_consumer_adapter.py（生产/消费双侧契约校验对）。
5. **门禁层**：GATE-ERRCODE（:335 pytest 对账）+GATE-ERRCODE-CONSISTENCY（:1070）——承载悬空待接线。

## 三、接线四态独立复核

- **契约实件→消费链：已接线**（ctr002 双侧适配器+errors/ 六类被 risk/execution 面引用；freeze 头注 SSoT 声明）。
- **GATE-ERRCODE 对账：悬空**（wiring_gap §1.6 机判+gate_registry 在册无钩子承接——"账在闸空"样本；同族 GATE-DRIFT/GATE-ZR 同判）。
- **788 码↔errors/ 六件映射：未证**——注册表体量大而代码错误类型件仅 6，覆盖率未机检（悬空门本应拦的正是此面）。
- **停用/弃用：无**。

### 骨架勘误
1. 总册 F110"built"须加黄旗：**SSoT 账实相符（38/788 本日精确复现）但执法门悬空**——"注册表↔代码双向对账"当前无人执行，漂移发现靠偶然；建议随 wiring_gap §2.1-C5"装饰件接线"批同窗接 GATE-ERRCODE。
2. SSoT physical_path 在仓外目录 architecture_model/contracts/（ROOR:469）——ROOR 条目路径前缀口径与仓内路径并存，检索时易扑空，勘误登记。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | GATE-ERRCODE 悬空（对账无人跑） | 接 pre-commit/CI 钩子（C5 装饰件接线批） | P1 |
| 2 | 788 码↔六错误类覆盖率未证 | 随门接线出首份对账报告定基线 | P2 |
| 3 | 冻结契约 38 条冻结态逐条年检 | ContractImpactAnalyzer 触发面抽样 | P2 |

## 五、自审闸三态

**挖干（38/788 双实测+六错误件 ls+双 gate 在册锚+悬空判引用）✅；待裁（无——接线归 C5 批既有排期）；待挖（788 码逐族透视=待门接线后机出）。**

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
grep -c "contract_id" src/zephyr/shared/contracts/freeze_manifest.yaml   # 38
python -c "
import yaml;from pathlib import Path
d=yaml.safe_load(Path('architecture_model/contracts/error_code_registry.yaml').read_text(encoding='utf-8'))
print('error_codes=',len(d['error_codes']))"                             # 788
ls src/zephyr/shared/contracts/errors/
sed -n '335,338p' docs/01_policies_and_standards/_registry/catalogs/gate_registry.yaml
```
