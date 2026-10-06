---
campaign: matrix-20261006
lane: m2
status: draft
ttl: task_bound
---

# 规格卡 X-07 | TDM-X-S1-05 信号融合与紧迫度评分

- 车道: M2 离场族+板块族接线挖矿 | 2026-10-06
- 接法分级: **M**（模块补写；纯向量化，X 族中唯一无路径依赖的决策层）
- 真源: `config/trading_decision_map.yaml#TDM-X-S1-05`（权重表/三档/确认层 D69）

## 1. 机制定义

各桶信号按类型权重加权融合成 0~1 卖出意愿分 + 多周期共振加成（日线周线同向 +0.2）；紧迫度
三档：>0.8 立即市价（S2-01 快速通道）/ 0.5-0.8 分批从容 / <0.5 等确认。D69 确认层三段式
（triggered→confirmed→released）：risk/time/volatility 桶 immediate 不辩论，signal/target/
trailing 桶 close_confirm 收盘确认；去抖三参数 confirm_bars∈{0,1}/buffer_pct 0.2-0.5%/
量能≥20日均量 1.5 倍；**去抖与强制清仓互斥（S1-06 绕过确认层）**。

## 2. 计算式

```
score_t,i = clip( 0.9·B_risk + 0.7·B_signal + 0.5·B_trailing + 0.5·B_target
                  + 0.2·resonance_t,i , 0, 1 )                # 权重=TDM 冻结口径，禁改
resonance   = 周线动量与日线同向（周线=close.resample('W').last().pct_change(4) 前向对齐 PIT：
              周线值仅用已完成周，shift 至周内最后交易日之后生效——防前视，过 S3 哨兵）
urgency     = 立即(>0.8) / 分批(0.5-0.8) / 等确认(<0.5)
close_confirm(t) = score_{t-1} ≥ 阈 且 C_t ≥ C_{t-1}×(1-buffer_pct)      # confirm_bars=1
```

## 3. 向量化实现要点

加权求和+clip+shift 全 DataFrame 算子，零行循环；共振的周线重采样需 PIT 对齐审查（周内信息
在周五收盘后才存在——用 `resample('W').last().shift(1)` 再 reindex 回日频）。量能确认=
rolling mean 比较。融合是桶信号的**静态函数**，可作为 X-S1-02/03 行循环外挂的独立纯函数
单测（唯一可独立于仓管理先行验收的 X 族决策件）。

## 4. 引擎接法（M 级）

`fuse_exit_signals(buckets: dict[str, DataFrame], params) -> (score, urgency, confirmed)`，
三产物并入 `exit_signal_surface`；urgency 列喂 X-S2-01 路由卡与 X-FLOW 审计列。
schema 无新维（融合参数进 prereg）；`X_exit_buckets` 维激活即包含本层。

## 5. 考法（T0 口径声明）

纯向量化：单独激活融合层不破坏 0.53s/格口径；**与仓管理（X_stop/X_tp）联跑格点仍受
T3b-T0 重标定约束**。周线共振的重采样在 gpu 薄核资格外（等形对齐否决→CPU 原路径），
耗时按 CPU 口径计。

## 6. 数据列名

close/amount（`c1_market.kline_daily`）。权重常量 0.9/0.7/0.5/0.2=TDM algo_note 冻结口径，
本卡如实引用。
