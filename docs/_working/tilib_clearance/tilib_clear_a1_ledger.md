---
ttl: task_bound
session: st-tilib-clear-20260920
title: 技术指标库清欠班台账（分包A·34指标三件套清零）
---

# a1 战役台账（总包唯一状态真源，会话中断后凭此续班）

- 目标：注册表 102→≥136 条；波1 M-L1/M-L2/M-L3、波2 M-L5、波3 M-L6 挖矿、波4 stretch 批9。
- 基线（2026-09-20 实测）：注册表 102 条 / 宽表 162 列 / 运行时 metas 101 / 测试 762 条。
- 记账规则：每行=波次｜指标｜commit｜测试数｜状态。总包统一登记；子代理禁改本文件。

## 编号预算（防撞号，总包专用）

| 域 | 既有 | 本班新分配 |
|---|---|---|
| IND-TREND | 001-021 | 022-028=M-L1（TEMA/TRIMA/T3/MAMA/VIDYA/FRAMA/JMA）；029-032=M-L2（AVGPRICE/MEDPRICE/TYPPRICE/WCPRICE） |
| IND-STAT | 001-004 | 005-008=M-L3（LINEARREG_ANGLE/SLOPE/INTERCEPT/STDERR） |
| IND-VOL | 001-015 | 波2：CHOP/CVI/ULCER 按落地顺序续号 |
| IND-CYC | 001-005 | 波2：EBSW/MSW 续号 |
| IND-MOM | 001-037 | 波2：RMI/PSL/PFE/FOSC/CTI/VHF/ER/INERTIA 续号 |
| IND-VOLUME | 001-014 | 波2：WAD/VO/MARKETFI 续号 |

## 波次台账

| 波次 | 指标 | commit | 测试数 | 状态 |
|---|---|---|---|---|
| 波1-L1 | MAMA+FAMA/FRAMA/JMA（trend.py 硬车道） | 同波1总包提交 | +31 用例（test_trend 190→221） | done（MAMA/FAMA 与 talib 逐位一致 0.0 偏差[亲验]） |
| 波1-L2 | LINEARREG_ANGLE/SLOPE/INTERCEPT/STDERR（statistics.py） | 同波1总包提交 | +12 用例（test_statistics 17→29） | done（golden 对照 1e-12~1e-13 级[亲验]） |
| 波1-L3 | TEMA/TRIMA/T3/VIDYA/AVGPRICE/MEDPRICE/TYPPRICE/WCPRICE（trend.py 易车道） | 同波1总包提交 | +33 用例（test_trend 221→294） | done（价格变换/TRIMA 逐位一致；TEMA/T3 第100根起 1e-6） |
| 波1-总包 | 注册表 117 条+schema 178 列+契约常量+memo v1.7.0+4条旧统计 module_id 治愈 | 并入 q-0003 | 目录全量 878 passed/5 skipped ×2 轮 | done |
| 波2-A | CHOP/CVI/ULCER（vol）+EBSW（cycle）+INERTIA/QSTICK（trend） | 并入 q-0003 | +60 用例（三测试文件） | done（独立复算+手工微样本 [亲验]） |
| 波2-B | RMI/PFE/FOSC/CTI/VHF/ER（momentum） | 并入 q-0003 | +36 用例 | done（FOSC/CTI/ER/VHF 镜像逐行；RMI/PFE 权威定义移植） |
| 波2-C | WAD/VO/MARKETFI（volume）+ZSCORE（statistics） | 并入 q-0003 | +36 用例 | done |
| 波2-总包 | 注册表 133 条+schema 194 列+契约 132/194+cycle 头 029 治愈+CREATE-GUARD token×3+memo v1.8.0 | q-0006+q-0007 拆件落地 | 目录全量 1038 passed/5 skipped ×2 轮 | done |
| 波3 | SUPERSMOOTHER/HIGHPASS/PTREND（trend.py，TASC 2024-09 学术族）+3 列 | 020728598c | +17 用例；目录 1070 passed ×2 轮 | done（双实现互证 1e-12+手算微样本 [亲验]） |
| 波3-总包 | 注册表 136 条+schema 198 列+契约 135/198+memo v1.9.0+a3 挖矿报告 | 020728598c | 四方探针 198×4 全等 | done |
| 收官 | D-15 三态核实 17 文件全一致（index 旧弹 git reset 消弹+capability 册 HEAD 超集收敛）；红蓝对抗 ALL PASS（PIT 零未来行+新种子 talib 复验 12 项+递推恒等 5 项+弱断言零命中）；波4 未启动（理由见 a5 §5） | （a5 随本行落地） | 136 条=终极目标达成 | done |

## 裁定与偏差记录

- 裁①（自裁 2026-09-20）：M-L3 清单中 "LINEARREG_BAR" 与既有 linearreg 指标（linearreg_14 列=TA-Lib LINEARREG 本体，statistics.py 既有）完全同义，不重复立条——M-L3 实现数=4 而非 5；缺口由波3 学术挖矿补足 ≥1 以达 34。理由：同一列两条目违反唯一性；registry unique_key=indicator_id，且 linearreg_bar 会被 ALGO 去重 gate 拦。
- 裁②（自裁 2026-09-20）：黄金样本参照=本地 TA-Lib（实测可 import，仅测试用，生产代码保持零 TA-Lib 依赖不违反 16 号 memo §2 设计口径）；JMA 无 TA-Lib 对应，用文献公式移植+性质测试（常数恒等/单调收敛/正弦周期恢复）。
- 裁③（自裁 2026-09-20）：M-L2 四个价格变换归 trend.py（indicator_class=trend，pandas-ta overlap 族先例）；statistics.py 行1 蓝图号 stale（MOD-L02-001 应为 MOD-L02-028），随 L2 顺手修正。
- 裁④（自裁 2026-09-20）：CH 宽表当日禁 INSERT 照办；但注册列的 DDL 同步走"干净子进程逐列 ALTER+system.columns 探针"（批6/批8 配方，ALTER=元数据操作不产 parts，不触碰 apply_market_tables_ddl.py 本体）——否则 02:30 夜跑回填因 INSERT_COLUMNS↔CH 列缺失必炸。若探针失败则夜间再补。

## 停手/待 Owner 项

- 登记债（非本班破损，未动）：①cycle.py 行1 [BLUEPRINT] stale=MOD-L02-001（[A_module]=029），注册表 IND-CYC-001..005 module_id 与行1自洽但与 [A_module] 不一致——属 S4 注入/历史批遗留，修复需 cycle.py 行1 与注册表 5 条同批改，超出本班波1爆炸半径；②reversal.py 等 [BLUEPRINT] 行1 计数散文 stale 同类。已记本节，建议对齐改图班收口。
- CH 宽表 16 新列 ALTER（批9-1）+ 夜跑回填验证：本班尾段执行（见裁④）。

## 环境事实（本班实测，续班直接用）

- 会话 st-tilib-clear-20260920 已注册+心跳守护 30s 在飞。
- claim 16 文件全成（TTL 30min，过期需重 claim）。
- talib 可 import（黄金参照）；scipy 可用；pandas_ta 不可用。
- 批8 commit 011ad6ba58=本班文件构成模板（8 类文件，无 algo_flow yaml）。

## 提交通道记录（波1）

- 裁⑤（门禁合规）：Owner 总令落盘路径 docs/_working/tilib_clearance_20260920/ 触发 R5-DIGIT-SUFFIX（gov_doc_003 数字后缀目录禁令）→ 已改名 **docs/_working/tilib_clearance/**（门禁机械优先，路径偏差于此登记）。死信 q-20260920-st-tilib-clear-20260920-0001（R5 阻断）内容被重提交取代，**勿 requeue**，留维护班清账。
- 裁⑥（代码质量治愈，重提交前）：NO-HIGH-COMPLEXITY `_mama_recursion`(16>15) 与 NO-LONG-PARAM-LIST `_hilbert_stage`(8>7)——重构：a/b 常量提级模块级（8→6 参数）、抽 `_mama_wma_seed`/`_mama_period_update` 纯函数；878 passed 复证 MAMA/FAMA 与 talib 逐位一致不变 [亲验]。
- RULE-WORKTREE 降级登记：Owner 通宵总令 §6 明令主区 --files 白名单提交流（本班 132 脏区为他会话 final3 在途件）；session_worktree_start 已注册（.aidrafts worktree 已建未用），主区白名单车道+claim 全程执行。
- 本节补记于 q-0002 入袋之后（改名导致 Edit 前置读断链），随波2 提交落地。

## 波2 记录

- 裁⑦：M-L5 清单 PSL 与既有 PSY（心理线同式）、MSW 与既有 ht_sine/ht_leadsine（Ehlers 正弦波同义）按裁①先例剔除——波2 实作 16 指标；波1+2 累计 31，34 缺口=3 由波3 学术挖矿补足。
- 裁⑧：q-0002 死因=CREATE-GUARD（3 新 .md 无 creation_token）→ 已按坑册配方 CAS 登记顶级 creation_tokens 节（tilib-clear-ledger/wave1card/index-20260920 三条，进程外核实行 5019-5030 [亲验]）；工作树已累积波2 改动（同文件），波1 单独落地会造成注册表↔代码快照不一致 → **波1+波2 合并为 q-0003 一次落地**；q-0001/q-0002 死信内容均被 q-0003 取代，勿 requeue。
- 裁⑨（提交通道连环治愈，q-0003..q-0005 四连死因）：q-0003=R5-DIGIT-SUFFIX（目录 _20260920 后缀）→ 目录改 tilib_clearance；q-0004=EXEMPT-ZONE-FM（自动生成的 index.md 带 doc_type）→ 该生成件删除不入提交；q-0005=GATE-NAMING N-16（a1_campaign_ledger.md 基名撞 final3_campaign）→ 三件战役文档统一前缀 tilib_clear_*（本文件 canonical 名=tilib_clear_a1_ledger.md，续班凭此名）；q-0005 前另一死因=ruff/ruff-format（#341 新钩子）→ 13 py 文件 format 对齐+3 处 zip strict=False+导入序（1038 passed 复证行为中性）。**本文件路径自 q-0006 起生效**。
- 治愈件：cycle.py 行1 [BLUEPRINT] stale 001→029（与 [A_module]/depgraph 对齐）+注册表 5 条旧 cycle 条目同步——wave1 登记债①就地清偿（reversal 行1 散文债仍挂）。
- 波2 黄金参照弱化说明：CHOP/CVI/ULCER/EBSW/INERTIA/QSTICK/RMI/PFE/FOSC/CTI/VHF/ER/WAD/VO/MARKETFI/ZSCORE 均无 TA-Lib 对应（talib 0.7.1 实测无此 16 函数），黄金锚=测试内独立路径复算+手工微样本写死值；RMI/PFE 公式源为权威定义移植（pandas-ta-classic 镜像 404，GitHub API 树核对+docstring 注明）[推断级口径、亲验级数值]。
