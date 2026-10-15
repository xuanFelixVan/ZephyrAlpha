---
blueprint_id: MOD-SIG-089
module_id: MOD-SIG-089
module_name: auction_microstructure_analyzer
domain: D_ASHARE_SIGNAL
doc_type: blueprint
ttl: permanent
design_maturity: design
stability: evolving
safety_level: M
ai_autonomy: ai_modifiable
version: "0.1.1"
created: 2026-08-25
last_updated: 2026-08-25
owner: ZephyrAlpha-Owner
responsibility_domain: 
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

---

## 3. 已实现代码完整路径索引

> **蓝图-代码同步强制约定**（稳定锚：AGENTS.md RULE-DEPGRAPH / RULE-PANORAMA；验证端 validate_blueprint_code_sync.py）——本节是蓝图与磁盘代码的「地址簿」。
> 蓝图声称的文件必须与磁盘实际一致。不一致 = 蓝图漂移 = 下一个 AI session 冷启动时被误导。
> **AUTOGEN**：本表由 sync_blueprint_code_index.py 从 depgraph.nodes 运营态（build_status∈generated/testing/stable）单向派生，禁止手写；重跑本脚本幂等更新。
> 

### 3.1 源码文件

| 文件路径 | 实现状态 | 说明 |
|---------|:---:|------|
| — | — | 本模块尚无已实现代码 |

### 3.5 路径索引使用指南

**新 AI session 读取顺序**：
1. 读本蓝图 §3（本节）→ 知道「哪些已实现、在哪里」
2. 读模块分解 → 知道「每个模块的职责和 AI 自治权限」
3. 读施工 Phase 规划 → 知道「下一步该做什么」

**路径约定**：
- 所有路径相对于仓库根目录（REPO_ROOT，不写死盘符绝对路径）
- 源码在 `src/zephyr/` 下
- 测试在 `tests/` 下
- 配置在 `config/` 下
- 治理脚本在 `scripts/governance/` 下

### §0.6 五图对齐视图

<!-- AUTOGEN: source=depgraph+dataflow+decision, generator=generate_blueprint_panorama.py, reconciler=sync_panorama_module.py -->

> **自动生成**：本节由 generate_blueprint_panorama.py 从全景真源派生，禁止手写。
> 生成命令：`python scripts/governance/d5_architecture/generators/generate_blueprint_panorama.py MOD-SIG-089`

#### 全景位置

| 图 | 位置 | 状态 | 链接 |
|----|------|------|------|
| 依赖图 (depgraph) | `blueprint_id=MOD-SIG-089` 的 2 个 file 节点 | design | `extract_depgraph.py --modules MOD-SIG-089` |
| 数据流图 (dataflow) | 0 个 Dataset / 1 个 Job | planned | `apply_dataflowgraph.py --list-datasets` |
| 决策架构图 (decision) | 0 个决策节点 / 1 个决策层 | N/A | `generate_decision_diagram.py` |
| 蓝图 (blueprint) | 本文件 | Draft | — |

#### 四核心字段

| 字段 | depgraph 值（真源） | 蓝图 frontmatter 值（声明） | 是否一致 |
|------|-------------------|--------------------------|:-------:|
| module_id | MOD-SIG-089 | MOD-SIG-089 | ✅ |
| domain_id | N/A | N/A | ✅ |
| build_status | planned | N/A | — |
| file_count | 2 文件 | N/A | — |

> 冲突时以 depgraph 为准（ARCH-056 + ARCH-MM-001 声明 vs 验证框架）。
