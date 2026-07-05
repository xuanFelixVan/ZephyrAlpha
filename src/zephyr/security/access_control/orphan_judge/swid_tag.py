# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §7.3
# [MODULE] zephyr.security.access_control.orphan_judge.swid_tag
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.orphan_judge.models
# [CONSUMERS] orphan-judge.db.JudgmentDB; report_generator
# [STARTUP] imported
# [MATURITY] prototype
# [INVARIANTS] 生成SWID标签记录文件来源和判决归属
# [MODIFY-GUARD] SWID标签格式变更时同步blueprint.md §7.3
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 生成失败返回空标签
# [TESTS] tests/orphan-judge/test_swid_tag.py
# [A_module] module_id=MOD-SEC_swid_tag | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
import hashlib
import uuid
from typing import Any

from zephyr.security.access_control.orphan_judge.models import JudgmentRecord

__all__ = ["SwidTag", "generate_swid"]


class SwidTag:
    def __init__(self, tag_creator: str = "orphan-judge") -> None:
        self.tag_creator = tag_creator
        self.tag_id: str = str(uuid.uuid4())

    def build(self, record: JudgmentRecord, file_content: str = "") -> dict[str, Any]:
        return generate_swid(record, file_content, self.tag_creator, self.tag_id)


def generate_swid(
    record: JudgmentRecord,
    file_content: str = "",
    tag_creator: str = "orphan-judge",
    tag_id: str | None = None,
) -> dict[str, Any]:
    file_hash = hashlib.sha256(file_content.encode("utf-8")).hexdigest() if file_content else record.file_hash

    return {
        "swid_tag": {
            "tag_id": tag_id or str(uuid.uuid4()),
            "tag_version": 0,
            "tag_creator": tag_creator,
            "software_identity": {
                "name": record.path,
                "unique_id": f"zephyr-alpha:{record.path}",
                "version_scheme": "multipartnumeric",
            },
        },
        "entity": {
            "name": "ZephyrAlpha-OrphanJudge",
            "reg_id": "zephyr-alpha.dev",
            "role": "tagCreator",
        },
        "evidence": {
            "created_at": record.scanned_at.isoformat(),
            "file_hash_sha256": file_hash,
            "verdict": record.verdict,
            "confidence": record.confidence,
        },
        "payload": {
            "path": record.path,
            "reason": record.reason,
            "layers": record.layers_json,
        },
    }
