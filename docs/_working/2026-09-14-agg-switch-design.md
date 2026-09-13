---
ttl: task_bound
---

# TDM AGG 消费切换设计稿（预算带映射+双轨并行方案，2026-09-14）

- **task_bound**：TDM AGG 生产消费切换的前置设计；映射表数字待 Owner 签字；会话 st-fingov-20260912 单写手
- **前序**：裁定#228/#229/#230；语义复核+重印批（2026-09-13/14）；锚定态夜批已接线（tasks.yaml anchored_state_build，2026-09-14 首跑待验证）

## 1. 现状与切换范围

- 现状：TDM-E-L1-AGG（市场状态判定）消费 RegimeSnapshot 的 HMM 7 态 dominant——该判定已被 P0-002 证伪（态标签 OOS 反转，裁定#229）并重印为**锚定风险四档**（c1_backtest.regime_state_anchored，零拟合零漂移，④⑤ 证据齐，⑥ 多头组合不达标=降级为风险路由使用）。
- 切换范围 = AGG 节点的**状态输入源**从 HMM dominant 换为锚定四档；**不含** L1 总闸（谨慎度/shrinkage 轴继续用 RegimeSnapshot，P0-001 valid 不动）。

## 2. 核心设计决策：预算数字与状态路由**分家**（治双重计算）

病根：L1 谨慎度（shrinkage）与锚定档（vol_pct 分档）**都含波动率信息**——若两者都参与仓位数字计算，波动率被双重计入（牛市双信号同时压仓 → 长期半仓）。

**推荐方案 A（分家）**：
- **仓位数字**仍由 L1 总闸独家给出（shrinkage 预算带，P0-001 已验证）；
- 锚定四档只做两件 L1 不做的事：
  1. **熔断上限**（风险档对仓位设硬顶，只减不加）；
  2. **策略路由**（高风险档停开进攻型 sleeve）；
- 映射表（数字待 Owner 签字）：

| 锚定档 | vol_pct | 仓位硬顶 | 策略路由 |
|---|---|---|---|
| r3 低风险 | ≤0.30 | 不设顶（L1 说了算） | 全部 sleeve 可开 |
| r2 中风险 | 0.30-0.60 | 不设顶 | 常规 |
| r1 中高风险 | 0.60-0.80 | **70%** | 进攻 sleeve 停开 |
| r4 高风险 | >0.80 | **50%** | 只保留防御 sleeve |

- 否决方案 B（乘法合成 L1×档位系数）：双重打折已由数据证伪路径预警（vol 信息双计）；
- 否决方案 C（维持 HMM）：态标签 OOS 反转已判死（裁定#229）。

## 3. 双轨并行与切换判据

- 锚定态夜批（anchored_state_build，daily_kline 档）2026-09-14 接线，首跑=首个交易日 16:30；
- 双轨对比器（compare_state_dualrun.py）每日并排：旧 HMM dominant vs 新锚定档 vs L1 shrinkage 分位；
- **切换判据（预注册）**：①夜批连续 5 个交易日零缺勤且当日更新（trade_date=当日）；②并行期内无解析/供给事故；③Owner 对本映射表数字签字。三条全满足→切 AGG 输入源（decision map AGG 节点 module_ref/口径改读锚定表），旧 HMM 链保留退役观察一个月后下线。

## 4. FQ-01 剔除器接线点（M5，待 C5 解冻）

- 接线位置：`src/zephyr/signal_fundamental/negative_veto.py` 的 `apply_negative_veto` + `NegativeFacts` 增 `accrual_ttm` 字段 → 第七检（应计>阈值→veto，与商誉减值检同构）；
- 纯函数已就绪：`fundamentals.accrual_negative_screen`（NaN 不误杀语义与 veto 的"事实缺失不算命中"铁律一致）；
- 实施时机=C5 解冻（M5 门位），本设计稿仅锁定接线点。
