---
ttl: task_bound
campaign: fullscore_night/03_integrated_backtest
created: 2026-10-01
session: st-fullscore-20260930
verdict: BLOCKED_PRE_LAUNCH（HOLDOUT 未烧）
---

# BLOCKED——IBT-v2 发车前置失败：考卷（池）不存在，HOLDOUT 不烧

> 纪律依据：开工令自身条款"根本性问题→停，写 BLOCKED 报告，不烧 HOLDOUT"。
> 池=考卷内容；在**开考前**（而非三窗后）发现考卷缺失，属同一根本性问题且更靠前，
> 同条款适用。烧掉一次性 HOLDOUT 于未经 Owner 确认的代用池=最坏结局，故停船。

## §1 结论

**BLOCKED_PRE_LAUNCH。W_IS/W_OOS/sensitivity/W_HOLDOUT 一律未发车；W_HOLDOUT 零消耗
（--holdout-guard 从未传入，artifacts/W_HOLDOUT v1 产物 mtime 未动，artifacts_v2 无新窗产物）。**

## §2 缺失资产（简报声称"全部就绪"，实测不存在）

| # | 资产 | 简报口径 | 实测 |
|---|---|---|---|
| 1 | docs/_working/fullscore_night/03_integrated_backtest/fresh_pool_v2.yaml | 14 员，v1.1 格式已验证 | **不存在**（主树、全部 .aidrafts/.worktrees 工作树、.runtime/sessions 暂存、git 全历史均无；F:/E:/G: 盘浅扫未命中，深扫超时中止） |
| 2 | fresh_pool_v2_notes.md | FACT 族 6 件拉持有期建议在案 | 不存在；且盘上合法 FACT 翻译件仅 5 件（第 6 件 FACT-4db4c41e=死刑件已剔，#326 冻结）——简报"FACT 6 件"与现有资产**不可满足**，指向一个未落盘的批 D 产物 |
| 3 | 批 D 新鲜窗重考"新 15 员名单" | 池的来源 | 不存在（backlog F01"批 D 新鲜窗收口"仍开放，见 decision_map_campaign_20260924/19_gpu_plan_and_master_backlog.md D5 行） |
| 4 | IBT-D01 成本口径统一施工 | "引擎 _c4_engine._net_line 已可注入" | 半成品：cost_model.py 三档+_net_line 注入位已落（可 import，指纹在 prereg 附录 A），但 **ibt_runner 组合引擎侧接线、IBT-D01 CASE.md、红证测试（cost_model 头注所引 test_ibt_d01_cost_caliber_redproofs.py）均不存在**（backlog D5/D01 仍开放） |

## §3 全绿项（复航即用）

- ibt_runner.py 在案且面完整：`--window/--pool-file/--sensitivity/--holdout-guard`（指纹 5dac62676982d8e3）
- cost_model.resolve_from_env 实测三档选档正常（合法档名 legacy/calibrated/participation，未知档 fail-closed）
- _c4_engine import OK，_net_line 在位；标定表 SLIPPAGE_TIER_BPS 五分位活读正常
- CH 可达（regime 表 1812 行 canonical run 在案；kline_index 表读通）
- reaper 存活（scanned=37/killed=0）；`ibt_runner` 已登记 process_reaper_keep.txt 防误杀
- 磁盘 D: 剩 33G；v1 四窗产物+RUN-LOGS 在案可对照（git 已跟踪，只读保护）

## §4 本夜已完成（可逆工作，零考试消耗）

1. **prereg_v2.md**（LOCK-PENDING）：非池参数全冻结（四窗/成本双档/regime 关闭档/引擎参数/
   敏感性格点/发车序）+ 合格线预注册（HOLDOUT 净夏普≥0.5 且换手≤10x 且回撤≤20% + 完整性门）
   + "此卷最后一考"签署。
2. **regime 独立 OOS 复验完成，判不过**（prereg 附录 C 全数字）：r3 攻击槽 IS +1.33% → OOS −0.79%
   （pre/post-924 两段皆负）；r10 OOS fwd20 +1.96%（win 76.7%）=节流即反弹卖压。v2 冻结 regime
   关闭档（A only），与裁定 R3 退役语义一致。
3. **锁箱协议就绪**：池 sha256 指纹位已留（附录 A PENDING），填入即锁箱，随后按 §1 发车序执行。

## §5 复航路径（Owner 二选一）

- **路径甲（最快）**：Owner 提供 fresh_pool_v2.yaml（含 14 员清单与 notes）→ 核对格式+员数
  → 填 prereg 附录 A 指纹（锁箱）→ 按 prereg §1 发车序执行 → 四窗判据落 v2_verdict.md。
- **路径乙（补课）**：授权补做批 D 新鲜窗重考（E4 全链+成本门过滤）+ IBT-D01 组合引擎成本接线
  → 产物即新池 → 同甲发车。工时显著更长，且批 D 以 2025-09..2026-09 为选择窗的"烧毁语义"
  需 Owner 再确认（该段即本考 HOLDOUT，选择窗与考窗同段则本卷判据口径须重新定义）。

## §6 关联在途事项（不代修，留痕）

- capability_canonical_file_registry.yaml 暂为破损 YAML（他会话 MM 态在途编辑）——CREATE-GUARD
  token 批量登记通道暂不可用，本域新 .md 的 token 于该册恢复后随批登记。
- scripts/backtest/translated/_c4_engine.py 存在 .tmp 残留（safe_write 中断痕迹，GPU 班凌晨产物），
  不动，留其属主处置。
