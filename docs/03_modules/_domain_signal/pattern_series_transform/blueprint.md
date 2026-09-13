---
blueprint_id: MOD-SIG-146
module_name: pattern_series_transform
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-09-14
last_updated: 2026-09-14
owner: ZephyrAlpha-Owner
---

# MOD-SIG-146 pattern_series_transform 蓝图

> 设计真源：2026-09-14 Owner 拍板"替代图形族以变换层立项"（会话
> st-pattern-20260914）。本蓝图升级 REG-PAT-001 头部旧裁定（"Renko/P&F/Kagi
> 属数据图表类型，非形态语义"=排除）为：**归数据/序列层变换，立项施工**。
> 代码（拟）：`src/zephyr/signal_ashare/strategy_signal/pattern_series_transform/`。

## 0. 定位

治本路径不开"第 10 大类"铺形态条目，而是造一个"换记账方式"的底座：
OHLCV 时间序列 → 替代序列（Renko 砖块 / P&F 点数列 / Kagi 阈值线），让
MOD-SIG-091 现有几何腿（双顶/双底/趋势线/通道/突破）在更干净的价格表示上
重跑——一个抽象层让全库形态的有效覆盖翻倍，而非目录膨胀。

三实现共用一个 SeriesTransform 接口；施工序 Renko→P&F→Kagi（实现成本递增、
公开证据递减；Renko 对 A 股涨跌停平坦 bar 与跳空噪声适配最好）。
规则纯机械（每族仅 1-2 个参数）：对 100% AI 开发语境=可实现/可测试/过拟合
自由度最小。第一性依据：K 线族按时间记账（每天一笔，没动静也记），本族按
"价格真动了"记账（固定砖块/格值反转/阈值拐弯）——本质是去噪滤波器。

## 1. 接口（拟）

    SeriesTransform.build(ohlcv: DataFrame, params) -> TransformedSeries
    TransformedSeries: 事件流（砖/列/拐弯段），带 confirmed_ts 锚点
    实现：RenkoTransform(brick_size, close_to_close=True)
         PnFTransform(box_size, reversal_boxes=3)
         KagiTransform(reversal_threshold)

## 2. PIT 口径（防前视铁律）

- 全部 close-to-close 构造：已完成 bar 收盘定砖/定列/定拐弯；
  禁盘中触格判定——盘中触格=回测偷看未来（业界著名陷阱）。
- 变换序列上的形态事件：confirmed_ts=确认 bar 收盘时刻，事件落库/统计
  统一走 MOD-SIG-145（本模块不建独立统计通道）。

## 3. 目录侧联动（净零预算）

- REG-PAT-001 不开第 10 大类；仅补 P&F 原生形态 10-15 条（catapult /
  双重三重顶底 / 牛熊陷阱类），逐条带 regime 标注。
- 既有几何形态条目加 applicable_series 标注（time_bars/renko/pnf/kagi）。
- REG-PAT-001 头部 10849 行裁定注释同步升级为"已立项变换层（MOD-SIG-146）"。

## 4. 边界

- 不做：替代图形的前端渲染；tick 级盘中 Renko（日线 close-to-close 先行，
  盘中版留 tick_depth5 数据成熟后评估）。
- 消费端就绪前不启用：引擎腿经 TransformedSeries 适配器注入，无消费端=不上线。
