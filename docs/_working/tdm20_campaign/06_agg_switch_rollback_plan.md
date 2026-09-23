---
ttl: task_bound
completes_when: 回滚窗关闭（2026-10-23 退役复审）后随战役归档
title: AGG 消费切换·一键切回预案（增补令终批，st-tdm20-20260923）
owner: st-tdm20-20260923
session: st-tdm20-20260923
date: 2026-09-23
---

# AGG 消费切换·一键切回预案

> 增补令（Owner 2026-09-23，production 翻转已确认）+ agg-switch-design §2/§3（映射数字 Owner 2026-09-14 签字）+ 裁定#229（重印批）。
> 切换判据复核：①夜批连续 5 交易日零缺勤+当日更新——机械复核**通过**（09-14..09-22 七个交易日全在，最新 09-22）；②并行期无解析/供给事故；③Owner 签字=本令。

## 1. 本次切换了什么（全部可逆）

| 面 | 切换前 | 切换后 |
|---|---|---|
| TDM-E-L1-AGG module_ref | src/zephyr/regime/core/regime_detector.py | **src/zephyr/regime/core/anchored_state_machine.py**（module_id=MOD-REGIME-001 不变，同族蓝图） |
| 运行时消费（pf_alloc 链） | —（无锚定消费） | 组合层新增 **ANCHORED_CAP 总暴露熔断上限**：cap=1−0.70×clamp((vol_pct−0.30)/0.70,0,1)，与总暴露取 min 只减不加（_LayerFacts.anchored_cap → TOTAL 层 ANCHORED_CAP 裁剪，违规留痕可归因） |
| L1 总闸（TDM-E-L1，shrinkage 轴） | RegimeSnapshot | **不动**（P0-001 valid；两套各管各的） |
| 策略路由（vol_pct 阈值停开进攻 sleeve） | — | **未接线**（设计稿原文"阈值随双轨并行期证据定稿"，未冻结不施工） |

## 2. 一键切回（30 秒，零代码改动）

```powershell
# 切回（旁路锚定 cap，下一个分配日生效；按文件存在性逐次调用时检查，无需重启）
New-Item -ItemType File -Path data\runtime\anchored_cap.disabled -Force | Out-Null
# 恢复锚定 cap（回滚窗内验证后重新启用）
Remove-Item data\runtime\anchored_cap.disabled
```

- 机制：`allocation_inputs.anchored_cap_enabled()` 每次调用检查文件存在性 → 存在即 `applied=False, degraded_reasons=("disabled_flag",)` → 组合层零施加。
- 旁路态留痕：enabled 旁路不产生告警（与 crisis 闸旁路有声化不同——cap 是增益约束非保命闸；旁路即回到 2026-09-23 前的既有生产行为）。
- 切回后验证：次日 alloc 预算面 warnings 无 `anchored_cap_*` 条目 + `alloc_shrinkage_daily`/预算快照与切换前同构。

## 3. 旧 HMM 链保留清单（回滚窗 2026-09-23 → 2026-10-23）

- `src/zephyr/regime/core/regime_detector.py`（MOD-REGIME-001 主蓝图）：保留，零改动；
- `c1_backtest.regime_snapshot_history` + HMM 夜批供给：保留在产（L1 总闸仍在消费——它不是死代码，是另一套的活踩）；
- `scripts/backtest/compare_state_dualrun.py`（双轨对比器）：保留，退役复审前持续观察；
- TDM-E-L1 总闸 module_ref=regime_detector.py：不动。

## 4. 回滚窗关闭（2026-10-23）

- 动作：退役复审呈 Owner（裁定#231 框架：有无机械消费点/唯一责任）——HMM 链是否下线由 Owner 门位裁定，本班不自动执行；
- 复审输入：双轨对比器一个月曲线 + ANCHORED_CAP 触发/留痕记录 + 判据①②持续达标证据。

## 5. 应急联系面

- 锚定表断供 >7 日历日：`anchored_cap_degraded: stale` 告警留痕，cap 自动跳过（不盲用陈旧锚，行为=切回态）；
- 异常表现（预算面无端收紧）：先查 `alloc_shrinkage_daily` warnings 的 `anchored_cap_*` 与 `ANCHORED_CAP` 裁剪违规标签，再按 §2 切回。
