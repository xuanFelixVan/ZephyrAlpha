---
blueprint_id: MOD-SIG-089
module_name: auction_microstructure_analyzer
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: testing
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.0"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
---

# MOD-SIG-089 auction_microstructure_analyzer 蓝图

> 设计真源：AUD-DRAFT-001 深挖批 B1-00171（开盘竞价微结构分析模型，裁定=做 P1）+
> 候选注册表 CAND-TESTB-004。代码：`src/zephyr/signal_ashare/auction_microstructure_analyzer.py`

## 0. 定位

竞价命中记录器在（MOD-PLAN-015 auction_hit_recorder），竞价信息提取/行为分类/
信号生成模型未成（深挖裁定理由）。本模块是**竞价三件套**：

1. **9:15-9:25 量价特征提取**：虚拟撮合价漂移、虚拟撮合量斜率、撤单率、
   封单变化、9:20 后（不可撤单段）量占比。
2. **行为分类**（规则引擎，MVP）：抢筹（价升+低撤单+封单增）/诱多（早段价升
   +高撤单+9:20 后封单塌）/压价（价跌+封单缩）/中性。
3. **竞价信号输出**：AuctionSignal（方向/置信度/特征明细），候选消费方=
   盘前计划（D_PLAN）与打板监控。

与既有件边界：MOD-PLAN-015 auction_hit_recorder 管"竞价结果命中记录"（盘后
对账），本模块管"竞价过程微结构解读"（盘前信号），数据正交不合并。

## 1. 接口

```python
class AuctionBehavior(str, Enum)     # 抢筹/诱多/压价/中性
@dataclass(frozen=True) class AuctionSnapshot      # 单时点竞价快照
@dataclass(frozen=True) class AuctionMicroConfig   # 阈值全可配
@dataclass(frozen=True) class AuctionFeatures      # 提取的五族特征
@dataclass(frozen=True) class AuctionSignal        # 行为+方向+置信度
def analyze_auction(symbol, snapshots, config=None) -> AuctionSignal
```

## 2. 纪律

- 快照时间戳须严格递增、价格/量非负，违例 ValueError（fail-closed）；
  空快照序列 ValueError；单快照退化为 NEUTRAL+notes（特征不全非异常）。
- 撤单率=累计撤单量/累计申报量（申报为 0 → 0.0 并留 notes）。
- 置信度=命中规则条数/该行为规则总数（文档化 MVP 初拍，待回验标定）。
- frozen dataclass、to_dict JSON 可序列化；纯函数核，不直连 DB/行情。
