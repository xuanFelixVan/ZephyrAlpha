---
ttl: task_bound
---

# 环节5：门禁链全景清单（171 台）

> 挖矿：子代理 2026-09-22 凌晨（1125 行 pre-commit config 全文+114 台 commit_gates+注册表机读解析）。本文档存结构化精华，全表以代码+注册表为真源。

## A 三层结构与执行序

| 层 | 载体 | 规模 | 顺序语义 |
|---|------|------|---------|
| L2 in-process | gateway `_check_gates_with_drift_watch` | 114 台 | GateSpec **priority 升序 28→200→830/833**（撞号 fail-closed） |
| L2.5 通道 | GATE-PRECOMMIT-RUN（GW:3134/3366） | 55 hooks | own-scope 临时索引跑 `pre-commit run --files`；**fail-fast 关=全部 hook 都跑**；超时 900s；own→阻断/foreign→warn+审计/hook 变异→阻断 |
| L3 hooks | 裸 commit 面 | 同一 config | gateway 恒 --no-verify 不触发（L2.5 补偿） |
| L4 CI / L5 reconciler | governance.yml Tier1-5 / post-commit | — | 兜底层 |

**链序结论**：in-process(28→200) → step5.5 precommit 通道（真 commit 前最后一道）→ commit。T0 级网关门禁（CREATE-GUARD pri60/TRANSLATION 59/RULING-REFERENCE 74/ARCH-REFERENCE 75/NO-BARE-SQL 94/TABLE-NAME 120）**本就排在通道前**，单次尝试内秒杀。

## B 成本分档（判据+代表）

- **T0 毫秒**：路径表/正则/单 YAML 键查（PROTECTED-PATHS、RULING/ARCH-REFERENCE、EXEMPT-ZONE-FM、TRANSLATION-COVERAGE、CLAIM、SESSION）。
- **T1 秒**：staged 文件 AST/全文扫+注册表读（NO-BARE-SQL、TABLE-NAME、ALGO-FLOW-LINK、SYNTAX、COMMIT-SCOPE 系）。
- **T2 十秒**：全 staged 跨文件（ruff 系、naming 基线、import 解析、生成器单项）。
- **T3 分钟**：全仓自扫描/pytest 收集/生成器全簇/全图对齐（gate-test、gate-21、gate-ssot-code、gate-zr、triple-align、全景图系）——**通道慢尾**。
- pre-commit hook 每台固定 spawn 开销（python+git 子进程），55 台全跑=分钟级底座。

## C 死因时空分配修正（重要）

created_at→dead_at 差值≈**排队等待+单次尝试**。0091（116 分钟）大头=租约等待期排在 110 文件巨批之后；其自身尝试死于 CREATE-GUARD 只需秒级。**真实租约燃烧模型= doomed 尝试的单次落地时长（遥测：均值 79s/P90 189s）× doomed 次数（285/日）≈ 6-12 小时租约/日白烧** + 成功大项的全通道时长（2-10 分钟/项）×排队放大。→ R1（队外杀）治 doomed 次数；R2（拆批）治单次时长与等待放大；R3（两段式）治 doomed 残余在通道内的燃烧。

## D T0 闭包预检资格判定（R1 白名单候选，全部可 import 复用）

✅ RULING-REFERENCE / ARCH-REFERENCE（_reference_helpers 同族，纯文本+YAML）；✅ CREATE-GUARD token+14 字段头（registry 精确比对；需 HEAD ls-tree 判"新文件"=内联化改造，DIRECTORY-CONTRACT 先例）；✅ TRANSLATION-COVERAGE（loader 只读 YAML）；✅ NO-BARE-SQL（added 行正则+AST 豁免）；✅ TABLE-NAME-REGISTRY（ast.parse+registry）；✅ ALGO-FLOW 标记（_has_algo_flow AST）；✅ 合并冲突标记/私钥（纯正则）；✅ NO-BARE-GETENV。实现=轻量 stub gateway（project_root+run_git 两点，_diff_helpers 兼容），**零新检测器**（净零铁律）。naming --check-new 需 ls-files 基线=T1 秒级可入但标档。

## E 重复检测矩阵（摘要）

L2.5 与 L3 完全同构；真重复=pre-commit↔CI（8+ 对）与 in-process↔hook（DIRECTORY/ENCODING/VOCAB/PURE-SHIM/ERRCODE/NODE-ID 6 对，双层有意）。T0 五台仅 L2 单层——enqueue 预检复用闭包**不构成第四层**，是单层检测的暴露点前移。

## F 升级机会

1. 【快】入队面 T0 预检白名单扩容（=R1，见 D；挂 commit_preflight.py PREFLIGHT_GATES）。
2. 【快】**两段式通道**（=R3 主形态）：gateway 在全通道前先跑确定性子集（conflict/private-key/algo-flow/any-abuse/naming/encoding/ruff-check ≈7 hooks，15-40s），fail→快速阻断；clean→全通道照旧（保 own/foreign 归因语义）。禁 config 顶部 fail_fast（会以 foreign 失败掩蔽 own 失败→误放行，语义危险）。
3. 【快】5 台 T0 gate 补 own_scope:true 登记（宪法 §3.3 补账）。
4. 🌑 gate_cache_preflight 启用+扩面：flag 出厂 OFF=Owner 手柄；扩注册表输入类需先把 mtime 纳入指纹——挂起。
5. 🌑 per-hook 慢尾计时落审计：先观测后动——挂起（两段式落地后复测）。
6. 封矿：任何 gate 逻辑改写/新检测器（净零）；hooks 顶部全局 fail_fast（归因语义危险）。

## G 挖矿日志表

config 全文/114 gate priority 提取/注册表机读（171 条+own_scope 27 条）/GW 通道段精读（3100-3420）/七台 T0 gate 闭包依赖面核实/gate_cache_preflight 白名单/CI Tier 对照/矩阵交叉。

## H 自审闸三态裁定（主会话融合）

施工：F1+F2+F3（=Owner R1/R3 原文+登记补账）。挂起：F4/F5。封矿：F6。
