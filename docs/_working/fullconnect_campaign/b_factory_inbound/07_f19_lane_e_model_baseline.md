---
ttl: task_bound
title: F19 车道E·模型基线（QR/Kronos 分布预测对台）——L02 接线矿道案卷
session: zc-l02-20260927
---

# F19 · 车道E-模型基线

> 挖矿基册=01_strategy_factory/07_f19_lane_e_model_baseline.md（SF-A）。本卷=独立复核+09-27 增量。

## 一、六向台账
| 向 | 实证锚点 |
|----|------|
| 上游 | 000300 指数日线（translated/_c4_engine.load_index，lane_e_quantile_baseline.py:50-57）；Kronos=CH kline→OHLCV+amount（kronos_adapter.py） |
| 下游 | MOD-BT-194 考尺 distribution_forecast_eval→E4 分布预测双标准首例→TDM UP-2..5 升级蓝图解锁件；**不卸进货台账（设计如此）** |
| 自动触发 | 无常驻；Kronos 评估=GPU 事件；零计划任务（schtasks 09-27） |
| 真源注册表 | MOD-BT-084（084 段）/089/194=:9390,15865/195=:15991（grep 实证）；图 9 FAC-E1E partial+algo_note_extra（600519 实测数据在案）；tests 四套在盘（quantile_baseline/enhanced/distribution_forecast_eval/kronos_adapter） |
| 门禁质量尺 | PIT 不变式（特征 ≤T-1 无同窗泄漏）；评估三标准（PIT 覆盖率/锐度/pinball）；随机游走无信息基准对照；双档权重可回滚；判定权留 E4 |
| 运行状态 | 绿（考尺件）/黄（复跑资产断）。09-27 复测 .runtime/tmp/kronos_repo 与 kronos_weights **仍不存在**（ls 实证）——复跑断链维持；git 1ce3e275（09-13 QR）/672dec4319（09-15 多标的）/50944b2a00（09-16 tokenizer 治本+冒烟 calibrated=true）为战绩锚点 |

## 二、子模块三级枚举
1. **代码面**：lane_e_quantile_baseline.py:60-（QR q05/50/95）｜lane_e_enhanced.py:29-（linear_qr/gbr/lgbm×IS+OOS）｜lane_e_enhanced_cli.py｜distribution_forecast_eval.py（194 考尺，车道 E/Kronos 通用）｜kronos_adapter.py（walk-forward+多路径采样+多标的窗口+_resolve_weight_dirs 换装）｜kronos_finetune_prep.py+kronos_finetune_pkl_prep.py（MOD-BT-204 微调两件）。
2. **注册表/文档面**：path_ownership_map 四锚点；FAC-E1E（store_refs 空数组——run_archive 评估档案位未登记）；design_refs=Kronos AAAI 2026+官方仓。
3. **数据/资产面**：评估档案 run_archive；Kronos 权重/仓镜像**零在盘**（复跑断链实证）；09-16 实测数据（锐度 109 vs 随机游走 314、校准 0.4 vs 0.2）存图 9 algo_note_extra。

## 三、接线四态独立复核
- 图 9 四态 partial → **维持 partial**（四件考尺线 built 有实战；复跑链断+因子登记通道缺）。
- **骨架勘误**：①图 9 双口径漂移（FAC-E1E"实测已跑" vs FAC-E3 尾注"MOD-BT-195 登记跳过网络不可达"）维持未合并——09-27 复核两注仍在 yaml，实况=资产在盘期实测过、现不可复跑，两注各半真；建议下版图合并口径（基册已提，未落地）。②"分布预测输出登记为前瞻性因子（factor_registry 准入）"承诺仍无实件（FAC-E1E algo_note 与因子登记通道缺失并存）。

## 四、缺口清单
| # | 现象 | 证据 | 处置 | 优先 |
|---|------|------|------|------|
| 1 | Kronos 复跑断链（资产放 TTL 区已蒸发+外网不可达） | ls 两路径不存在（09-27）；kronos_adapter eval 会 RuntimeError | 施工（资产管理）：权重+仓镜像挪 F:/zephyr_cold 或 G:/backup 冷储位；0.5 天 | P1 |
| 2 | 前瞻性因子登记通道缺 | factor_registry 无分布预测来源登记记录 | 施工：评估达标件走 factor_mining_sop S1 立卡；1 天（或图 9 删承诺） | P1 |
| 3 | 校准系统性过窄 | 09-15 19 票实测诊断（0.4 vs 0.2） | P2 研究项：样本×路径扩容或 Conformal 层 | P2 |
| 4 | 图 9 双口径漂移 | FAC-E1E vs FAC-E3 尾注矛盾并存 | 文档工：下版图合并 | P2 |

## 五、自审闸三态
- **三态：partial**。沿用基册+复核无新缺口（资产缺失 09-27 复测维持；四件代码/tests 全在盘无退化）。

## 六、复跑命令
```bash
python scripts/backtest/lane_e_quantile_baseline.py --help
ls .runtime/tmp/kronos_repo .runtime/tmp/kronos_weights 2>&1          # 双不存在=复跑断链实证
git log --oneline -3 -- scripts/backtest/kronos_adapter.py            # 09-15/16 实战批
python -m pytest tests/backtest/test_lane_e_quantile_baseline.py tests/backtest/test_lane_e_enhanced.py tests/backtest/test_distribution_forecast_eval.py -q
```
