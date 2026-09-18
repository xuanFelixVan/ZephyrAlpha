---
ttl: task_bound
completes_when: 第四腿按本件配方落完 T4 三分组并回写本件状态
---

# 落地接力第三腿 st-ff-land3-20260918 · 逐件断点与第四腿配方

> 本腿三笔落地面（T1/T2/T3）+ T4 **未开工**的原因与配方。测试数全部本腿亲跑，未沿用前手声称。

## 已落

| T | 主题 | commit | 本腿自跑测试 |
|---|---|---|---|
| T1 | R-L3 资金安全幂等键三件套 + 4 红治本（测试隔离） | `9e16e884af`（队列 q-…-0001） | tests/ex_core 全目录 **1304 collected / 1303 passed + 1 xfailed / 0 failed**；隔离前后差 4 红 |
| T2 | 危机闸三批（pf_alloc E1/E4/E5 + alt_data + sector + 月度演练件） | 队列 q-…-0004（经两次死信修正，见下） | pf_alloc 四件 **152 passed**；alt_data+sector **40 passed**；crisis_gate 复跑 **23 passed** |
| T3 | 战役真源 docs 49 件 + 注册表 token 载体同批 | 本件同批 | 无码测（纯 docs）；机械校验=yaml 复解析 + frontmatter 逐件核对 |

### T2 两次死信（R-017 处置：全是真问题，走治本，未走任何豁免旗）
1. `q-…-0002` **MSG-EXPOSURE**：`crisis_gate.py` 三处 `raise CrisisGateError(f"…{path}…")` 把绝对路径
   写进消息文本 → 治本=`CrisisGateError` 增 `details` 结构化通道（口径对齐
   `ZephyrBaseError` 的 message/details 双通道与仓内既有 9 处同款），路径进 `details`、消息只留摘要。
   复跑门禁自家 `_detect_msg_exposure` = **violations []**，测试 23 passed 不变。
2. `q-…-0003` **NO-BARE-SQL** 4 处：`crisis_drill_monthly.py:352/359/394` + `crisis_gate.py:366`
   → 治本=提为模块级 **plain `SQL_*`** 常量（**刻意不加 `Final`**——R-029 实证
   `_extract_sql_constant_lines` 只识别 `ast.Assign`，`AnnAssign` 不被豁免），表名经 `_table()`
   占位注入，调用侧 `.format(...)`。

## T4 未开工的机械前提：任务书"260 件"口径本身不成立（已记 R-032）

`.runtime/tmp/ff-land/rest.txt` 260 件对 HEAD 的 staged numstat 分档（清单
`.runtime/tmp/ff-land3/rest_class.txt`，格式 `kind/state/insert/delete/path`）：

- **has-add 75 件** = docs 34（本腿 T3 已落其中 ~40 件含非 rest 的战役件）/ scripts 23 / src 14 / tests 3 / other 1
- **revert-only 185 件** = tests 122 / src 43 / scripts 20（零 insert）

185 件里两型**肉眼不可分**，本腿抽样实证：
- 型①（合法待落的 BRK-086 TTL 去重）：`tests/signal_ashare/sector/test_sector_conduction.py`
  —— 删两行后文件里**仍有** `# [TTL] permanent`；
- 型②（stale index 纯回退，落它=回退 HEAD 且触 TTL-METADATA）：
  `tests/pf_alloc/test_correlation_persistence.py`、`src/zephyr/shared/infra/__init__.py`
  —— 删掉的是 HEAD 里**唯一**的 `# [BLUEPRINT] …(auto-injected by S4 reconciler)` + `# [TTL] permanent`。

→ **第四腿配方（按序，勿整批 add）**：
1. `python - <<PY` 式批量判据：对每个 revert-only 件跑
   `git show :<f> | grep -c '^# \[TTL\]'`，=0 者判型②（`git restore --staged -- <f>` 归位，
   工作区不动、零内容损失，与第一腿对 5 件 STALE_INDEX 的处置同法）；=1 者型①可入批。
2. 型①按域分批（tests 域一批 / scripts 域一批 / src 域一批），每批 ≤40 件，
   跑该域测试面再入队；src 域含 `src/zephyr/data/**` 者**本战役禁写**（任务书禁越界项），须剔除。
3. has-add 的 scripts 23 件 / src 14 件按 R-028 协议：先复制到 `.runtime/tmp/ff-land4/staged_src/`
   做 import 冒烟，**过后再入批**（本轮 R-028 已实证一次编辑竞态打死 57 个测试文件收集）。
4. 新 .py 三件套：`batch_creation_tokens.py --prefix <完整路径>`（单值 argparse，逐件跑）+
   `apply_depgraph.py --add-design-node`（状态链 planned→generated→testing→stable→production）+
   `add_module_translation.py`（**必须在主仓跑**）；token 载体册 **与代码同批进 --files**（R-017②）。

## 本腿另记的两件未完

- `tests/pf_alloc/__init__.py`：任务书列了，盘上/index 里都不存在，pf_alloc 382 例收集正常 ⇒ 判陈旧项未建（req_land3_01 ITEM-3）。
- `docs/_working/{residual_construction/00_master_ledger.md, tdchain_mine/a0_master_ledger.md, factory/strategy_cards/e4_report_s_owner_002_regime_switcher.md}`：
  三件 staged 面含**真删除**（4/2/0 但跨他道主题），本腿未入批以免把别道台账折到中间态；
  `sim-memo-202609.json`（1378 行）按 DIRECTORY-CONTRACT 永久剔除（本腿亦未 add，落点请裁=ITEM-4）。
- `src/zephyr/risk/paper_hedge_leg.py` + `config/paper_hedge.yaml`（R-020/R-022① 指派给 z-land2 的两件）：
  **本腿仍未落**——不在本腿独占路径内（`src/zephyr/risk/**`），且 R-022③"保命轨盘内自动拉闸"仍挂 Owner 门位，
  第四腿接手时先核这是否已被 z-drift/z-orphan 侧吸收（本腿观察到 `8b12ffa789` 已由 z-drift 落了
  `slippage_bps` Nullable 对齐，说明 R-014 一条链别道在推进，勿重复施工）。
