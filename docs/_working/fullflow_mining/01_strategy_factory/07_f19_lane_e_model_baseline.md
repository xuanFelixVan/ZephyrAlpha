---
ttl: task_bound
session: st-ailayer-fullflow-sf-a
title: F19 车道E·模型基线（分布预测/Kronos 对台）——六向台账与三态结论
date: 2026-09-25
module_ref: MOD-BT-084+089+194+195
map_node: FAC-E1E
---

# F19 · 车道E-模型基线

## 一、环节定义与边界
一句话：分布预测线只当"基线对台"不当交易信号——分位数回归起步原型（084）→三模型对比增强（089）→Kronos K 线基础模型接入（195），统一 E4 双标准考尺（194：PIT 校准+锐度+pinball）评分；产出登记为前瞻性因子反哺全厂（factor_registry 准入），**不卸 strategy_intake 进货台账**（与五车道的关键结构差异）。
上游供料=CH kline（沪深300 指数/个股 OHLCV）；下游消费=MOD-BT-194 考尺→E4 分布预测双标准首例→TDM UP-2..5 升级蓝图依赖解锁件。

## 二、六向台账
| 向 | 实证 |
|----|------|
| 上游输入 | 000300 指数日线（translated/_c4_engine.load_index，lane_e_quantile_baseline.py:50-57）；Kronos=CH kline→OHLCV+amount（kronos_adapter.py，权重 .runtime/tmp/kronos_weights 镜像下载） |
| 下游消费 | 194 考尺（distribution_forecast_eval.py）；E4 分布预测件双标准（图9 FAC-E4 algo_note）；run_archive 评估档案；**无进货台账消费方**（设计如此） |
| 自动化触发 | 无常驻（manual；Kronos 评估=GPU 事件） |
| 真源与注册表 | MOD-BT-084:（084 段）/089/194:9390,15865/195:15991 四件在 path_ownership_map；tests 四套在盘（test_lane_e_quantile_baseline/test_lane_e_enhanced/test_distribution_forecast_eval/test_kronos_adapter）；git 实证：1ce3e275=09-13 车道 E MVP 落地；672dec4319=09-15 Kronos 多标的窗口模式（19 票×60 日×8 路径，实测 19/19 锐度胜、校准系统性过窄已诊断）；50944b2a00=09-16 tokenizer 错位治本+GPU 冒烟 600519.SH n-test=20 calibrated=true |
| 门禁与质量尺 | PIT 不变式（特征 ≤T-1、滚动前推无同窗泄漏，084 INVARIANTS）；评估三标准（PIT 经验覆盖率/区间锐度/pinball）；无信息基准对照（随机游走±滚动 std 分位——Kronos 必须跑赢才算有信息，195 头注）；双档权重（kronos_daily_ft+底座 bak 可回滚）；只当基线判定权在 E4 |
| 当前运行状态 | **绿（考尺件）/黄（复跑资产）**。最近真实出货=2026-09-16（Kronos GPU 冒烟 calibrated=true，commit 50944b2a00）；09-13 QR 基线落地。**Kronos 复跑资产已清**：.runtime/tmp/kronos_repo 与 kronos_weights 实测不存在——图9 FAC-E3 尾注"GitHub/HF 双通道不可达，网络恢复后激活"与此互证；FAC-E1E 的 600519 实测数据（锐度 109 vs 随机游走 314、校准 0.4 vs 0.2）为资产在盘期战绩 |

## 三、子模块清单
| 是什么 | 入口 file:line | 状态 |
|--------|---------------|------|
| QR 分位数基线 lane_e_quantile_baseline（沪深300，q05/50/95） | scripts/backtest/lane_e_quantile_baseline.py:60- | built（09-13 落地） |
| 三模型对比 lane_e_enhanced（linear_qr/gbr/lgbm×IS+OOS） | scripts/backtest/lane_e_enhanced.py:29- | built（增强实验件） |
| CLI 封装 lane_e_enhanced_cli | scripts/backtest/lane_e_enhanced_cli.py | built |
| 双标准考尺 distribution_forecast_eval（MOD-BT-194） | scripts/backtest/distribution_forecast_eval.py | built（车道 E/Kronos 通用） |
| Kronos 适配器 kronos_adapter（MOD-BT-195：walk-forward+多路径采样+多标的窗口） | scripts/backtest/kronos_adapter.py | built（实测在案）但**复跑链路当前断**（仓+权重已清+外网不可达） |
| Kronos 微调两件 kronos_finetune_prep/pkl_prep（MOD-BT-204） | scripts/backtest/kronos_finetune_*.py | built（09-16 tokenizer 治本在案） |
| 分布预测→factor_registry 前瞻性因子登记通道 | — | **missing**（图9 说"登记为前瞻性因子反哺全厂"，无实件） |
| vendor 仓不入库换装机制 | kronos_adapter _resolve_weight_dirs | built（50944b2a00） |

## 四、堵点与病灶
1. **Kronos 复跑断链**：资产放 .runtime/tmp（TTL 清理区）注定蒸发，外网不可达期无法重装；修法=权重挪 F:/zephyr_cold 或 G:/backup 冷储位（INFRA-STORE-003 地图内合法位）+仓镜像同挪；0.5 天；本车道可修（属资产管理非施工）。
2. **前瞻性因子登记通道缺**：图9 承诺"分布预测输出登记为前瞻性因子（factor_registry 准入）反哺全厂"——无实件无登记记录；修法=评估达标件走 factor_mining_sop S1 立卡（candidate 态）进 factor_registry；1 天；本车道可修（方法论真源已备）。
3. **图9 双口径漂移**：FAC-E1E 说实测已跑、FAC-E3 尾注说"登记跳过（网络不可达）"——两注各半真（实测发生在资产在盘期，现状不可复跑）；修法=下版图合并为"09-16 实测在案；复跑待资产重装+网络"；文档工；回填总筹。
4. **校准系统性过窄**（09-15 19 票实测诊断结论）：多路径采样分位数区间偏窄——模型侧未修，登记为 E 域开放问题（样本数×路径数扩容或 Conformal 校准层）；P2 研究项。

## 五、提速与合并机会
- 084/089/195 三件共享 194 考尺与 _c4_engine.load_index——真源已收敛，无需合并。
- Kronos 多标的 window 模式（批量 generate 跨票复用单载）已是省算力形态（f487d44acc 优化批）；无再合并点。

## 六、自审闸三态
- **三态结论：partial**（四件考尺线 built 且有实战；复跑链断+因子登记通道缺）。
- **差什么才算 built**：①Kronos 资产冷储重装（复跑可达）；②前瞻性因子登记通道跑通首例（或图9 删除该承诺）；③（研究项非门槛）校准过窄修正。

## 七、复核命令
```bash
python scripts/backtest/lane_e_quantile_baseline.py --help   # 基线入口
python scripts/backtest/kronos_adapter.py eval --symbol 600519.SH --n-test 5   # 会因资产缺失报 RuntimeError（复跑断链实证）
git log --oneline -- scripts/backtest/kronos_adapter.py | head -3   # 09-15/16 实战批
python -m pytest tests/backtest/test_lane_e_quantile_baseline.py tests/backtest/test_lane_e_enhanced.py -q
```
