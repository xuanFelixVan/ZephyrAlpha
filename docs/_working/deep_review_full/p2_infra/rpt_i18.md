---
ttl: task_bound
doc_type: report
title: 深度审查作业簿——capability语义/符号门
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：capability语义/符号门（I18）

- 状态: **已审**
- 级别: P2｜类型: 门禁
- 基线 commit: 2fa92002c3（工作区 HEAD=b80084c0df）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/data/capability_semantic_gate.py:177`（check_capability_api_whitelist_content）+ `src/zephyr/data/capability_symbol_gate.py:286`（check_declaration_impl_consistency）
- 生产调用方: symbol_gate→`src/zephyr/gov_enforcement/commit_gates/capability_consistency_gate.py:64`（CAP-CONSISTENCY 硬阻断 gate）；semantic_gate→**无（见 D-1）**
- 测试文件: tests/zephyr/data/test_capability_semantic_gate.py、tests/zephyr/data/test_capability_symbol_gate.py
- 备注: —

## 1 对象快照

- 审查范围：两文件全文（semantic 214 行 / symbol 292 行），病根=#ARCH-DATA-001（hk_trade_calendar 用 A 股日历冒充）与 #ARCH-CH-INDUSTRY-CLASS-MIGRATE（mootdx 板块成分冒充申万行业）；17 号 §5.3/§5.4/§5.5/§5.8 施工项 2+3+4。
- 排除项：capability_validator.py（被复用的 AST 真源 `_ROUTE_VAR_PATTERN/_extract_str_constant/_meta_caps_from_tree`，下沉为上游只审契约）；CAP-CONSISTENCY gate 装配层在 I30 侧审视。
- 测试覆盖概况：两套单测均在；symbol_gate v0.2.0 按 akshare_alt setattr 形态校准过豁免规则（真实误报驱动），测试较实。
- 材料包缺项：无运行时证据包（gate 触发日志未取）；17 号文档未全文核对（以代码头注引用为准）。
- 变更热力：两文件各 6 次提交，低热区，但 v0.2.0 一次豁免规则扩权（setattr 形态）值得盯。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| E 对抗/C 下游 | **semantic gate 未接电**：check_capability_api_whitelist 全仓 grep 零生产消费方（仅测试+本体），头注声称"commit gate（17 号 §5.4 施工项 3）装配批"未兑现——防 hk 日历/申万行业冒充的白名单闸门从未在提交链运行 | capability_semantic_gate.py:5 + grep "capability_semantic_gate\|check_capability_api_whitelist" src/ scripts/ 仅命中本体/测试 | P1 | `grep -rn "capability_semantic_gate" src/zephyr/gov_enforcement/` 零命中即证 |
| E 对抗 | semantic gate 提取只认 `import x as y; y.z()` 形态：`_import_aliases` 不处理 ast.ImportFrom——`from akshare import xxx` 后直接调用、或 `from mootdx.quotes import Quotes; Quotes.factory(...)` 全部漏提，白名单形同虚设（对绕过者） | capability_semantic_gate.py:118-125（仅 ast.Import 分支） | P2 | 构造 `from akshare import tool_trade_date_hist_sina` 版 _fetch_hk_trade_calendar 跑 check，零违规即证 |
| A 深度 | `_extract_called_apis` 命中第一个含目标方法的 ClassDef 即 return：同文件多 provider 类（基类+实现、或两市场 provider 合文件）只有第一个被校验 | capability_semantic_gate.py:136-163（return apis 在循环内） | P3 | 双 ClassDef 各含 _fetch_hk_trade_calendar，第二类放白名单外 API 不报 |
| E 对抗 | symbol_gate 反向校验存在**整体豁免面**：模块级任一 `for ... setattr(Cls, f"_fetch_{...}", ...)` 即全文件豁免（fail-open 设计自认）；攻击者/粗心者加一行哑 setattr 循环即可绕过声明残留检查 | capability_symbol_gate.py:95-121, 272-273 | P3 | 构造哑 setattr 循环+声明残留文件跑 check 零违规 |
| A 深度 | `_collect_method_defs` 跨类并集：A 类定义的 _fetch_x 可满足 B 类的路由调用/声明检查（跨类误豁免），与"类体内未定义"报错语义不一致 | capability_symbol_gate.py:67-75, 246, 257 | P3 | 两类分别声明/实现不同 capability 子集交叉验证 |
| A 深度 | setattr/setattr 豁免只扫 `tree.body` 顶层 for：循环在 `if`/`try`/函数内则豁免失效→误报（fail-closed 方向，烦人但不漏） | capability_symbol_gate.py:103-105 | P3 | setattr 循环包进 try 块观察误报 |
| B 上游 | 全链 fail-open：SyntaxError→[]、OSError→[]、CAP-CONSISTENCY 再包一层 broad except→[]（capability_consistency_gate.py:114-124）——语法错误的 provider 提交时完全跳过双 gate | capability_semantic_gate.py:187-190, 211-213; capability_symbol_gate.py:234-237, 288-292 | P3 | 已文档化不变式，但三层 fail-open 叠加值得Owner确认知情 |
| D 旁系 | semantic gate 注册表以**代码常量**承载（DEFAULT_SEMANTIC_REGISTRY 3 条），头注自述"docs/ YAML 由施工项 2 另行落地"未落地——治理注册表双真源缺口（模式 #4 前兆：将来 YAML 落地后两处承载） | capability_semantic_gate.py:25-29, 68-96 | P3 | grep docs/ 无 capability_semantic_registry.yaml 即证 |
| A 深度(测试) | semantic 测试未覆盖 ImportFrom 形态；symbol 测试覆盖 setattr/getattr/字面量路由/dict 路由等真实形态（v0.2.0 误报驱动，质量好） | tests/zephyr/data/test_capability_semantic_gate.py | P3 | grep 测试文件无 ImportFrom 用例 |
| E 对抗 | 通配白名单 `THS_*`/`ifind.*`（startswith 前缀匹配）：THS_iFinD 模块名本身含 "THS_"，`_DATA_SOURCE_MODULES` 里 THS_iFinD 与 ifind 并存——前缀通配使任何 THS_ 新 API 自动放行，语义收紧时易被遗忘 | capability_semantic_gate.py:93, 166-174 | P3 | code review |

## 3 SOTA 对照

| 对照项 | 结论 | 来源 |
|---|---|---|
| AST 级 API 使用白名单/策略静态检查 | **对等已有（方向）**：业界标配是 Semgrep 自定义规则（pattern: `$M.$F(...)` + metavariable-regex）在 CI 强制 API 白名单；本对象手写 AST 等价实现，功能对等但缺 `from x import y` 归一化（Semgrep 默认处理 import resolution） | Semgrep 官方文档 pattern 语法与 import 处理, semgrep.dev, 2025（检索受阻：WebSearch 429 限流，2026-09-18 三次重试失败；来源=训练知识+semgrep.dev 已知文档域，收录存疑） |
| capability-based data access 静态校验（数据源语义冒充防护） | 立卡候选：学界无直接同构工作（属领域自研）；可对照"taint tracking from source to sink"思路把「数据源 API→capability」建为 source-label 传播 | 同上受阻记录 |
| 声明-实现一致性（protocol/接口契约检查） | 对等已有：mypy protocol/abstract 检查属类型层，本对象为命名约定层 AST 检查，互补不冲突 | mypy 官方文档 Protocol stubs, mypy.readthedocs.io, 2025（同一受阻记录） |

**轴 F 受阻声明**：本轮 WebSearch 连续 429 限流（错误码 1302），以上三条对照基于已知文档域+训练知识，未做实时双源核验，收口方如采纳米赛决策请补搜。

## 4 缺陷清单

1. **D-1（P1）语义白名单闸门未装配（17 号 §5.4 施工项 3 未兑现）**
   - 现状→证据：semantic gate 零生产消费方（轴 E/C 行）；CAP-CONSISTENCY 只接了 route-meta（capability_validator）+ symbol（capability_symbol_gate）两路（capability_consistency_gate.py:111-117）。
   - 影响：#ARCH-DATA-001 同型缺陷（声明 hk/跨品种 capability 但调用 A 股 API）提交时无任何拦截，病根复发零防线。爆炸半径=跨市场数据语义污染→策略信号错（下游决策链）。
   - 建议修法：在 `_check_provider_content` 中追加 `check_capability_api_whitelist_content(content)`（同 own-scope staged 内容），并补 ImportFrom 提取（D-2）。
   - 验证法：临时提交 `_fetch_hk_trade_calendar` 调用 `ak.tool_trade_date_hist_sina` 的 provider 改动，观察 gate 拦截。
2. **D-2（P2）ImportFrom 提取缺口使 D-1 即便接电也可绕过**
   - 建议修法：`_import_aliases` 补 ast.ImportFrom 分支（`aliases[asname or name] = f"{module}.{name}"`），提取时 Name 调用也查映射表。
   - 验证法：构造 from-import 冒充样例断言报违规。
3. **D-3（P3）semantic 注册表代码常量承载+YAML 缺位**：按 17 号 §5.3 补 YAML 真源与加载器，或明确撤销 YAML 计划修头注（消双真源预期）。
4. **D-4（P3）豁免面/误报面双向打磨**：setattr 整体豁免（:272-273）建议收窄为「setattr 迭代源变量可静态求值出 cap 集」才豁免对应 cap；setattr 循环非顶层场景补扫描。
5. **D-5（P3）跨类方法并集误豁免**：`_collect_method_defs` 建议按 ClassDef 分组，正向检查限同类内。

## 5 挂起疑问

- 17 号文档 §5.4 施工项 3 是否被显式降级/延期（若有裁定登记则 D-1 降级为"文档漂移"）？建议收口方查 ruling_registry。
- CAP-CONSISTENCY 的 own-scope 行为（他改 provider 文件时是否被豁免）归 I30 审，本报告未展开。

## 6 完备性自评

- 六轴全查：A（AST 提取逻辑逐分支推演）、B（fail-open 契约）、C（消费方全列）、D（validator 复用与 YAML 缺位）、E（绕过面三条：ImportFrom/哑 setattr/语法错误）、F（受阻如实记）。
- 长尾：capability_validator.py 的 `_ROUTE_VAR_PATTERN` 正则本身未逐字符审（上游对象）；gate 注册表 priority=101 与其他 gate 的顺序交互归 I30。
