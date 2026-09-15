---
ttl: task_bound
session: st-btfix-p14-20260914
date: 2026-09-15
---

# P2-1 ALGO_FLOW 逐域出仓三期报告（批1 回测域 + 批2 合规域）

> 会话 st-btfix-p14-20260914 | 2026-09-15 | 承接外审 P2-1 契约注释过载项

## 一、成果总览

| 域 | 内联块出仓 | 外部 yaml | creation_token | 测试验证 | 落库 commit |
|---|---|---|---|---|---|
| 回测（批1） | 42+试点1 = 43 | 43 | 43 | tests/backtest+extractor 1272 passed | 77da93ad00（yaml 票A）+ 96abc25939（源码票B） |
| 合规（批2） | 29 | 29 | 29（随批1 token 批登记） | tests/compliance 354 passed | 同上两 commit |
| 合计 | 72 | 72 | 72 | — | — |

- 全景图算法卡真源迁移：`docs/03_modules/<域>/algo_flow/<stem>.yaml`（`doc_type: architecture_view` 过 DCR-001；`__init__` 用父目录前缀防覆盖）
- 源码 docstring 累计削减 ~2000 行机器块，换 `# [ALGO_FLOW] external:` 单行锚
- extractor/解析器/translation_reconciler 零改动（yaml block-scalar 逐字节副本，round-trip 断言 nodes/edges 逐项一致）

## 二、工具沉淀

`scripts/governance/d5_architecture/generators/externalize_algo_flow.py`（--domain/--file/--dry-run/--limit）

安全序：抽内联块 → 写 yaml → 源码换锚 → 内存 round-trip 断言 → 落盘 → extractor 全链终验 → 失败 .bak 回滚+删 yaml。实测三坑修入工具：

1. `_docstring_line_base` 文本级三态定位（引号同行/独立行+空行剥离）
2. `__init__.py` rerouting：遮蔽释放后卡片真源可合法重定向子文件（io→backtest_result_sink、services→anomaly_diagnoser），结果标 `rerouted_to`
3. `_DOMAIN_DIRS` 对齐 docs/03_modules 实存 54 目录（初版 10 域落空，普查修正）

## 三、排队落库攻坚战（基础设施发现与修复）

### 已修（随批落库）
- **落地器快照预暂存**（commit 2096a06c47）：ALGO-NOTE-SYNC gate 设计前提="暂存集冻结后运行"（diff=git diff --cached），而落地器序=gate 先于 add——快照只写工作区时 gate 读空 diff 误拦。新增 `_prestage_snapshot` 补齐前置。死信 0013/0014 实证+离线重演铁证（stage 前 blocked=True / stage 后 False）。
- **ALGO-NOTE-SYNC 归因窗口盲区绕行**：gate 按"hunk 上下文最近 node_id"归因；note 行距 node_id 行 >3 行即失联。修法=note_confirmed 行紧贴 node_id 行（值更新制造归因 ± 对）。
- **CloneGuard 合理重复登记**（echo-guard.yml 新建）：合规域两处惰性样板 `__getattr__`/`__init__` 100% 相似系 PEP 562 惯用法，非算法克隆；出仓删 docstring 后首次暴露给结构比对。按 RULE-CLONEGUARD 正门 acknowledged 登记（引擎无关对账层 stable_key 格式验证命中）。
- **TDM 三节点同步**：TDM-F-C3-04 / TDM-E-L1-S0-1 / TDM-E-L3-04 note_confirmed + algo_note_zh 出仓注记（ALGO-NOTE-SYNC 口径）。

### 遗留风险（建议 Owner 排产）
1. **SessionRegistry 多进程 last-writer-wins**：CLI claim 进程与 serializer drain 进程并发读写 `.runtime/session_registry.json`，互相覆盖 held_files → CLAIM_REQUIRED 死信（0023/0025/0027 间歇复现）。建议：registry 写路径加文件锁或改单写者（serializer 独占写）。
2. **落地器-门禁时序的结构性缺口**：任何依赖 staged diff 的 gate 在队列路径都可能重演 ALGO-NOTE-SYNC 同型问题（本次只修了已爆雷的一个）。建议：落地器统一"快照后立即全量 prestage"作为协议（本次已做），并在 gate 注册表标注 staged-diff 依赖型 gate 清单。
3. **ALGO-NOTE-SYNC 归因窗口**：± 行距 node_id >3 行即归因失败的粗粒度窗口，建议后续按 @@ hunk 行号映射回文件定位 node_id（大改，留待立项）。

## 四、下一批（批3+）路线

- 普查基线：全仓 3,302 内联模块 / ~154k 块行 / 58 域组（`.runtime/tmp/inline_algo_inventory.json`）；已完成 72（2.2%）
- 小域先行：compliance 已毕；下一批建议 regime(42)/ex_core(61)/ml_train(43) 或按 `--domain` 单域滚动：出仓 → 复扫幂等 → 域测试 → token 登记 → 队列入库
- 12 个域目标目录缺失（`_cross_layer_shared`/`_domain_autonomy` 等映射已修但需 Owner 确认归并口径）；`scripts/governance` 6 个内联工具最后处理
- 大域（feedback_loop 340 / infrastructure 336 / governance 296）建议单独立项带节奏

## 五、收尾状态

- 本会话 14 条 claim 全部释放；72 文件批1+批2 全量落库（yaml 43+29、源码锚行 43+29、生成器、token 登记、TDM 补注、echo-guard.yml）
- 既有失败三件套与本批无关（c4_fact_e831084c 哨兵/词表、factory flaky），已移交责任线（st-autopipeline 20260915 批注清偿）
