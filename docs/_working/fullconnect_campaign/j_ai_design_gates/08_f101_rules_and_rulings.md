---
ttl: task_bound
title: F101 规则与裁定体系——挖干案卷
session: zc-l10-20260927
---

# F101 · 规则与裁定体系（86 trae_*.yaml+ruling_registry 同 commit 原子）

> 总册行（00_全环节总册.md:176）：built｜上游 Owner 门｜下游 全链｜P1｜G5
> 第一证据源：fullflow_mining/m3_governance/03_registry_families.md＋docs/01_policies_and_standards/rules/＋catalogs/ruling_registry.yaml

## 一、六向台账（实证锚点）

| 向 | 实测证据（本日复核） |
|---|---|
| 上游输入 | Owner 裁定（RULE-RULING：裁定#NNN 先登记 ruling_registry 同 commit 原子）＋Owner 修标（OBJ_R 四步流水线上游客户，F95） |
| 下游消费 | F98 门禁面（rule_enforcement/ 45 个 g_trae_*.yaml 门定义即规则→门的编译产物）；capability_lookup 渐进披露；宪法 AGENTS.md 细节检索序 |
| 自动化触发 | GATE-RULES-INTEGRITY reconciler 每 commit 恒真触发（M3 02 §3.3 :6741"总是触发"；batcher 启用时 defer 到 post-flush :6763-6772） |
| 真源与注册表 | 规则真源=docs/01_policies_and_standards/rules/（**本日 ls trae_*.yaml = 86，与总册一致**）；裁定真源=catalogs/ruling_registry.yaml（**本日 grep "^- ruling_id:" = 231，与 M3 03 分册实测一致**） |
| 门禁与质量尺 | 规则→门的编译由 F98 消费；规则自身执法=GATE-RULES-INTEGRITY（恒真）＋RULING-REFERENCE（**疑似判据失效：零配对红证，§1.6 宪法映射行**） |
| 当前运行状态 | built（黄）：86 册+231 裁定在产；裁定引用校验执法件疑似失效=RULE-RULING 第 8 条硬规则的执法链半断 |

## 二、子模块三级枚举

1. **规则册层（86 trae_*.yaml）**：编号连续域 003-054 区间与 rule_enforcement/ 门定义覆盖域对照——门定义 45 个 g_trae_*.yaml（F98 卷 §二.6）对 86 规则的覆盖率≈52%，**"一规则一门"未满配**（门可多规则合一，但映射关系无册面记录=待裁项）。
2. **裁定册层（ruling_registry.yaml，231 rulings）**：entry_schema 九字段（OBJ_R DESIGN R1 行引用）＋#20-D 编号铁律＋RULE-RULING 同 commit 原子；消费例=OBJ_R 历史重放器的重考历史源＋risk_tier 门位变更留痕。
3. **规则→门编译层**：src/zephyr/gov_enforcement/rule_enforcement/ 内 g_trae_*.yaml 门定义+rule_engine/（RuleLoader:79/canary/shadow_runner/debt_auditor——规则上线的金丝雀/影子/债务审计三态）。rule_shadow_runner+rule_canary_manager=新规则投产的灰度通道（设计在库；生产接线度本卷未测压，进待裁）。
4. **执法对账层**：GATE-RULES-INTEGRITY reconciler（恒真+defer 双形态）＋secret_registry_drift 类对账先例。

## 三、接线四态独立复核

- 总册判 **built**：册面成立（86/231 双复算一致）；**执法链面打折**——§1.6 实证 RULING-REFERENCE"零配对红证"（疑似判据失效 43 门之一）：裁定引用是否被门真实校验无测试证据，RULE-RULING 同 commit 原子实际靠流程纪律而非机检闭环。
- **骨架勘误（口径补强）**：总册 F101 行"86 trae_*.yaml"指规则册目录文件数；F98 canonical 91 门为另一对象（执行面 canonical 登记，M3 03 §六明确"同为 gate 名录但对象不同，不并"）。两数并存非矛盾，引用时禁混用。
- rule_canary/rule_shadow 灰度通道的活跃度未测压——rule_engine 5 件代码在产但无运行记录锚，进待裁。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| G1 | RULING-REFERENCE 零配对红证（RULE-RULING 执法半断） | 补配对红证测试+同 commit 原子机检闭环 | P0 |
| G2 | 86 规则→45 门定义映射无册面 | 映射段生成器产出（对齐"清单生成器产出"红线） | P1 |
| G3 | 规则灰度通道（canary/shadow）活跃度不明 | 试运行一次 shadow_runner 留痕后判定 | P2 |
| G4 | 231 裁定无触发率/消费率统计 | 对齐宪法 §4 季度退役审计（reconcile_execution_log 触发率）出对账段 | P2 |

## 五、自审闸三态

**册面=挖干可施工**（86/231 双复算）；**执法闭环=待裁**（RULING-REFERENCE 红证+映射册）；**灰度通道=挂起**（活跃度待测压）。

## 六、复跑命令

```bash
ls docs/01_policies_and_standards/rules/trae_*.yaml | wc -l          # 86
grep -c "^- ruling_id:" docs/01_policies_and_standards/_registry/catalogs/ruling_registry.yaml  # 231
ls src/zephyr/gov_enforcement/rule_enforcement/g_trae_*.yaml | wc -l # 45（门定义覆盖面）
grep -n "总是触发" src/zephyr/governance/audit/reconciliation_registry.py | head -2  # GATE-RULES-INTEGRITY 恒真
```
