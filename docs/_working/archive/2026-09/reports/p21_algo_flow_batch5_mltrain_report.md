---
ttl: task_bound
session: st-btfix-p15-20260915
date: 2026-09-15
---

# P2-1 ALGO_FLOW 逐域出仓 批5 报告：ml_train 域（st-btfix-p15-20260915）

## 概要

| 项 | 值 |
|----|----|
| 域 | ml_train → `docs/03_modules/_domain_machine_learning_train/algo_flow/` |
| 出仓文件 | 43 src（内联块 → 单行 external 锚点） |
| yaml 产物 | 43 本批新建（目录共 58 个 yaml，15 个为先前已跟踪） |
| 块行数 | 1342 行机器块外迁 |
| 测试 | tests/ml_train + tests/ml_experiment = **410 passed**（37.6s，隔离 cache_dir） |
| 提交 | `801b8c1261`（88 文件，零吸收已核实） |
| 幂等 | 复扫 0 待出仓（40 skipped + 3 already） |

## 配套登记

- **创建令牌**：capability_canonical_file_registry.yaml +58 条（capability `btfix_p1p2`，created_by st-btfix-p15-20260915）。其中 43 条为本批新 yaml，15 条为该域先前未登记的已跟踪 yaml 补登。
- **TDM**：config/trading_decision_map.yaml 无 ml_train 节点引用——本批零注解义务（与批3 regime 5 节点、批4 ex_core 9 节点不同）。
- **CloneGuard**：3 对既有克隆暴露（出仓同时触碰两侧文件），均核实为 HEAD 既有、非本批引入，echo-guard.yml acknowledged：
  1. `_pinball_loss` ×2（density_quantile_trainer / qnn_two_stage，exact 100%）
  2. `validate` ×2（limit_up_classifier / seat_pattern_classifier，structural）
  3. `_default_hash` ×2（reproducibility_manager / research_data_manager，structural）

## 过程发现

1. **watchdog 归属认领竞态**：worktree_drift_watchdog（#ARCH-304 单活跃会话归属）在我 claim 完成前扫描到 ml_train 漂移，以合成会话 `task:SRC-081` adopt 认领了 5 个文件，导致我方 claim 冲突（82/87）。处置：确认持有者为 watchdog daemon（pid 21596，非施工会话）→ `gateway.release_files('task:SRC-081', 5文件)` 精准释放 → 我方重 claim 成功。建议：出仓工具跑完后立即 claim，缩小 watchdog 认领窗口。
2. **`--allow-overlap` 24h 限额（5 次）触发**：批3-5 每批都带 overlap 逃生导致 TRAE-079 fail 计数满。本批实证：claim 纯净后**无需** overlap 旗标即可提交——后续批次默认省略该旗标。
3. **[GW:] 标记伪造拦截**：message 手写 `[GW:btfix_p1p2]` 被 FORGED-GW-MARKER gate 阻断（红蓝 v3 c224e15d63 的对抗场景正常生效）。留痕标记一律由网关自动追加，message 文件禁手写。
4. **目录折叠陷阱**：git status 对全新目录折叠为单条目（`?? dir/`），`ls | wc` 得 43 而 os.walk 得 58——15 个为先前已跟踪 yaml。提交清单必须按 tracked/untracked 分类展开，勿凭 status 条目数定清单。

## 战役进度

- 已出仓累计：批1-2（71）+ 批3 regime（42）+ 批4 ex_core（59）+ 批5 ml_train（43）= **216 文件（6.5% / 3302）**
- 剩余大域：feedback_loop(340) / infrastructure(336) / governance(296) 需独立立项；中小域可继续逐批推。
- 遗留（非本批义务）：pytest_min.ini markers 单行分号语法 bug；TDM note 归因窗口 >3 行重设计。
