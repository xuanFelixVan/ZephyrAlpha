# [BLUEPRINT] MOD-INF-029 | docs/03_modules/_cross_layer/orphan_judge/blueprint.md | §7.3
# [MODULE] zephyr.security.access_control.orphan_judge.swid_tag
# [DOMAIN] D_SECURITY
# [DEPENDENCIES] zephyr.security.access_control.orphan_judge.models
# [CONSUMERS] orphan-judge.db.JudgmentDB; report_generator
# [STARTUP] imported
# [MATURITY] production
# [INVARIANTS] 生成SWID标签记录文件来源和判决归属
# [MODIFY-GUARD] SWID标签格式变更时同步blueprint.md §7.3
# [STABILITY] evolving
# [SAFETY] M
# [AI_AUTONOMY] ai_modifiable
# [ERROR_CONTRACT] 生成失败返回空标签
# [TESTS] tests/orphan-judge/test_swid_tag.py
# [A_module] module_id=MOD-INF-029 | layer=module | stability=evolving | safety=L | ai_autonomy=ai_modifiable
# [TTL] permanent
"""


# [ALGO_FLOW]
# 层: 输入
# - id: I1
#   name: record 参数
#   fields: 参数 record，类型注解 JudgmentRecord
#   code: swid_tag.py 顶层公共函数形参（AST 提取）
# - id: I2
#   name: file_content 参数
#   fields: 参数 file_content，类型注解 str
#   code: swid_tag.py 顶层公共函数形参（AST 提取）
# - id: I3
#   name: tag_creator 参数
#   fields: 参数 tag_creator，类型注解 str
#   code: swid_tag.py 顶层公共函数形参（AST 提取）
# - id: I4
#   name: tag_id 参数
#   fields: 参数 tag_id，类型注解 str | None
#   code: swid_tag.py 顶层公共函数形参（AST 提取）
# 层: 算法
# - id: A1
#   name_zh: ① SwidTag
#   name_en: SwidTag
#   intro: class SwidTag 源码 L79-L85
#   desc: 公共方法（定义序）: build；源码 L79-L85
#   inputs: tag_creator
#   outputs: 返回值
# - id: A2
#   name_zh: ② generate_swid
#   name_en: generate_swid
#   intro: generate_swid(record, file_content, tag_creator, tag_id) 源码…
#   desc: 源码 L88-L123
#   inputs: record file_content tag_creator tag_id
#   outputs: dict[str, Any]
# 层: 输出
# - id: O1
#   name_zh: dict[str, Any]
#   name_en: dict[str, Any]
#   intro: 顶层公共函数返回值（真实返回注解，AST 提取）
#   downstream: orphan-judge.db.JudgmentDB; report_generator
# [/ALGO_FLOW]
#
# 边:
# I1 --> A1
# I2 --> A1
# I3 --> A1
# I4 --> A1
# A1 --> A2
# A2 --> O1
"""

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
