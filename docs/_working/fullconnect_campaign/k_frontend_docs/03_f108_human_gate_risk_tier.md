---
ttl: task_bound
title: L11 案卷 F108 — 人机门位（域风险分级 18 条→四类 Owner 门位，REG-RISK-TIER-001）
session: zc-l11-20260927
---

# F108 人机门位（K 段 G12，骨架态=built/P1）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | 真源=`docs/01_policies_and_standards/_registry/catalogs/risk_tier_registry.yaml`（REG-RISK-TIER-001，last_updated 2026-09-12，本日头读实证）；默认档 default_tier 键在册 |
| 下游消费 | 生产消费方本日 grep 实取 5+：ai_layer/switch_engine/approval_router.py、ai_layer/scheduling/router.py、ai_layer/redline/no_delete_manifest.py、governance/audit/reconciliation_registry.py、trading/decision_map.py |
| 自动化触发 | 无独立守护件——门位在消费方决策路径内联判（approval_router 审批路由、reconciliation 对账判定）；宪法 §5"未列出域默认 low"由 default_tier 承载 |
| 真源与注册表 | domain_tiers=**18 条**（本日 yaml 实测，与总册"18 条"吻合）；样例=D_EX_CORE tier=high，human_gate 4 门（首次施工转 production/注册表净删/flag 出厂翻转/资金破坏性操作）——四类 Owner 门位字面实证 |
| 门禁与质量尺 | 门位与 gate 体系分离（宪法 §5.3"门禁强度由 gate 体系独立保证"）；entry_schema 键在册=条目结构受控 |
| 当前运行状态 | **绿**：18 域分级+5 生产消费方+四门样例齐；黄点=high 域门位的触发是否全部走裁定登记（宪法 §9.11 口径）未逐域核=P2 待挖 |

## 二、子模块三级枚举（册内三级：tier→domain→human_gate）

1. **tier 层**：high/medium/low 三档（default_tier=low 兜底；tiers 键在册）。
2. **domain_tiers 层**：18 条（本日 len 实测），样例锚=D_EX_CORE/high/rationale"实盘执行引擎/订单状态机，资金安全直接承载"。
3. **human_gate 层**：每域 4 门位（production 流转/注册表净删/flag 出厂翻转/资金破坏性操作）——与宪法 §5.2 四类一一对应。
4. **消费件层**：approval_router（J 段开关引擎审批）、scheduling/router（AI 层排产路由）、no_delete_manifest（红线禁删）、reconciliation_registry（对账判定）、decision_map（TDM 挂轴）。

## 三、接线四态独立复核

- **册→消费方：已接线**（5 文件 import/读取锚，本日 grep 实取）。
- **Owner 门位执行链：半接线待证**——门位"是否触发即登记 ruling_registry/§99 台账"未见机械强制（99_skipped_for_owner 台账为人工登记面）；四门逐门触发留痕抽样未做。
- **未列出域默认 low：已接线**（default_tier 键）。
- **停用/弃用：无**。

### 骨架勘误
1. 无口径冲突；总册"18 条"与册内 domain_tiers=18 本日吻合（前日案例多为漂移，此条为吻合样本，录为对照）。
2. 补充：册 last_updated=2026-09-12（宪法定版日同窗刷新），支持"宪法§5 真源=本册"口径。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | high 域门位触发留痕无机械强制 | 门位触发即写裁定登记的 gate 化（与 §99 台账对账） | P2 |
| 2 | 18 域之外新域入册时效 | 新域登记随施工批强制项（NEW-FILE-DEPGRAPH 同款挂点候选） | P2 |

## 五、自审闸三态

**挖干（18 条 yaml 复数+四门样例+5 消费方 grep）✅；待裁（无）；待挖（四门触发留痕抽样=P2）。**

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
python -c "
import yaml;from pathlib import Path
d=yaml.safe_load(Path('docs/01_policies_and_standards/_registry/catalogs/risk_tier_registry.yaml').read_text(encoding='utf-8'))
print('domain_tiers=',len(d['domain_tiers']));print(d['domain_tiers'][0]['domain'],d['domain_tiers'][0]['tier'],len(d['domain_tiers'][0]['human_gate']))"
grep -rln "risk_tier_registry" src/zephyr --include="*.py" | grep -v __pycache__ | head -6
```
