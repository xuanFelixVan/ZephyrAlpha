---
ttl: task_bound
doc_type: report
title: 深度审查报告——TDM决策地图加载校验（T01）
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：TDM决策地图加载校验（T01）

- 状态: **已审**
- 级别: P0｜类型: 闸门
- 基线 commit: 2fa92002c3（工作树 bf65648609；本文件自基线起零变更，锚点双有效）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/trading/decision_map.py:348(load_decision_map)/:888(validate_decision_map)/:1011(pit_drift_report)`
- 生产调用方: decision_map_gate:96（经 check_decision_map.run_checks）、algo_note_sync_gate:227-229、decay_watch:75-80、trading/__init__:77-84、daily_decision_orchestrator:340（旁系：绕过本模块裸 yaml.safe_load，见 T03 报告）
- 测试文件: tests/trading/test_decision_map.py（929 行/67 测试）+ test_decision_map_adversarial.py（540 行/38 测试）
- 缺陷模式 checklist 15 条已前置过一遍（命中：#4 双份承载、#10 YAML 静默缺陷面）
- 材料包缺项: 运行时证据（gate 日志近 N 天）未取数；数据画像不适用（本对象消费注册表 YAML 非行情数据）

## 1 对象快照

- 范围：`load_decision_map`（YAML→frozen dataclass）、`validate_decision_map`（R1-R41+R98/R99 门禁纯函数）、`pit_drift_report`（D119/D121 PIT 漂移三态）、`__main__` CLI。排除项：`scripts/governance/d5_architecture/generators/check_decision_map.py`（封装层，属 P2 基建对象）；gate 侧只审消费方式。
- 运行时证据：实跑 `python -m zephyr.trading.decision_map validate` → `{"ok": true, "issue_count": 101}`（全 warning 级，fail=0），与 gate"error=0 才可消费"契约一致。附带观察：runpy 方式触发 RuntimeWarning（模块经包导入已被预载，`decision_map.py:1073` CLI 入口与包 `__init__` 导入顺序问题，纯噪音 P3）。
- 测试覆盖概况：正反两套共 105 测试，覆盖 R 规则矩阵较全；R12 权重 NaN/inf 边界与 duplicate (node_id,state) 格未见专测（见 §2/§4）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A | R12 权重只设上界无下界/无和≥1约束：sleeve 全体权重和可低至 >0（如 0.01）静默通过；NaN/inf 权重被 `not (0<w<=1)` 正确拦截（假阳性方向安全） | decision_map.py:975-994 | P3 | 构造 weight=0.001 单 sleeve 地图跑 validate，观察无 error |
| A | R41 `mounted_reason` 首词校验对 mounted 非空的格子也生效（填了 mounted 又写了词表外 reason → error）：过严不漏，方向安全 | decision_map.py:652-661 | P3 | mounted 非空+reason="随手写的" 跑 R41 分支 |
| A | 矩阵格 (node_id,state) 二元组无唯一性校验：同一格写两遍各自通过 R7/R41，下游按遍历序取值 | decision_map.py:373-383（load 无去重）、:930-931（逐格校验无跨格查重） | P2 | 两格同 node_id+state 跑 validate→ok=true |
| A | cell.mounted 列表不去重：`["a","a"]` 通过全部规则 | decision_map.py:377 | P3 | 同上构造法 |
| A | `_collect_sequence_cycle` 每个成环节点各报一次同环（重复告警噪音）；DFS `path` 集合跨分支共享对"经此点不成环"的剪枝在本图规模下无害 | decision_map.py:482-502, :932-933 | P3 | 双节点互相 sequence 边→2 条重复环报告 |
| A | pit_drift 边界：`u_d > s_d` 不含等号——updated_at==回测起点的知识不算漂移（同日快照语义，需 Owner 确认口径）；`e_d < eff_d` 分支注释"完全在生效前"与 drift 语义一致 | decision_map.py:1039, :1045-1048 | P3 | 造 updated_at==start 的条目跑 pit-drift |
| A.3 | 测试两文件 105 用例断言强度抽读合格（红蓝对抗套含结构变异）；但无 R12 权重 NaN 与重复格用例 | tests/trading/test_decision_map.py:全卷 | P3 | grep "nan\|float(" 两测试文件无命中 |
| B | 注册表 YAML 语法损坏→`yaml.YAMLError` 直接穿出 validate（违反头注 ERROR_CONTRACT "validate 不抛异常只产 GapReport"、INV-3）；方向 fail-closed 无资金险，但契约失真 | decision_map.py:426, :910-912（_load_registry_ids 无 try）；头注 :13 | P3 | 临时破坏副本注册表语法跑 validate（用 tmp_path，勿改真源） |
| B | 地图 YAML 顶层类型错误（nodes 为字符串/标量）→ `AttributeError`/`TypeError` 而非 DecisionMapSchemaError；`e["from_node"]`/`s["weight"]` 缺键抛裸 KeyError——同上契约失真 | decision_map.py:361, :365, :393 | P3 | load 一份 nodes:"abc" 的 YAML 看异常类型 |
| B | R99 真源缺失检测面完整（6 核心注册表+12 交叉轴库全部入环）；`_load_registry_ids` 缺文件静默空集被 R99 兜住——设计正确 | decision_map.py:907-909 | 已查无 | — |
| C | 下游 gate（DECISION-MAP）对 run_checks 任何异常 fail-closed 阻断（INVARIANTS 明示），静默吞掉点无；algo_note_sync_gate 与 decay_watch 均显式 try+log | decision_map_gate.py:104-118 | 已查无 | — |
| C | `repo_root = registry_dir.parents[3]` 硬编码目录深度：调用方传非 catalogs 标准深度路径时 R13/R14/R19 文件存在性检查全部打错根（假 error 刷屏）；当前两调用方（CLI:1089、check_decision_map）均传 _PIT_CATALOG 深度合规 | decision_map.py:702, :944 | P3 | 以 docs/ 为 registry_dir 跑 validate 观察 R14/R19 误报 |
| D | `_CODE_STRATEGY_IDS` 手工维护 8 码静态清单（宪法 §9.5 红线"静态清单禁手工维护"）：当前 8 码在 pf_core/*.py+pf_core/strategies/ 实存、且与 registry aliases 三重承载（决策地图/registry aliases/此常量）；新策略上码不改此清单→漏纳（R3 假 error 阻断无辜提交）；策略下码不改→假接受死策略引用 | decision_map.py:1064-1070；strategy_registry.yaml:11954/12036/12118 | P2 | 从 frozenset 删一码跑 validate 对比；AST 扫 StrategyMeta 可机生 |
| D | 点位双词表：`_POINTS`（盘前/盘中/盘后/持续，:51）与 `_ACTIVATIONS`（premarket/intraday/...，:75）同域异构无映射文档，新节点作者需自行猜测两字段对应关系 | decision_map.py:51, :75 | P3 | 读两词表对照 |
| E | `_resolve_mod_id` 只认当前 sha256 命中条目、禁回退首条+陈旧降级 warning（q-…-0012 实证教训固化）：对抗陈旧缓存假阳性的设计正确 | decision_map.py:449-479, :727-740 | 已查无（正面） | — |
| E | V1 真源缺失=error、V4 空地图防御（空 nodes/markets/列轴禁静默全绿）：假阳性过关面已封 | decision_map.py:906-921 | 已查无（正面） | — |
| E | 重复触发/重放：load+validate 纯函数无状态，重入安全；无写副作用（INV-3 成立，除 depgraph 缓存只读） | decision_map.py:888-1000 | 已查无 | — |
| E | yaml.safe_load 仍受 anchor/alias 展开攻击面（billion laughs 类）：内部工具+真源受 gate 保护，实际风险低 | decision_map.py:352 | P3 | PyYAML 版本号+构造深嵌套 alias 小样本（勿入库） |

## 3 SOTA 对照

1. **模型治理清单对齐 SR 11-7 → 已被 SR 26-2 取代（立卡候选）**：代码 :166 注释"备忘 96 治理元数据（SR 11-7 对齐，2026-09-14）"。美联储 2026 年发布 SR 26-2《Revised Guidance on Model Risk Management》正式取代 SR 11-7（发布方：Federal Reserve Board，2026，https://www.federalreserve.gov/supervisionreg/srletters/SR2602.pdf；解读：Domino，2026，https://domino.ai/blog/what-changes-with-sr-26-2）。last_validated_at/validated_by/materiality 等字段与新版"validation/documentation/governance/monitoring 四支柱"仍对得上，但引用真源应升级注记 SR 26-2（低成本文档改）。
2. **PIT 漂移三态诊断（对等已有）**：pit_drift_report 的"只认回测起点前知识、晚登记强制声明"与业界 point-in-time backtest 纪律一致（daily.dev《Designing a Point-in-Time Backtest You Can Actually Trust》，2025；Risk.net《Backtesting a PD Model in the PIT vs TTC Context》，Journal of Risk Model Validation，https://www.risk.net/journal-of-risk-model-validation/7890646/）。D121 自限"仅地图层+数据资产层"与业界 feature-store as-of join 全字段 PIT 相比是声明过的收窄（对等+欠账已自白）。
3. **结论**：无"立卡即改算法"项；SR 26-2 注记升级立卡（P3 文档级）。

## 4 缺陷清单

1. **[P2] 矩阵格 (node_id,state) 可重复且无跨格查重**
   - 现状：load 逐格构造不查重，validate 逐格校验无 seen 集合。
   - 证据：decision_map.py:373-383、:930-931。
   - 影响：同格双写（复制粘贴事故）静默通过；下游按格遍历（如 orchestrator `_lookup_state_cell` 取首个命中，daily_decision_orchestrator.py:351-356）时另一格成幽灵数据——状态路由语义可被静默改写。爆炸半径：该状态格所辖策略包选择。
   - 建议修法：load 或 validate 加 `(node_id,state)` 唯一性 error（一行 seen 集）。
   - 验证法：构造双格 YAML 跑 validate，当前 ok=true 即复现。
2. **[P2] `_CODE_STRATEGY_IDS` 手工静态清单（checklist #4 双份承载）**
   - 现状：8 码 frozenset 手工维护，与 strategy_registry aliases 及 pf_core 代码三处承载。
   - 证据：decision_map.py:1064-1070；strategy_registry.yaml:11954。
   - 影响：新增策略忘登记→R3 假 error 阻断无辜提交（fail-closed 烦人）；下码忘删→死策略引用假接受（fail-open 静默）。爆炸半径：地图挂载真源性。
   - 建议修法：AST 扫 pf_core/**.py 的 `strategy_id=` 字面量机生（或以 registry aliases 为唯一真源、删除本清单）。
   - 验证法：`grep -rn 'strategy_id="' src/zephyr/pf_core/` 与该清单 diff。
3. **[P3] load/validate 异常契约失真**（非 DecisionMapSchemaError 的裸 KeyError/AttributeError/YAMLError 穿出）——证据：decision_map.py:361/:365/:393/:426；影响：消费方按头注契约 catch DecisionMapSchemaError 会漏接（当前 gate 全捕获 fail-closed 故无实害）；修法：统一包 `_require`/try→SchemaError；验证法：喂畸形 YAML 断言异常类型。
4. **[P3] R12 权重无下界/无和≥1**——证据：decision_map.py:975-994；影响：聚合器 aggregator 字段是 proposed 占位，权重和远小于 1 时整装回测资金大量闲置不告警；修法：加 `weight_sum < 1-1e-9` warning 或按 aggregator 语义定下界；验证法：单 sleeve weight=0.01 构造跑 validate。
5. **[P3] R41 reason 校验对 mounted 非空格也生效（过严）**——证据：decision_map.py:652-661；验证法：mounted 非空+词表外 reason。
6. **[P3] pit_drift 畸形 effective_from 抛 ValueError 而非 blocked 三态**——证据：decision_map.py:1024-1026（空串走 blocked，但非 ISO 串直接崩）；验证法：effective_from:"soon" 跑 pit-drift。
7. **[P3] `registry_dir.parents[3]` 深度硬编码**——证据：decision_map.py:702/:944；验证法：换深度传参看 R14/R19 误报。
8. **[P3] SR 11-7 注记已过时（SR 26-2 取代）**——证据：decision_map.py:166；验证法：读 SR 26-2 原文 §scope。

## 5 挂起疑问

1. updated_at==回测起点的知识条目不计漂移（:1039 无等号）是否 Owner 认可的 PIT 口径？（同日快照两读：盘后更新视为当日知识则应含等号。）
2. 状态矩阵是否存在合法的"同格双写"业务语义（如分时段覆盖）？若无，建议按缺陷 1 收紧。
3. `weight` 语义是"占保本金比例"还是"可加和<1 的裁量配置"？决定缺陷 4 修法方向。

## 6 完备性自评

- 六轴全查：是。A（数学四问逐规则过+边界构造验证）、A.3（两测试套抽读）、B（三输入源逐条追源）、C（gate/decay_watch/api_server 调用方逐个核）、D（双词表/三重承载/裸读旁系）、E（五问逐条，含重入/重放/陈旧缓存）。
- 长尾：①api_server 对本模块的消费路径未逐端点追（前端只读端点，属 P2 域）；②check_decision_map.py 封装层未深审（触发面/性能属基建对象，P2 战役覆盖）；③test_decision_map.py 67 用例未逐条跑（绿证取自仓库门禁现状+抽读）；④运行时 gate 日志近 N 天取证未做（材料包缺项已声明）。

## 7 收口裁定（收口方填）
- 三态逐条:
- 修复 commit:
- 复检结论:
