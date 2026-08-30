# [BLUEPRINT] MOD-INF-020 | docs/03_modules/_domain-governance/audit-trail/blueprint.md
# [MODULE] zephyr.gov_audit.provenance_tracker
# [DOMAIN] D_GOV_AUDIT
# [DEPENDENCIES]
# [CONSUMERS] MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 不可变审计记录;密码学完整性;只追加
# [MODIFY-GUARD] docs/03_modules/_domain-governance/audit-trail/blueprint.md;src/zephyr/audit-trail/__init__.py
# [STABILITY] stable
# [SAFETY] H
# [AI_AUTONOMY] immutable_core
# [ERROR_CONTRACT] IntegrityError;WriteError
# [TESTS] tests/test_audit_trail/
# [A_module] module_id=MOD-INF-020 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent

"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: module_id 参数
#   fields: 参数 module_id，类型注解 str
#   code: provenance_tracker.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: source_section 参数
#   fields: 参数 source_section，类型注解 str
#   code: provenance_tracker.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: agent_session_id 参数
#   fields: 参数 agent_session_id，类型注解 str
#   code: provenance_tracker.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: target_dict 参数
#   fields: 参数 target_dict，类型注解 dict[str, object]
#   code: provenance_tracker.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① generate_provenance
#   name_en: generate_provenance
#   intro: generate_provenance(module_id, source_section, agent_sessio…
#   desc: 源码 L115-L125
#   inputs: module_id source_section agent_session_id
#   outputs: ProvenanceRecord
# - id: A2
#   name_zh: ② embed_provenance
#   name_en: embed_provenance
#   intro: embed_provenance(target_dict, record) 源码 L128-L135
#   desc: 源码 L128-L135
#   inputs: target_dict record
#   outputs: dict[str, object]
# - id: A3
#   name_zh: ③ extract_provenance
#   name_en: extract_provenance
#   intro: extract_provenance(obj) 源码 L138-L147
#   desc: 源码 L138-L147
#   inputs: obj
#   outputs: ProvenanceRecord | None
# - id: A4
#   name_zh: ④ is_session_owned
#   name_en: is_session_owned
#   intro: is_session_owned(prov, session_id) 源码 L150-L151
#   desc: 源码 L150-L151
#   inputs: prov session_id
#   outputs: bool
# - id: A5
#   name_zh: ⑤ provenance_key
#   name_en: provenance_key
#   intro: provenance_key(prov) 源码 L154-L155
#   desc: 源码 L154-L155
#   inputs: prov
#   outputs: str
#   （注：A5 之后另有 1 个公共定义未列入（含 1 个数据契约/异常/枚举声明类），见源码）
# 层: 输出
# - id: O1
#   name_zh: ProvenanceRecord
#   name_en: ProvenanceRecord
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# - id: O2
#   name_zh: dict[str, object]
#   name_en: dict[str, object]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: MOD-INF-027;MOD-INF-015;MOD-FEEDBACK_LOOP
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> A3
# A3 --> A4
# A4 --> A5
# A5 --> O1
"""

from __future__ import annotations

from datetime import UTC, datetime

from pydantic import BaseModel


class ProvenanceRecord(BaseModel):
    module_id: str
    source_section: str
    agent_session_id: str
    generated_at: str


def generate_provenance(
    module_id: str,
    source_section: str,
    agent_session_id: str = "session-20260507-005",
) -> ProvenanceRecord:
    return ProvenanceRecord(
        module_id=module_id,
        source_section=source_section,
        agent_session_id=agent_session_id,
        generated_at=datetime.now(UTC).isoformat(),
    )


def embed_provenance(target_dict: dict[str, object], record: ProvenanceRecord) -> dict[str, object]:
    target_dict["__provenance__"] = {
        "module_id": record.module_id,
        "source_section": record.source_section,
        "agent_session_id": record.agent_session_id,
        "generated_at": record.generated_at,
    }
    return target_dict


def extract_provenance(obj: object) -> ProvenanceRecord | None:
    prov = getattr(obj, "_zephyr_provenance", None) or getattr(obj, "__provenance__", None)
    if isinstance(prov, dict):
        return ProvenanceRecord(
            module_id=str(prov.get("module_id", "UNKNOWN")),
            source_section=str(prov.get("source_section", "UNKNOWN")),
            agent_session_id=str(prov.get("agent_session_id", "UNKNOWN")),
            generated_at=str(prov.get("generated_at", "")),
        )
    return None


def is_session_owned(prov: ProvenanceRecord, session_id: str) -> bool:
    return prov.agent_session_id == session_id


def provenance_key(prov: ProvenanceRecord) -> str:
    return f"{prov.module_id}/{prov.source_section}"
