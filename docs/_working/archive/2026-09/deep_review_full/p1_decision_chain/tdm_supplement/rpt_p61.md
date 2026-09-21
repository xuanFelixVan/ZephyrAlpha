---
ttl: task_bound
title: 深度审查作业簿——买入逻辑存活判定
owner: st-deeprev-20260918
created: 2026-09-18
---

# 深度审查报告：买入逻辑存活判定（P61）

- 状态: **已审**
- 级别: P1｜类型: stage
- 基线 commit: 2fa92002c3（已核：本对象文件在基线/HEAD/工作区零漂移）
- 审查者: GLM-5.3-Flash / st-deeprev-20260918
- 入口锚点: `src/zephyr/plan_engine/thesis_survival.py:107`（evaluate_thesis）
- TDM 节点: TDM-P-P1-03（stage，config/trading_decision_map.yaml:2656，C8 施工回填 MOD-PLAN-024）
- 生产调用方: **零**（header 自认 `[MATURITY] design`+CONSUMERS"X 流离场评估（待接线）"——诚实声明；grep 仅 intraday_tomorrow_forecast.py:8 文档模式引用）
- 测试文件: tests/plan_engine/test_thesis_survival.py（54 passed 同批）

## 1 对象快照

- 范围：evaluate_thesis 纯函数核全文件（166 行）——四类买入理由分派（打板查梯队/多因子查漂移/事件查兑现/做T查趋势）→三态判定（ALIVE/WEAKENED/DEAD）；证据缺失→WEAKENED 不武断判死；阈值 config 注入（proposed）。
- 排除项：证据生产方（行情/事件源，调用方职责）；plan_deviation_monitor/execution_deviation_attributor（docstring :31-33 已声明正交分工）。
- 测试覆盖概况：三态×四类覆盖+阈值校验；无多理由复合持仓场景（模块本身也不支持，见轴 A）。
- 材料包缺项声明：运行时证据包未取（design 态无运行痕迹）；数据画像不适用。

## 2 六轴审查日志表

| 轴 | 发现 | 证据锚点 | 严重级 | 验证法 |
|---|---|---|---|---|
| C | **孤儿（design 态，声明诚实）**：零生产调用方；TDM-P-P1-03 的"失效=转离场评估"出边（→P1-06 动作清单/X 流）无人消费 DEAD 判定——四类判据的产出当前无处可达 | thesis_survival.py:5,7；grep evaluate_thesis src/ 零生产 | P2 | `grep -rn "evaluate_thesis" src/ --include=*.py` |
| A | **单理由假设未文档化为约束**：evaluate_thesis 按单一 ThesisType 分派（:118-124），一仓多理由（打板+事件双逻辑）只判一种——TDM algo_note"按买入理由逐仓回查"未声明单/多理由语义；复合逻辑仓的判定覆盖面取决于调用方标注纪律，模块不设防 | thesis_survival.py:107-124 | P3 | 读签名确认单类型入参 |
| A | 多因子漂移判据的量纲未定义：factor_exposure_drift ∈[0,1] 校验存在，但"漂移"如何从因子暴露算出（L1 距离? 相关性衰减? IC 变化?）无契约——调用方各自发明则同类仓位判定不可比；阈值 0.30/0.60 proposed 已声明 | thesis_survival.py:8,67-68,87-88 | P3 | 读 ThesisEvidence 字段注释确认无计算契约 |
| A | 事件仓 decay 语义双关：字段名 event_decay_ratio 注释"衰减/兑现度"，判定按"兑现度"（>0.8 =利好兑现完→DEAD）——若调用方按字面"衰减比例"喂入（衰减 80%=事件快死），语义恰好相反（衰减 80% 应该 DEAD 但按兑现度喂入方向一致；若喂"剩余动能 0.2"则判定反转）——无枚举约束，方向错误静默 | thesis_survival.py:89,148-157 | P3 | 喂 0.2（剩余动能口径）看 ALIVE（语义反转例） |
| B | 证据快照无时效字段：ThesisEvidence 无 observed_at/as_of——盘前判定用隔夜证据还是实时证据不可辨；PIT 纪律靠调用方自觉 | thesis_survival.py:83-96 | P3 | 读 dataclass 确认无时间字段 |
| A(亮点) | 证据缺失→WEAKENED 的"不确定不武断判死"设计优秀（判死=触发离场高代价动作，须明确证伪）；阈值单调校验（weak<dead）完备；frozen 三件套纯函数确定性；类型驱动分派清晰 | thesis_survival.py:27-28,72-80,107-124 | — | — |

## 3 SOTA 对照

- 按买入 thesis 存活性的离场判定：**对等已有**——thesis-based investing / "sell when the reason you bought is gone" 是基本面与事件驱动交易的经典纪律（Investopedia Exit Strategy 词条族，investopedia.com，2026；与本项目 42 号卖出流"逻辑失效"桶同构）；四分类判据与 A 股语境（打板梯队/做T底仓）适配合理。
- 证据缺失降预期不判死：**对等已有**——与本项目已固化纪律同构（37 号 hysteresis 无数据=不变、pf_alloc 空数据无罪推定），项目内自洽。
- 阈值 proposed 待回测校准：**对等已有（流程声明）**——参数分级治理（proposed→validated）是项目内体系，无需外部源。

## 4 缺陷清单

1. **[P2] 孤儿（design 态）+DEAD 出边无处可达**。建议修法：随 P1-06 动作清单/体检编排接线；接线前维持 design 声明（勿升 production）。验证法：grep。
2. **[P3] 事件 decay 字段语义双关（兑现度 vs 衰减度方向相反）**。建议修法：字段改名 event_realized_ratio 或注释加"必须喂兑现度（0=未兑现，1=完全兑现）"铁律+测试锁定。验证法：0.2 反转探针。
3. **[P3] 漂移量纲未定义+证据无时效+单理由假设未声明**。建议修法：蓝图补三行契约（drift 计算式/observed_at 必填/多理由仓=调用方逐理由分别调用取最严）。验证法：读蓝图 diff。

## 5 挂起疑问

- 多理由复合仓的判定聚合规则（取最严=任何 DEAD 即离场 vs 投票）待接线设计时裁定——本报告建议取最严（离场评估是高代价但可逆的人工确认面）。
- 阈值 0.30/0.60/0.50/0.80 的回测校准数据源（哪些历史事件样本）未登记。

## 6 完备性自评

六轴全查（A 数学四问：三段阈值判定单调无交叠/边界=证据缺失与越界已测/量纲契约缺口已记；B 上游=证据由调用方注入的契约边界已声明并审；C 下游=零调用方判孤儿（design 态诚实）；D=与 plan_deviation_monitor/execution_deviation_attributor 正交分工核读无双承载；E 五问：静默失败=decay 双关方向错、假阳性=无、断供=缺失→WEAKENED（已防）、重复触发=纯函数幂等、时序=无时钟依赖（证据时效缺口已记）。长尾：①证据生产方（情绪梯队/因子漂移/事件兑现度/趋势判定四路）全部未审（各自因子/事件域对象）；②蓝图文档与代码一致性只抽查 INVARIANTS 行。

## 7 收口裁定（收口方填）
- 三态逐条: 
- 修复 commit: 
- 复检结论: 
