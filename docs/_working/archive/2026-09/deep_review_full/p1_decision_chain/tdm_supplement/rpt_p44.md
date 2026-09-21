---
ttl: task_bound
title: 深度审查作业簿——盘中涨速异动扫描
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：盘中涨速异动扫描（P44）（GLM-5.3-Flash / 基线 2fa92002c3）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（目标文件零漂移已核）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/signal_ashare/intraday_t0/intraday_volume_orderflow.py`
- TDM 节点: TDM-E-L3-11-2（stage）
- 备注: 阶段0对账补册对象（T08 缺口清册）；MOD-SIG-093/B10-01361；节点名"盘中涨速异动扫描"与文件实为"日内量能结构三件套（VP/CVD 背离/VPIN）"——名实差距见 §5
- 生产调用方: **0（grep 仅包门面 `signal_ashare/__init__.py:34` 再导出+三邻件头注"候选/CVD 契约上游"声明（wyckoff_accumulation_signal.py:37、false_breakout_trap_detector.py:5 均未接线）；[CONSUMERS]"候选"声明诚实）**
- 测试文件: `tests/signal_ashare/intraday_t0/test_intraday_volume_orderflow.py`（13 用例，本班次实跑 13/13 绿）

## 1 对象快照

333 行纯函数三件套：Volume Profile（典型价 (H+L+C)/3 分桶+POC+VA70% 贪心双侧扩展）、CVD（BVC 简化 sign(close−open)×volume 累加，PIT 严格）+峰谷对位背离（magnitude=价格腿±CVD 逆向腿归一化）、VPIN（等量 50 桶按量比例拆分 delta，尾窗均值，桶数不足 degraded=True 不静默）。Config 构造即校验。与 P43（盘前）时段正交声明、与 event_score 内嵌 CVD 查重裁定不收编（:30-36 纪律良好）。测试覆盖：三件套主路径+degraded。排除项：wyckoff/false_breakout 上游消费件（各自域）。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| A 深度 | 数学①：VP 分桶 digitize+clip 边界正确、POC=桶中点、VA 贪心扩展自 POC 向大量侧（va_low≤POC≤va_high 不变量天然成立 :195-206）；CVD BVC 口径 PIT 严格（:216-220）；VPIN 跨桶比例拆分 `d×(take/v)`（:309）量加权正确、尾部窗口+degraded 语义（:321-322）与 Easley-O'Hara bulk VPIN 简化口径一致 | intraday_volume_orderflow.py:187-213,309-322 | 通过 | 手算 3-bar VP/VPIN |
| A 深度 | 边界②：缺列/空表/负量/零总量/桶数不足全 fail-closed 或 degraded（:141-151,297-299,316-318）；hi≤lo 退化早退（:178-185）；**但 NaN 无防御：volume/价格 NaN 经 `(NaN<0).any()=False` 滑过 `_require_bars`，NaN 传染 bin_volume（np.argmax 遇 NaN 返 NaN 位）/CVD cumsum/VPIN 均值→输出 NaN 垃圾**（vpin 钳制 min/max 对 NaN 无效实测语义）——停牌/坏数据 bars 常见 NaN，静默产出毒输出 | :149-151 | P2(接线期必修) | 造含 NaN volume 的 bars 跑三件套观察 NaN 输出 |
| A 深度 | 语义③：背离检测窗口 `close[i-lb:i]` 不含当根（:238）——新高的判定基准为前 lb 根，连续新高会逐 bar 重复报同一背离事件（去重责任在消费方，无 dedup 无 refractory 期） | :237-271 | P3 | 单边上涨序列观察连续 bearish 事件 |
| B 上游 | checklist #6 断供：分钟K 注入（tick_subscriber 上游为 P2 域已审族）；缺列/空表显式 raise 断供有痕；NaN 断供（坏数据）无痕=上述 P2；config 全校验 | :141-151 | P2(同 NaN 案) | — |
| C 下游 | **孤儿裁定：生产零调用方**（三候选消费方 Wyckoff CVD 确认/背离 CVD 腿/精筛装配层全部未接线）；爆炸半径=CVD/VPIN 毒 NaN 若被 Wyckoff 消费→买点误判（下游无防御声明） | grep 证据 | P1(接线期)+P2(NaN) | `grep -rn "IntradayVolumeOrderflow\|cvd_divergences" src/ --include=*.py` |
| D 旁系 | checklist #4 双承载：与 event_score 内嵌 CVD 助手两处 CVD 计算——查重裁定已做（:33-34"局部计算不收编"登记在案），但**同一 BVC 口径两处实现漂移风险在册**（建议接线时对拍符号约定与量纲）；与 P43 盘前/盘中正交声明清晰 | :30-36 | 通过 | 两处 CVD 同输入对拍 |
| E 对抗 | 五问：①静默失败=NaN 垃圾输出（实锤）；degraded 有标志②假阳性=VPIN 在 A 股涨跌停一字板的 delta 分布失真（一字板 close=open→delta=0，知情交易度量在极端制度性场景失效——BVC 对 A 股制度性 K 线的适配缺口，声明未提）③断供有痕④重触发幂等⑤时序=bars 时序不校验（乱序注入 CVD 背离全反——隐式"时间升序"契约未文档化） | :216-220 | P3 | 倒序 bars 观察背离方向反转 |
| F 新鲜度 | VPIN=Easley, López de Prado & O'Hara（Review of Financial Studies 2012 flow toxicity；bulk volume classification 口径与 Easley et al. 2017 改进版注释一致）；VA/POC=Market Profile 标准算法；CVD BVC=无 tick 买卖方向的标准近似——**对等已有（文献正源）** | https://www.stern.nyu.edu/sites/default/files/assets/documents/con_035928.pdf ；https://ideas.repec.org/a/now/jnlcfr/104.00000047.html | 通过 | WebSearch 2026-09-18 |

## 3 SOTA 对照

- 对等已有：VPIN 等量桶+BVC 拆分与 ELO 2012/2017 正源口径一致（简化近似声明诚实）；VA 贪心扩展为 Market Profile 常规近似。
- 立卡候选：A 股制度适配（涨跌停一字板 delta 失真的屏蔽/降级标记）——VPIN 消费前建议处理。

## 4 缺陷清单

1. P2：NaN bars 无防御→三件套静默产出 NaN（`_require_bars` 只查负量不查 isfinite）；建议补 finite 校验对齐 ERROR_CONTRACT；验证法=含 NaN volume bars 实跑。
2. P1（接线期）：零生产调用方孤儿（三候选消费方均未接线）；验证法=§2 C 轴 grep。
3. P3：背离事件无 refractory 去重；bars 时间升序契约未文档化；一字板 delta=0 的 VPIN 制度性失真未声明。

## 5 挂起疑问

- 节点名"盘中涨速异动扫描"（涨速/异动语义）与本件（量能结构/订单流统计）名实差距明显——涨速扫描承载件查无（grep `涨速` 无专件），建议收口方核对 TDM-E-L3-11-2 映射或立涨速扫描缺口卡。

## 6 完备性自评

六轴全查（F 带 URL）。长尾：①VA 贪心扩展 vs 标准进度法的覆盖率差异未量化②VPIN 桶切分的 1e-9 浮点残差在大总量下的累积未验③13 测试无 NaN/乱序 case。

## 7 收口裁定（收口方填）
