---
ttl: task_bound
title: M4 分册02 — capability_lookup 反查注册表（RULE-CAPABILITY-LOOKUP 审计面）
lane: m4_ai_layer
session: st-commitspeed-tbl-20260924
date: 2026-09-25
status: mined
---

# 02 — CapabilityLookup 审计面

## 一、环节定义与边界

`zephyr.governance.capability_lookup`（`src/zephyr/governance/capability_lookup.py`，1672 行，MOD-INF-037，MATURITY=production）：能力→真源文件反查注册表。宪法 RULE-CAPABILITY-LOOKUP 的执行体——写第一行业务代码前 `capability_lookup.find(<kw>, session_id=<sid>)` 或 MCP `rule_discovery` 留审计。上游=YAML 能力索引真源+磁盘扫描+git log 派生；下游=AI 会话（查询）、GitCommitGateway（check_ssot_conflicts/check_capability_duplicates 两 gate）、scaffold。

## 二、六向台账

| 向 | 实测证据 |
|---|---|
| 上游输入 | YAML 真源=`docs/01_policies_and_standards/_registry/catalogs/capability_canonical_file_registry.yaml`（py:97-100 常量+summary 实测 yaml_path）；扫描根=`src/zephyr`+`scripts/governance`（summary scan_roots 实测） |
| 下游消费 | 头部 CONSUMERS 声明（py:5）：AI sessions/GitCommitGateway/scaffold/check_ssot_gate；CLI `python -m zephyr.governance.capability_lookup --find/--list-conflicts/--check-file` |
| 自动化触发 | 按需调用型（STARTUP manual）；初始化即扫盘+派生（"无需同步"设计原则④，查询时实时算零持久化投影） |
| 真源与注册表 | YAML 人工只声明 capability_id/aliases/description（+override/manual）；canonical_file/module_id/blueprint_id/domain/maturity/duplicates/removed_duplicates 全部磁盘扫描+git log 自动派生（INVARIANTS py:8） |
| 门禁与质量尺 | 审计面=`.runtime/lookup_audit/<session_id>.jsonl`（LOOKUP_AUDIT_DIR py:109-110；write_lookup_audit_log py:297，best-effort fail-open，gate 端对 log 缺失 fail-closed 补位）；tests/capability/test_capability_lookup.py |
| 当前运行状态 | **绿**。实测 summary：total_declared=388 / alive=367 / dead=21 / with_duplicates=27 / ssot_conflicts=2 / pending_candidates=32551 |

## 三、审计面实测（今晚真流量证据）

- `.runtime/lookup_audit/` 按 session 分文件 jsonl，**今晚多会话在写**：st-commitspeed-tbl-20260924.jsonl（本会话）、st-metaq-20260923.jsonl、st-metaq-gc-20260924.jsonl、st-cmd-20260924.jsonl、st-mapbuild-20260924.jsonl、st-audit-fix-20260924.jsonl、st-wm1-wave0-20260924.jsonl、st-cleanup-final-20260924.jsonl 等
- 条目形态实测：`{"ts": "...", "tool": "capability_lookup.find", "query": {"keyword": "..."}, "result_count": 0, "rule_ids": []}`
- MCP 侧对称件：rule_discovery_server.write_lookup_audit_log（py:309-321 注释声明对称设计）
- AI 层反查命中实测：`--find redline` → obj_s_redline 卡，canonical=src/zephyr/ai_layer/redline/negative_list.py（canonical_override 人工钉定），aliases 含"OBJ_S红线/负面清单机检/自由域周报"等

## 四、capability 卡与 AI 层覆盖

- `data/capability_cards/` 共 44 卡，其中 AI 层 10 张：ai_perceive_l1 / ai_intake_l2 / ai_cleaning_l3 / ai_comparator_l4 / ai_scheduling_l5 / ai_switch_l6 / ai_heritage_l7 / obj_m_models / obj_s_redline / obj_t_tools（ailayer 战役接线批产物，红蓝抽验"lookup 可发现 5/5"在案）
- 另有 skill_dom_lsg_001（LSG 卡）、meta_question_registry 卡（metaq 消费面卡）

## 五、堵点与病灶

1. **ssot_conflicts=2**：summary 实测两处同蓝图多实现冲突未清——根因=重构批（HeritageStore 拆分等）落地滞后使新旧 basename 并存窗口拉长；修法=v4 批落地后重扫，歧义补 canonical_override
2. **pending_candidates=32551 海量**：磁盘 basename 候选池远大于声明 388——属设计内（ARCH-031 局限2 文档化：能力发现≠符号发现，Grep 补位），非病灶；但数值级膨胀值得关注（扫描根只含 src+scripts/governance，候选主要来自 src 全树 basename）
3. **审计 fail-open 不对称**：写侧 best-effort（log 故障不抛），读侧 gate fail-closed——单侧故障时会话可无审计通过 find；修法意见=高敏域（施工类 find）可加抽查比对，暂无必要（gate 已兜底）

## 六、自审闸三态

**挖干可施工**：六向全实证+审计面今晚真流量在案+388 能力/10 AI 卡两源交叉。无待裁项。

## 七、复核命令

```bash
python -m zephyr.governance.capability_lookup --find "redline"
python -c "from zephyr.governance.capability_lookup import CapabilityLookup; s=CapabilityLookup().summary(); print(s)"
ls .runtime/lookup_audit/ | tail -8
ls data/capability_cards/ | grep -cE "ai_|obj_"
```
