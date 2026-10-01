---
ttl: task_bound
completes_when: 总筹把本清单全部条目合批登记进热册（token/翻译/depgraph/ROOR）并回执本道
---

# 戊道（st-p3-matrix / 包 13.4）· 待登记清单

> 热册唯一写手制：本道**未写**任何热册（capability_canonical_file_registry / module_translation_registry /
> depgraph / ROOR 一律只读）。下表逐行 = 文件 / capability / merge_evaluation / plain_zh / domain，请总筹合批登记。
> creation_token 建议统一 `wave13-p3-matrix-20260926`（已在各文件头以 `pending-registration:` 形式占位）。

## 一、新建文件（CREATE-GUARD token + 大白话翻译 + depgraph 节点）

| 文件 | capability（关键词面） | merge_evaluation | plain_zh（大白话简介） | domain |
|---|---|---|---|---|
| `src/zephyr/governance/scan_scope_converged.py` | scan scope / 扫描口径 / 消费者判定 / grep 口径 / §3.4 定档 | **新立唯一真源**：波 13 全波"有没有消费者/有没有接线"的口径定义处；丁道普查引擎应 import 本常量，禁各处重述（否则三套口径互斥复发） | 判断仓库里某个东西到底有没有人用、有没有接上时，全项目共用的那一把尺子：只翻 src/scripts/config 下的 .py 与 .yaml，文档和 docs 一律不算消费者 | D_GOV |
| `scripts/governance/d5_architecture/generators/generate_connection_matrix.py` | connection matrix / 连接矩阵 / 该连未连 / 六类边 / W-154 / 四向对账 | **新立**：W-154 首件；不并入 `check_decision_map.py`（那尺是 commit 门禁的 R1-R45 引用存在性校验，本件是"声明×实存"的矩阵产物，消费者与产出面不同→跨域不同对象不并），且直接 import 复用其 R9/R11/R3 判据 | 把"谁该连谁"和"谁真连上了"摆进同一张表，逐条给可复跑证据，只数一个头条：该连未连。没人声明过的边单独记账，绝不算成缺口 | D_GOV_SCRIPTS |
| `src/zephyr/frontend/dashboard/components/connection_matrix.py` | dashboard connection matrix tab / 连接矩阵面板 / 仪表盘数据源 | **新立**：契约二选一里取"components 新文件 + build_tabs 一行"，未动既有面板逻辑；与 `api_server.py` /api/tdm 无重叠（那是地图画布真源，本件只读矩阵产物） | 仪表盘上新增的"连接矩阵"页，只负责把生成器算好的差集与六类边分母摊给人看，自己一行判据都不算 | D_FRONTEND |
| `tests/governance/test_connection_matrix_rulers.py` | connection matrix red blue tests / 矩阵红证 | **新立**（tests/ 对 CREATE-GUARD 豁免，仍列此备查） | 全连接矩阵的四条必备红证：抹 module_ref 必点名、假 data_refs 必走 R11 判悬空、无声明因子不得算缺口、改过的 CSV 必让 --check 返非零 | D_GOV |
| `docs/_working/three_piece_infra/piece3_matrix/CASE.md` | 包 13.4 案卷 / 连接矩阵案卷 | 新立（本道唯一案卷，无重复册） | 全连接矩阵首次真跑的账：六类边分母、208 条该连未连、声明侧欠账清单、CH 读数通道披露 | D_GOV |
| `docs/_working/three_piece_infra/piece3_matrix/register_manifest.md` | — | 本清单（新 .md，一并领号） | 戊道交总筹合批登记的待登记清单 | D_GOV |

## 二、新建产物（非 .py/.yaml/.md 七格式，但要落归属）

| 产物 | 归属 | 跟踪态 | 备注 |
|---|---|---|---|
| `docs/_working/decision_map_campaign_20260924/connection_matrix.csv` | 戊道（契约 §包13.4 指定路径） | git 可跟踪（未被 ignore） | 1328 行 × 9 列，全量矩阵真物；**生成物禁手改**（改则 `--check` 判 artifact_stale → rc=1） |
| `data/runtime/connection_matrix/connection_matrix.json` | 戊道 | **被 .gitignore:339 `data/runtime/` 忽略** | CSV 的 JSON 兄弟（`--json-out` 默认位，仪表盘读它）。契约 §五.7 禁 .json 进 docs/_working，故落运行区。**落地侧后果**：合并后此文件不在库里，面板首帧会显示"矩阵产物未生成"，须跑一次生成器（事件触发与否归总筹排产，本道未擅自新增 reconciler，保持波 13 净零门禁=0） |

## 三、改动过的既有文件（仅 1 个，最小侵入）

- `src/zephyr/frontend/dashboard/app_panel.py`
  - import 组件 4 行 + 新增 `_tab_connection_matrix()` 方法 + `build_tabs()` 加 1 条 `("连接矩阵", self._tab_connection_matrix)`
  - 文件头 `[DEPENDENCIES]` 补 `zephyr.frontend.dashboard.components.connection_matrix`
  - 类 docstring Tab 目录补第 15 行；`build_tabs` docstring 里"构建 14 个 Tab"改为"Tab 数以 tabs_spec 为准，散文不背数"
    （依据 #ARCH-310 §4.3：静态计数写进散文必漂移）
  - **未改任何阈值、断言、skip/xfail，未动其他 Tab 逻辑**

## 四、需要总筹决策/代做的项（本道无权做）

1. `config/trading_decision_map.yaml` 61 个 `module_ref=null` 节点：本道**零改动请求**（冻结面）。
   其中 20 个带消费声明的节点是"该连未连"最高信号簇（L9 知识供给层 12 个），要补的是执行路径本身，不是 YAML 字段。
2. 两本注册表的声明侧欠账（详见 CASE.md §三 表）：`factor_registry` 缺表轴与 owner 轴、
   `strategy_registry` 缺因子轴与 TDM 节点轴——补一个，矩阵的 NO_DECLARED_EDGE 就掉一片；本道未越权补数据。
3. depgraph 新节点登记：`apply_depgraph.py --add-design-node` 三条（本道未跑，避免与总筹/他会话抢写）。
4. 若要把矩阵挂成事件触发（post-commit 重生成），属新增 reconciler，与波 13 "净新增门禁台数=0" 冲突，
   本道**未擅自做**，仅在此登记为待决项。
5. 丁道（消费面普查）若已定档 §3.4 常量，请以 `zephyr.governance.scan_scope_converged` 为唯一入口合并；
   若丁道另立了一份口径，判据以本清单先落地的常量为准并请删重（同真源可派生→必并）。

## 五、本道自证（可复跑）

```
cd D:\ZephyrAlpha\.worktrees\st-p3-matrix
PYTHONPATH="src;." python scripts/governance/d5_architecture/generators/generate_connection_matrix.py --print-summary
PYTHONPATH="src;." python scripts/governance/d5_architecture/generators/generate_connection_matrix.py --check   # 当前 rc=1（差集 208 非空）
PYTHONPATH="src;." python -m pytest tests/governance/test_connection_matrix_rulers.py -q                        # 12 passed
git status --porcelain                                                                                          # 零 git 写：无 add/commit/enqueue
```
