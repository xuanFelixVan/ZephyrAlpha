---
ttl: task_bound
completes_when: 总包对 req_land3_01 五 item 逐条裁定（A/B/C 三清单归档）
---

# 裁定书 req_land3_01 · 落地接力第三腿（st-ff-land3-20260918）无法自裁五项

> 按 R-018 三清单口径书写；本车道**未停等**，五项登记后继续施工（任务书"禁停等"条款）。

## ITEM-1（A 类·需裁定）residG 半截接线件把生产唤醒链留在破件态，本车道是否有权代修

- 实测（本腿亲跑，非转报）：`src/zephyr/strategy_pipeline/pipeline_events.py:510` 调
  `_crisis_l1_check(day)`，全仓 grep 该符号 = **1 处注释 + 1 处调用，零定义**
  → `tests/pf_alloc/test_pf_alloc_event_wiring.py` **8 failed**，traceback 全是
  `NameError: name '_crisis_l1_check' is not defined`。
- 同批在途编辑还在 `_default_handler` 里引用 `run_attribution_daily` / `run_crisis_drill_monthly`
  两个函数（`git diff HEAD` 该文件 33 insert / 1 delete，diff 头部自带归属注释
  `2026-09-18 st-ff-residG-20260918`）。
- 冲突：该文件按 ledger §2 是 **residG 独占**；宪法 §3.4 + R-016 三分法②要求"不代修"。
  但它现在是**盘上破件**（R-028 类并发危害）：`pf_alloc_daily` 一旦被唤醒即 NameError，
  而它的 L1 判读件 `zephyr.pf_alloc.crisis_gate` **已由本腿 T2 批落地**（`crisis_block_check`
  等签名齐）→ 缺的只是 residG 侧那个 6 行的 importlib 包装体。
- 请裁：①等 residG 复飞自补（本车道默认走这条）；②授权本车道补 `_crisis_l1_check`
  （需先撤销 §2 独占权，否则算越界并发改同区）。
- 验真命令：
  `git show HEAD:src/zephyr/strategy_pipeline/pipeline_events.py | grep -c _crisis_l1_check`（=0，证 HEAD 干净）
  与 `python -m pytest tests/pf_alloc/test_pf_alloc_event_wiring.py -q -p no:cacheprovider -W "ignore::pytest.PytestConfigWarning" --basetemp=.runtime/tmp/ff-verify-ew`（=8 failed NameError）

## ITEM-2（B 类·需执行）索引地雷：G1 治本两件在 index 里是"删除"态

- 实测：`git status --porcelain` 显示 `D  src/zephyr/ex_core/execution_report_producer.py` 与
  `D  tests/ex_core/test_execution_report_producer.py`，而两者**已在 HEAD**（z-land2 `175f837e89`）
  且盘上文件仍在（20,975B）。
- 危害：任何按目录/通配列清单的提交一旦吸收 index = **当场回退 FF-12 生产端**（R-014 地雷复发）。
  本车道 T1/T2 清单均逐件具名，不受影响；但**未自愈**（修它要动他人 index，按 §3.4 不代修）。
- 建议动作（谁执行请裁）：`git restore --staged -- <两件>`（index-only、工作区不动、零内容损失，
  与第一腿对 5 件 STALE_INDEX 的处置同法）。

## ITEM-3（C 类·需复查）任务书的 `tests/pf_alloc/__init__.py` 判为陈旧项，未新建

- 实测：任务书 T2 清单含 `tests/pf_alloc/__init__.py`，但该文件**盘上不存在、index 里也不存在**
  （`git status --porcelain tests/pf_alloc` 只有 test_correlation_persistence.py 一条 M），
  且 `tests/pf_alloc` 382 例收集正常、无跨目录同名冲突。
- 判断：新建它 = 凭空造件（且可能改变 pytest 收集根）。故**不建**，请复查该派工项来源。

## ITEM-4（A 类·需裁定）`sim-memo-202609.json`（1378 行）无落点

- 第一腿按 DIRECTORY-CONTRACT（`docs/_working` 只放 .md/.yaml/.csv/.html）判其**永久剔除**，
  本腿遵守未 add。但其内容（2026-09 模拟盘月结数据）**同名的 .md 件已随 T3 落地**
  （`docs/_working/pipeline-research/sim-memos/sim-memo-202609.md`）→ 数据面是否另落
  `data/` 或 `docs/_working/**/*.csv`，请裁。本腿未自行改格式（转换=造数据，非落地）。

## ITEM-5（C 类·需复查）`crisis_drill_monthly.py` 的"复杂度堵死"预裁已失效，本腿按复跑结果随批落地

- 任务书与 z-land 交接令均记 `scripts/backtest/crisis_drill_monthly.py` 撞
  NO-HIGH-COMPLEXITY（阈值 15、无 noqa 逃生）→ 预裁 R-K1"抽 helper"。
- 本腿按 R-019 复跑**门禁自家判据函数** `high_complexity_gate._cyclomatic_complexity`
  于 staged 版：239 个 AST 节点里全部函数 **over15 = 空集**，最高
  `compute_window_metrics`=14 / `run_drill`=10 / `build_equal_weight_nav`=8。
- 结论：该件已不需要摘批，本腿**未抽 helper**（抽了就是无据改动）。请复核"前手报的复杂度红
  对应的是哪一版字节"——若前手看到的是另一版，说明该件在 T2 之前被外部重写过（与 ITEM-2
  同源的 index/工作区漂移），属普查第 1/8 型失效。

## ITEM-6（附报）热文件并发写实测：TDM 一次 PermissionError + 一次整文件被外部还原

- 实测：对 `config/trading_decision_map.yaml` 的 `safe_write_text` 首投撞
  `WinError 32`（另一进程正读写）；重试成功，但期间**前手留在工作区的 2 处
  algo_note_zh 换行重包被外部还原回 HEAD**（`git diff --numstat HEAD` 一度归零）。
- 本腿 TDM 两次改动均以 CAS 落笔（base 哈希校验通过才写），未覆盖他人：
  TDM-E-L4-10（T1 批）、TDM-F-C3-03（T2 批），各 1 insert / 1 delete 纯单行。

## ITEM-7（A 类·需 Owner 门位）危机闸异常码无处登记：`error_code_registry.yaml` 是 PROTECTED 件

- 实测：`crisis_gate.CrisisGateError` 原声明 `error_code = "ZA-PA-CRISIS"` →
  `GATE-ERRCODE-CONSISTENCY`（priority=131，观测面=git index，基线=HEAD，只判本次新增）
  报 `[unregistered_code] ZA-PA-CRISIS` **硬阻断**。
- 两难：①注册新码要写 `architecture_model/contracts/error_code_registry.yaml`，而该路径对本战役是
  **PROTECTED-PATHS（无 CLI 逃生旗，重大修改须 Owner 审批）**——与 req_land2_01 同一堵墙；
  ②该码本身也不合注册表自述格式 `ZA-XX-NNNN`（四位序号），照格式改号同样要登记。
- 本腿处置（不越权、不硬闯、不占他道号）：**撤下 `error_code` 声明置 `None`** 并就地写明原因，
  使批次可落；**不复用**任何已登记的 ZA-PA-00NN（复用=造重码，同一门禁硬拦）。
- 请办：Owner 批准在 `error_code_registry.yaml` 为危机闸配一枚 `ZA-PA-00NN`
  （类名 CrisisGateError / 模块 `zephyr.pf_alloc.crisis_gate` / 域 D_PORTFOLIO），
  批后由后继车道把 `None` 改回该码并**与注册表同一 commit 原子**（#ARCH-ERRCODE-001 要求成对）。
- 验真命令：`grep -n "ZA-PA-CRISIS" src/zephyr/pf_alloc/crisis_gate.py`（落地后应为空）。

## ITEM-8（B 类·需执行）施工期战役暂存面被外部整片收割（冷库救回本腿九件）

- 现象（本腿入队前一刻实测）：`src/zephyr/pf_alloc/crisis_gate.py`、
  `src/zephyr/alt_data/cohort_daily_ledger.py`、`scripts/backtest/crisis_drill_monthly.py`、
  `tests/signal_ashare/test_sector_{ecology_judge,strength_wiring}.py` **五件盘上不存在且 index 里也没有**；
  `allocation_orchestrator.py`(+53/-3)、`regime_meta_allocator.py`(+12/-2)、`alt_data/__init__.py`(+1/0)
  三件工作区内容同时退回 HEAD；`git diff --cached --numstat HEAD` 全仓行数从开工时 ~650 跌到 **26**。
- 判：CONSTRUCTION_DISCIPLINE §8 明文病根"未提交的车道成品会被外部 reconciler / pre-merge
  **整文件还原回 HEAD**"复发（新文件被还原=直接消失）；非 `git stash`（`git stash list` 空、
  `stash_notice.json` 最新条属 09-17 他道）、非本腿动作。
- 治本：**R-030 的 G 盘冷库救了这一批** —— 逐件从
  `G:\zephyr_cold\30_corpus\fullflow_harvest\20260918-194729\{index,worktree}\` 取回原字节，
  再重放本腿的门禁治本（MSG-EXPOSURE / NO-BARE-SQL / MUTABLE-CONST-WITHOUT-FINAL / sector TTL 头 / TDM 注记）。
- **须总包立即办**：同窗口内**其他车道的未提交成品同样可能已被抹**，本腿只复原自己独占的九件、
  未越权代查他道 ⇒ 建议对 `rest.txt` 全 260 件跑一次冷库差集普查
  （比对 `MANIFEST.json` 与 `git diff --cached --name-only HEAD` 的集合差）。
- 附：本腿另撞 `DEPGRAPH-PRE-REGISTRATION`（planned→production 需走
  planned→generated→testing→stable→production 全链，中间态每次会触后台 REGENERATE，
  首投直转被拒且状态被重生回 planned）⇒ 三节点 14830693/14830694/14799384 已按链走完至 production。
