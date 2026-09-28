---
ttl: task_bound
title: L09 案卷 F91 — 能力反查渐进披露（CapabilityLookup 388 声明/44 卡/审计面）
session: zc-l09-20260927
---

# F91 能力反查渐进披露（J 段 A6，骨架态=built/P2）

## 一、六向台账（2026-09-27 实证）

| 向 | 实测证据 |
|---|---|
| 上游输入 | YAML 真源=`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`；扫描根=src/zephyr+scripts/governance；磁盘扫描+git log 派生（canonical_file/module_id/domain/maturity 全派生，禁手填） |
| 下游消费 | AI 会话查询+GitCommitGateway 两 gate（check_ssot_conflicts/check_capability_duplicates）+scaffold+MCP rule_discovery（对称审计 py:309-321）；**F93 library.lookup 引用（capability_lookup.py 内，本日 grep 实证两系统互链）** |
| 自动化触发 | 按需调用型（查询时实时算零持久化投影）；审计面 `.runtime/lookup_audit/<session>.jsonl` 按会话落盘（M4 实测多会话真流量） |
| 真源与注册表 | 人工只声明 capability_id/aliases/description；m3_governance 03 册：能力卡 44 张（手工）+capability canonical 册（结构型）双面在册 |
| 门禁与质量尺 | 审计写侧 best-effort fail-open、读侧 gate fail-closed 不对称设计（M4-02 §五.3）；tests/capability/test_capability_lookup.py |
| 当前运行状态 | **绿（本日 summary 实跑）**：total_declared=388 / alive=367 / dead=21 / with_duplicates=27 / ssot_conflicts=2 / pending_candidates=33042 |

## 二、子模块三级枚举

1. 查询体：`zephyr.governance.capability_lookup`（1672 行，MOD-INF-037，MATURITY=production）；CLI `--find/--list-conflicts/--check-file`。
2. 卡面：`data/capability_cards/` 44 卡；其中 AI 层 10 张（ai_perceive_l1…obj_t_tools）+skill_dom_lsg_001（F88 卡）+meta_question_registry 卡（F92 消费面卡）。
3. 审计面：`.runtime/lookup_audit/` 会话级 jsonl（工具名/查询/结果数/rule_ids 四字段形态，M4 实锚）。
4. MCP 对称件：rule_discovery_server.write_lookup_audit_log（双通道同构审计）。
5. 派生面：ssot_conflicts/duplicates/removed_duplicates 三投影（INVARIANTS py:8 声明）。

## 三、接线四态独立复核

- **查询主链=已接线**：本日实跑 summary 正常（388/367/21/27/2/33042 六字段全出）。
- **gate 消费=已接线**：两 gate 挂 GitCommitGateway（M4-02 头 CONSUMERS+gate 名录）；ssot_conflicts=2 两处冲突未清（维持 M4 判定）。
- **卡面=已接线**：44 卡与 AI 层 10 张双实存（m3 03 册+本日 ls 双源）。
- **漂移点=登记两处**：①pending_candidates 32551→33042（5 日 +491，候选池膨胀维持"设计内、数值级关注"判定）；②与 F93 互链（capability_lookup 引 library.lookup）是骨架未记的新消费边（渐进披露⇄图书馆双向发现）。

## 骨架勘误

1. 骨架"capability 378 条"与本日 total_declared=388 漂移（+10，AI 卡批次落地后增长）——骨架数字系时点值，按 RULE-REGISTRY 勿背数，以 summary 实跑为准。
2. 其余维持 built 判定，无矛盾。

## 四、缺口清单

| # | 缺口 | 处置 | 优先 |
|---|---|---|---|
| 1 | ssot_conflicts=2 未清（重构批新旧 basename 并存窗口） | v4/v6 批已落 HEAD，重扫后歧义补 canonical_override | P2 |
| 2 | pending_candidates 33042 候选池膨胀 | 设计内（能力发现≠符号发现，Grep 补位）；观察值级增速即可 | P2 |
| 3 | 审计 fail-open 不对称 | gate 端已 fail-closed 兜底；高敏域抽查比对缓行 | P2 |

## 五、自审闸三态

**挖干（summary 本日实跑+双册双源+互链新边）✅；无待裁；无待挖（P2 支线建成态，深挖无增量）。**

## 六、复跑命令

```bash
export PATH="$LOCALAPPDATA/Programs/Python/Python312:$LOCALAPPDATA/Programs/Python/Python312/Scripts:$PATH"
python -c "from zephyr.governance.capability_lookup import CapabilityLookup; s=CapabilityLookup().summary(); print({k:s[k] for k in ('total_declared','alive','dead','with_duplicates','ssot_conflicts','pending_candidates')})"
python -m zephyr.governance.capability_lookup --find "redline"
ls data/capability_cards/ | wc -l    # 44
```
