---
ttl: task_bound
completes_when: "族 10 的 W-100..W-103 在落地面（git show HEAD 口径）取得两轮零未收敛与红蓝补测记录，且本册每条数字都附可复跑命令"
source_rows: "docs/_working/total_command_closeout/00_master_skeleton.md 行 157-163"
measured_at: "2026-09-27 03:53-04:05（本地钟）"
---

# 族 10 · 终验与对抗 — 叶册（子类目逐个挖到底）

> 归属：本役 `st-final-build-20260926`（总筹本班自挖，未派单）。
> 与 00 册的关系：00 册本族只到"一行一环节"，本册把它拆到**可复跑判据 + 实测三态 + 缺陷修法**。
> 与 02 册冲突时以 02 册为准；本册不改任何判据阈值，只报实测。

## §〇 一句话结论（先给坏消息）

**W-100 从未达成，而且本班此前"两轮全绿"的读数是假的——假在自己写的跑批尺上。**
`wave7.py`（逐目录回归编排器）对"该面不存在"的目录返回 `rc=0 summary="absent at this surface"`，
于是 14 个目录里有 **9 个根本没跑却被计为通过**。修前的 round1 真值只有 5 个目录跑过，
其中 1 个（`tests/infrastructure`）1500s 超时未收敛。⇒ 本族的"终验"目前＝**未开始**，
不是"快完成"。

这条是自犯自捕（不是别人告知），因为它同时证明了一件事：
**本仓"判通过的尺必须先证明能红"这条铁律（autoclaw 战役在册），对我自己写的编排器同样成立。**
修法见 §一·四。

## 一 · W-100 冻结车道后在落地面逐目录两轮回归

### 1.1 判据（done 的定义）
1. 跑道＝**落地面**：`D:/ZephyrAlpha` 主区、`HEAD` 已含全部件；活树（`.aidrafts/<sid>/`）两轮一致**不算认证**（在册铁律）。
2. 逐目录跑，每个目录记 `rc/耗时/通过数`；**未收敛（超时、缺面、收集为 0）一律计红**，不得记通过。
3. 连续两轮 `n_fail=0` 且两轮之间无人改动被验面（冻结车道）。

### 1.2 实测（三态：落地面 / 车道面 / 在册声明）

| 项 | 数 | 取数命令（cwd） | 态 |
|---|---|---|---|
| 落地面测试件总量 | **3758** 个 `.py` | `git ls-files 'tests/**/*.py' \| wc -l` @`D:/ZephyrAlpha` 03:53 | 【HEAD实测】 |
| 其中最大目录 | governance 692 / signal_ashare 146 / infrastructure 136 / zephyr 133 | 同上 + `awk -F/ '{print $2}' \| sort \| uniq -c` | 【HEAD实测】 |
| pytest 配置面 | `addopts = -q --strict-markers`、`testpaths = tests`、`norecursedirs` 含 `.runtime` | `grep -nE "addopts\|testpaths\|norecursedirs" py.ini` | 【HEAD实测】 |
| 已跑过的轮数（**具名子集**，落地面） | **2 轮**，同面同码：`tests/gov_enforcement + tests/backup + tests/data + tests/governance/commit_gates` = **3328 passed / 1 skipped / 0 failed**（173.17s 与 210.84s 各一轮，04:44:20-04:50:51 本地钟，cwd=`D:/ZephyrAlpha`，命令见 §1.3 末）——**注意量纲**：这是 4/14 个目录面，其余 10 面含本班未落地新件，落地面根本无面可跑 | `python -c "import json;print(len(json.load(open(r'D:/ZephyrAlpha/.runtime/tmp/st-final-build-20260926/wave7_history.json'))))"` | 【车道实测】 |
| round1 真跑目录 | **5/14** | 读 `wave7_round1.json` 的 `summary` | 【车道实测】 |
| round1 被假绿目录 | **9/14**（全部为 `absent at this surface` 计 rc=0） | 同上 | 【车道实测】 |
| 未收敛项 | `tests/infrastructure` `rc=124 TIMEOUT>1500s` | 同上 | 【车道实测】 |
| 未收敛项定位（新） | `tests/infrastructure` 的 `mcp/test_mcp_full_lifecycle_e2e.py:310 test_boot_returns_boot_report` 被 pytest-timeout（`py.ini:50 timeout = 120`）击杀，栈停在 `auto_runtime_core.py:531 shutdown()` → `local_model_scheduler.py:206 stop()` → `thread.join()`；`stop()` 本身带 `timeout=10.0` 且线程 daemon=True ⇒ 卡点在 boot/关闭路径的另一处等待，不在这个 join | 读 `.runtime/tmp/infra2.log` 栈帧 | 【车道实测】 |
| 真跑通过数（5 目录合计） | 69 + 589(1 skip) + 26 + 2601 = **3285** | 同上 | 【车道实测】 |
| 车道面新件复测 | `tests/governance/data_supply` + `test_enforcement_surface_reconcile_canary.py` + `tests/data/test_wave3_date_normalize.py` = **47 passed in 3.02s** | 见 §1.3 的 PYTHONPATH 自证式 | 【车道实测，非认证】 |

### 1.3 取数命令原文（可整块复跑）

```bash
# 落地面测试面
cd /d/ZephyrAlpha && git ls-files 'tests/**/*.py' | wc -l
# 车道面复测（必须先自证导入的是车道包，否则读数无效——在册假绿源）
cd /d/ZephyrAlpha/.aidrafts/st-final-build-20260926 && export PYTHONPATH="$PWD/src"
python -c "import zephyr; print(zephyr.__file__)"   # 期望 .../.aidrafts/<sid>/src/...
python -m pytest tests/governance/data_supply \
  tests/governance/test_enforcement_surface_reconcile_canary.py \
  tests/data/test_wave3_date_normalize.py --no-header -q \
  --basetemp=D:/ZephyrAlpha/.runtime/tmp/bt_lane1
```

> 注：`-p no:cacheprovider` 在本仓会 INTERNALERROR（`Unknown config option: cache_dir`）并报
> "no tests ran"，极易被读成"没问题"——已在册，本册命令里不带该旗。

### 1.4 缺陷与修法（尺自身的红）
- 缺陷：`wave7.py` 缺面分支 `"rc": 0, "summary": "absent at this surface"`。
- 已修（04:0x）：改为 `"rc": 1, "n_fail": 1, "fails": ["ABSENT " + rel]`，摘要文案加"（不是通过）"。
  验证方式＝**反向自测**：修前用同一 ROOT 跑一次能得 9 个 rc=0；修后同一命令面（车道面）应得 0 个 ABSENT。
- 遗留：`tests/infrastructure` 136 件在 1500s 内跑不完 ⇒ 必须**拆子集**（建议按文件名三等分）并先测单件耗时，
  不许用"提高超时上限"掩盖未收敛（那是放宽判据，属禁手）。

### 1.5 为什么现在还不能认证
新测试目录 `tests/governance/data_supply/` 与 8 个 canary 文件**只在车道**，主区 `HEAD` 无面——
在落地面跑它们必然是 ABSENT。⇒ **W-100 的前置是 B2/B3 落地**，顺序不可倒。

## 二 · W-101 红蓝极限对抗补测（图14/图15 + 提交链场景⑦）

### 2.1 判据
每个图（架构地图）都要有：图定义件（`config/*.yaml`）+ 校验器 + **独立红队件**，三件都在 `HEAD`，
且红队件能红（有反例用例落盘）。

### 2.2 实测

| 对象 | 落地面（HEAD） | 车道面（我的 lane） | 结论 |
|---|---|---|---|
| `config/construction_workflow_map.yaml`（图14） | **不存在** | 存在 | 三件套缺第一件 |
| `config/strategy_card_lifecycle_map.yaml`（图15） | **不存在** | 存在 | 同上 |
| `config/data_supply_chain_map.yaml` | **不存在** | 存在 | 同上 |
| `config/dev_delivery_map.yaml` | **不存在** | 存在 | 同上 |
| `config/trading_day_cycle_map.yaml` | **不存在** | 存在 | 同上 |
| `tests/governance/d5_architecture/` | **2 件**（`__init__.py` + `test_check_vocab_domain_convergence.py`） | 7 件（多出 5 份 `test_*_adversarial.py`） | 红队件已写、**整面未落地** |
| 全仓 `*adversarial*.py` | **45 件** | — | 对抗面在别处成熟，独缺 d5 五图 |
| 队列里是否有人在投这批 | `pending/processing` 4+3 件中**零袋**携带 `construction_workflow_map`/`strategy_card_lifecycle`/`d5_architecture` | — | 无主面，随时可蒸发（见 §六） |

**改判**：00 册 W-101 原文"图14/图15 **从未被独立红队打过**"量纲不对——
红队件在车道里写了（construction 60 例、strategy_card 70 例，案卷 `dossier_C_six_maps.md` 行 66 已记），
真问题是**整面从未落地，所以在落地面等于没打过**。改判不放松要求，只把矛头从"没写"指向"没落"。

### 2.3 场景⑦跨道连坐：同名不同物的坑（差点记成功劳）
- `grep -rl "场景⑦" tests/` 只命中 `tests/backtest/test_toy_reconciliation_night001.py:629`，
  但那一处是**回测调仓语义**的第七场景（"跌出信号的持仓必须清仓"），与提交链"跨道连坐"无关。
  ⇒ 引用前先验对象，否则就是给未做的事记功（在册形态：覆盖尺"提到即算"被裁定册假绿）。
- 提交链侧确有门测试在 HEAD：`test_held_overlap_gate.py`／`test_foreign_change_gate.py`／
  `test_worktree_required_gate.py`（`git ls-files` 实测）。
- 但**归属篡改红证不存在**：`WorktreePunchThrough`（在测试里造出"成果被卸走"的现场并让新断言报警）
  在 `tests/` 全域 **零命中**，只出现在 5 份案卷文档里（`grep -rl` 实测）。
  ⇒ 93 册菜单"甲案"要求的 EV-02 复现红证＝**未交付**，不得声称已具备。
- 在册禁令：`tests/governance/test_ops_guard_red_team.py` 禁跑 ⇒ ops_guard 红队面本轮不复核，登记待窗。

## 三 · W-102 三把尺常设化（禁缓存背书 / 供数守恒 / 反事实控制组入判据模板）

### 3.1 判据
"常设"＝有**生产调用者**（门禁 / AutoRuntime 排产 / 施工 SOP 判据模板），不是"脚本存在且能手跑"。
本仓在册缺陷族＝装饰件无调用者（判"已防护"必测"谁调它＋能否改变行为"）。

### 3.2 实测：调用者集合（`git grep -l -w`，车道面）

| 尺 | 调用者 | 生产调用者 |
|---|---|---|
| `no_cache_endorsement.py` | `check_wave3_rulers.py`、`strict_truth_reader.py`、`test_no_cache_and_cli_rc.py` | **0** |
| `supply_conservation.py` | `check_wave3_rulers.py`、`gen_registration_needs.py`、`strict_truth_reader.py`、`supply_sources.py`、`test_supply_conservation.py` | **0** |
| `false_green_crosscheck.py` | `check_wave3_rulers.py`、`gen_registration_needs.py`、`strict_truth_reader.py`、`supply_conservation.py`、`supply_sources.py`、`test_false_green_crosscheck.py` | **0** |
| `ch_probe.py` | `ch_read_shape_ruler.py`、`src/zephyr/data/ch_reader.py`、`src/zephyr/frontend/dashboard/services_registry.py` | **2**（真被生产侧引用） |

⇒ **三把尺目前是 CLI 聚合器的成员，零生产消费者**：手跑有效，不手跑无事。
反事实控制组也未进模板：`grep -rln "反事实\|counterfactual" docs/01_policies_and_standards/`
命中 5 件，无一是施工判据模板（`sop_d_run_archive_naming.md` + 三本注册表 + 一个 .bak）。
W-176 的业界对表四家（great_expectations / pandera / dbt tests+data-diff / QLib）仍未落。

### 3.3 常设位三选一（我给唯一推荐，代价标满）
- 甲 **接施工 SOP 判据模板 + 门禁 pre-check**（推荐）。理由：三把尺的对象是"读数可信性"，
  天然属"施工前/提交前"位，不属交易运行时位；且 `check_wave3_rulers.py` 已是聚合入口，接线成本＝一个 GateSpec。
  代价＝新增门要先过 `gate_registry.yaml` 装载与 priority 撞号风险（本仓有 103 台门集体装载失败的先例），
  且**判据类门禁会拖慢提交链**（现 p50=263s）。
- 乙 接 AutoRuntime 排产（每日巡检）。代价＝把"开发期尺"变"生产期负载"，与"事件触发禁 cron"红线纠缠。
- 丙 只进文档模板（人读）。代价＝等于不设防，是现状的另一种写法。
⇒ 本班不自裁（新增执法面属结构变更，且甲案要新门＝需净零声明与替代对象）。列为 Owner 门位候选。

## 四 · W-103 端到端交付报告 + Owner 一页菜单

| 载体 | 落地面 | 态 |
|---|---|---|
| `93_owner_menu.md` | **已在 HEAD** | 可点菜单在册 |
| `95_dispatch_ledger.md`（派单台账） | 不在 HEAD | 仅车道 |
| `96_final_delivery.md`（端到端交付） | 不在 HEAD | 仅车道，B2 在投 |

- 在册判语（`review_int_first_principles.md` 行 28）：W-103 载体错——**菜单现＝手写散文**，
  违"凡条目列表+计数必须生成器产出"铁律，且 X-63② 已实际漂过一次。
- 本班不新建生成器（净零令：新件须声明替代对象），把"菜单生成器化"并入族 5 的派生计数治理
  （`leaf_books/f05_registry_books_and_netzero.md`，同窗由另一路挖），避免两处各造一套。

## 五 · 本族封矿判据（什么才算挖完）

1. W-100：落地面逐目录两轮 `n_fail=0`，且**目录数＝DIRS 全集**（不得有 ABSENT）。当前＝**具名 4 面两轮零失败已达成**（3328 passed×2），全集 14 面仍 0/2（9 面待本班件落地，`tests/infrastructure` 待修超时件）。
2. W-101：五图的 `config/*.yaml` + 校验器 + 红队件**全部在 HEAD**，且红队件含至少一个已落盘的反例用例。当前 0/5 图落地。
3. W-102：三把尺各有 ≥1 个生产调用者（或 Owner 明令"只作人工尺"并撤"常设化"要求）。当前 0/3。
4. W-103：`96_final_delivery.md` 落 HEAD，菜单载体按族 5 结论生成器化或经 Owner 确认保留手写。当前未落。
5. 追加自检尺（本册新得，建议入 92 册）：**G-77 编排器假绿自检**——任何"逐目录/逐件"跑批器，
   必须对"面不存在"返回红；判定方法＝临时删掉一个目录名再跑，看 `n_fail` 是否 +1。
   本族 §〇 的缺陷正是这把尺要防的形态。

## 六 · 交班位（具名，不留暗面）

| 序 | 待做 | 前置 | 风险 |
|---|---|---|---|
| R-10a | B2/B3 落地后在**主区**跑两轮逐目录回归 | 袋落地 | `tests/infrastructure` 超时未拆 ⇒ 必然再红 |
| R-10b | 六图 83 件（5 图 yaml + 5 红队件 + 校验器）定归属并落地 | Owner/属主车道决策 | 属主车道 `st-mapbuild-20260924` 已 locked、脏件 319、自有 commit 0，队列零袋携带 ⇒ **蒸发时限** |
| R-10c | EV-02 `WorktreePunchThrough` 红证落盘 | 施工令甲案放行 | 无它则 93 册甲案验收条件不成立 |
| R-10d | 三把尺常设位裁定（§3.3） | Owner | 甲案要新门＝净零声明 + 提交链变慢 |
| R-10e | `test_ops_guard_red_team.py` 待窗复跑 | 在册禁令解除窗 | 现由他役执行，本班不碰 |
